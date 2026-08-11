---
name: ten-step-08-adaptive-exam
description: "Run step 8 of the ten-step learning method as an adaptive one-question-at-a-time examination with scoring and remediation. Use only when the user explicitly selects or names ten-step-08-adaptive-exam; never activate implicitly from an ordinary question."
---

# Step 08: adaptive exam

Run only after explicit selection or mention of `$ten-step-08-adaptive-exam`. Measure recall and transfer without leaking the answer before the learner commits.

## Establish scope

1. Reuse a report, sprint result, notes, or checkpoint when available.
2. Identify the topic, examinable scope, target difficulty, and desired stopping rule. Ask one combined question only for missing essentials.
3. If the learner supplies no materials, state the assumed scope before the first question.

## Examine one question per turn

1. Maintain an internal mix of introductory, intermediate, advanced, and expert questions covering explanation, application, comparison, diagnosis, and transfer.
2. Ask exactly one question, then wait.
3. Before the learner answers, do not reveal the reference answer, scoring points, misconception target, or future questions.
4. If the learner asks for help, give the smallest useful hint and mark the attempt as assisted. Do not turn a hint into the answer.
5. If the learner skips, record the objective as unassessed and move on only after confirming the skip.

## Score and adapt

After each answer, use this fixed response order:

1. **Score: X/10** and whether it meets the current level.
2. **Demonstrated evidence:** quote or paraphrase the parts that earned credit.
3. **Specific gap:** identify the missing, incorrect, or unsupported element.
4. **Correction:** provide the minimum explanation needed to repair that gap.
5. **Next difficulty:** state easier, same, harder, or targeted variant, then ask the next single question.

Use 0-3 for absent or substantially wrong understanding, 4-6 for partial understanding, 7-8 for sound understanding with limited gaps, and 9-10 for accurate transfer with boundaries. Probe a core misconception with a changed example before treating it as resolved.

## Stop and hand off

Declare the target level stable only after at least two unassisted passes at that level and no open core misconception. On stop, summarize demonstrated boundary, assisted versus unassisted performance, unresolved gaps, and recommended review. Suggest but do not invoke:

`$ten-step-09-feynman-loop Test my explanation of [weakest concept] from this exam.`

When the user explicitly requests a checkpoint, read [references/checkpoint.md](references/checkpoint.md) and return that format. Exclude hidden questions and reference answers. Never auto-start another Skill.
