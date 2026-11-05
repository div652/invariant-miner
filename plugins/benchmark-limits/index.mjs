/**
 * Benchmark budgets implemented on the Harness's public agent hooks (from agentic-evolution's
 * eval/harness/benchmark-limits.mjs; here each budget is optional: null turns it off).
 *
 *   maxSteps     model steps per agent session (root and each subagent); the turn ends {hook, "benchmark:max-steps"}
 *   timeoutMs    wall clock per agent turn; the turn ends {hook, "benchmark:timeout"}
 *   temperature  number: set on every request; null: removed from every request
 *                (absent: requests are left as the provider builds them)
 */
export const name = "benchmark-limits";
export const inject = ["agents", "timer"];

/**
 * Bound a benchmark turn without replacing the Harness agent loop.
 * @param {import("@deepseek-ai/cordis").Context} ctx
 * @param {{maxSteps: number, timeoutMs: number, temperature: number | null}} config
 */
export function apply(ctx, config) {
  const maxSteps = config.maxSteps ?? null;
  const timeoutMs = config.timeoutMs ?? null;
  if ((maxSteps !== null && (!Number.isSafeInteger(maxSteps) || maxSteps < 1))
      || (timeoutMs !== null && (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1))
      || (config.temperature !== undefined && config.temperature !== null && !Number.isFinite(config.temperature))) {
    throw new Error("benchmark-limits: invalid budgets");
  }
  const timers = new Map();
  ctx.on("agent/pre-step", async ({ agent, step }, next) => {
    if (maxSteps !== null && step > maxSteps) {
      agent.cancel({ kind: "hook", reason: "benchmark:max-steps" });
      return { kind: "reject" };
    }
    if (timeoutMs !== null && !timers.has(agent)) {
      timers.set(agent, ctx.setTimeout(() => {
        agent.cancel({ kind: "hook", reason: "benchmark:timeout" });
      }, timeoutMs));
    }
    return next();
  }, { prepend: true });
  ctx.on("agent/status", ({ agent, status }) => {
    if (status === "idle") {
      timers.get(agent)?.();
      timers.delete(agent);
    }
  });
  if (config.temperature === undefined) return;
  ctx.on("agent/request", async (_payload, next) => {
    const request = await next();
    if (config.temperature === null) {
      const { temperature: _temperature, ...rest } = request;
      return rest;
    }
    return { ...request, temperature: config.temperature };
  });
}
