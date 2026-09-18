---
title: "黑客利用Anthropic的Claude入侵了OpenAI"
source: "https://cn.wsj.com/articles/%E9%BB%91%E5%AE%A2%E5%88%A9%E7%94%A8anthropic%E7%9A%84claude%E5%85%A5%E4%BE%B5%E4%BA%86openai-1be7e472?mod=cn_hp_tech_pos1"
published: "2026-09-18"
created: "2026-09-18"
description: "一个参加漏洞搜寻计划的独立安全研究团队访问了OpenAI的内部代码系统。该事件暴露了自动化网络威胁日益增长的风险。"
author:
  - "[[Robert McMillan]]"
topics:
  - tech
  - business
---

# [黑客利用Anthropic的Claude入侵了OpenAI](https://cn.wsj.com/articles/%E9%BB%91%E5%AE%A2%E5%88%A9%E7%94%A8anthropic%E7%9A%84claude%E5%85%A5%E4%BE%B5%E4%BA%86openai-1be7e472?mod=cn_hp_tech_pos1)

独立研究人员利用Anthropic的Claude漏洞攻破Discourse论坛并获取OpenAI内部代码库访问权限，展示了AI工具如何降低复杂网络攻击的门槛。

## 要点
- 独立安全公司Hacktron AI的三名研究人员在OpenAI漏洞赏金计划下，利用Anthropic的Claude Opus 4.8/5模型编写攻击代码，攻破托管OpenAI社区论坛的Discourse服务器，窃取用户认证令牌。
- 令牌意外在ChatGPT上有效，部分属于OpenAI员工，进而获得OpenAI GitHub私有代码库（Monorepo）的读取权限；Monorepo存放核心算法机密，但据信不含模型权重。
- 研究人员通过ChatGPT界面读取Monorepo文件，并提交带有“Hacktron AI Team PoC”标记的拉取请求作为访问证明，随后主动停止入侵并上报；OpenAI支付6,500美元赏金并修复了Discourse漏洞及内部令牌权限问题。
- OpenAI总裁Greg Brockman披露事后抽调25%生产工程师进行安全审计，发现并修复多个严重问题；Sam Altman等业界领袖同周呼吁暂停AI开发以降低风险。
- [AI Synthesis] 事件表明AI编码能力正让低技能攻击者也能实施复杂入侵，黑市上仅需800美元即可购买同类AI增强账号访问权，企业防御面临指数级压力。
- [AI Synthesis] 在中美争夺AI主导权背景下，研究者直言国家级黑客利用同类手段窃取美AI机密的概率极高，暴露软件供应链与身份联邦登录的系统性脆弱性。

## 相关文章

- [[tech/ai-native-companies-few-employees|AI原生公司：员工很少，老板更少]]
- [[tech/2026-05-29-ai-film-cannes-compute-costs|AI长片在戛纳首映：50万美元制作成本，算力支出占40万]]
- [[tech/2026-05-28-cheap-humanoid-robots|下一波中国冲击：比二手车还便宜的人形机器人]]
- [[business/novo-nordisk-anthropic-claude-drug-discovery|诺和诺德将用Anthropic的Claude助力药物研发]]
