// One-shot helper: extract frontmatter descriptions from the plugin's own skills/
// directory and writes skills.metadata.json (array of { name, description }).
// Run after updating any SKILL.md so index.js serves fresh metadata.
import { readFileSync, statSync, writeFileSync, readdirSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const SELF_DIR = dirname(fileURLToPath(import.meta.url))
const SKILLS_ROOT = join(SELF_DIR, 'skills')

function stripBom(text) {
  return text.charCodeAt(0) === 0xfeff ? text.slice(1) : text
}

function extractFrontmatter(text) {
  text = stripBom(text)
  const m = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(text)
  if (!m) return {}
  const lines = m[1].split(/\r?\n/)
  const out = {}
  let currentKey = null
  let currentLines = null
  for (const raw of lines) {
    const line = raw
    if (/^[a-zA-Z][a-zA-Z0-9_-]*:/.test(line)) {
      if (currentKey) out[currentKey] = currentLines.join('\n')
      const idx = line.indexOf(':')
      currentKey = line.slice(0, idx).trim()
      currentLines = [line.slice(idx + 1).trim()]
    } else if (currentKey) {
      currentLines.push(line)
    }
  }
  if (currentKey) out[currentKey] = currentLines.join('\n')
  return out
}

function cleanYamlScalar(value) {
  let v = value.trim()
  // YAML folded/literal block markers
  if (v.startsWith('>') || v.startsWith('|')) v = v.slice(1).trim()
  // Join continuation lines (folded semantics: single spaces; literal: keep newlines).
  // Claude skills overwhelmingly use one-line intent; normalize to single line with spaces.
  v = v.replace(/\s*\n\s*/g, ' ').trim()
  // Strip stray YAML quoting
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    v = v.slice(1, -1)
  }
  return v
}

const result = {}
const entries = readdirSync(SKILLS_ROOT, { withFileTypes: true })
  .filter((e) => e.isDirectory())
  .map((e) => e.name)
  .sort()
for (const name of entries) {
  const mdPath = join(SKILLS_ROOT, name, 'SKILL.md')
  if (!statSync(mdPath).isFile()) {
    result[name] = { name, description: '' }
    continue
  }
  const text = stripBom(readFileSync(mdPath, 'utf8'))
  const fm = extractFrontmatter(text)
  result[name] = {
    name: cleanYamlScalar(fm.name ? fm.name : name),
    description: fm.description ? cleanYamlScalar(fm.description) : '',
  }
}

writeFileSync(
  join(dirname(fileURLToPath(import.meta.url)), 'skills.metadata.json'),
  JSON.stringify(Object.values(result), null, 2) + '\n',
  'utf8',
)
console.log('Wrote skills.metadata.json')
console.log(JSON.stringify(result, null, 2))
