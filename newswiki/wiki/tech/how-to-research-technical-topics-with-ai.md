---
title: "How to Research Technical Topics With AI"
source: "https://www.0xkato.xyz/how-to-research-technical-topics-with-ai/"
published: "2026-07-28"
created: "2026-09-28"
description: "How I go from a technical question I cannot answer to an explanation I can reconstruct without the model"
author:
  - "[[0xkato]]"
topics:
  - tech
  - career
---

# [How to Research Technical Topics With AI](https://www.0xkato.xyz/how-to-research-technical-topics-with-ai/)

The author presents a rigorous AI-assisted research methodology: narrow the question, map dependencies, study one component at a time while keeping sources separate from mental models, stress-test explanations against primary sources, reconstruct the topic from memory, and only then use AI for prose polishing.

## Key Points
- Start by narrowing a broad technical question (e.g., "How do LLMs work?") into a scoped investigation with a clear beginning and end, then ask a model to map the dependency chain of concepts needed to answer it. [[tech/ai-research-methodology|AI Research Methodology]]
- Learn the missing terminology first — knowing the right terms (e.g., positional encodings, RoPE, multi-head attention projections) makes ordinary search and paper reading far more effective. [[tech/transformer-architecture|Transformer Architecture]]
- Research one component at a time until you can explain its inputs, operation, and outputs; use AI to locate relevant paper sections and compare tutorials, but ask for criticism of your own explanation rather than a rewrite. [[tech/multi-head-attention|Multi-Head Attention]]
- [AI Synthesis] Keep the exact technical claim and its source separate from the mental model that made it click; record the limits of each simplification (e.g., implementations often fuse projections for efficiency even though the mental model describes learned views)
- The chat is not the source — open the original paper, documentation, or code yourself, verify the surrounding context, and check for later versions or implementations that may have changed the conclusion. [[tech/source-verification|Source Verification]]
- [AI Synthesis] Actively try to prove your explanation wrong: ask what a knowledgeable reader would object to, where the mental model breaks, and whether a claim describes every model or one common implementation; narrow wording or drop claims that overreach
- Close the chat and reconstruct the topic from a blank page (pen and paper); if you cannot explain the transition between two adjacent components, you have found a gap — return to sources at that exact point. [[tech/feynman-technique|Feynman Technique]]
- Only after you can reconstruct the subject without the model do you use AI for prose: give it your structured notes, mental models, and limitations, then edit for voice, clarity, and factual accuracy against your verified notes. [[tech/technical-writing|Technical Writing]]

## Related Articles

- [[tech/2x-not-10x-coding-llms-2026|2x, not 10x: coding with LLMs in 2026]]
- [[tech/ai-food-metadata|Building Food Metadata with LLM Juries, Context Optimization & Multimodal AI]]
- [[tech/local-llm-question-categorization|Fine Tuning a Local LLM to Categorize Questions]]
- [[tech/gareth-price-ai-setup|Gareth Price’s AI setup]]
