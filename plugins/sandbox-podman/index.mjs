// sandbox-podman: DSH's `ctx.sandbox` provider that runs confined commands inside the task's container.
//
// DSH routes every command it runs through `ctx.sandbox.confine(argv, policy)`: bash (one process per call),
// background jobs and glob/grep (ripgrep). The local provider wraps that argv in bwrap or Landlock; this one wraps
// it in `podman exec` into a running container (podman-exec.sh). The tools themselves are unchanged.
//
// The container mounts the workspace at the same absolute path as the host, so a path means the same thing to the
// file tools (they run on the host, in DSH) and to bash (container). The container must already be running; the
// launcher starts and stops it.
//
// Row (replaces the base profile's `sandbox` row):
//   - id: sandbox
//     disabled: true
//   - insert:
//       - id: sandbox-podman
//         name: <abs path>/plugins/sandbox-podman/index.mjs
//         config:
//           container: <name or id>          # required
//           runtime: podman                  # or docker
//           env: { WORKSPACE_DIR: /abs/ws }  # set inside the container for every command
//           hostCwd: /abs/host/dir           # optional: host directory the wrapper starts in, for a workspace that
//                                            # exists only in the container (default: the workspace path itself)
//
// The DSH checkout is found through $DSH_BENCH_DSH_ROOT, else ../../work/deepseek-harness from this file.
import { fileURLToPath, pathToFileURL } from 'node:url'
import { basename, isAbsolute, resolve } from 'node:path'

const HERE = fileURLToPath(new URL('.', import.meta.url))
const DSH_ROOT = process.env.DSH_BENCH_DSH_ROOT ?? resolve(HERE, '../../work/deepseek-harness')
const { SandboxProvider } = await import(pathToFileURL(`${DSH_ROOT}/packages/sandbox/sandbox/lib/index.js`).href)

// What a denied file effect looks like inside the container: a read-only mount, or file permissions.
const DENIAL_SIGNATURES = ['read-only file system', 'permission denied']
// podman / docker exit 125 when they fail to run the command at all (container gone, bad workdir).
const RUNNER_FAILURE_RULES = [{ allowedExitCodes: [125, 126], fatalSignatures: ['Error: ', 'Error response from daemon'] }]

export const name = 'sandbox-podman'

export default class PodmanSandboxProvider extends SandboxProvider {
  constructor(ctx, config = {}) {
    super(ctx)
    if (typeof config.container !== 'string' || config.container.length === 0) {
      throw new Error('sandbox-podman: config.container (the running container name or id) is required')
    }
    const env = config.env ?? {}
    for (const [key, value] of Object.entries(env)) {
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key) || typeof value !== 'string') {
        throw new Error(`sandbox-podman: env entry ${JSON.stringify(key)} must be a NAME with a string value`)
      }
    }
    this.settings = {
      container: config.container,
      runtime: config.runtime ?? 'podman',
      wrapper: config.wrapper ?? resolve(HERE, 'podman-exec.sh'),
      env,
      hostCwd: config.hostCwd,
    }
  }

  confine(argv, policy) {
    const { container, runtime, wrapper, env, hostCwd } = this.settings
    const workdir = policy.workingDirectory ?? policy.workspaceRoot
    let [program, ...args] = argv
    // glob/grep launch DSH's bundled ripgrep by its host path; the image provides `rg`.
    if (isAbsolute(program) && basename(program) === 'rg') program = 'rg'
    return {
      argv: [wrapper, runtime, container, workdir, ...Object.entries(env).map(([k, v]) => `${k}=${v}`), '--', program, ...args],
      cwd: hostCwd ?? policy.workspaceRoot,
      enforcement: 'full',
      denialSignatures: DENIAL_SIGNATURES,
      runnerFailureRules: RUNNER_FAILURE_RULES,
    }
  }
}
