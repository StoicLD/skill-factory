# 自动触发与安装

本文件只用于配置或维护，不是日常写作的必读材料。Skill 源码和主入口是同目录的 `SKILL.md`；把源码放在普通项目目录，不代表宿主已经发现或加载它。

## 常驻规则片段

将下面两段并入当前生效的全局规则，保留其他规则；同一宿主只配置一份。Skill 的名称、描述及路径必须能够被该宿主发现。

> 面向用户的技术说明，应让懂相关技术、但没有参与前文讨论的读者顺着理解。明确必要的对象、动作和条件，保留正式名称与技术含义。刚交代清楚的内容可以简称；容易遗忘的背景，在影响理解时补充。
>
> 当准备解释或比较技术方案，或起草、审阅、改写工程文档内容时，使用 `technical-prose` Skill；聊天中的技术讨论同样适用，按当前任务判断，不只匹配本轮关键词。显式要求展开或改善技术表述也使用。简短事实回答、常规进度通知、仅修错字或排版只遵循前述原则。正文仍在上下文中时直接应用，无需每轮重读。

## 宿主接入

| 宿主 | 常驻规则放在哪里 | Skill 如何可被发现 |
| --- | --- | --- |
| Codex | 当前生效的用户级 `AGENTS.md`；检查 `CODEX_HOME` 及 `AGENTS.override.md`，避免编辑被覆盖的文件。 | 将 Skill 安装到宿主支持的用户级技能目录。当前官方文档列出 `~/.agents/skills/technical-prose/`。 |
| Cursor Agent Chat | User Rules。项目专用配置可以用 Always Apply 项目规则。 | 当前官方文档支持 `~/.agents/skills/technical-prose/` 与 `~/.cursor/skills/technical-prose/`。 |

维护一份源码，安装时复制或使用目标环境支持且经过验证的链接；避免同一宿主重复发现同名 Skill。安装包包含 `SKILL.md`、`agents/`、`references/` 及正文链接的维护文件。源目录与安装目录不同，更新源码后需同步或核对链接。

`agents/openai.yaml` 明确允许 Codex 隐式调用；通用 frontmatter 不设置仅手动调用或文件匹配限制。这样不依赖打开 Markdown 文件才能覆盖聊天讨论。Cursor 的 User Rules 适用于 Agent Chat，不能据此声称 Tab 或 Inline Edit 同样受约束。

以上入口依据 2026-09-27 已查阅的 [Codex Skills](https://learn.chatgpt.com/docs/build-skills)、[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Cursor Skills](https://cursor.com/docs/skills) 和 [Cursor Rules](https://cursor.com/docs/rules)。实际安装应核对所用版本及本地发现结果；远程宿主还需要其自身可访问的文件。

## 上下文与触发检查

常驻只保留上面的短规则和 Skill 发现信息。触发后读正文；仅遇到难判断的情况才读案例相应条目。不要常驻注入案例、验证记录或本安装说明。已读取内容不保证立即退出上下文。

在新会话中，不提 Skill 名称，分别请求讨论模块职责、比较方案、起草实施计划、解释验证记录，检查是否确实读取并应用正文。再以简短状态问答检查是否过度触发；用“继续”及上一轮任务检查是否依赖单轮关键词。按 [validation.md](validation.md) 记录宿主、加载证据和实际输出。

自动选择是模型判断；常驻加载要求能提高稳定性，但不构成每次必触发的程序保证。正文格式通过、独立 Agent 试用通过，也都不能代替 Codex/Cursor 新会话的真实自动发现与调用检查。
