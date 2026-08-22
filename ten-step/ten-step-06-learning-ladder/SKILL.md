---
name: ten-step-06-learning-ladder
description: "执行十步学习方法的第 06 步：先让学习者完成真实诊断任务，再依据表现定位五级学习阶段、能力证据和下一项晋级任务。仅当用户通过 /skills 选择或显式调用 ten-step-06-learning-ladder 时使用；不要从普通学习问题中推断并启动本模式。"
---

# 十步学习方法：06 水平诊断与学习阶梯

Run only after explicit selection or mention of `$ten-step-06-learning-ladder`. Diagnose demonstrated capability and identify the learner's next reachable milestone.

## 建立诊断背景

1. Reuse the current conversation, a ten-step report, supplied notes, or a learning checkpoint when available.
2. Identify the topic, target use, and target depth. If any are missing, ask for them together in one short question.
3. Treat self-reported level as a hypothesis, never as proof.

## 先诊断，再定位阶段

1. Give one compact diagnostic task that requires the learner to explain, choose, troubleshoot, compare, or produce something relevant to the target use.
2. Ask only the task and wait. Do not reveal the ladder placement, solution, or a model answer in the same turn.
3. Evaluate the response using observable evidence: conceptual accuracy, procedural fluency, transfer to a new example, and awareness of limits.
4. If the evidence straddles two levels, state the uncertainty and use one discriminating follow-up task.

## 构建五级学习阶梯

After sufficient evidence, define five topic-specific levels:

1. Complete beginner.
2. Basic understanding.
3. Practical user.
4. Problem solver.
5. Confident practitioner.

For every level include the required understanding, observable mastery, focus concepts or skills, promotion milestone, one hands-on task, common error, and one self-test. Then state:

- current supported rung and evidence;
- capabilities not yet demonstrated;
- nearest development zone;
- exactly one next milestone task.

On later turns, assess the milestone task before offering another. Do not dump the full future curriculum repeatedly.

## 总结或导出检查点

When the learner stops or meets the agreed milestone, summarize the placement, demonstrated evidence, unresolved gaps, and next task. Suggest but do not invoke:

`$ten-step-07-core-sprint Continue [topic] from this ladder placement.`

When the user explicitly requests a checkpoint, read [references/checkpoint.md](references/checkpoint.md) and return that format. Never auto-save a file or auto-start another Skill.
