import { readdir, readFile } from "node:fs/promises"
import { fileURLToPath } from "node:url"

const skillsURL = new URL("../../plugins/gopher/skills/", import.meta.url)

function frontmatter(markdown, key) {
  const match = markdown.match(new RegExp(`^---\\r?\\n[\\s\\S]*?^\\s*${key}:\\s*(.+?)\\s*$[\\s\\S]*?^---\\s*$`, "m"))
  return match?.[1]?.replace(/^["']|["']$/g, "")
}

function body(markdown) {
  return markdown.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "")
}

export default {
  id: "gopher",
  async setup(ctx) {
    const entries = (await readdir(skillsURL, { withFileTypes: true }))
      .filter((entry) => entry.isDirectory())
      .sort((a, b) => a.name.localeCompare(b.name))

    const skills = await Promise.all(entries.map(async (entry) => {
      const skillURL = new URL(`${entry.name}/SKILL.md`, skillsURL)
      const markdown = await readFile(skillURL, "utf8")
      return {
        id: entry.name,
        name: frontmatter(markdown, "name") ?? entry.name,
        description: frontmatter(markdown, "description") ?? "",
        path: fileURLToPath(skillURL),
        content: body(markdown),
      }
    }))

    ctx.skill.transform((editor) => {
      for (const skill of skills) {
        editor.add(skill)
      }
    })
  },
}
