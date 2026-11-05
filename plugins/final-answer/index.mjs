// final-answer: a `final_answer` tool that records the agent's answer and ends its turn.
//
// The answer is written to <answersDir>/<session id>.json (outside the workspace; the launcher reads the root
// session's file). Before the agent's next step, the turn is ended through the public `agent/pre-step` hook, the
// same mechanism as benchmark-limits: the turn ends `aborted` with reason {kind: 'hook', reason: 'final_answer'}, which
// the launcher reports as finish reason `final_answer`. Other tool calls made in the same step still complete.
//
// Row:
//   - insert:
//       - id: final-answer
//         name: <abs path>/plugins/final-answer/index.mjs
//         config:
//           answersDir: /abs/run/answers      # required
//           description: <optional tool description override>
import { mkdirSync, writeFileSync } from 'node:fs'
import { isAbsolute, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = fileURLToPath(new URL('.', import.meta.url))
const DSH_ROOT = process.env.DSH_BENCH_DSH_ROOT ?? resolve(HERE, '../../work/deepseek-harness')
const { defineTool } = await import(pathToFileURL(`${DSH_ROOT}/packages/core/tools/lib/index.js`).href)

export const name = 'final-answer'
export const inject = ['tools']

const DESCRIPTION = 'Submit your final answer and end the task. Call it once, only when your work is complete: '
  + 'every deliverable file must already be saved. The answer text is your final response to the task.'

export function apply(ctx, config = {}) {
  if (typeof config.answersDir !== 'string' || !isAbsolute(config.answersDir)) {
    throw new Error('final-answer: config.answersDir must be an absolute path')
  }
  const answered = new WeakSet()

  ctx.tools.register(defineTool({
    name: 'final_answer',
    description: config.description ?? DESCRIPTION,
    parameters: {
      answer: { type: 'string', required: true, description: 'Your final answer to the task.' },
    },
    output: {
      schema: { type: 'object', additionalProperties: false, properties: { text: { type: 'string', required: true } } },
      render: (_args, value) => [{ type: 'text', text: value.text }],
    },
    async execute(args, exec) {
      const sessionId = String(exec.agent?.session?.id ?? 'no-session')
      mkdirSync(config.answersDir, { recursive: true })
      writeFileSync(join(config.answersDir, `${sessionId}.json`), JSON.stringify({
        session_id: sessionId,
        answer: String(args.answer),
        recorded_at: new Date().toISOString(),
      }, null, 2) + '\n')
      if (exec.agent !== undefined) answered.add(exec.agent)
      return { text: 'Final answer recorded. The task is complete.' }
    },
  }))

  ctx.on('agent/pre-step', async ({ agent }, next) => {
    if (answered.has(agent)) {
      agent.cancel({ kind: 'hook', reason: 'final_answer' })
      return { kind: 'reject' }
    }
    return next()
  }, { prepend: true })
}
