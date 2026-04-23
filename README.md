# xxthunder-agentic-skills

Marketplace of agentic skill plugins by xxthunder. Hosts one or more plugins that extend coding agents with reusable skills. Claude Code is the initial supported target; additional agent targets (e.g. GitHub Copilot) are planned.

## Plugins

Each skill links to its `SKILL.md` for the full description, triggers, and instructions.

### `xxthunder-dev-skills`

Developer workflow skills:

| Skill | Description |
|---|---|
| [**backlog-ops**](plugins/xxthunder-dev-skills/skills/backlog-ops/SKILL.md) | Lifecycle operations on backlog items — pull, tick acceptance/UAT criteria, close with epic-status cascade |
| [**commit-helper**](plugins/xxthunder-dev-skills/skills/commit-helper/SKILL.md) | Conventional commit creation with mandatory pre-commit checks |
| [**refinement**](plugins/xxthunder-dev-skills/skills/refinement/SKILL.md) | Interactive backlog refinement sessions — review project state, prioritize work, add new items, discuss architecture |
| [**retrospective**](plugins/xxthunder-dev-skills/skills/retrospective/SKILL.md) | Incident-driven learning — captures lessons from unmet expectations and encodes them into project guidelines |
| [**tdd-workflow**](plugins/xxthunder-dev-skills/skills/tdd-workflow/SKILL.md) | Test-driven development workflow following Red-Green-Refactor principles |

### `xxthunder-paperless-skills`

Skills for digitizing household paperwork:

| Skill | Description |
|---|---|
| [**naps2-scan**](plugins/xxthunder-paperless-skills/skills/naps2-scan/SKILL.md) | End-to-end scan pipeline — drives NAPS2.Console with OCR, chains into `simplex-merge` for double-sided documents on a simplex scanner, and proposes a content-derived filename |
| [**simplex-merge**](plugins/xxthunder-paperless-skills/skills/simplex-merge/SKILL.md) | Post-processing merge of two existing PDFs (odd + even pages) into one correctly ordered document |

## Installation (Claude Code)

Add the marketplace, then install one or more plugins:

```bash
claude plugin marketplace add https://github.com/xxthunder/xxthunder-agentic-skills.git
claude plugin install xxthunder-dev-skills
claude plugin install xxthunder-paperless-skills
```

Or test locally by pointing Claude Code at a plugin directory:

```bash
claude --plugin-dir /path/to/xxthunder-agentic-skills/plugins/xxthunder-dev-skills
```

### With claude-code-action (GitHub)

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    plugin_marketplaces: |
      https://github.com/xxthunder/xxthunder-agentic-skills.git
    plugins: |
      xxthunder-dev-skills
      xxthunder-paperless-skills
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Usage

Skills trigger automatically based on conversation context, or can be invoked explicitly. See each skill's `SKILL.md` (linked above) for the full trigger list. Common cues:

**xxthunder-dev-skills**
- [**backlog-ops**](plugins/xxthunder-dev-skills/skills/backlog-ops/SKILL.md): "start XAS-025", "tick AC 2 on XAS-025", "close XAS-025"
- [**commit-helper**](plugins/xxthunder-dev-skills/skills/commit-helper/SKILL.md): triggered when creating commits
- [**refinement**](plugins/xxthunder-dev-skills/skills/refinement/SKILL.md): "let's refine", "backlog refinement", "what should we work on next?"
- [**retrospective**](plugins/xxthunder-dev-skills/skills/retrospective/SKILL.md): "I'm not happy with...", "that's wrong", "why did you...?"
- [**tdd-workflow**](plugins/xxthunder-dev-skills/skills/tdd-workflow/SKILL.md): triggered when implementing features, fixing bugs, or refactoring

**xxthunder-paperless-skills**
- [**naps2-scan**](plugins/xxthunder-paperless-skills/skills/naps2-scan/SKILL.md): "scan this", "scan another", "digitize this letter/invoice", "run NAPS2"
- [**simplex-merge**](plugins/xxthunder-paperless-skills/skills/simplex-merge/SKILL.md): "merge these two PDFs", or filenames containing "ungerade"/"gerade", "odd"/"even", "front"/"back"

## Roadmap

See `docs/backlog/` for current epics and stories. Near-term focus:

- Canonical skill source format enabling multi-agent emission
- GitHub Copilot target
- Additional plugins beyond dev-skills

## Development

Plugin helper scripts (Python) are covered by a pytest suite at repo root.

```bash
uv run --group dev pytest
```

The `pyproject.toml` at repo root is a dev-only harness — it is not part of
any plugin and is not installed when users install a plugin via
`claude plugin install`. Helper scripts remain PEP 723 inline-metadata
files invokable via `uv run <script>`; the test harness imports their
top-level functions directly.

## License

[MIT](LICENSE)
