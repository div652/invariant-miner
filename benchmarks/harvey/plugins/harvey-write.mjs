// harvey-write: Harvey LAB's `write` path rule on DSH's own `write` tool.
//
// Harvey's tasks name deliverables without a folder ("write your complete answer to `response.md`") and its grader
// reads only output/. Harvey's harness bridges that in its `write` tool: a relative path is written under the output
// directory (lab_core/harness/tools.py `_resolve_write_path`); an absolute path is used as is. This plugin gives DSH's
// `write` the same rule for Harvey runs only: a relative `file_path` becomes `output/<file_path>` before DSH's write
// runs (confinement, read-before-overwrite and output format are DSH's, unchanged). One safeguard Harvey lacks: a
// relative path that already starts with `output/` is not prefixed again.
//
// DSH lets no hook change a call's arguments, so the registered `write` definition's execute is wrapped in place, and
// its description says where relative paths go. `edit` and `read` keep DSH's rule (relative to the workspace).
//
// Row (benchmarks/harvey/patch.yml):
//   - insert:
//       - id: harvey-write
//         name: __BENCH_REPO__/benchmarks/harvey/plugins/harvey-write.mjs
//         config: { outputDir: output }
import { isAbsolute, normalize } from 'node:path'

export const name = 'harvey-write'
export const inject = ['tools']

export function routeWritePath(filePath, outputDir = 'output') {
  if (typeof filePath !== 'string' || filePath.length === 0 || isAbsolute(filePath)) return filePath
  const clean = normalize(filePath)
  if (clean === outputDir || clean.startsWith(`${outputDir}/`)) return clean
  return `${outputDir}/${clean}`
}

export function apply(ctx, config = {}) {
  const outputDir = config.outputDir ?? 'output'
  // Plugins load concurrently: wrap `write` whenever it is (re)registered, and refuse to start a step without it.
  const wrap = () => {
    const tool = ctx.tools.get('write')
    if (tool === undefined || tool.harveyWrite) return
    const execute = tool.execute
    tool.execute = (args, exec) => execute.call(tool, { ...args, file_path: routeWritePath(args.file_path, outputDir) }, exec)
    tool.description = `${tool.description} A relative path is written under the output directory (\`${outputDir}/\`): `
      + `\`response.md\` is saved as \`${outputDir}/response.md\`. An absolute path is used as is.`
    if (tool.parameters?.file_path) {
      tool.parameters.file_path = { ...tool.parameters.file_path,
        description: `Path to write. Relative paths go under \`${outputDir}/\`; absolute paths are used as is.` }
    }
    tool.harveyWrite = true
  }
  wrap()
  ctx.on('tools/change', wrap)
  ctx.on('agent/pre-step', async (payload, next) => {
    wrap()
    if (!ctx.tools.get('write')?.harveyWrite) throw new Error('harvey-write: DSH has no `write` tool to wrap')
    return next()
  })
}
