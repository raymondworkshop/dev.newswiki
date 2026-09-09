---
title: "My agent.md to improve LLM-assisted code quality"
source: "https://fabiensanglard.net/agent.md/index.html"
created: "2026-08-31"
description: "How a personal agent.md file dramatically improves LLM-generated code quality by encoding style rules, architectural principles, and commit conventions."
author:
  - "[[Fabien Sanglard]]"
topics:
  - tech
---

# [My agent.md to improve LLM-assisted code quality](https://fabiensanglard.net/agent.md/index.html)

## Core View
- Early LLM coding attempts (mid-2025) produced non-compiling Rust code for `libadbmdns`; by Jan 2026 LLMs could write complex data structures and debug obscure crate bugs like the Windows IOCP issue in the [[tech/polling-crate|polling crate]].
- Agentic IDEs (Antigravity, VS Code Claude Code) enabled iterative refinement but required repetitive style guidance — "don't use magic numbers," "add comments," "short function names" — per session.
- Solution: place an `agent.md` in the project root (or symlink `gemini.md`/`claude.md` to it) so the harness injects it into every prompt, encoding preferences once.
- Author's `agent.md` enforces: concise human-facing text, no magic numbers (use constants/enums), reduced indentation via early returns, short function names (<30 chars), enums over booleans, whitespace between logical blocks, explanatory comments with ASCII diagrams, strict private-by-default visibility, layered architecture boundaries, minimal diffs, mandatory braces, and a 7-rule commit message format.
- Workflow for bug fixes: write failing test first, observe failure, then implement fix, observe pass — prevents hallucinated fixes.
- Context dilution (per [[tech/lost-in-the-middle|Lost in the Middle]] paper) degrades adherence to `agent.md` in long sessions; mitigations: start new session per feature, or explicitly ask the harness to "reload agent.md" when quality drops.
- Meta-tip: ask the agent to update `agent.md` directly when a new rule emerges, avoiding manual edits.

## Key Takeaways
- A project-level `agent.md` is a high-leverage lever for consistent, production-grade LLM code — it moves style/architecture guidance out of the chat loop and into the system prompt.
- Enforce architectural discipline (layered boundaries, private-by-default, minimal diffs) alongside style rules; LLMs respect structural constraints when they're explicit.
- Context dilution is real: keep sessions short and reload `agent.md` proactively to maintain instruction adherence.
- Treat `agent.md` as living documentation — let the agent maintain it.

## Related Articles

- [[tech/best-simple-system-for-now|Best Simple System for Now]]

---
**Topics**: [[tech/_index|Tech]]  
**Tags**: #tech #llm-coding #developer-tools #agent-md #code-quality
