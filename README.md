# Claude Code Skills Plugin

Reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills packaged as a plugin for use across projects.

## Installation

### As a Plugin (recommended)

Install via the Claude Code CLI:

```bash
# Add as a marketplace
claude plugin marketplace add https://github.com/xxthunder/xxthunder-dev-skills.git

# Install the plugin
claude plugin install xxthunder-dev-skills
```

Or test locally:

```bash
claude --plugin-dir /path/to/xxthunder-dev-skills
```

### With claude-code-action (GitHub)

```yaml
- uses: anthropics/claude-code-action@v1
  with:
    plugin_marketplaces: |
      https://github.com/xxthunder/xxthunder-dev-skills.git
    plugins: |
      xxthunder-dev-skills
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
```

### Manual (legacy)

Copy individual skill directories from `skills/` into your project's `.claude/skills/` directory.

## Skills

| Skill | Description |
|---|---|
| **commit-helper** | Conventional commit creation with mandatory pre-commit checks |
| **refinement** | Interactive backlog refinement sessions — review project state, prioritize work, add new items, discuss architecture |
| **retrospective** | Incident-driven learning — captures lessons from unmet expectations and encodes them into project guidelines |
| **tdd-workflow** | Test-driven development workflow following Red-Green-Refactor principles |

## Usage

Skills trigger automatically based on conversation context, or can be invoked explicitly:

- **Commit Helper**: triggered when creating commits
- **Refinement**: "let's refine", "backlog refinement", "what should we work on next?"
- **Retrospective**: "I'm not happy with...", "that's wrong", "why did you...?"
- **TDD Workflow**: triggered when implementing features, fixing bugs, or refactoring

## License

[MIT](LICENSE)
