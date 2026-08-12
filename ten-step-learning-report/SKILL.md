---
name: ten-step-learning-report
description: "为指定主题生成有来源、可打印的完整十步学习报告和独立 HTML。仅当用户显式调用本 Skill，或明确要求使用十步学习方法、STORM 学习流程、01–10 完整学习报告时使用；不要用于单一事实问答，也不要代替步骤 06–09 的独立互动入口。"
---

# 十步学习方法：01–10 完整学习报告

Produce a durable learning artifact, not a generic topic summary. Preserve the dependency chain: every step must consume named outputs from earlier steps.

## 收集学习画像

1. Identify the topic, current level, target depth, role, and intended use.
2. If any are missing, combine the missing fields into at most two short questions.
3. Default the target depth to "hold a substantive conversation with a professional" only when the user does not choose one.
4. After the profile is complete, run without further interruption unless evidence access fails.

## 执行十步报告流程

1. Read [references/ten-step-method.md](references/ten-step-method.md) completely.
2. Use available search, browser, connector, or repository tools for steps 1 and 5. Prefer primary and authoritative sources; record title, publisher or author, URL, publication date when available, and the claim supported.
3. If no evidence tool is available, do not invent facts, citations, or resources. Ask for a source pack. If the user explicitly accepts an offline draft, label every unverified section and omit fake links.
4. Execute steps 1 through 10 in order. At the start of each step, name the upstream artifacts being consumed. Carry the learning profile into steps 3, 5, 6, and 7.
5. Keep step 8 static in this report: create a graduated question bank with concealed answers and rubrics. Keep step 9 static: create a layered Feynman explanation. Do not impersonate an interactive exchange inside the report.
6. Distinguish three fields for every step: **input and upstream**, **full artifact**, and **learning takeaways**. Do not repeat the same prose across the three fields.

## 生成报告产物

1. Read [references/report-contract.md](references/report-contract.md) completely.
2. Copy [assets/report-template.html](assets/report-template.html) to a safe output name ending in `-ten-step-learning.html`; replace every placeholder without changing the template's CSS or JavaScript.
3. Match the user's language. Retain important original terminology and explain it on first use.
4. Put citations next to supported claims and repeat a normalized source list in the Sources section.
5. In the final section, include copyable explicit invocations for `$ten-step-06-learning-ladder`, `$ten-step-07-core-sprint`, `$ten-step-08-adaptive-exam`, and `$ten-step-09-feynman-loop`.
6. If Python is available, run `python scripts/validate_report.py <output.html>`. Otherwise apply the equivalent checklist in the report contract.

## 交付报告

Return the report path, the topic and profile used, which evidence steps were searched, and any sections that remain unverified. When the host cannot write files, return the same structure as Markdown and state that the HTML artifact could not be created.

Do not activate this heavy workflow for a narrow factual answer, ordinary tutoring, translation, presentation creation, or an explicitly requested isolated step 6-9.
