# xxthunder-dev-skills

Claude Code plugin providing reusable skills: commit-helper, refinement, retrospective, tdd-workflow.

## Project Structure

- `.claude-plugin/plugin.json` — plugin metadata and **version**
- `.claude-plugin/marketplace.json` — marketplace registry entry and **version**
- `skills/<name>/SKILL.md` — skill definitions (reusable across repos)
- `skills/<name>/references/` — supporting material for skills

## Key Rules

### Skills are portable

Skills in `skills/` are installed into other repos via the plugin system. Never add repo-specific logic, paths, or assumptions to skill files. Keep them generic and reusable.

### Version bump on every skill change

When any file under `skills/` is added, modified, or removed, you MUST bump the version in **both**:
- `.claude-plugin/plugin.json` → `"version"`
- `.claude-plugin/marketplace.json` → `plugins[0].version`

Use semantic versioning: patch for fixes/wording, minor for behavior changes or new skills, major for breaking changes.

### Conventional commits

This repo uses conventional commit format. Scope should match the skill name when the change is skill-specific (e.g., `refactor(refinement): ...`, `feat(tdd-workflow): ...`). Use `chore` for version bumps and repo maintenance.
