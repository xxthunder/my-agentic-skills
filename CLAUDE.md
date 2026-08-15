# xxthunder-agentic-skills

Marketplace of agentic skill plugins. Hosts one or more plugins that extend coding agents; initial target is Claude Code, with additional agent targets planned.

## Project Structure

- `.claude-plugin/marketplace.json` — marketplace registry (one entry per plugin)
- `plugins/<plugin-name>/.claude-plugin/plugin.json` — plugin manifest + version
- `plugins/<plugin-name>/skills/<skill-name>/SKILL.md` — skill definitions
- `plugins/<plugin-name>/skills/<skill-name>/references/` — supporting material
- `docs/backlog/` — epics and user stories (prefix `XAS`)

Current plugins:
- `xxthunder-dev-skills` — dev workflow skills (commit-helper, refinement, retrospective, tdd-workflow, backlog-ops)
- `xxthunder-paperless-skills` — skills for digitizing household paperwork (scan, OCR, merge, file)

Plugins version independently; a change in one plugin only bumps that plugin's version (plus its entry in `marketplace.json`).

## Key Rules

### Skills are portable

Skills under any plugin's `skills/` are installed into other repos via the plugin system. Never add repo-specific logic, paths, or assumptions to skill files. Keep them generic and reusable.

### Version bump on every plugin change

When any file under `plugins/<plugin-name>/` is added, modified, or removed, you MUST bump the version in **both**:
- `plugins/<plugin-name>/.claude-plugin/plugin.json` → `"version"`
- `.claude-plugin/marketplace.json` → the matching `plugins[...].version`

Use semantic versioning: patch for fixes/wording, minor for behavior changes or new skills, major for breaking changes.

The rule covers the whole plugin directory, not just `skills/` — hooks under `hooks/` and the manifest itself are shipped to consumers exactly as skills are, and a change to any of them changes what an installer receives.

### Conventional commits

This repo uses conventional commit format. Scope should match the skill name when the change is skill-specific (e.g., `refactor(refinement): ...`, `feat(tdd-workflow): ...`). Use `chore` for version bumps and repo maintenance, and `docs(backlog)` for backlog changes.
