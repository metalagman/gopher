# Repository instructions

- Keep the public skill names listed in `README.md` stable.
- Treat `plugins/gopher/canonical-skills/<name>` as the canonical host tree.
- Keep `plugins/gopher/skills/gopher-<name>` byte-for-byte equivalent to the
  canonical tree except for the `name` field in `SKILL.md` and the absence of
  Codex-only `agents/openai.yaml` files.
- Update `skills.lock.json` whenever vendored source content or provenance
  changes.
- Keep all plugin and marketplace versions aligned.
- Do not execute vendored scripts during validation.
- Run `python3 -m unittest discover -s tests -v` and
  `npm pack --dry-run --ignore-scripts` before publishing.
