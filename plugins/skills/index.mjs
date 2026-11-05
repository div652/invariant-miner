// skills: register a benchmark's skills with DSH's skill registry.
//
// Reads <dir>/<name>/SKILL.md for every subdirectory of config.dir (a host path OUTSIDE the workspace: the file tools
// are workspace-isolated, so DSH's own filesystem skill provider could not load bodies from there). Each SKILL.md has a
// frontmatter block with one-line `name:` and `description:` (one pair of enclosing quotes removed), then the body.
// Registered with ctx.skills.register in the global layer, so subagents see them too: DSH's `skill` tool lists the
// catalog (name + description) and loads a body on demand. Scripts the manuals mention are staged into the workspace
// by the benchmark, not by this plugin.
//
// Row:
//   - insert:
//       - id: skills
//         name: <abs path>/plugins/skills/index.mjs
//         config:
//           dir: /abs/path/to/skills         # required
import { existsSync, readdirSync, readFileSync, statSync } from 'node:fs'
import { isAbsolute, join } from 'node:path'

export const name = 'bench-skills'
export const inject = ['skills']

const FRONTMATTER = /^---\n([\s\S]*?)\n---\n?([\s\S]*)$/
const unquote = v => (v.length >= 2 && ((v[0] === '"' && v.at(-1) === '"') || (v[0] === "'" && v.at(-1) === "'")) ? v.slice(1, -1) : v)

export function loadSkills(root) {
  const skills = []
  for (const dir of readdirSync(root).sort()) {
    const file = join(root, dir, 'SKILL.md')
    if (!statSync(join(root, dir)).isDirectory() || !existsSync(file)) continue
    const match = readFileSync(file, 'utf8').replace(/\r\n/g, '\n').match(FRONTMATTER)
    if (!match) throw new Error(`skills: ${file} has no frontmatter`)
    const meta = {}
    for (const line of match[1].split('\n')) {
      const kv = line.match(/^([A-Za-z][\w-]*):\s*(.*)$/)
      if (kv) meta[kv[1]] = unquote(kv[2].trim())
    }
    if (!meta.name || !meta.description) throw new Error(`skills: ${file} needs one-line name and description`)
    if (meta.name !== dir) throw new Error(`skills: ${file} is named ${JSON.stringify(meta.name)}, not its directory ${dir}`)
    skills.push({ name: meta.name, description: meta.description, content: match[2].trim() + '\n' })
  }
  return skills
}

export function apply(ctx, config = {}) {
  if (typeof config.dir !== 'string' || !isAbsolute(config.dir) || !existsSync(config.dir)) {
    throw new Error('skills: config.dir must be an existing absolute directory')
  }
  const skills = loadSkills(config.dir)
  if (skills.length === 0) throw new Error(`skills: no <name>/SKILL.md under ${config.dir}`)
  for (const skill of skills) {
    ctx.skills.register({ name: skill.name, description: skill.description, source: 'runtime', content: skill.content })
  }
}
