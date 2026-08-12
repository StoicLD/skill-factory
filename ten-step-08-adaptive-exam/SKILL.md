---
name: ten-step-08-adaptive-exam
description: "执行十步学习方法的第 08 步：每轮只出一道题，答后评分、纠正具体缺口，并依据表现动态升降难度。仅当用户通过 /skills 选择或显式调用 ten-step-08-adaptive-exam 时使用；绝不从普通问题中隐式启动。"
---

# 十步学习方法：08 自适应逐题考试

Run only after explicit selection or mention of `$ten-step-08-adaptive-exam`. Measure recall and transfer without leaking the answer before the learner commits.

## 确定考试范围

1. Reuse a report, sprint result, notes, or checkpoint when available.
2. Identify the topic, examinable scope, target difficulty, and desired stopping rule. Ask one combined question only for missing essentials.
3. If the learner supplies no materials, state the assumed scope before the first question.

## 每轮只出一道题

1. Maintain an internal mix of introductory, intermediate, advanced, and expert questions covering explanation, application, comparison, diagnosis, and transfer.
2. Ask exactly one question, then wait.
3. Before the learner answers, do not reveal the reference answer, scoring points, misconception target, or future questions.
4. If the learner asks for help, give the smallest useful hint and mark the attempt as assisted. Do not turn a hint into the answer.
5. If the learner skips, record the objective as unassessed and move on only after confirming the skip.

## 评分并自适应调整

After each answer, use this fixed response order:

1. **Score: X/10** and whether it meets the current level.
2. **Demonstrated evidence:** quote or paraphrase the parts that earned credit.
3. **Specific gap:** identify the missing, incorrect, or unsupported element.
4. **Correction:** provide the minimum explanation needed to repair that gap.
5. **Next difficulty:** state easier, same, harder, or targeted variant, then ask the next single question.

Use 0-3 for absent or substantially wrong understanding, 4-6 for partial understanding, 7-8 for sound understanding with limited gaps, and 9-10 for accurate transfer with boundaries. Probe a core misconception with a changed example before treating it as resolved.

## 停止与交接

Declare the target level stable only after at least two unassisted passes at that level and no open core misconception. On stop, summarize demonstrated boundary, assisted versus unassisted performance, unresolved gaps, and recommended review. Suggest but do not invoke:

`$ten-step-09-feynman-loop Test my explanation of [weakest concept] from this exam.`

When the user explicitly requests a checkpoint, read [references/checkpoint.md](references/checkpoint.md) and return that format. Exclude hidden questions and reference answers. Never auto-start another Skill.
