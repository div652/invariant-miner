// fs-podman: DSH's `ctx.fs` backend inside a running container, so `read`, `write`, `edit` and `read_image` work on
// the container's files instead of the host's.
//
// The counterpart of sandbox-podman (which runs commands in the container): with both, every DSH tool sees the same
// files under the same paths. Modelled on DSH's own remote backend `@deepseek-ai/dsh-fs-e2b`; every operation is a
// `podman exec` (coreutils: realpath, stat, cat, head, dd, find, mktemp, ln, mv) in the container. Replaces the
// profile's `fs-sandbox` row.
//
// Containment is fixed, not a policy choice: every path is resolved inside the container (symlinks followed) and must
// lie under `root`, else `FS_SANDBOX_DENIED` with fs-sandbox's own wording for workspace-isolated mode. The
// container's other files (and anything a symlink points at outside `root`) are unreachable through these tools.
// `sandboxMode` reports the deployment default like fs-sandbox, so the tools' schemas are the same as with it.
//
// Row:
//   - id: fs-sandbox
//     disabled: true
//   - insert:
//       - id: fs-podman
//         name: <abs path>/plugins/fs-podman/index.mjs
//         config:
//           container: <name or id>   # required, running
//           root: /filesystem         # required: absolute path in the container; the only files the tools reach
//           cwd: /filesystem          # optional: base for relative paths (default: root)
//           runtime: podman           # optional (or docker)
//           diffBasisMaxBytes: 1048576  # optional: larger prior files get no diff basis on overwrite
import { spawn } from 'node:child_process'
import { createHash } from 'node:crypto'
import { posix, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = fileURLToPath(new URL('.', import.meta.url))
const DSH_ROOT = process.env.DSH_BENCH_DSH_ROOT ?? resolve(HERE, '../../work/deepseek-harness')
const { FileSystem, FsError, FsTargetKey, FsVersion } = await import(pathToFileURL(`${DSH_ROOT}/packages/fs/fs/lib/index.js`).href)

export const name = 'fs-podman'

const BINARY_SAMPLE_BYTES = 8192
const STAT_FORMAT = '%F\t%s\t%.9Y\t%.9Z\t%i\t%d\t%a'

function assertNotAborted(signal, operation) {
  if (signal?.aborted === true) throw new FsError(`${operation} aborted`, 'FS_ABORTED')
}

const normalizeLineEndings = value => value.replaceAll('\r\n', '\n')

function detectsCrlf(value) {
  const sample = value.slice(0, 4096)
  const crlf = sample.split('\r\n').length - 1
  const lf = sample.split('\n').length - 1 - crlf
  return crlf > lf
}

const restoreLineEndings = (value, crlf) => (crlf ? normalizeLineEndings(value).replaceAll('\n', '\r\n') : value)

function decodeText(bytes, displayPath, binarySampleBytes) {
  if (bytes.subarray(0, binarySampleBytes).includes(0)) {
    throw new FsError(`cannot read "${displayPath}": binary file`, 'FS_NOT_TEXT')
  }
  try {
    return new TextDecoder('utf-8', { fatal: true }).decode(bytes)
  } catch (error) {
    throw new FsError(`cannot read "${displayPath}": invalid UTF-8 text`, 'FS_NOT_TEXT', { cause: error })
  }
}

function literalEdit(content, request, displayPath) {
  const oldString = normalizeLineEndings(request.oldString)
  const newString = normalizeLineEndings(request.newString)
  if (oldString.length === 0) {
    throw new FsError(`cannot edit "${displayPath}": old_string must be non-empty`, 'FS_EDIT_NOT_FOUND')
  }
  let matches = 0
  let offset = 0
  while (true) {
    const found = content.indexOf(oldString, offset)
    if (found < 0) break
    matches += 1
    offset = found + oldString.length
  }
  if (matches === 0) throw new FsError(`cannot edit "${displayPath}": old_string was not found`, 'FS_EDIT_NOT_FOUND')
  if (!request.replaceAll && matches !== 1) {
    throw new FsError(`cannot edit "${displayPath}": old_string matched ${matches} times`, 'FS_AMBIGUOUS_EDIT')
  }
  return request.replaceAll ? content.split(oldString).join(newString) : content.replace(oldString, newString)
}

/** Parse one `stat -c STAT_FORMAT` line. */
function parseStat(line) {
  const [kind, size, mtime, ctime, inode, device, mode] = line.trim().split('\t')
  const type = kind === 'regular file' || kind === 'regular empty file' ? 'file'
    : kind === 'directory' ? 'directory'
      : kind === 'symbolic link' ? 'symlink' : 'other'
  const facts = JSON.stringify([kind, size, mtime, ctime, inode, device, mode])
  return { type, size: Number(size), mode, version: FsVersion(`podman:${createHash('sha256').update(facts).digest('hex')}`) }
}

const isUnder = (path, root) => {
  const relative = posix.relative(root, path)
  return relative === '' || (relative !== '..' && !relative.startsWith('../') && !posix.isAbsolute(relative))
}

/** Container-side filesystem backend; one `podman exec` per operation. */
export default class PodmanFileSystem extends FileSystem {
  static inject = ['sandboxPolicy']

  constructor(ctx, config = {}) {
    super(ctx)
    if (typeof config.container !== 'string' || config.container.length === 0) {
      throw new Error('fs-podman: config.container (the running container name or id) is required')
    }
    if (typeof config.root !== 'string' || !posix.isAbsolute(config.root)) {
      throw new Error('fs-podman: config.root must be an absolute path in the container')
    }
    const cwd = config.cwd ?? config.root
    if (!posix.isAbsolute(cwd)) throw new Error('fs-podman: config.cwd must be an absolute path in the container')
    this.settings = {
      container: config.container,
      runtime: config.runtime ?? 'podman',
      root: posix.normalize(config.root),
      cwd: posix.normalize(cwd),
      diffBasisMaxBytes: config.diffBasisMaxBytes ?? 1024 * 1024,
    }
    this.locks = new Map()
    this.canonicalRoot = undefined
  }

  /** The deployment default mode, as fs-sandbox reports it (the tools advertise escalation fields from it). */
  get sandboxMode() {
    return this.ctx.sandboxPolicy.defaultMode
  }

  // --- process plumbing --------------------------------------------------------------------------------------------

  /** Spawn `sh -c SCRIPT sh ARGS...` (or bash) in the container; positional args are never interpolated. */
  spawnIn(script, args, { input, shell = 'sh' } = {}) {
    const { runtime, container } = this.settings
    const argv = ['exec', ...(input === undefined ? [] : ['-i']), container, shell, '-c', script, shell, ...args.map(String)]
    return spawn(runtime, argv, { stdio: [input === undefined ? 'ignore' : 'pipe', 'pipe', 'pipe'] })
  }

  /** Run a script to completion: { code, stdout (Buffer), stderr (string) }. */
  run(script, args, { input, shell, signal } = {}) {
    return new Promise((resolvePromise, reject) => {
      const child = this.spawnIn(script, args, { input, shell })
      const out = []
      const err = []
      const onAbort = () => child.kill('SIGKILL')
      signal?.addEventListener('abort', onAbort, { once: true })
      child.stdout.on('data', chunk => out.push(chunk))
      child.stderr.on('data', chunk => err.push(chunk))
      child.on('error', reject)
      child.on('close', code => {
        signal?.removeEventListener('abort', onAbort)
        resolvePromise({ code, stdout: Buffer.concat(out), stderr: Buffer.concat(err).toString('utf8') })
      })
      if (input !== undefined) child.stdin.end(input)
    })
  }

  failure(result, operation, displayPath, signal) {
    if (signal?.aborted === true) return new FsError(`${operation} aborted`, 'FS_ABORTED')
    const message = result.stderr.trim()
    if (/No such file or directory/i.test(message)) return new FsError(`cannot ${operation} "${displayPath}": not found`, 'FS_NOT_FOUND')
    if (/Not a directory/i.test(message)) return new FsError(`cannot ${operation} "${displayPath}": not a directory`, 'FS_NOT_DIRECTORY')
    if (/permission denied|operation not permitted/i.test(message)) {
      return new FsError(`cannot ${operation} "${displayPath}": permission denied`, 'FS_PERMISSION_DENIED')
    }
    return new FsError(`cannot ${operation} "${displayPath}": ${message || `exit ${result.code}`}`, 'FS_IO_ERROR')
  }

  // --- paths and containment ---------------------------------------------------------------------------------------

  async canonical(path, signal) {
    const result = await this.run('realpath -m -- "$1"', [path], { signal })
    assertNotAborted(signal, 'resolve')
    if (result.code !== 0) throw this.failure(result, 'resolve', path, signal)
    const resolved = result.stdout.toString('utf8').replace(/\n$/, '')
    if (!posix.isAbsolute(resolved)) throw new FsError(`cannot resolve "${path}": not absolute in the container`, 'FS_IO_ERROR')
    return resolved
  }

  async rootPath(signal) {
    this.canonicalRoot ??= await this.canonical(this.settings.root, signal)
    return this.canonicalRoot
  }

  async assertContained(canonicalPath, displayPath, verb, signal) {
    if (isUnder(canonicalPath, await this.rootPath(signal))) return
    throw new FsError(`cannot ${verb} "${displayPath}": file access denied under workspace-isolated mode`, 'FS_SANDBOX_DENIED')
  }

  async resolve(path, opts) {
    assertNotAborted(opts?.signal, 'resolve')
    if (typeof path !== 'string' || path.trim().length === 0) throw new FsError('file_path must be a non-empty string', 'FS_NOT_FOUND')
    const displayPath = posix.resolve(opts?.cwd ?? this.settings.cwd, path)
    const targetKey = await this.canonical(displayPath, opts?.signal)
    await this.assertContained(targetKey, displayPath, 'access', opts?.signal)
    return { targetKey: FsTargetKey(targetKey), displayPath }
  }

  processPath(target) {
    return String(target.targetKey)
  }

  fileUrl(target) {
    return `file://${this.processPath(target).split('/').map(segment => encodeURIComponent(segment)).join('/')}`
  }

  contains(parent, child) {
    return isUnder(this.processPath(child), this.processPath(parent))
  }

  // --- metadata ------------------------------------------------------------------------------------------------------

  async probe(path, displayPath, { follow = true, signal } = {}) {
    assertNotAborted(signal, 'stat')
    const result = await this.run(`stat ${follow ? '-L ' : ''}-c '${STAT_FORMAT}' -- "$1"`, [path], { signal })
    assertNotAborted(signal, 'stat')
    if (result.code !== 0) {
      if (/No such file or directory/i.test(result.stderr)) return undefined
      throw this.failure(result, 'stat', displayPath, signal)
    }
    return parseStat(result.stdout.toString('utf8'))
  }

  async stat(target, signal) {
    const entry = await this.probe(String(target.targetKey), target.displayPath, { signal })
    if (entry === undefined) return undefined
    const type = entry.type === 'symlink' ? 'other' : entry.type
    return { version: entry.version, type, ...(type === 'file' ? { size: entry.size } : {}) }
  }

  async lstat(path, opts, signal) {
    assertNotAborted(signal, 'lstat')
    if (typeof path !== 'string' || path.trim().length === 0) throw new FsError('file_path must be a non-empty string', 'FS_NOT_FOUND')
    const displayPath = posix.resolve(opts?.cwd ?? this.settings.cwd, path)
    await this.assertContained(await this.canonical(displayPath, signal), displayPath, 'access', signal)
    const entry = await this.probe(displayPath, displayPath, { follow: false, signal })
    if (entry === undefined) return undefined
    return { version: entry.version, type: entry.type, ...(entry.type === 'file' ? { size: entry.size } : {}) }
  }

  async requireRegular(target, signal) {
    const info = await this.stat(target, signal)
    if (info === undefined) throw new FsError(`cannot read "${target.displayPath}": not found`, 'FS_NOT_FOUND')
    if (info.type !== 'file') throw new FsError(`cannot read "${target.displayPath}": not a regular file`, 'FS_NOT_REGULAR_FILE')
    return info
  }

  // --- reads ---------------------------------------------------------------------------------------------------------

  async readAll(target, operation, signal) {
    const result = await this.run('cat -- "$1"', [String(target.targetKey)], { signal })
    assertNotAborted(signal, operation)
    if (result.code !== 0) throw this.failure(result, operation, target.displayPath, signal)
    return new Uint8Array(result.stdout)
  }

  async readText(target, signal) {
    await this.requireRegular(target, signal)
    return decodeText(await this.readAll(target, 'read', signal), target.displayPath, BINARY_SAMPLE_BYTES)
  }

  async readBytes(target, signal, maxBytes) {
    const info = await this.requireRegular(target, signal)
    if (info.size !== undefined && info.size > maxBytes) {
      throw new FsError(`cannot read "${target.displayPath}": ${info.size} bytes exceeds the ${maxBytes}-byte limit`, 'FS_TOO_LARGE')
    }
    const result = await this.run('head -c "$2" -- "$1"', [String(target.targetKey), maxBytes + 1], { signal })
    assertNotAborted(signal, 'read')
    if (result.code !== 0) throw this.failure(result, 'read', target.displayPath, signal)
    if (result.stdout.length > maxBytes) {
      throw new FsError(`cannot read "${target.displayPath}": content exceeds the ${maxBytes}-byte limit`, 'FS_TOO_LARGE')
    }
    return new Uint8Array(result.stdout)
  }

  async readByteRange(target, range, signal) {
    await this.requireRegular(target, signal)
    if (range.length === 0) return new Uint8Array(0)
    const result = await this.run(
      'dd if="$1" iflag=skip_bytes,count_bytes skip="$2" count="$3" status=none',
      [String(target.targetKey), range.offset, range.length],
      { signal },
    )
    assertNotAborted(signal, 'read')
    if (result.code !== 0) throw this.failure(result, 'read', target.displayPath, signal)
    return new Uint8Array(result.stdout)
  }

  async streamText(target, signal) {
    await this.requireRegular(target, signal)
    const backend = this
    const displayPath = target.displayPath
    return {
      async *[Symbol.asyncIterator]() {
        const child = backend.spawnIn('cat -- "$1"', [String(target.targetKey)])
        const onAbort = () => child.kill('SIGKILL')
        signal?.addEventListener('abort', onAbort, { once: true })
        const stderr = []
        child.stderr.on('data', chunk => stderr.push(chunk))
        const exited = new Promise(resolvePromise => child.on('close', code => resolvePromise(code)))
        const decoder = new TextDecoder('utf-8', { fatal: true })
        let sampledBytes = 0
        let completed = false
        try {
          for await (const chunk of child.stdout) {
            assertNotAborted(signal, 'read')
            if (sampledBytes < BINARY_SAMPLE_BYTES) {
              const sample = chunk.subarray(0, BINARY_SAMPLE_BYTES - sampledBytes)
              if (sample.includes(0)) throw new FsError(`cannot read "${displayPath}": binary file`, 'FS_NOT_TEXT')
              sampledBytes += sample.length
            }
            let text
            try {
              text = decoder.decode(chunk, { stream: true })
            } catch (error) {
              throw new FsError(`cannot read "${displayPath}": invalid UTF-8 text`, 'FS_NOT_TEXT', { cause: error })
            }
            if (text.length > 0) yield text
          }
          const code = await exited
          if (code !== 0) {
            throw backend.failure({ code, stderr: Buffer.concat(stderr).toString('utf8') }, 'read', displayPath, signal)
          }
          try {
            decoder.decode()
          } catch (error) {
            throw new FsError(`cannot read "${displayPath}": invalid UTF-8 text`, 'FS_NOT_TEXT', { cause: error })
          }
          completed = true
        } finally {
          signal?.removeEventListener('abort', onAbort)
          if (!completed) child.kill('SIGKILL')
        }
      },
    }
  }

  // --- listing -------------------------------------------------------------------------------------------------------

  async listDir(target, signal) {
    const info = await this.stat(target, signal)
    if (info === undefined) throw new FsError(`cannot list "${target.displayPath}": not found`, 'FS_NOT_FOUND')
    if (info.type !== 'directory') throw new FsError(`cannot list "${target.displayPath}": not a directory`, 'FS_NOT_DIRECTORY')
    // One record per child: name NUL canonical-path NUL stat-line-or-MISSING NUL.
    const script = `find "$1" -mindepth 1 -maxdepth 1 -printf '%f\\0' | while IFS= read -r -d '' n; do
  p="$1/$n"; c="$(realpath -m -- "$p")"; s="$(stat -L -c '${STAT_FORMAT}' -- "$p" 2>/dev/null || echo MISSING)"
  printf '%s\\0%s\\0%s\\0' "$n" "$c" "$s"
done`
    const result = await this.run(script, [String(target.targetKey)], { shell: 'bash', signal })
    assertNotAborted(signal, 'list')
    if (result.code !== 0) throw this.failure(result, 'list', target.displayPath, signal)
    const fields = result.stdout.toString('utf8').split('\0')
    const entries = []
    for (let i = 0; i + 2 < fields.length; i += 3) {
      const [childName, canonicalPath, statLine] = fields.slice(i, i + 3)
      const displayPath = posix.join(target.displayPath, childName)
      await this.assertContained(canonicalPath, displayPath, 'access', signal)
      const meta = statLine === 'MISSING' ? undefined : parseStat(statLine)
      const type = meta === undefined || meta.type === 'symlink' ? 'other' : meta.type
      entries.push({
        name: childName,
        type,
        target: { targetKey: FsTargetKey(canonicalPath), displayPath },
        ...(meta !== undefined ? { version: meta.version } : {}),
        ...(type === 'file' ? { size: meta.size } : {}),
      })
    }
    return entries.sort((left, right) => left.name.localeCompare(right.name))
  }

  // --- writes --------------------------------------------------------------------------------------------------------

  async writeText(target, content, expected, signal) {
    const fresh = await this.resolve(target.displayPath, { signal })
    await this.assertContained(String(fresh.targetKey), target.displayPath, 'write', signal)
    return this.withLock(String(fresh.targetKey), async () => {
      const existing = await this.probe(String(fresh.targetKey), fresh.displayPath, { signal })
      if (existing !== undefined && existing.type !== 'file') {
        throw new FsError(`cannot write "${fresh.displayPath}": not a regular file`, 'FS_NOT_REGULAR_FILE')
      }
      if (expected?.kind === 'createIfAbsent' && existing !== undefined) {
        throw new FsError(`cannot overwrite existing "${fresh.displayPath}" without reading it first`, 'FS_NOT_OBSERVED')
      }
      if (expected?.kind === 'replaceIfVersion' && (existing === undefined || existing.version !== expected.version)) {
        throw new FsError(`cannot write "${fresh.displayPath}": file changed since it was read`, 'FS_STALE_VERSION')
      }
      let before = null
      if (existing !== undefined && existing.size <= this.settings.diffBasisMaxBytes) {
        try {
          before = normalizeLineEndings(decodeText(await this.readAll(fresh, 'read', signal), fresh.displayPath, Infinity))
        } catch (error) {
          if (!(error instanceof FsError && error.code === 'FS_NOT_TEXT')) throw error
        }
      }
      const version = await this.writeAtomic(fresh, content, existing, expected?.kind === 'createIfAbsent', signal)
      return { operation: existing === undefined ? 'create' : 'update', version, before, after: normalizeLineEndings(content) }
    })
  }

  async editText(target, edit, expected, signal) {
    const fresh = await this.resolve(target.displayPath, { signal })
    await this.assertContained(String(fresh.targetKey), target.displayPath, 'write', signal)
    return this.withLock(String(fresh.targetKey), async () => {
      const existing = await this.probe(String(fresh.targetKey), fresh.displayPath, { signal })
      if (existing === undefined) {
        throw new FsError(`cannot edit "${fresh.displayPath}": file changed since it was read`, 'FS_STALE_VERSION')
      }
      if (existing.type !== 'file') throw new FsError(`cannot edit "${fresh.displayPath}": not a regular file`, 'FS_NOT_REGULAR_FILE')
      if (expected !== undefined && existing.version !== expected.version) {
        throw new FsError(`cannot edit "${fresh.displayPath}": file changed since it was read`, 'FS_STALE_VERSION')
      }
      const raw = decodeText(await this.readAll(fresh, 'edit', signal), fresh.displayPath, Infinity)
      const before = normalizeLineEndings(raw)
      const after = literalEdit(before, edit, fresh.displayPath)
      const version = await this.writeAtomic(fresh, restoreLineEndings(after, detectsCrlf(raw)), existing, false, signal)
      return { version, before, after }
    })
  }

  async withLock(key, operation) {
    const prior = this.locks.get(key) ?? Promise.resolve()
    const run = prior.then(operation, operation)
    const tail = run.then(() => undefined, () => undefined)
    this.locks.set(key, tail)
    try {
      return await run
    } finally {
      if (this.locks.get(key) === tail) this.locks.delete(key)
    }
  }

  /** Stage the content next to the target, then publish it with one rename (or a guarded hard link for a create). */
  async writeAtomic(target, content, existing, createIfAbsent, signal) {
    assertNotAborted(signal, 'write')
    const script = `set -e
t="$1"; mode="$2"; create="$3"
d="$(dirname -- "$t")"; mkdir -p -- "$d"
tmp="$(mktemp -- "$d/.dsh-write-XXXXXXXX")"
trap 'rm -f -- "$tmp"' EXIT
cat > "$tmp"
chmod "$mode" -- "$tmp"
if [ "$create" = 1 ]; then
  if ln -T -- "$tmp" "$t" 2>/dev/null; then :; elif [ -e "$t" ] || [ -L "$t" ]; then echo EXISTS; exit 0; else exit 1; fi
else
  mv -f -T -- "$tmp" "$t"
fi
stat -c '${STAT_FORMAT}' -- "$t"`
    const mode = existing === undefined ? '644' : existing.mode
    const result = await this.run(script, [String(target.targetKey), mode, createIfAbsent ? 1 : 0], { input: Buffer.from(content, 'utf8'), signal })
    if (result.code !== 0) throw this.failure(result, 'write', target.displayPath, signal)
    const out = result.stdout.toString('utf8')
    if (out.trim() === 'EXISTS') {
      throw new FsError(`cannot overwrite existing "${target.displayPath}" without reading it first`, 'FS_NOT_OBSERVED')
    }
    return parseStat(out).version
  }
}
