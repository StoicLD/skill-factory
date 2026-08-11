# Ten-step Skill suite validation

Status: implementation and available forward validation complete
Date: 2026-08-11

## Artifacts under validation

- `ten-step-learning-report`: complete sourced ten-step HTML workflow; strict natural trigger plus explicit invocation.
- `ten-step-06-learning-ladder`: explicit-only diagnostic ladder.
- `ten-step-07-core-sprint`: explicit-only micro-lesson sprint.
- `ten-step-08-adaptive-exam`: explicit-only adaptive examination.
- `ten-step-09-feynman-loop`: explicit-only explain-diagnose-reteach loop.

The implementation is independently written from the user-supplied article and the public Daliu-Awesome-Skills repository. The upstream repository exposed no root license when checked on 2026-08-11, so its prompt text, code, and HTML template were not copied.

## Trigger matrix

Positive report triggers:

1. `$ten-step-learning-report 帮我系统学习 RAG。`
2. `用十步学习法把概率论从零学到能用于数据分析。`
3. `用 STORM 十步流程生成一份量子计算学习 HTML。`

Negative report triggers:

1. `SQL JOIN 是什么？请用两句话回答。`
2. `只按费曼法检查我对 CAP 定理的解释。`
3. `把这份笔记翻译成英文并做成 PPT。`

Positive interactive triggers require explicit selection or mention. Representative examples:

1. `$ten-step-06-learning-ladder 评估我学习 RAG 的当前阶段。`
2. `$ten-step-07-core-sprint 带我学习 SQL JOIN 最关键的 20%。`
3. `$ten-step-08-adaptive-exam 基于这份材料逐题考我。`
4. `$ten-step-09-feynman-loop 让我用自己的话解释 CAP 定理。`
5. Select the corresponding named entry through Codex `/skills`, then supply the topic.

Negative interactive triggers:

1. `我最近在学 RAG，有什么建议？` without explicit Skill selection.
2. `考研应该怎么复习？` without explicit Skill selection.
3. Explicitly selecting a different member of the suite.

The OpenAI adapters set `allow_implicit_invocation: false` for all four interactive Skills. Their portable descriptions repeat the explicit-only boundary for hosts that ignore the adapter.

## Automated evidence

Run from the product repository root:

```powershell
python -B scripts/validate_skills.py .
python -B -m unittest discover -s tests -v
python -B -m py_compile ten-step-learning-report/scripts/validate_report.py
```

Current result: five Skill directories pass structural validation; fourteen unit tests pass. Tests cover unique display metadata, explicit invocation policy, default prompts, checkpoint fields, answer protection, learner-first Feynman behavior, template placeholders, and report validation success/failure paths.

## Forward evidence

- Adaptive exam, two turns: passed. With a bounded intermediate TCP congestion-control request, the Skill stated scope and stopping rule, then asked one question without revealing an answer, rubric, or future question. After a deliberately incorrect answer it scored 3/10, cited the demonstrated fragment, corrected the `ssthresh` and AIMD errors, kept difficulty stable, and asked a targeted variant.
- Feynman loop, two turns: passed. With a CAP theorem request, the Skill asked the learner to explain, provide an example, describe the tradeoff, and name a boundary before offering instruction. After an overgeneralized answer it isolated the missing partition boundary, gave a minimal scenario hint, and requested a revised explanation rather than replacing the learner's work with a lecture.
- Full HTML report: passed. An isolated SQL JOIN run produced a 54,912-byte self-contained report with all ten required step IDs, no unresolved placeholders, nine normalized sources, and all four continuation invocations. The report validator rejected the intermediate template before the step body was inserted and accepted the completed file afterward, demonstrating that the completion gate catches partial artifacts.
- Live Codex `/skills` picker discovery: not yet verified. The installed desktop-app executable is visible but cannot be launched from the current restricted Windows process (`Access denied`). Static adapter and discovery-location contracts are verified; do not claim live picker validation until a usable Codex CLI/IDE session confirms it.

## Host status

- Portable structure: validated against the repository contract.
- Codex/ChatGPT adapter: statically validated; report and interactive behavior forward-tested; live `/skills` picker pending.
- Claude, Cursor, WorkBuddy/CodeBuddy: unverified. Do not claim behavioral parity until a forward task succeeds on each host.
