# xxthunder-agentic-skills

Marketplace of agentic skill plugins by xxthunder. Hosts one or more plugins that extend coding agents with reusable skills. Claude Code is the initial supported target; additional agent targets (e.g. GitHub Copilot) are planned.

## Plugins

### `xxthunder-dev-skills`

Developer workflow skills:

| Skill | Description |
|---|---|
| **commit-helper** | Conventional commit creation with mandatory pre-commit checks |
| **refinement** | Interactive backlog refinement sessions — review project state, prioritize work, add new items, discuss architecture |
| **retrospective** | Incident-driven learning — captures lessons from unmet expectations and encodes them into project guidelines |
| **tdd-workflow** | Test-driven development workflow following Red-Green-Refactor principles |

## Installation (Claude Code)

Add the marketplace, then install a plugin:

```bash
claude plugin marketplace add https://github.com/xxthunder/xxthunder-agentic-skills.git
claude plugin install xxthunder-dev-skills
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
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Usage

Skills trigger automatically based on conversation context, or can be invoked explicitly:

- **Commit Helper**: triggered when creating commits
- **Refinement**: "let's refine", "backlog refinement", "what should we work on next?"
- **Retrospective**: "I'm not happy with...", "that's wrong", "why did you...?"
- **TDD Workflow**: triggered when implementing features, fixing bugs, or refactoring

## Roadmap

See `docs/backlog/` for current epics and stories. Near-term focus:

- Canonical skill source format enabling multi-agent emission
- GitHub Copilot target
- Additional plugins beyond dev-skills

## License

[MIT](LICENSE)
