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

A project-level `agent.md` is a high-[[hubs/leverage|leverage]] lever for consistent, production-grade [[hubs/llm|LLM]] code — it moves style/architecture guidance out of the chat loop and into the system prompt.

## Key Points
- Early [[hubs/llm|LLM]] coding attempts (mid-2025) produced non-compiling Rust code for `libadbmdns`; by Jan 2026 LLMs could write complex data structures and debug obscure crate bugs like the Windows IOCP issue in the [[tech/polling-crate|polling crate]].
- Agentic IDEs (Antigravity, VS Code Claude Code) enabled iterative refinement but required repetitive style guidance — "don't use magic numbers," "add comments," "short function names" — per session.
- Solution: place an `agent.md` in the project root (or symlink `gemini.md`/`claude.md` to it) so the harness injects it into every prompt, encoding preferences once.
- Author's `agent.md` enforces: concise human-facing text, no magic numbers (use constants/enums), reduced indentation via early returns, short function names (<30 chars), enums over booleans, whitespace between logical blocks, explanatory comments with ASCII diagrams, strict private-by-default visibility, layered architecture boundaries, minimal diffs, mandatory braces, and a 7-rule commit message format.
- Workflow for bug fixes: write failing test first, observe failure, then implement fix, observe pass — prevents hallucinated fixes.
- Context dilution (per [[tech/lost-in-the-middle|Lost in the Middle]] paper) degrades adherence to `agent.md` in long sessions; mitigations: start new session per feature, or explicitly ask the harness to "reload agent.md" when quality drops.
- Meta-tip: ask the agent to update `agent.md` directly when a new rule emerges, avoiding manual edits.

## Related Articles

- [[tech/2x-not-10x-coding-llms-2026|2x, not 10x: coding with LLMs in 2026]]
- [[tech/ai-food-metadata|Building Food Metadata with LLM Juries, Context Optimization & Multimodal AI]]
- [[tech/local-llm-question-categorization|Fine Tuning a Local LLM to Categorize Questions]]
- [[tech/how-i-use-llms-to-learn-complex-topics|How I use LLMs to learn complex topics]]
