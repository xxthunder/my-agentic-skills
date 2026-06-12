---
name: hermes-tweet
description: "Install, configure, diagnose, and safely operate Hermes Tweet, the Hermes Agent X/Twitter plugin powered by Xquik. Use when the user asks to add Hermes Tweet to Hermes Agent, connect Hermes to X/Twitter, configure XQUIK_API_KEY, run tweet_explore, tweet_read, or tweet_action, troubleshoot plugin enablement, or plan approval-gated social media automation."
---

<!-- Source: https://github.com/Xquik-dev/hermes-tweet -->

# Hermes Tweet

Use this skill when a Hermes Agent session needs X/Twitter search, reads,
monitoring context, or explicitly approved actions through the Hermes Tweet
plugin. Keep setup portable and keep secrets out of prompts, commits, issues,
and logs.

## Setup

1. Confirm Hermes Agent is installed:

   ```bash
   command -v hermes >/dev/null || echo "Install Hermes Agent first."
   ```

2. Install and enable Hermes Tweet:

   ```bash
   hermes plugins install Xquik-dev/hermes-tweet --enable
   ```

3. If the Hermes runtime environment needs the Python package explicitly, install
   the published package into that environment:

   ```bash
   ~/.hermes/hermes-agent/venv/bin/python -m pip install hermes-tweet
   ```

4. Configure runtime environment variables on the host where Hermes executes the
   plugin. Do not paste the real key into chat:

   ```bash
   export XQUIK_API_KEY="xq_..."
   export HERMES_TWEET_ENABLE_ACTIONS="false"
   ```

## Operating Rules

1. Start with `tweet_explore`. It is the safe discovery tool and should work
   before authenticated reads are configured.
2. Use `tweet_read` only after `XQUIK_API_KEY` is present. Treat its result as a
   JSON string and parse it before summarizing.
3. Use `tweet_action` only when `HERMES_TWEET_ENABLE_ACTIONS=true` and the user
   approved the exact outward-facing action.
4. Keep actions disabled by default for research, monitoring, support triage, and
   launch-listening workflows.
5. For copied URL examples, use only catalog-documented `/api/v1/...` paths. Do
   not use account connection, reauth, API key management, billing, credit
   top-up, or support-ticket endpoints.
6. For Hermes Desktop remote gateway profiles, install Hermes Tweet and set
   environment variables on the remote Hermes host. The desktop client is not
   automatically the plugin runtime.

## Diagnostics

- Run `hermes plugins` to confirm installation and enablement.
- Re-run `tweet_explore` after install or upgrade to verify the tool surface.
- If authenticated reads fail, check only whether `XQUIK_API_KEY` exists. Never
  print the value.
- If an action is blocked, verify the action gate and ask the user to approve the
  exact action before retrying.

## References

- Hermes Tweet repository: https://github.com/Xquik-dev/hermes-tweet
- Hermes Tweet PyPI package: https://pypi.org/project/hermes-tweet/
