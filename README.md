# Gopher

Gopher packages 11 Go engineering skills from
[`metalagman/agent-skills`](https://github.com/metalagman/agent-skills) for
Codex, Claude Code, Grok Build, GitHub Copilot CLI, Cursor, OpenCode v2,
and hosts that implement [Agent Plugins 1.0](https://agent-plugins.org/).

## Skills

| Skill | Purpose |
| --- | --- |
| `adk` | Build Go agents with Google ADK. |
| `fx` | Design applications with Uber Fx. |
| `google-best-practices` | Apply Google's Go best practices. |
| `google-style-decisions` | Apply Google's style decisions. |
| `google-style-guide` | Apply Google's Go style guide. |
| `goose` | Work with Goose database migrations. |
| `options-gen` | Generate functional options. |
| `oss-maintainer` | Maintain production-quality Go OSS. |
| `senior-developer` | Review architecture, APIs, concurrency, and operations. |
| `uber-style-guide` | Apply Uber's Go style guide. |
| `golangci-lint-strict` | Install and use a strict golangci-lint configuration. |

Codex and Claude Code expose the canonical names through the `gopher`
namespace. Hosts that discover a flat `skills/` directory expose prefixed
names such as `gopher-senior-developer`, which avoids collisions with other
plugins.

## Install

### Codex

```bash
codex plugin marketplace add metalagman/gopher
codex plugin add gopher@gopher
```

Start a new session and invoke a skill, for example:

```text
$gopher:senior-developer Review this Go service.
```

### Claude Code

```text
/plugin marketplace add metalagman/gopher
/plugin install gopher@gopher
```

Start a new session, then invoke `/gopher:senior-developer`.

### GitHub Copilot CLI

```bash
copilot plugin marketplace add metalagman/gopher
copilot plugin install gopher@gopher
```

Invoke `/gopher-senior-developer` in an interactive session.

### Grok Build

```bash
grok plugin marketplace add metalagman/gopher
grok plugin install gopher@gopher
```

Invoke `/gopher-senior-developer`. The Grok-native manifest is included under
`.grok-plugin/`.

### Cursor

```bash
agent plugin marketplace add https://github.com/metalagman/gopher.git
```

Install **Gopher** from **Customize**, then invoke
`/gopher-senior-developer` in chat. Team administrators can alternatively
import the repository in **Dashboard → Plugins & MCPs**.

### OpenCode v2

```bash
opencode plugin add github:metalagman/gopher
```

The OpenCode entrypoint registers only the 11 prefixed skills. It does not
install tools, hooks, MCP servers, or agents.

### Agent Plugins 1.0

The portable package root is `plugins/gopher`. A compatible host discovers
the 11 prefixed skills from its `skills/` directory. Installation is
host-specific; Agent Plugins defines the package, not a universal installer.

## Provenance and maintenance

The initial vendored source is `metalagman/agent-skills` commit
`023dfe82afa5fbbb4a630c5dc73d43cdd124932a`. `skills.lock.json` records that
revision, the name mapping, and SHA-256 hashes for every vendored source file.
Canonical and portable trees are kept in parity except for their intentional
frontmatter names and Codex-only `agents/openai.yaml` metadata.

Run the contract suite before publishing changes:

```bash
python3 -m unittest discover -s tests -v
npm pack --dry-run --ignore-scripts
```

The repository CI performs static contract and package checks. At the initial
publication, only the Codex CLI was present locally; runtime loading in Claude
Code, Grok Build, Copilot CLI, Cursor, and OpenCode was therefore not claimed.

## License

MIT. The vendored skill provenance is recorded in `skills.lock.json`.
