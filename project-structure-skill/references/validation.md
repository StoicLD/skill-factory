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
      "max_lines": 100,
      "ordered_links": ["docs/INDEX.md"]
    },
    {
      "path": "CLAUDE.md",
      "max_lines": 100,
      "ordered_links": ["docs/INDEX.md"]
    }
  ],
  "index": {
    "path": "docs/INDEX.md",
    "max_lines": 200,
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
- `authoritative_docs` 只列事实文档；它们位于 `docs_root`，不同于根入口和文档索引，并全部由索引链接。
- 每个 `entrypoints` 项必须位于 `required_files`，不超过 `max_lines`，并在 Markdown 中按顺序出现 `ordered_links`。每个入口必须直接链接 `map_target`。
- `index` 的 `path` 等于 `map_target`，其 `ordered_links` 覆盖全部 `authoritative_docs`。
- 链接必须是真实 Markdown 相对链接，解析后落在契约声明的仓库文件内；网页链接、锚点和图片不计入读取链。
- `ignored_directories` 是可选的窄目录路径。验证器通过 `git check-ignore --no-index <dir>/.project-probe` 检查规则，不要求创建空目录。
- `forbid_nested_git` 为 `true` 时，根 marker 之外任意深度的 `.git` 目录或文件都会失败。
- 契约拒绝未知字段、重复或大小写碰撞路径，避免拼写错误被静默忽略。

示例名称不是固定要求。根据预览替换为项目真实入口、文档根、索引和 ignored 目录。

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
- 审计发现不得自动转为写入。修复需要用户显式调用 `evolve`，并遵循写入预览和授权边界。

## 人工复核

检查：

- 根入口只包含地图、最小启动规则和真实链接，没有详细项目事实副本。
- 每个正式事实只有一个权威路径；索引准确说明何时读取。
- 文档与当前代码、测试、决策和计划没有已知冲突；状态/验证日期在项目需要时存在。
- private/scratch 不含秘密、完整聊天或内部推理，也不被构建、测试、运行、CI 或交接依赖。
- 并行写入者使用独立 worktree 和非重叠所有权。
- linter/CI 的错误信息包含具体 remediation，且在当前环境真实运行过。

任一自动或人工检查失败时不宣称完成。
