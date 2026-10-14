---
title: "My Homelab Two Years Later, Every Upgrade and What It Cost"
source: "https://www.joekarlsson.com/blog/homelab-two-years-later/"
published: "2026-03-05"
created: "2026-10-07"
description: "Two years after a $200 ThinkServer: two Dell R730s, 73 containers, metered power data, and an honest look at whether a homelab pays for itself."
author:
  - "[[Joe Karlsson]]"
topics:
  - tech
---

# [My Homelab Two Years Later, Every Upgrade and What It Cost](https://www.joekarlsson.com/blog/homelab-two-years-later/)

A two-year homelab evolution from a $200 ThinkServer to a $7,440 dual-server rack with 73 containers shows that financial break-even hinges on a single $80/month security monitoring substitution, while the real return was infrastructure engineering skills that transferred directly to professional work.

## Key Points
- Evolved from a $200 ThinkServer (4 cores, 32GB RAM, 15 containers) to two Dell R730s (80 cores, 256GB RAM, 2× [[hubs/nvidia|NVIDIA]] GPUs, 73 containers + 1 VM) with ~$7,440 hardware spend.
- Rack averages 430W metered (~$47/month at $0.15/kWh); CPUs average 13% busy, 10G links peak at ~12% of one link — significant over-provisioning.
- Night mode [[hubs/automation|automation]] saves only ~5W (not the claimed 175W) because stopped containers were idle; CPU governor drift on prxbox2 went undetected because hosts aren't in OpenTofu.
- Every container now defined in OpenTofu with drift detection; 185 health checks catch failures but missed a frozen power sensor for 3 weeks — check 186 will monitor sensor staleness.
- Break-even ~4.6 years ($7,240 hardware / $131/mo net savings) but leans 40%+ on replacing an $80/mo security monitoring plan; without it, break-even exceeds 11 years.
- Real ROI was professional: running the full stack (network, hosts, deploys, monitoring, power) built infrastructure engineering skills that transfer directly to day-job work.
- [AI Synthesis] The project illustrates how hobbyist infrastructure often over-provisions compute while under-investing in observability and network bottlenecks (NAS on 1G uplink).
- [AI Synthesis] DDR4 ECC RAM prices rose ~5× due to AI cluster demand, making memory the new hidden cost in used enterprise hardware — buy what you'll use upfront.

## Hardware Evolution
- Phase 1: Lenovo ThinkServer (Xeon E3-1226 v3, 4C/32GB) ran Plex, *arr stack, Pi-Hole for 6 months until Plex transcoding and Frigate AI detection saturated CPU.
- Phase 2: Two Dell PowerEdge R730s (dual Xeon E5-2698 v4, 40C/80T each, 128GB/host) from Server Design Lab (~$1,850 each configured) for PCIe [[hubs/gpu|GPU]] slots, ECC RAM, iDRAC, dual PSUs.
- Phase 3: Added Quadro RTX 4000 (8GB) on prxbox1 for always-on Frigate/Whisper/Tdarr; RTX A4000 (16GB) on prxbox2 for bursty Plex/Immich/Tdarr/Ollama LLMs.
- Rack: StarTech 25U, MikroTik CRS317 (10G), UniFi US-24 (1G), Synology DS418play (48TB), 2× CyberPower UPS, UniFi Cloud Gateway Ultra + 3× U7 Pro APs.

## [[hubs/gpu|GPU]] & PCIe Constraints
- 2U servers require single-slot blower-style workstation GPUs; gaming cards exceed height, connector clearance, and airflow limits — RTX 4090 does not fit at all.
- Both pro cards draw >75W, requiring Dell [[hubs/gpu|GPU]] power cables off the riser; Quadro RTX 4000 averages ~41W, RTX A4000 ~25W.
- VRAM usage: prxbox1 steady ~4GB (Frigate + Whisper + Tdarr); prxbox2 bursts to 15GB for 30B coding model but averages <1GB — models unload when idle.

## Networking & VLANs
- Dual 10G LACP bonds (Intel X710) per host to MikroTik — 20Gbps theoretical, but 30-day peaks ~1.2Gbps (12% of one 10G link); NAS on 1G uplink is the bottleneck.
- Four VLANs via UniFi Cloud Gateway Ultra: Default LAN (trusted), Guest (internet + speakers), IoT (Home Assistant + music + internet), Cameras (Frigate + HA + DNS) — IoT/Guest/Cameras blocked from Main LAN.
- mDNS reflection across VLANs is overly broad; 11 devices on IoT VLAN, older smart devices still on main LAN behind MikroTik firewall list.

