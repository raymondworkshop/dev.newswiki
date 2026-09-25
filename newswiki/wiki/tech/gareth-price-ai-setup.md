---
title: "Gareth Price’s AI setup"
source: "https://mysetup.ai/u/gareth"
published: "2026-09-18"
created: "2026-09-18"
description: "Cofounder and CTO of CorralData. tmux to a headless Linux workstation, llama.cpp on 4000 Ada SFF, \\\"glass factory\\\" automated production facility [screenshots attached] and wiki for context."
author:
  - "[[Gareth Price]]"
topics:
  - tech
---

# [Gareth Price’s AI setup](https://mysetup.ai/u/gareth)

Gareth Price runs a headless local-AI workstation with custom agent orchestration (Glass Factory) and llama.cpp on an RTX 4000 Ada, treating the model as both coder and sysadmin while routing tasks across cloud and local models for cost and control.

## Key Points
- Primary harness is **Claude Code** (several hundred sessions/month); custom **Glass Factory** orchestrator routes Linear tickets through an autonomous pipeline (audit → plan → build → QA → promote) with deterministic state-machine control and human gates.
- Local inference runs on a headless **HP Z2 Mini G9** (Ubuntu 24.04, 96 GB RAM, **[[hubs/nvidia|NVIDIA]] RTX 4000 SFF Ada 20 GB**) via **llama.cpp**; current sweet spot is a 4-bit **Qwen 3.8 27B** vision model at 128K context (~30 tok/s), with faster smaller models (gemma-4-e4b, minicpm-2b) for quick tasks.
- Access pattern: **tmux over SSH/mosh** through **Tailscale**; **Sunshine + Moonlight** for GUI streaming (including 3840×1080 ultrawide for Xreal One Pro AR glasses); M3 MacBook Pro and Samsung S23 DeX as clients.
- Personal **n8n** skills: **arxiv-digest** (weekly scored arXiv papers → Slack), **china-digest** (Chinese AI news translated), **daily-cto-briefing** (morning prioritization), **MagicMirror [[hubs/llm|LLM]] Summary** (dashboard widget on Samsung Frame TV), and **Frigate** NVR [[hubs/llm|LLM]] integration for motion-alert interpretation.
- Team skill pack (private) covers ticket-to-PR flow, git worktrees, standup/incident reports, ISO 24495-1 plain-language rewrites, **Gherkin**→**Playwright** browser QA with MP4 demo recording, and **pr-review** against Notion-cached style guides.
- **Glass Factory** reporting shows token usage, model routing share, stage advancement, and quality scores; QA uses a different lab's model than the coder and requires screenshot evidence (mocked renders rejected).
- Agent doubles as sysadmin: durable fixes with "why/how" recorded in a local wiki; zsh-quoting bug promoted to global instruction (use bash for loops/splits/arrays). [[hubs/gpu|GPU]] reserved for inference; remote encoding on iGPU/NVENC; **nvtop**/**btop** for monitoring.
- Cost breakdown: **Claude Max $200/mo** (heavily subsidized), **OpenAI Pro $100/mo**, local inference **~$0.13/h electricity** (70 W on 4000 Ada), **OpenRouter ~$20/mo** for larger-model experiments; local still at "fun hobby" economics vs. cloud APIs.

## Related Articles

- [[design/nvidia-ai-agent-pcs-launch|英伟达推出首批专为AI智能体设计的个人电脑]]
- [[tech/coreweave-earnings-q2-2026|CoreWeave股价大涨，收入同比增长一倍]]
- [[tech/ibm-quantum-advantage-era|IBM宣称“量子优势”进入新时代]]
- [[tech/humanoid-robots-brain-memory-challenge|要颠覆现实世界，人形机器人需解决“大脑”短板]]
