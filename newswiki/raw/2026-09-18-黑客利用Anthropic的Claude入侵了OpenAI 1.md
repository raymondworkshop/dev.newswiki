---
title: "黑客利用Anthropic的Claude入侵了OpenAI"
source: "https://cn.wsj.com/articles/%E9%BB%91%E5%AE%A2%E5%88%A9%E7%94%A8anthropic%E7%9A%84claude%E5%85%A5%E4%BE%B5%E4%BA%86openai-1be7e472?mod=cn_hp_tech_pos1"
author:
  - "[[Robert McMillan]]"
published: 2026-09-18
created: 2026-09-18
description: "一个参加漏洞搜寻计划的独立安全研究团队访问了OpenAI的内部代码系统。该事件暴露了自动化网络威胁日益增长的风险。"
---
![[_resources/2026-09-18-黑客利用Anthropic的Claude入侵了OpenAI 1/d8cce48e49c290fcafebfd1c2ce7423d_MD5.jpg]]

OpenAI首席执行官山姆·阿尔特曼

OpenAI首席执行官山姆·阿尔特曼 图片来源：Benjamin Fanjoy/Getty Images

一群AI智能体 [突破OpenAI的隔离环境](https://cn.wsj.com/articles/how-the-futuristic-hack-by-rogue-openai-models-unfolded-9f25c656) 、黑入Hugging Face两周后，这家ChatGPT开发商得知了又一起由人工智能(AI)驱动的入侵事件；这一次， [OpenAI](https://www.wsj.com/topics/subject/openai) 自己成了目标。

独立安全研究人员借助Anthropic的Claude软件，获取了一名OpenAI员工ChatGPT账号的访问权限，从而可以读取该公司的私有软件库，并提出修改建议。

这个团队参加了OpenAI的一项漏洞搜寻计划，研究人员可在安全港保护下尝试攻入企业系统。发现问题后，该团队很快向OpenAI报告。OpenAI向他们支付了6,500美元赏金。该团队首次向《华尔街日报》(The Wall Street Journal)披露了这项工作。

最近，科技巨头和研究人员披露了一系列借助快速演进的AI工具实施网络入侵的事件，上述黑客事件即是最新一例。尽管数月来业界就AI系统能力发出警告，但这起新的入侵事件表明，当今计算机系统高度复杂，防御起来并不容易。

上周六，OpenAI首席执行官山姆·阿尔特曼(Sam Altman)及其同行 [呼吁暂停AI开发](https://cn.wsj.com/articles/%E4%B8%89%E5%A4%A7ai%E4%BC%81%E4%B8%9A%E6%8E%8C%E9%97%A8%E4%BA%BA%E8%BE%BE%E6%88%90%E5%85%B1%E8%AF%86-%E6%8A%80%E6%9C%AF%E7%A0%94%E5%8F%91%E8%A6%81%E4%B8%BB%E5%8A%A8%E9%99%8D%E9%80%9F-edd19b9d) ，称AI发展太快，开发这项技术的公司难以安全地降低相关危害。OpenAI周三披露了 [此前未报道过的安全事件](https://cn.wsj.com/articles/openai%E6%8A%AB%E9%9C%B2%E6%9B%B4%E5%A4%9A%E5%AE%89%E5%85%A8%E4%BA%8B%E4%BB%B6%E5%B9%B6%E9%87%87%E7%94%A8%E4%B8%8A%E6%8A%A5%E6%96%B0%E8%A7%84-387d401e) ，并公布了有关今后如何报告这类问题的新政策。

美国正与中国争夺AI主导地位。在这一背景下，攻入OpenAI的研究人员说，这次攻击表明，那些获得国家支持、具备高超网络能力的黑客团队确实有很大机会窥见美国的AI机密。

“我不认为我们有中国黑客那么强，”开展这项研究的安全公司Hacktron AI首席技术官莫汉·佩达帕蒂(Mohan Pedhapati)说。“我们只不过是三个花钱订阅了Claude和Codex的人。”

![[_resources/2026-09-18-黑客利用Anthropic的Claude入侵了OpenAI 1/93c0a53f4bdb80d060d7a37fd96964cf_MD5.jpg]]

Hacktron AI的研究人员成功获取了一名OpenAI员工ChatGPT账号的访问权限。左起：拉胡尔·迈尼(Rahul Maini)、莫汉·佩达帕蒂和哈什·贾斯瓦尔。

Hacktron AI的研究人员成功获取了一名OpenAI员工ChatGPT账号的访问权限。左起：拉胡尔·迈尼(Rahul Maini)、莫汉·佩达帕蒂和哈什·贾斯瓦尔。 图片来源：Harsh Jaiswal

OpenAI说，这些黑客发现了两个漏洞：一个存在于名为Discourse的第三方服务中，该服务托管OpenAI的社区讨论论坛；另一个问题出在OpenAI自身。OpenAI说，这两个问题目前均已解决。

“我们感谢这些研究人员联系我们并分享他们的发现。我们收紧了社区登录令牌的权限，并撤销了受影响的令牌和会话，”该公司表示。

Anthropic的一名发言人不予置评。

网络安全研究人员经常参加漏洞赏金计划，以此对大型公司的数字基础设施进行压力测试。

这场针对OpenAI的攻击始于7月23日。当时，Hacktron AI的研究人员发现，社区论坛Discourse在处理某些图像文件时存在一个漏洞。研究人员可以使用一个特殊版本的Claude Opus 4.8；该版本向符合资格的网络安全从业人员开放。他们要求这个Claude模型编写可在网络攻击中利用该漏洞的代码。

一开始，这一尝试并未奏效。不过，就在当晚Anthropic发布了Opus 5；到了第二天，Claude就找到利用该漏洞的方法。它生成的攻击代码让研究人员潜入了托管OpenAI论坛的一台Discourse服务器。在这台服务器上，他们获得了用户的身份验证令牌。身份验证令牌是一串由字母和数字组成的独特数字字符，可让用户访问在线服务。

![[_resources/2026-09-18-黑客利用Anthropic的Claude入侵了OpenAI 1/5f1763154a05d0509010f6edc8bb300c_MD5.jpg]]

今年早些时候，在伦敦举行的“Anthropic Code with Claude”开发者大会上的一场演示。

今年早些时候，在伦敦举行的“Anthropic Code with Claude”开发者大会上的一场演示。 图片来源：Chris Ratcliffe/Bloomberg News

令他们意外的是，这些令牌在ChatGPT上有效，其中一些属于OpenAI员工。这些令牌还可用于访问OpenAI的GitHub服务，也就是其软件代码托管库。

由于不想触碰敏感数据，研究人员无法确切说明OpenAI这个源代码系统的具体用途，但他们说，该系统名为“Monorepo”。熟悉OpenAI架构的人士称，Monorepo是一个存放OpenAI算法机密的大型软件代码库。

这些知情人士说，从软件角度看，Monorepo相当于该公司的核心秘方，可以让OpenAI的模型运行更快、更高效；但据信它不包含模型权重，后者相当于OpenAI最核心的资产。模型权重是大语言模型核心处的数万亿个数字，帮助模型判断哪些信息应被强化、哪些应被忽略。

研究人员以ChatGPT作为界面，可以读取Monorepo中的文件。他们说，在意识到自己能够访问敏感数据后，便停止了这次入侵；但在停止之前，他们提交了所谓的“拉取请求”。

他们指示该聊天机器人向该代码库中的一份文档文件提交一个“拉取请求”，也就是修改建议。该团队提出的修改建议如果被采纳，会使这份文档文件加入“Hacktron AI Team PoC”字样，以及一个指向佩达帕蒂和Hacktron AI研究主管哈什·贾伊斯瓦尔(Harsh Jaiswal)的X账号的链接。他们说，这是他们已成功访问OpenAI机密的证明。

研究人员说，这项修改建议最终未被采纳。OpenAI表示，经审查GitHub记录，发现有人对私有代码库的元数据和代码改动进行了“有限读取”。

Discourse表示，公司在7月25日，也就是收到通知的当天，修复了这一安全漏洞。

AI安全公司Abundant Security首席技术官约书亚·萨克斯(Joshua Saxe)查阅了Hacktron AI关于这起事件的报告。他说，这次黑客事件表明，在AI黑客攻击时代，保护企业机密变得何等复杂。

“全世界的软件里充斥着安全漏洞。我们之所以还没有把它们全揪出来，是因为直到去年，精通寻找这类漏洞的人也才只有几千个，”他说。

萨克斯说，如今，AI智能体正在让那些技能水平较低的人也具备这种黑客能力。

网络安全公司ThreatDown称，犯罪分子也在获取这些能力。ThreatDown称，在网络论坛上，人们最低只需花800美元，就能买到Hacktron AI研究人员所使用的那类网络增强型账号的非法访问权限。

OpenAI总裁兼联合创始人格雷格·布罗克曼(Greg Brockman)本周表示，在7月Hugging Face遭攻击以及这些研究人员实施入侵后，OpenAI对自家系统认真开展了一次安全审计。“我们抽调了25%的生产工程师，对他们说，‘抱歉，你们所有项目都暂停。你们现在转去防御。’”他说。“我们发现了一些严重问题，并修复了它们。”

《华尔街日报》记者Amrith Ramkumar详细剖析了OpenAI等公司的AI模型如何为达成训练目标而突破测试环境，失控闯入互联网并窃取信息。这些事件对企业界和美国的AI监管政策而言意味着什么？封面图片来源：Jason Redmond/Agence France-Presse/Getty Images

Copyright ©2026 Dow Jones & Company, Inc. All Rights Reserved. 87990cbe856818d5eddac44c7b1cdeb8