## Container Workloads & OpenTofu
- 73 LXC containers (45 on prxbox1, 28 on prxbox2) + Home Assistant VM: media (Plex, Immich, *arr, Tdarr, Audiobookshelf), security (Frigate, Vaultwarden, Authentik, CrowdSec), AI (Ollama, llama.cpp, LiteLLM gateway), monitoring (Prometheus, Grafana, Loki, Alertmanager, Uptime Kuma), productivity (Paperless-NGX + AI tagging, Syncthing).
- All containers defined in OpenTofu with shared `bpg/proxmox` module; provision scripts enforce immutability — SSH fixes banned; drift check runs `tofu plan` every 6 hours.
- Home Assistant moved into VM on prxbox1 after VLANs enabled isolation; enables 134 automations (night mode, AI alert rewriting, backup recovery, UPS monitoring) but creates single-point-of-failure on prxbox1.

## Monitoring & Health Checks
- Prometheus scrapes every 15s (CPU, RAM, disk, network, [[hubs/gpu|GPU]], VRAM, temps, iDRAC power, rack power); 30-day retention sourced all metrics in article.
- 185 health checks (153 shell + 32 Python): backup verification, SSL expiry, disk thresholds, DNS, container restarts, subtitle generation — each checks one thing, exits 0/1.
- Critical gap: frozen rack power sensor (flat 541W for 3 weeks) undetected; new check will alert on stale sensors. Proxmox hosts not in OpenTofu allowed CPU governor drift.

## Power Consumption & Costs
- Metered (7-day smart plug): prxbox1 ~215W, prxbox2 ~191W, both servers ~406W, whole rack ~430W → ~10 kWh/day, ~$47/mo, ~$565/yr at $0.15/kWh.
- Night mode (stop 11 containers 11PM–6AM) saves ~5W, not 175W — containers were idle; overnight backups run in same window. CPU `powersave` governor drifted on 31/80 threads of prxbox2.
- R730s designed for [[hubs/ai-infrastructure|datacenter]] power/cooling; in Minnesota attic they're free heat in winter, cooling problem in summer. Mini PCs would run most workloads at fraction of power but can't hold 16GB GPU or provide iDRAC/ECC.

## Break-even Analysis
- Replaced subscriptions: iCloud/Dropbox ($22), NordVPN→Tailscale ($13), 1Password→Vaultwarden ($4), ChatGPT Plus→local LLMs ($20), Ring Protect ($12), security monitoring ($80), Audible ($15), Bluehost ($21) = ~$187/mo gross.
- Net ~$131/mo after $47 power + $9 Backblaze B2 (PBS offsite); break-even ~4.6 years on $7,240 hardware (excl. ThinkServer). Remove $80 security monitoring → break-even >11 years.
- NAS B2 backup and Claude API usage not counted; time investment excluded. Author frames it as a hobby: "Nobody asks a golfer to justify their club membership with a break-even analysis."

## Lessons Learned
- Infrastructure as code from day one — including Proxmox hosts — to prevent config drift (CPU governor, iDRAC network).
- Measure before automating: 5 minutes in Prometheus would have shown night mode saves ~5W, not 175W.
- VLANs from day one: retrofitting segmentation onto running services is a miserable weekend of IP updates.
- Buy for the bottleneck: 10G between servers wasted while NAS stayed on 1G uplink.
- Monitoring before first failure, not after third: uptime checks and backup verification should exist from start.
- Offsite copy before you need it: local backups don't survive attic fire.
- GPU form factor research: rack servers ≠ desktop cases — measure twice, buy once.
- Budget for RAM upfront but buy only what you'll use: DDR4 ECC ~5× price spike from AI demand; using 72GB of 256GB.

## Related Articles

- [[design/nvidia-ai-agent-pcs-launch|英伟达推出首批专为AI智能体设计的个人电脑]]
- [[tech/gareth-price-ai-setup|Gareth Price’s AI setup]]
- [[tech/coreweave-earnings-q2-2026|CoreWeave股价大涨，收入同比增长一倍]]
- [[finance/2026-05-21-nvda-undervalued|即使市值高达5万亿美元，英伟达依然被低估]]
