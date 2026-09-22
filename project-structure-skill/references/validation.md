# 单仓库验证契约

## 验证层次

自动验证负责可判定结构，人工复核负责语义。不要用字符串匹配假装证明“事实正确”或“入口没有重复内容”。

所有深度至少确认：

- 解析后的目标就是 Git 顶层，可以是普通 `.git` 目录或 worktree 根的 `.git` 文件。
- 不存在未声明的 nested Git marker；允许的 submodule 或嵌套仓库必须由用户明确选择并采用相应契约，而不是忽略失败。
- branch、commit 和 remote 状态符合写入预览。

## `mapped` / `structured` JSON 契约

从写入预览生成一次性 JSON，放在目标仓库外的临时位置。不要把契约当成新的项目 manifest 提交。

```json
{
  "version": 1,
  "docs_root": "docs",
  "map_target": "docs/INDEX.md",
  "required_files": [
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "docs/INDEX.md",
    "docs/architecture/repository.md"
  ],
  "authoritative_docs": [
    "docs/architecture/repository.md"
  ],
  "entrypoints": [
    {
      "path": "AGENTS.md",
      "ordered_links": ["docs/INDEX.md"]
    },
    {
      "path": "CLAUDE.md",
      "ordered_links": ["docs/INDEX.md"]
    }
  ],
  "index": {
    "path": "docs/INDEX.md",
    "ordered_links": ["docs/architecture/repository.md"]
  },
  "ignored_directories": [
    ".agent-private",
    "scratch"
  ],
  "forbid_nested_git": true
}
```

字段规则：

- 所有路径是仓库根内的安全相对路径，不使用绝对路径、`..`、空段或逃逸 symlink。
- `docs_root` 是事实文档根；`map_target` 是共同文档索引且位于其中。
- `required_files` 只列必须存在的文件，不列空目录。
- `authoritative_docs` 只列事实文档；它们位于单一 `docs_root`，不同于入口和索引，并全部从共同索引可达。尚无事实内容时可以为空数组；索引说明现状，不创建占位事实文档。
- 每个 `entrypoints` 项必须位于 `required_files`，并在 Markdown 中按顺序出现 `ordered_links`。每个入口必须直接或经兼容入口到达 `map_target`。
- 入口和索引不做行数检查；MAP 职责由人工复核。新契约不填写 `max_lines`；兼容旧的一次性契约时，该字段仍可读取但不参与验证。
- `index` 的 `path` 等于 `map_target`；其声明的读取链可经子索引到达全部 `authoritative_docs`。
- 可选 `navigation_maps` 数组声明中间地图，每项使用与入口相同的 `path`、`ordered_links` 格式；入口、共同索引和中间地图的路径不能重复，也不能兼作事实文档。路径及链接目标均列入 `required_files`。
- `ordered_links` 声明该文件的前向读取依赖，允许为空。验证器检查这些链接实际存在、目标文件存在、入口到共同索引及共同索引到事实的可达性，并拒绝声明的读取链中的循环。普通返回目录或交叉引用无需列入读取依赖，不因这些链接构成环而报错。
- 链接必须是真实 Markdown 相对链接，解析后落在仓库内。声明的读取链支持内联链接（含 `<带空格路径>`、括号、可选标题）、完整/折叠/简写引用式链接和 URL 编码路径；网页链接、纯锚点、图片、代码示例和 HTML 注释不计入读取链。验证器是轻量解析器，不覆盖所有 Markdown 扩展或工具专属 include 语法；使用其他语法时报告该链未验证，并人工核实，不以自动结果冒充完整支持。
- `ignored_directories` 是可选的窄目录路径。验证器通过 `git check-ignore --no-index <dir>/.project-probe` 检查规则，不要求创建空目录。
- `forbid_nested_git` 为 `true` 时，根 marker 之外任意深度的 `.git` 目录或文件都会失败。
- 契约拒绝未知字段、重复或大小写碰撞路径，避免拼写错误被静默忽略。

示例名称不是固定要求。根据预览替换为项目真实入口、文档根、索引和 ignored 目录。

间接导航示例：`CLAUDE.md → AGENTS.md → docs/INDEX.md → docs/design/INDEX.md → docs/design/model.md`。两个入口分别声明下一跳，共同索引声明子索引；`navigation_maps` 声明子索引到事实文档的链接。`required_files` 包含这五个文件，`authoritative_docs` 只包含最后一个。没有事实文档时仍需入口到共同索引可达，索引的 `ordered_links` 可以为空。

## 运行

```bash
python "<SKILL_DIRECTORY>/scripts/project_probe.py" inspect --root "<REPOSITORY_ROOT>"

python "<SKILL_DIRECTORY>/scripts/project_probe.py" validate \
  --root "<REPOSITORY_ROOT>" \
  --contract "<TEMPORARY_CONTRACT_JSON>" \
  --expect-branch "<BRANCH>" \
  --expect-no-remotes
```

只有预览选择“尚无 commit”时才增加 `--expect-no-commits`。用户选择了 initial commit 或 remote 时不要使用相反检查。

脚本输出 JSON，任一检查失败返回非零状态。失败时保留目标现场和契约，报告具体 check；修复后重跑同一契约。

## 初始化验证

- `skeleton-only` 不需要契约，但要确认唯一 Git 根、branch 和所选 commit/remote 状态，并人工确认除用户允许内容外没有写入。
- `mapped` 和 `structured` 使用写入预览生成完整契约。
- 初始化契约可以把所有新建文件列入 `required_files`，但不要把既有项目的未知文件当成错误；本验证器不做仓库全量 allowlist。

## 演进验证

- 演进契约只声明本次必须满足的结构，不宣称拥有整个仓库。
- 验证前后比较 Git diff，确认只改了预览路径。
- 对从双仓库迁移的项目，另外搜索代码、测试、CI 和正式文档是否仍引用旧 Workspace、Context 仓库或 ignored 路径。
- 再次运行同一目标，预期无 diff；这才是幂等证据。

## 审计验证

- 审计契约只声明用户确认或项目现有规范已经要求的结构；未选择的可选入口、文档模块、ignored 目录、worktree 或 CI 约束不得视为缺陷。
- 审计前后比较 Git 状态，确认目标仓库没有因审计产生变化；临时契约必须位于目标仓库外。
- 自动检查通过只证明契约中可机械判定的结构。人工复核结果分别标记为 `conformant`、`non-conformant` 或 `unverified`，并附具体路径和证据。
- 审计发现不得自动转为写入。用户明确要求修复后按 `evolve` 处理，遵循写入预览和已有授权，无需重复要求操作名或已给出的批准。

## 人工复核

检查：

- 根入口只包含地图、最小启动规则和真实链接，没有详细项目事实副本。
- 每个正式事实只有一个权威路径；索引准确说明何时读取。
- 文档与当前代码、测试、决策和计划没有已知冲突；状态/验证日期在项目需要时存在。
- private/scratch 不含秘密、完整聊天或内部推理，也不被构建、测试、运行、CI 或交接依赖。
- 并行写入者使用独立 worktree 和非重叠所有权。
- linter/CI 的错误信息包含具体 remediation，且在当前环境真实运行过。

任一自动或人工检查失败时不宣称完成。

## 维护验证器

修改验证器后运行[回归测试](../scripts/test_project_probe.py)：

```bash
python -B -m unittest discover -s "<SKILL_DIRECTORY>/scripts" -p test_project_probe.py
```

测试覆盖间接导航、循环与断链、空事实集合、Markdown 链接形式、旧契约兼容、单一文档根和 CLI 成功/失败退出状态。
