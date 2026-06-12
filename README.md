# xxthunder-agentic-skills

<p align="center">
  <a href="https://github.com/xxthunder/xxthunder-agentic-skills/actions/workflows/test.yml">
    <img src="https://github.com/xxthunder/xxthunder-agentic-skills/actions/workflows/test.yml/badge.svg" alt="CI Status">
  </a>
  <a href="https://github.com/xxthunder/xxthunder-agentic-skills/blob/develop/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/xxthunder/xxthunder-agentic-skills">
    <img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://codecov.io/gh/xxthunder/xxthunder-agentic-skills">
    <img src="https://codecov.io/gh/xxthunder/xxthunder-agentic-skills/branch/develop/graph/badge.svg" alt="Coverage">
  </a>
</p>

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
| [**split-batch**](plugins/xxthunder-paperless-skills/skills/split-batch/SKILL.md) | Post-processing split of a single multi-document PDF into one PDF per detected document — boundary detection from page content or blank separator sheets |

### `hermes-tweet-skills`

Skills for Hermes Agent X/Twitter workflows:

| Skill | Description |
|---|---|
| [**hermes-tweet**](plugins/hermes-tweet-skills/skills/hermes-tweet/SKILL.md) | Install, configure, diagnose, and safely operate Hermes Tweet with XQUIK_API_KEY setup, tweet_explore/read/action ordering, remote runtime guidance, and action gating |

## Installation

The `/plugin` slash command is supported across Claude Code, VS Code, and the GitHub Copilot CLI. Run these inside the agent's chat — each block is one command.

Add the marketplace:

```text
/plugin marketplace add xxthunder/xxthunder-agentic-skills
```

Install a plugin (swap in `xxthunder-paperless-skills` for the other one):

```text
/plugin install xxthunder-dev-skills@xxthunder-agentic-skills
```

For Hermes Tweet:

```text
/plugin install hermes-tweet-skills@xxthunder-agentic-skills
```

Update plugins — the command shape differs between hosts.

In Claude Code (marketplace-level; bumps installed plugins from the refreshed catalog):

```text
/plugin marketplace update xxthunder-agentic-skills
```

In GitHub Copilot CLI (per-plugin):

```text
/plugin update xxthunder-dev-skills
```

For everything else — enable/disable, uninstall, listing, removing a marketplace, reload — see the host's own `/plugin` documentation (Claude Code, VS Code, or GitHub Copilot CLI). Subcommand availability and flags differ slightly between hosts.

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
- [**split-batch**](plugins/xxthunder-paperless-skills/skills/split-batch/SKILL.md): "split this batch", "split this stack", "these are multiple documents", "I scanned a pile", "separate these documents"

**hermes-tweet-skills**
- [**hermes-tweet**](plugins/hermes-tweet-skills/skills/hermes-tweet/SKILL.md): "install Hermes Tweet", "connect Hermes to X/Twitter", "configure XQUIK_API_KEY", "run tweet_explore", "use tweet_read", "gate tweet_action"

## Roadmap

See the [backlog](docs/backlog/README.md) for current epics and stories. Near-term focus:

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

To run with coverage and the JUnit report locally (matches CI):

```bash
uv run --group dev pytest --cov --cov-report=xml --junit-xml=junit.xml
```

### CI secrets

CI uploads coverage and test results to [Codecov](https://about.codecov.io/) and
fails the build if the upload errors. The repository must define a
`CODECOV_TOKEN` secret (`Settings → Secrets and variables → Actions`) generated
from the Codecov dashboard for this repo. Without it, every push and PR will
fail at the Codecov upload step.

## License

[MIT](LICENSE)
