---
title: "No, local models will not win"
source: "https://www.seangoedecke.com/local-models-will-not-win/"
created: "2026-08-11"
topics:
  - tech
---

# [No, local models will not win](https://www.seangoedecke.com/local-models-will-not-win/)

User preference for the 'strongest model' creates a ceiling for the adoption of smaller local models.

## Key Points
- Most AI inference will remain in datacenters because users consistently prefer the strongest available models, which are too large for local hardware.
- Local models are economically inefficient compared to [[hubs/ai-infrastructure|datacenter]] models due to the lack of batching and inferior hardware specifications.
- [AI Synthesis] The 'local AI' movement underestimates the compounding advantage of [[hubs/ai-infrastructure|datacenter]] scale in both compute density and cost-per-token.

## The Efficiency Gap: Batching and Hardware
- Datacenters utilize **batching**, allowing hundreds of users to share the cost of moving model weights into the [[hubs/gpu|GPU]], whereas local users have zero batching efficiency.
- Hardware disparity: Datacenter GPUs (e.g., B200) provide significantly higher flops and memory bandwidth per watt than consumer gaming GPUs like the RTX 4090.
- Local hosting is often more expensive when accounting for the initial hardware investment and monthly electricity costs compared to API subscriptions.

## Niche Utility of Local Models
- Local models serve a niche for latency-sensitive applications, such as voice chat, acting as a fast interface that delegates complex tasks to larger [[hubs/ai-infrastructure|datacenter]] models.
- Specific value propositions for local models include [[tech/open-weight-models|open-weight models]] for steering vectors, total infrastructure control, and offline availability.

## Related Articles

- [[tech/homelab-two-years-later|My Homelab Two Years Later, Every Upgrade and What It Cost]]
- [[business/ai-software-company-moats|How does AI affect software company moats?]]
- [[tech/coreweave-earnings-q2-2026|CoreWeave股价大涨，收入同比增长一倍]]
- [[tech/ai-compute-scramble-reshapes-silicon-valley|AI算力争夺战愈演愈烈，硅谷格局面临重塑]]
