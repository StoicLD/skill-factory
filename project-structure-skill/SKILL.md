---
name: project-structure-skill
description: Explicitly initialize, structurally evolve, or audit a single-repository, agent-legible project where a few thin native entry files such as AGENTS.md and CLAUDE.md map to authoritative facts in docs/. Do not use for routine project work or ordinary updates to existing status, plans, README content, or document indexes.
---

# 构建单仓库 Agent 项目结构

## 调用边界

仅在用户显式调用本 Skill，并要求以下操作之一时使用：

- `initialize`：初始化符合本 Skill 目标结构的新项目。
- `evolve`：主动调整现有项目的结构，使其趋近本 Skill 的目标结构。
- `audit`：只读审计现有项目是否符合本 Skill 的结构规范。

项目初始化或演进完成后，项目内的原生入口、文档索引、权威事实和机械约束独立承担日常治理；Agent 不需要在项目推进过程中持续加载本 Skill。

不得因普通任务会修改新会话可读取的文件而使用本 Skill。更新现有项目的状态、计划、里程碑、检查表、README、文档正文或索引内容，本身不构成结构演进；只有仓库边界、原生入口、文档路由、事实归属或机械约束的结构契约需要改变时，才使用 `evolve`。

## 目标

把 Agent 直接启动在产品 Git 仓库根，并建立一条短读取链：

```text
<REPOSITORY_ROOT>/
├── .git/
├── <NATIVE_ENTRY_A>          # 薄地图，例如 AGENTS.md
├── <NATIVE_ENTRY_B>          # 仅在另一工具确实需要时，例如 CLAUDE.md
├── docs/
│   ├── <DOCUMENT_INDEX>      # 文档地图
│   └── <AUTHORITATIVE_DOCS>  # 需求、架构、决策、计划、质量等事实
├── <PRODUCT_FILES>
├── <IGNORED_PRIVATE_DIR>/    # 可选；非权威、仅本机
└── <IGNORED_SCRATCH_DIR>/    # 可选；可删除
```

始终保持：

- 一个产品仓库同时承载代码、测试、正式文档、当前计划和验证证据；不创建配套 Context Git 仓库或外层路由工作区。
- 每类已确认的工具原生入口只保留一个短地图。入口说明工作目录、权威来源、必读顺序和失败行为，并用相对链接导航；不复制项目事实。
- `docs/` 是结构化事实源。每项事实只有一个权威位置，入口和索引只引用它。
- 私有记忆、原始日志和一次性实验不是产品事实；需要仓库内路径时放入明确被 Git 忽略的目录，且不得成为构建、测试、运行或交接依赖。
- 同一工作树同一时刻只有一个写入者。并行实现使用按任务创建的独立 branch/worktree、明确路径所有权和单一合并负责人。
- 能机械验证的约束优先交给脚本、测试或 CI；不要只在提示词中要求 Agent 自觉遵守。

需要判断信息归属时读取[文件与事实契约](references/file-contracts.md)。

## 选择操作和深度

选择 `initialize` 创建新仓库，选择 `evolve` 最小修改现有仓库，或选择 `audit` 只读检查现有仓库。能够从显式请求、路径和 Git 状态可靠判断时不要重复询问；无法区分操作时先确认，不要把普通项目维护推断为结构演进。

采用满足目标的最低深度：

- `skeleton-only`：只建立或确认一个 Git 仓库，不创建入口或文档。
- `mapped`：增加已确认的原生入口和文档索引；有真实事实内容时再增加所需文档。
- `structured`：在 `mapped` 上增加用户确实需要的决策、计划、质量、运行手册、协作或机械约束模块。

读取[Profiles 与结构槽位](references/profiles.md)。当缺失选择会改变实际写入时，一次性说明推荐项和取舍后再确认；不要为结构对称创建空目录或占位文档。

## 收集配置

复用已提供信息，只补齐会改变产物的缺失项：

- 仓库绝对路径、`initialize`、`evolve` 或 `audit`，以及初始化时的 branch。
- 每种目标工具在仓库根实际会读取的原生入口文件。只使用用户提供、现有项目证明或当前工具文档确认的名称；未知时标记为手动入口或要求确认。
- 文档根和索引名称，以及现有项目约定优先级。
- 需要成为权威事实的真实模块和当前已有内容。
- 是否需要本地私有目录、临时目录、并行 worktree 或 CI/linter。
- 是否创建 commit、配置 remote、安装依赖或修改 CI；默认均不执行。

文件名和目录名是项目配置，不是本 Skill 的全局常量。`AGENTS.md`、`CLAUDE.md`、`docs/INDEX.md`、`.agent-private/` 和 `scratch/` 只是常见示例。

## 检查现状

写入前执行只读检查：

1. 解析仓库和父路径，识别大小写等价路径、symlink、junction、Git worktree 的 `.git` 文件及嵌套仓库。
2. 确认预期根目录就是 Git 顶层；初始化目标若存在未知内容，则改为演进分析，不覆盖或清空。
3. 读取已有原生入口、文档索引、`.gitignore`、当前计划、相关事实文档和 Git 状态。
4. 识别入口中的项目事实、重复文档、失效链接、未跟踪私有内容及仅靠文字声明的约束。
5. 解析本 `SKILL.md` 所在目录为 `<SKILL_DIRECTORY>`，运行 `python "<SKILL_DIRECTORY>/scripts/project_probe.py" inspect --root "<REPOSITORY_ROOT>"`，再结合人工阅读判断职责；脚本输出不是授权。

