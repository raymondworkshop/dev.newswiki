---
title: "Kimi K3, and what we can still learn from the pelican benchmark"
source: "https://simonwillison.net/2026/Jul/16/kimi-k3/"
published: "2026-07-16"
created: "2026-09-18"
description: "Chinese AI lab Moonshot AI announced Kimi K3 this morning, describing it as their “most capable model to date, with 2.8 trillion parameters”. It’s currently available via their website and …"
author:
  - "[[Simon Willison]]"
topics:
  - tech
  - business
---

# [Kimi K3, and what we can still learn from the pelican benchmark](https://simonwillison.net/2026/Jul/16/kimi-k3/)

Kimi K3 is a powerful but expensive 2.8T Chinese model with a single max reasoning effort that burns high token counts on simple tasks, and while the pelican benchmark remains a handy hands-on sanity check, it no longer reliably predicts real-world agentic performance.

## Key Points
- Moonshot AI released [[hubs/moonshot-ai|Kimi K3]], a 2.8 trillion parameter model priced at $3/M input and $15/M output tokens — the most expensive Chinese lab model to date, on par with [[hubs/anthropic|Anthropic]]'s Claude Sonnet series.
- Self-reported benchmarks show K3 mostly beating [[hubs/anthropic|Claude Opus 4.8]] and [[hubs/openai|GPT-5.5 high]], while trailing [[hubs/anthropic|Claude Fable 5]] and [[hubs/openai|GPT-5.6 Sol]]; it leads the [[hubs/arena-ai|Arena.ai Frontend Code arena]].
- The pelican benchmark (SVG generation) cost 25¢ via OpenRouter: 95 input tokens, 16,658 output tokens (13,241 reasoning tokens), exposing K3's single 'max' reasoning effort and high token consumption for simple tasks.
- Prompt tokenization anomaly: 'Generate an SVG of a pelican riding a bicycle' counted as 95 tokens vs. ~10 for OpenAI/Anthropic tokenizers; 'hi' counted 86 tokens, suggesting an ~85-token hidden system prompt that the model refuses to leak.
- Vision capability confirmed: K3 produced accurate alt text for the rendered pelican SVG at 0.6¢ cost.
- [AI Synthesis] The pelican test's correlation with model quality has largely severed — [[hubs/zhipu-ai|GLM-5.2]] outperforms Fable-class models on it — and it does not measure agentic tool-calling reliability, the key differentiator for today's models.
- [AI Synthesis] Despite limitations, the pelican remains a useful 'hello world' forcing function: it verifies API access, estimates cost/reasoning for a simple task, confirms SVG/geometry competence, enables intra-family release comparisons (K3 notably better than [[tech/kimi-k25|Kimi K2.5]]), and serves as a shareable artifact of hands-on evaluation.

## Related Articles

- [[tech/a-road-to-lisp-why-lisp|A road to Lisp: Why Lisp]]
- [[tech/ai-food-metadata|Building Food Metadata with LLM Juries, Context Optimization & Multimodal AI]]
- [[tech/sly-lexer-parser|SLY: lexer and parser - Playing with code]]
- [[tech/us-companies-ai-cost-shift|美国企业观念突变，不再为AI大肆烧钱]]
