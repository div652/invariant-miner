// tool-limits: caps on every tool call, the same for DSH's own tools and MCP tools.
//
//   maxLines, maxChars  Each text block of a tool result keeps its head: the first maxLines lines, then at most maxChars
//                       characters (Unicode code points), whichever cuts more, followed by a note of what was cut:
//                       "\n... (truncated N lines) ..." or, when no whole line was dropped, "\n... (truncated N chars) ...".
//                       Image and other non-text blocks are kept as they are.
//   timeoutMs           Wall clock per call. The call's abort signal fires at the deadline; its result becomes
//                       timeoutText (an error result). A tool that does not stop within graceMs of the deadline is
//                       left running and the timeout result is returned anyway.
//   timeoutText         Default "Tool call timed out".
//   timeoutExclude      Tool name patterns (`*` wildcard) the timeout does not apply to, e.g. ["mcp__*"] when an MCP
//                       server enforces its own per-call limit. The output cap still applies to them.
//   graceMs             Default 5000.
//
// Row:
//   - insert:
//       - id: tool-limits
//         name: <abs path>/plugins/tool-limits/index.mjs
//         config: { maxLines: 200, maxChars: 32768, timeoutMs: 60000 }
export const name = 'tool-limits'
export const inject = ['tools']

/**
 * Cut `text` to its head (see the header). Exported for tests.
 * @param {string} text
 * @param {number | undefined} maxLines
 * @param {number | undefined} maxChars
 * @returns {string}
 */
export function truncate(text, maxLines, maxChars) {
  if (!text) return text
  const lines = text.split('\n')
  const totalLines = lines.length
  const chars = s => Array.from(s)
  if (maxLines !== undefined && totalLines > maxLines) {
    let kept = lines.slice(0, maxLines).join('\n')
    let hidden = totalLines - maxLines
    if (maxChars !== undefined) {
      const points = chars(kept)
      if (points.length > maxChars) {
        kept = points.slice(0, maxChars).join('')
        hidden = totalLines - (kept.split('\n').length)
      }
    }
    return `${kept}\n... (truncated ${hidden} lines) ...`
  }
  if (maxChars !== undefined) {
    const points = chars(text)
    if (points.length > maxChars) {
      const kept = points.slice(0, maxChars).join('')
      const hidden = totalLines - kept.split('\n').length
      return hidden > 0
        ? `${kept}\n... (truncated ${hidden} lines) ...`
        : `${kept}\n... (truncated ${points.length - maxChars} chars) ...`
    }
  }
  return text
}

/**
 * @param {import("@deepseek-ai/cordis").Context} ctx
 * @param {{maxLines?: number, maxChars?: number, timeoutMs?: number, timeoutText?: string, graceMs?: number}} config
 */
export function apply(ctx, config = {}) {
  const positive = v => v === undefined || (Number.isSafeInteger(v) && v > 0)
  const { maxLines, maxChars, timeoutMs } = config
  const timeoutText = config.timeoutText ?? 'Tool call timed out'
  const graceMs = config.graceMs ?? 5000
  const excluded = (config.timeoutExclude ?? []).map(pattern =>
    new RegExp(`^${pattern.split('*').map(part => part.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*')}$`))
  if (!positive(maxLines) || !positive(maxChars) || !positive(timeoutMs) || !(Number.isSafeInteger(graceMs) && graceMs >= 0)) {
    throw new Error('tool-limits: maxLines, maxChars, timeoutMs must be positive integers (graceMs >= 0)')
  }

  if (maxLines !== undefined || maxChars !== undefined) {
    ctx.on('tools/post-execute', async (_exec, result, next) => {
      const downstream = await next()
      if (downstream.kind === 'block' || Object.hasOwn(downstream, 'value')) return downstream
      const content = downstream.content ?? result.content
      if (!Array.isArray(content)) return downstream
      let changed = false
      const capped = content.map((block) => {
        if (block?.type !== 'text' || typeof block.text !== 'string') return block
        const text = truncate(block.text, maxLines, maxChars)
        if (text === block.text) return block
        changed = true
        return { ...block, text }
      })
      return changed ? { ...downstream, content: capped } : downstream
    })
  }

  if (timeoutMs !== undefined) {
    ctx.on('tools/execute', async (exec, next) => {
      if (excluded.some(re => re.test(exec.name))) return next()
      const upstream = exec.signal
      const controller = new AbortController()
      const forward = () => controller.abort(upstream.reason)
      if (upstream?.aborted) controller.abort(upstream.reason)
      else upstream?.addEventListener('abort', forward, { once: true })
      let fired = false
      let release
      const expired = new Promise((resolve) => { release = resolve })
      const deadline = setTimeout(() => {
        fired = true
        controller.abort(new Error(`tool call exceeded ${timeoutMs} ms`))
        setTimeout(release, graceMs).unref?.()
      }, timeoutMs)
      deadline.unref?.()
      exec.signal = controller.signal
      try {
        const running = next()
        running.catch(() => {})  // a call that settles after we gave up must not become an unhandled rejection
        const outcome = await Promise.race([running.then(result => ({ result })), expired.then(() => ({ result: undefined }))])
        if (!fired) return outcome.result
        return { content: [{ type: 'text', text: timeoutText }], isError: true, error: { message: timeoutText } }
      } finally {
        clearTimeout(deadline)
        upstream?.removeEventListener('abort', forward)
        exec.signal = upstream
      }
    })
  }
}
