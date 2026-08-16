import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import metadata from './skills.metadata.json' with { type: 'json' }

const PROVIDER_NAME = 'cmchen-skills-bundled'
// DSH reserves rank 600 for skills shipped inside a package.
const BUNDLED_SKILL_RANK = 600
const INVOCATION = { modelInvocable: true, userInvocable: true }

function stripFrontmatter(source) {
  let text = source
  if (text.charCodeAt(0) === 0xfeff) text = text.slice(1)
  if (!text.startsWith('---\n') && !text.startsWith('---\r\n')) return text
  const end = text.indexOf('\n---\n', 4)
  const endCrlf = text.indexOf('\r\n---\r\n', 4)
  const found = end === -1 ? endCrlf : endCrlf === -1 ? end : Math.min(end, endCrlf)
  if (found === -1) return text
  return text.slice(found + (text[found + 1] === '\r' ? 6 : 5))
}

function buildSkill(entry) {
  const skillDir = new URL(`./skills/${entry.name}/`, import.meta.url)
  const skillUrl = new URL('SKILL.md', skillDir)
  const resourceBase = {
    kind: 'directory',
    path: fileURLToPath(skillDir),
  }
  const candidate = {
    name: entry.name,
    description: entry.description,
    invocation: INVOCATION,
    provider: PROVIDER_NAME,
    source: 'bundled',
    resourceBase,
    rank: BUNDLED_SKILL_RANK,
    locator: skillUrl,
  }
  return {
    candidate,
    async get() {
      const source = await readFile(skillUrl, 'utf8')
      return {
        name: entry.name,
        description: entry.description,
        invocation: INVOCATION,
        provider: PROVIDER_NAME,
        source: 'bundled',
        resourceBase,
        path: fileURLToPath(skillUrl),
        content: stripFrontmatter(source),
      }
    },
  }
}

const skills = metadata.map(buildSkill)
const byName = new Map(skills.map((s) => [s.candidate.name, s]))

const provider = {
  name: PROVIDER_NAME,
  list: () => Promise.resolve(skills.map((s) => s.candidate)),
  async get(selected) {
    const skill = byName.get(selected.name)
    if (skill === undefined) return undefined
    return skill.get()
  },
}

export const name = 'cmchen-skills'
export const inject = ['skills']

export function apply(ctx) {
  ctx.skills.registerProvider(() => provider)
}
