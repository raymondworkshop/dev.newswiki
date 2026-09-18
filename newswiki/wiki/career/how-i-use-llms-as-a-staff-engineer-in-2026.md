---
title: "How I use LLMs as a staff engineer in 2026"
source: "https://www.seangoedecke.com/how-i-use-llms-in-2026/"
created: "2026-07-16"
topics:
  - career
---

# [How I use LLMs as a staff engineer in 2026](https://www.seangoedecke.com/how-i-use-llms-in-2026/)

LLMs are now trusted for full PR generation in familiar domains, reducing manual effort and accelerating development cycles.

## Key Points
- Use LLMs for smart autocomplete with Copilot and for short tactical changes in unfamiliar domains, always reviewed by a SME.
- Write use-once-and-throwaway research code and ask targeted questions to learn about new topics like Unity game engine.
- Use LLMs for last-resort bugfixes and for big-picture proofreading of long-form English communication.
- [AI Synthesis] LLMs are now used to produce entire PRs in areas the engineer is familiar with, reducing manual typing and enabling faster iteration.
- [AI Synthesis] LLMs are used to investigate and diagnose 80% of bugs independently, especially when given cross-repo context.
- [AI Synthesis] The engineer performs extensive evaluation of agent-generated changes, rejecting most due to misalignment with intent, and only accepting changes after thorough review.
- [AI Synthesis] LLMs are used to generate test scripts and perform local setup tasks (e.g., Node version issues), replacing manual Googling with faster, automated troubleshooting.
- [AI Synthesis] The engineer still manually writes PR descriptions to ensure clarity and human oversight, as LLMs over-communicate and lack nuance.

## Tasks I Don’t Use AI For
- Do not use LLMs to write full PRs, ADRs, or technical communications — prefer human-written content to signal personal review and intent.
- Do not use LLMs to write blog posts, though drafts are reviewed for feedback.
- Do not use LLMs for UI testing or for changes requiring high-level design judgment.

## Key Shifts in 2025–2026
- Shifted from using LLMs in isolated, low-risk tasks to using them for full PRs and bug investigation with minimal supervision.
- [AI Synthesis] Agents now operate with greater autonomy and recover from errors more effectively than early versions, though human oversight remains critical for complex or ambiguous cases.
- [AI Synthesis] Human expertise is still essential in narrowing down bug search space — the engineer actively provides context, builds mental models, and guides agent sessions to improve accuracy.

## Related Articles

- [[tech/ai-food-metadata|Building Food Metadata with LLM Juries, Context Optimization & Multimodal AI]]
- [[tech/world-models-robotics-next-ai-leap|AI的下一次重大飞跃：走进现实世界]]
- [[career/ai-removing-middle-class-software-engineering|AI is removing the middle class of software engineering]]
- [[career/llm-burnout-impact|I Think I Have LLM Burnout]]
