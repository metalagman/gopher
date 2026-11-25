import hashlib
import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "gopher"
CANONICAL = PLUGIN / "canonical-skills"
PORTABLE = PLUGIN / "skills"
LOCK = json.loads((ROOT / "skills.lock.json").read_text())
NAMES = [entry["canonical"] for entry in LOCK["skills"]]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_name(path):
    text = path.read_text()
    match = re.search(r"^name:\s*([^\n]+)$", text, re.MULTILINE)
    if not match:
        raise AssertionError(f"missing name in {path}")
    return match.group(1).strip().strip("\"'")


def normalized_skill(path):
    text = path.read_text()
    return re.sub(r"^name:\s*[^\n]+$", "name: __SKILL__", text, count=1, flags=re.MULTILINE)


class ContractTest(unittest.TestCase):
    def test_expected_skill_names(self):
        self.assertEqual(
            NAMES,
            [
                "adk", "fx", "google-best-practices",
                "google-style-decisions", "google-style-guide", "goose",
                "options-gen", "oss-maintainer", "senior-developer",
                "uber-style-guide", "golangci-lint-strict",
            ],
        )
        self.assertEqual(sorted(path.name for path in CANONICAL.iterdir()), sorted(NAMES))
        self.assertEqual(
            sorted(path.name for path in PORTABLE.iterdir()),
            sorted(f"gopher-{name}" for name in NAMES),
        )

    def test_locked_canonical_hashes(self):
        self.assertEqual(LOCK["version"], 1)
        self.assertRegex(LOCK["source"]["commit"], r"^[0-9a-f]{40}$")
        for skill in LOCK["skills"]:
            base = CANONICAL / skill["canonical"]
            for item in skill["files"]:
                path = base / item["path"]
                self.assertTrue(path.is_file(), path)
                self.assertEqual(sha256(path), item["canonical_sha256"], path)

    def test_local_markdown_links_resolve(self):
        link = re.compile(r"(?<!!)\[[^]]*\]\(([^)]+)\)")
        for markdown in PLUGIN.rglob("SKILL.md"):
            for target in link.findall(markdown.read_text()):
                target = target.split("#", 1)[0]
                if not target or "://" in target or target.startswith(("mailto:", "#")):
                    continue
                self.assertTrue((markdown.parent / target).resolve().is_file(), f"{markdown}: {target}")

    def test_canonical_and_portable_parity(self):
        for name in NAMES:
            canonical = CANONICAL / name
            portable = PORTABLE / f"gopher-{name}"
            canonical_files = {
                path.relative_to(canonical)
                for path in canonical.rglob("*")
                if path.is_file() and path.relative_to(canonical) != Path("agents/openai.yaml")
            }
            portable_files = {
                path.relative_to(portable) for path in portable.rglob("*") if path.is_file()
            }
            self.assertEqual(canonical_files, portable_files, name)
            for relative in canonical_files:
                left = canonical / relative
                right = portable / relative
                if relative == Path("SKILL.md"):
                    self.assertEqual(normalized_skill(left), normalized_skill(right), name)
                else:
                    self.assertEqual(left.read_bytes(), right.read_bytes(), relative)
            self.assertEqual(skill_name(canonical / "SKILL.md"), name)
            self.assertEqual(skill_name(portable / "SKILL.md"), f"gopher-{name}")

    def test_codex_ui_metadata(self):
        for name in NAMES:
            path = CANONICAL / name / "agents" / "openai.yaml"
            text = path.read_text()
            self.assertRegex(text, r"(?m)^interface:\s*$")
            self.assertRegex(text, r"(?m)^  display_name:\s*\S")
            description = re.search(r"(?m)^  short_description:\s*[\"'](.+)[\"']$", text)
            self.assertIsNotNone(description, path)
            self.assertGreaterEqual(len(description.group(1)), 25)
            self.assertLessEqual(len(description.group(1)), 64)
            self.assertIn(f"$gopher:{name}", text)

    def test_agent_plugins_manifest(self):
        manifest = json.loads((PLUGIN / "plugin.json").read_text())
        allowed = {
            "$schema", "name", "version", "description", "author",
            "homepage", "repository", "license", "keywords", "extensions",
        }
        self.assertLessEqual(set(manifest), allowed)
        self.assertEqual(manifest["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
        self.assertEqual(manifest["name"], "gopher")
        self.assertRegex(manifest["name"], r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
        self.assertLessEqual(len(manifest["name"]), 64)
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["license"], "MIT")
        self.assertNotIn("skills", manifest)

    def test_host_manifests_and_paths(self):
        json_paths = list(ROOT.rglob("*.json"))
        documents = {path: json.loads(path.read_text()) for path in json_paths}
        versions = {
            document["version"]
            for path, document in documents.items()
            if path != ROOT / "skills.lock.json" and isinstance(document, dict) and "version" in document
        }
        self.assertEqual(versions, {"0.1.0"})
        self.assertEqual(documents[PLUGIN / ".codex-plugin" / "plugin.json"]["skills"], "./canonical-skills/")
        self.assertEqual(documents[PLUGIN / ".claude-plugin" / "plugin.json"]["skills"], "./canonical-skills/")
        self.assertEqual(documents[PLUGIN / ".grok-plugin" / "plugin.json"]["skills"], "./skills/")
        self.assertFalse((PLUGIN / ".plugin" / "plugin.json").exists())
        self.assertFalse((PLUGIN / ".cursor-plugin" / "plugin.json").exists())
        self.assertEqual(
            documents[ROOT / ".agents" / "plugins" / "marketplace.json"]["plugins"][0]["policy"],
            {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
        )

    def test_opencode_registers_only_skills(self):
        script = """
import plugin from './integrations/opencode/index.js'
const added = []
let transforms = 0
await plugin.setup({skill: {transform(fn) {transforms++; fn({add(value) {added.push(value)}})}}})
if (transforms !== 1 || added.length !== 11) process.exit(1)
if (added.some((item) => !item.id.startsWith('gopher-') || item.id !== item.name)) process.exit(2)
console.log(JSON.stringify(added.map((item) => item.id).sort()))
"""
        result = subprocess.run(
            ["node", "--input-type=module", "--eval", script],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        registered = json.loads(result.stdout)
        self.assertEqual(registered, sorted(f"gopher-{name}" for name in NAMES))

    def test_manifest_contains_exactly_142_files(self):
        files = [
            path for path in ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and path.suffix != ".pyc"
        ]
        self.assertEqual(len(files), 142)


if __name__ == "__main__":
    unittest.main()
