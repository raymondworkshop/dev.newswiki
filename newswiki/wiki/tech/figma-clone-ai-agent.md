---
title: "I Spent 120M Tokens Building a Figma Clone With an AI Agent"
source: "https://nirajrajgor.com/blog/figma-clone-ai-agent"
published: "2026-08-24"
created: "2026-10-13"
description: "What I learned about feedback loops, tests, skills, taste, and product decisions while building a Figma clone with Cursor CLI and Composer 2.5."
author:
  - "[[Niraj Rajgor]]"
topics:
  - tech
  - design
---

# [I Spent 120M Tokens Building a Figma Clone With an AI Agent](https://nirajrajgor.com/blog/figma-clone-ai-agent)

AI coding agents can autonomously build complex applications like a Figma clone when equipped with browser-based feedback loops, but human judgment remains indispensable for product definition, UI taste, and deciding when the product is truly complete.

## Key Points
- The author spent ~120M Composer 2.5 Fast tokens over ~10 hours across 13 sessions to build a functional Figma clone in a fresh Next.js repo, producing 215 tracked files, 193 automated tests (105 unit + 88 Playwright), and 19 git commits — all on a $20/month Cursor plan.
- The clone implemented a narrow but real editor workflow: name-based workspace/project access (no accounts), multiple artboards on a canvas, toolbar with shapes and text, nested layers panel, properties sidebar, PNG/JPEG export via Sharp, and SQLite persistence — deliberately excluding multiplayer to keep V1 tractable.
- Defining V1 required substantial upfront human work: the author used Matt Pocock's [[tech/grill-with-docs|grill-with-docs skill]] to answer ~40 planning questions, producing a 235-line PRD with 64 user stories, 4 ADRs (name-based access, Next.js+SQLite, deferred view-only sharing, fixed device frames), and 39 implementation issues with acceptance criteria before coding began.
- Adding [[tech/playwright|Playwright]] browser [[hubs/automation|automation]] created a closed feedback loop — Composer edits → run app → Playwright exercises feature → inspect UI/errors → Composer repairs → repeat — enabling the agent to autonomously fix issues like blank-frame drawing and missing migrations across three explicit repair commits.
- Passing tests created false confidence when assertions covered only happy paths: a cross-artboard drag test verified artboard counts and image presence but never checked that the image actually moved to the target artboard or that the source became blank; grouping tests missed z-index ordering bugs — green tests masked incomplete behavior.
- Drag-and-drop exposed the limits of browser automation: Playwright could execute the gesture but lacked reliable visual/coordinate assertions to confirm correct placement, snapping, or layer attachment — the agent reported success while the interaction felt broken to a human user.
- Vercel's React best-practices skill surfaced correct patterns (next/dynamic for the heavy editor, memoized artboards, React cache for server reads) but could not supply visual taste: the agent built a working vertical toolbar that clashed with the layers panel, and a properties sidebar with content controls but no font-size or color pickers — correctness ≠ good placement.
- Human decisions shifted upward: the author still chose the stack (Next.js, SQLite over IndexedDB), defined V1 scope, placed the toolbar atop the canvas, selected tools, designed export, and judged when the product 'felt right' — the agent provided options, not tradeoff resolutions.
- The experiment stopped at a quality plateau: V1 scope was mostly complete, but continuing would not fix incomplete test coverage, visual judgment gaps, or ambiguous product decisions — more tokens buy implementation velocity, not product clarity.

## Related Articles

- [[tech/ai-native-companies-few-employees|AI原生公司：员工很少，老板更少]]
- [[tech/ai-agents-privacy-unauthorized-actions|个人AI智能体很好用，却也有可能把你的银行账单发到工作群]]
- [[tech/top-ai-researchers-urge-regulation-self-improving-ai|顶尖AI研究人员呼吁紧急监管自我改进的AI系统]]
- [[finance/robinhood-ai-trading-agents-sleep|Robinhood的下一个重大押注：能在你熟睡时进行交易的AI机器人]]
