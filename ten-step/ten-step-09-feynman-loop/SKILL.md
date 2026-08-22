---
name: ten-step-09-feynman-loop
description: "执行十步学习方法的第 09 步：先让学习者用自己的话解释，再精确分类理解缺口，并通过最小提示、重讲和检验完成费曼纠错循环。仅当用户通过 /skills 选择或显式调用 ten-step-09-feynman-loop 时使用；绝不从普通解释请求中隐式启动。"
---

# 十步学习方法：09 费曼解释纠错

Run only after explicit selection or mention of `$ten-step-09-feynman-loop`. Make the learner explain first, then repair only the gaps their explanation reveals.

## 确定待检验概念

1. Reuse an exam result, report, notes, or checkpoint when available.
2. Identify one concept, the intended audience, and the target use. Ask one combined question only for missing essentials.
3. If the learner already supplied an explanation, treat it as the first attempt and diagnose it immediately.

## 先让学习者解释，再开始教学

Ask the learner to explain the concept in their own words, include one concrete example, and state when the idea may not apply. Then wait. Do not provide a standard explanation, final definition, or vocabulary list before the attempt.

## 精确诊断理解缺口

Classify each material gap as one of:

- jargon substitution: a label replaces an explanation;
- causal jump: a necessary step or mechanism is skipped;
- missing boundary: the explanation overgeneralizes;
- invalid example: the example does not instantiate the concept;
- factual error: a claim contradicts reliable domain knowledge.

Name only the highest-value gaps per turn. Cite the learner's wording so the diagnosis is inspectable.

## 用递进提示修复缺口

Repeat this loop:

1. identify one precise gap;
2. give the smallest hint that could unlock it;
3. ask the learner to explain again;
4. test the revision with a new example or counterexample;
5. increase hint detail only when the learner remains stuck.

Do not replace the learner's explanation with a polished lecture. When factual accuracy depends on current or specialized evidence, use available sources or clearly mark uncertainty.

## 通过与结束

Pass only when the explanation is simple, accurate, complete enough for the target, supported by a valid example, and bounded by at least one condition or limitation. Finish with:

- the learner's validated one-sentence definition, edited only for accuracy;
- the strongest example they produced;
- any remaining review point;
- a suggested review interval.

When the user explicitly requests a checkpoint, read [references/checkpoint.md](references/checkpoint.md) and return that format. Never auto-save or auto-start another Skill.