## 生成写入预览

`initialize` 或 `evolve` 的任何写入前列出：

- 操作、深度、解析后的仓库根、branch/commit/remote 选择。
- 每个工具的已确认入口能力，以及入口到文档索引再到事实文档的读取链。
- 每个事实的唯一权威路径；从入口迁出的内容及原位置保留方式。
- 每个 `keep`、`create`、`edit-in-place`、`move`、`rename`、`merge`、`archive` 或 `delete` 路径。
- `.gitignore` 变化、私有/临时目录语义、worktree 和机械约束选择。
- 一次性验证契约摘要，以及明确不会执行的 commit、remote、依赖、CI 或业务实现。

预览用于审查影响，不是自动新增的审批关卡。现有授权覆盖的新增、编辑和常规整理可在预览后继续；具体授权边界见[迁移授权规则](references/migration.md#授权与风险)，不要重复索取已获得的批准。

## 初始化

1. 确认目标不在另一个 Git 工作树内，且不会形成 nested Git；Git worktree 根本身可以使用 `.git` 文件。
2. 用用户选择的 branch 初始化唯一仓库；`skeleton-only` 随即停止。
3. 为每种已确认的原生入口创建一个短地图；多个 Agent 共用同一原生入口时合并为一个文件，不按 Agent 数量复制。
4. 创建一个文档索引，并只创建能够写入真实内容的事实文档。入口和索引保持 MAP 职责；篇幅建议见[根部原生入口契约](references/file-contracts.md#根部原生入口)，不以行数决定是否拆分。
5. 若选择本地私有或临时目录，先以最小方式合并 `.gitignore`，再按需创建实际文件；不要创建空目录占位。
6. `structured` 只增加已选择的模块。根据项目语言和 CI 环境实现 linter/test；错误信息同时指出违规路径、规则和修复动作。
7. 不创建第二仓库、外层 Workspace 路由、机器绝对路径、应用脚手架、commit、remote 或依赖，除非用户分别要求。

## 演进

必须读取[演进与单仓库迁移](references/migration.md)，计算现状到目标的逐路径差异并应用最小变化。

- 优先使用 `keep`、`create` 和 `edit-in-place`；已授权目标需要移动、重命名、合并或归档时，按迁移授权规则执行最小变化。
- 同名入口先读后合并项目专属规则；不要用模板覆盖。
- 先建立权威文档，再把入口缩减为链接地图；未验证新读取链前不要移除旧事实。
- 从双仓库结构迁移时，先把经确认的产品事实晋升到产品仓库，把必要私有状态降级到 ignored 本地目录；保留旧仓库，直至用户批准归档或删除。
- 重复执行相同目标应成为验证或无操作，不得追加重复段落或重写已满足内容。

## 审计

`audit` 默认且始终只读。显式调用审计不授权修复、移动、创建或删除文件，也不授权改变 Git、依赖、CI 或远程状态。

1. 确认审计目标、适用深度和项目已声明的工具原生入口；没有选择的可选模块不得记为违规。
2. 执行“检查现状”中的只读检查，并读取[文件与事实契约](references/file-contracts.md)和[验证契约](references/validation.md)。
3. 根据项目现有约定和用户确认的目标生成一次性审计契约；契约放在仓库外，不得成为新的项目 manifest。
4. 运行自动检查，并人工复核入口是否为薄地图、事实是否单一权威、私有内容是否脱离权威链、机械约束是否真实可执行。
5. 将结果分为 `conformant`、`non-conformant` 和 `unverified`，逐项给出路径、证据、适用规则和最小修复方向；不要把偏好或未选择的结构槽位写成违规。
6. 审计完成后停止。用户随后明确要求修复时，按 `evolve` 生成写入预览并执行已授权变更，不要求用户重复输入操作名。

## 验证

读取[验证契约](references/validation.md)。`initialize` 和 `evolve` 从写入预览生成工作区外的一次性 JSON 契约；`audit` 从已确认的审计目标生成同类一次性契约。执行：

```bash
python "<SKILL_DIRECTORY>/scripts/project_probe.py" validate \
  --root "<REPOSITORY_ROOT>" \
  --contract "<TEMPORARY_CONTRACT_JSON>"
```

按预览选择 branch、commit 和 remote 检查。验证器应确认单一 Git 根、无意外 nested Git、必需文件、真实相对链接、共同文档索引和事实文档可达、声明的读取链无循环及 ignore 规则。允许兼容入口和子索引形成间接导航；入口和索引的篇幅不设机械门槛。

人工复核验证器无法证明的语义：入口是否只做地图；事实是否唯一且具体；私有内容是否未进入权威链；构建是否不依赖 ignored 路径；并发写入是否使用独立 worktree；CI remediation 是否可执行。

任一检查失败时不要宣称完成。保留现场，报告准确失败项、已完成写入和安全后续选择。

## 最终交付

`initialize` 或 `evolve` 报告最终深度、仓库根、实际入口链、权威文档、ignored 路径、机械约束、Git 状态、自动与人工验证结果，以及未执行操作。`audit` 报告审计目标、合规项、不合规项、未验证项、证据和最小修复方向。完成结构任务后停止，不自动开始产品设计、业务实现或审计修复。
