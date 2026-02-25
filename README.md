# Claude Code Skills

Reusable [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills for use across projects.

## Installation

Pick whichever approach fits your workflow:

**Option A — Clone as your user-level skills directory** (all skills, all projects):

```bash
git clone git@github.com:xxthunder/my-agentic-skills.git ~/.claude/skills
```

**Option B — Clone anywhere and symlink/copy what you need**:

```bash
git clone git@github.com:xxthunder/my-agentic-skills.git ~/my-agentic-skills
# symlink a single skill into a project
ln -s ~/my-agentic-skills/refinement .claude/skills/refinement
```

**Option C — Copy individual skills** directly into any project's `.claude/skills/` directory — no clone required.

Skills placed in `~/.claude/skills/` are automatically available in all projects. Project-level skills (`.claude/skills/`) take precedence when names overlap.

## Skills

| Skill | Description |
|---|---|
| **refinement** | Interactive backlog refinement sessions — review project state, prioritize work, add new items, discuss architecture |
| **retrospective** | Incident-driven learning — captures lessons from unmet expectations and encodes them into project guidelines |
| **skill-creator** | Guide for creating new Claude Code skills with proper structure, progressive disclosure, and bundled resources |

## Usage

Skills trigger automatically based on conversation context, or can be invoked explicitly:

- **Refinement**: "let's refine", "backlog refinement", "what should we work on next?"
- **Retrospective**: "I'm not happy with...", "that's wrong", "why did you...?"
- **Skill Creator**: "create a new skill", "update this skill"

## License

[MIT](LICENSE)
