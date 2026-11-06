// toolbelt: managed tools start hidden; the agent discovers and adds them with four meta-tools.
//
// A port of the "toolbelt" of Archipelago's react_toolbelt_agent (Mercor; agents/runner/agents/react_toolbelt_agent),
// whose reason is context size: a large tool catalog is not sent to the model on every request. Only the tools the
// agent has added are. Tool names, descriptions, results and error texts are Archipelago's.
//
//   toolbelt_list_tools     names of the managed tools NOT in the toolbelt (sorted JSON list)
//   toolbelt_inspect_tool   one tool's name, description and parameters ($defs/$ref resolved)
//   toolbelt_add_tool       put a managed tool in the toolbelt (at most maxSize tools)
//   toolbelt_remove_tool    take it out again
//
// Which tools are managed: config.managed, name patterns where `*` matches any characters (default ["mcp__*"]: every
// MCP tool). Every other tool (DSH's own tools, final_answer, the four meta-tools) stays visible and callable as usual;
// adding one returns Archipelago's "always available" error.
//
// How: DSH rebuilds the tool list before every model step (`system-prompt/assemble`, with the step's agent in its
// context); this plugin drops the managed tools that are not in that agent's toolbelt. A call to a hidden tool is
// denied in `tools/pre-execute`; the model reads "Error: '<name>' not in toolbelt. Use toolbelt_add_tool first."
// (Archipelago's text). Each agent (root, every subagent) has its own toolbelt, empty at start unless config.initial
// names tools. Not ported: Archipelago's todo gate on final_answer (a separate feature of its harness).
//
// Row:
//   - insert:
//       - id: toolbelt
//         name: <abs path>/plugins/toolbelt/index.mjs
//         config:
//           managed: ["mcp__*"]     # optional
//           maxSize: 80             # optional (Archipelago's max_toolbelt_size)
//           initial: []             # optional: managed tools already in every new toolbelt
import { resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const HERE = fileURLToPath(new URL('.', import.meta.url))
const DSH_ROOT = process.env.DSH_BENCH_DSH_ROOT ?? resolve(HERE, '../../work/deepseek-harness')
const { defineTool } = await import(pathToFileURL(`${DSH_ROOT}/packages/core/tools/lib/index.js`).href)

export const name = 'toolbelt'
export const inject = ['tools']

export const META_TOOL_NAMES = ['toolbelt_list_tools', 'toolbelt_inspect_tool', 'toolbelt_add_tool', 'toolbelt_remove_tool']

/** JSON text as Python's json.dumps writes it by default (", " / ": " separators, non-ASCII escaped): Archipelago's
 * meta-tools return json.dumps(...) strings, so the model reads the same bytes. */
export function pyDumps(value) {
  const ascii = s => JSON.stringify(s).replace(/[\u007f-￿]/g, c => `\\u${c.charCodeAt(0).toString(16).padStart(4, '0')}`)
  if (value === null || value === undefined) return 'null'
  if (typeof value === 'string') return ascii(value)
  if (typeof value === 'number' || typeof value === 'boolean') return JSON.stringify(value)
  if (Array.isArray(value)) return `[${value.map(pyDumps).join(', ')}]`
  return `{${Object.entries(value).filter(([, v]) => v !== undefined).map(([k, v]) => `${ascii(k)}: ${pyDumps(v)}`).join(', ')}}`
}

/** Archipelago's _flatten_schema: resolve every "$ref": "#/$defs/X" inline and drop "$defs" (Gemini rejects them).
 * A recursive reference becomes {"type": "object"} plus the referencing node's other keys. */
export function flattenSchema(schema) {
  if (schema === null || typeof schema !== 'object' || Array.isArray(schema)) return schema
  const { $defs: defs = {}, ...rest } = schema
  const resolveRefs = (obj, visiting) => {
    if (obj === null || typeof obj !== 'object' || Array.isArray(obj)) return obj
    if ('$ref' in obj) {
      const refPath = obj.$ref
      const refName = String(refPath).split('/').at(-1)
      const others = Object.entries(obj).filter(([k]) => k !== '$ref')
      if (visiting.has(refName)) {
        return Object.fromEntries([['type', 'object'], ...others.map(([k, v]) => [k, resolveRefs(v, visiting)])])
      }
      if (String(refPath).startsWith('#/$defs/') && Object.hasOwn(defs, refName)) {
        const definition = defs[refName]
        const resolved = typeof definition === 'boolean' ? (definition ? {} : { not: {} })
          : resolveRefs({ ...definition }, new Set([...visiting, refName]))
        for (const [k, v] of others) resolved[k] = resolveRefs(v, visiting)
        return resolved
      }
      const unresolved = { type: 'object' }
      const inner = new Set([...visiting, refName])
      for (const [k, v] of others) unresolved[k] = resolveRefs(v, inner)
      return unresolved
    }
    const out = {}
    for (const [k, v] of Object.entries(obj)) {
      out[k] = Array.isArray(v) ? v.map(item => (item !== null && typeof item === 'object' ? resolveRefs(item, visiting) : item))
        : resolveRefs(v, visiting)
    }
    return out
  }
  return resolveRefs(rest, new Set())
}

const patternToRegExp = p => new RegExp(`^${p.split('*').map(s => s.replace(/[.+?^${}()|[\]\\]/g, '\\$&')).join('.*')}$`)
const alwaysAvailable = n => `'${n}' is always available; call it directly without adding it to the toolbelt`
const TEXT_OUTPUT = {
  schema: { type: 'object', additionalProperties: false, properties: { text: { type: 'string', required: true } } },
  render: (_args, value) => [{ type: 'text', text: value.text }],
}
const TOOL_NAME = description => ({ tool_name: { type: 'string', required: true, description } })

export function apply(ctx, config = {}) {
  const managed = (config.managed ?? ['mcp__*']).map(patternToRegExp)
  const maxSize = config.maxSize ?? 80
  const initial = config.initial ?? []
  if (!Number.isSafeInteger(maxSize) || maxSize < 1) throw new Error('toolbelt: maxSize must be a positive integer')
  const isManaged = n => !META_TOOL_NAMES.includes(n) && managed.some(re => re.test(n))
  for (const n of initial) {
    if (!isManaged(n)) throw new Error(`toolbelt: initial tool ${JSON.stringify(n)} is not managed`)
  }
  if (initial.length > maxSize) throw new Error('toolbelt: more initial tools than maxSize')

  // Per agent: the toolbelt (names) and every tool schema of its latest assembly, managed ones included.
  const states = new WeakMap()
  const stateOf = agent => {
    let state = states.get(agent)
    if (state === undefined) {
      state = { belt: new Set(initial), schemas: new Map() }
      states.set(agent, state)
    }
    return state
  }

  ctx.on('system-prompt/assemble', async (_assembly, context, next) => {
    const assembled = await next()
    if (context?.agent === undefined) return assembled
    const state = stateOf(context.agent)
    state.schemas = new Map(assembled.tools.map(tool => [tool.name, tool]))
    return { ...assembled, tools: assembled.tools.filter(tool => !isManaged(tool.name) || state.belt.has(tool.name)) }
  }, { global: true, prepend: true })

  ctx.on('tools/pre-execute', async (exec, next) => {
    if (exec.agent !== undefined && isManaged(exec.name) && !stateOf(exec.agent).belt.has(exec.name)) {
      return { kind: 'deny', reason: `'${exec.name}' not in toolbelt. Use toolbelt_add_tool first.` }
    }
    return next()
  }, { global: true, prepend: true })

  const meta = (toolName, description, parameters, handle) => ctx.tools.register(defineTool({
    name: toolName,
    description,
    parameters,
    output: TEXT_OUTPUT,
    async execute(args, exec) {
      return { text: handle(args ?? {}, stateOf(exec.agent ?? ctx)) }
    },
  }))
  const requireName = args => (typeof args.tool_name === 'string' ? args.tool_name : '')

  meta('toolbelt_list_tools',
    'List all available tools that are NOT currently in your toolbelt. Returns a list of tool names you can add.',
    {},
    (_args, state) => pyDumps([...state.schemas.keys()].filter(n => isManaged(n) && !state.belt.has(n)).sort()))

  meta('toolbelt_inspect_tool',
    'Get detailed information about a tool, including its description and parameters.',
    TOOL_NAME('The name of the tool to inspect'),
    (args, state) => {
      const n = requireName(args)
      if (!n) return pyDumps({ error: 'tool_name is required' })
      if (META_TOOL_NAMES.includes(n) || (state.schemas.has(n) && !isManaged(n))) return pyDumps({ error: alwaysAvailable(n) })
      const tool = state.schemas.get(n)
      if (tool === undefined) return pyDumps({ error: `Tool '${n}' not found` })
      return pyDumps({ name: tool.name, description: tool.description, parameters: tool.parameters ? flattenSchema(tool.parameters) : tool.parameters })
    })

  meta('toolbelt_add_tool',
    'Add a tool to your toolbelt so you can use it.',
    TOOL_NAME('The name of the tool to add'),
    (args, state) => {
      const n = requireName(args)
      if (!n) return pyDumps({ error: 'tool_name is required' })
      if (META_TOOL_NAMES.includes(n) || (state.schemas.has(n) && !isManaged(n))) return pyDumps({ error: alwaysAvailable(n) })
      if (!state.schemas.has(n)) return pyDumps({ error: `Tool '${n}' not found` })
      if (state.belt.has(n)) return pyDumps({ error: `Tool '${n}' already in toolbelt` })
      if (state.belt.size >= maxSize) return pyDumps({ error: 'Toolbelt full. Remove a tool first.' })
      state.belt.add(n)
      return pyDumps({ success: true, toolbelt_size: state.belt.size })
    })

  meta('toolbelt_remove_tool',
    'Remove a tool from your toolbelt to free up space.',
    TOOL_NAME('The name of the tool to remove'),
    (args, state) => {
      const n = requireName(args)
      if (!n) return pyDumps({ error: 'tool_name is required' })
      if (!state.belt.has(n)) return pyDumps({ error: `Tool '${n}' not in toolbelt` })
      state.belt.delete(n)
      return pyDumps({ success: true, toolbelt_size: state.belt.size })
    })
}
