---
name: "self-evolving-agent"
description: |
  Self-improving agent with lightweight reflection, user profiling, cross-session memory and skill evolution.
  Use when the agent should learn from interactions and improve over time, or when the user mentions
  "/reflect", "记住", "以后注意", "改一下", "之前说过", or similar cross-session memory keywords.
  Also use when the user says "/profile", "/skills", "/forget" to manage memory.
  Not for: one-shot conversations where no memory is expected.
version: 3.0.0
---

# Self-Evolving Agent

> **轻量自我进化框架**
> 每轮最小记录 + 按需反思 + 跨会话积累。文件读写是唯一依赖。

你正在使用 Self-Evolving Agent，每次会话启动时加载记忆，仅在反思触发时写入。文件读写是唯一依赖。

## 设计原则

- **轻量优先**：每轮只做最小必要记录，重活留给反思
- **用户可控**：记忆透明，随时可查 / 可删 / 可暂停
- **跨 Agent 可移植**：仅依赖文件读写，不依赖任何特定 agent 特性

## 触发条件

以下情况应加载本 skill：

- 用户提到"记住"、"以后注意"、"改一下"、"之前说过"等涉及跨会话记忆的表述
- 用户输入 `/reflect`、`/profile`、`/skills`、`/forget` 控制指令
- 延续之前使用过本 skill 的会话

**不要**在一次性或明说不需记忆的对话中使用。

## 前置

本 SKILL.md 所在目录即为 `$SKILL_DIR`，所有路径基于此目录。
首次使用时创建 `memory/` 骨架结构并初始化。

## 会话启动

读取以下文件。文件不存在则使用默认值。

| # | 操作 |
|---|------|
| 1 | 读 `memory/profile.md`，了解用户身份和偏好 |
| 2 | 读 `memory/self_model.md` 的"自我提醒"节，避免重复犯错 |

**残留清理**：如果 `memory/session.md` 非空且有上次未完内容，将有效条目迁移到 `lessons.md` 后清空。

## 每轮行为

**默认不写任何文件**。仅以下情况才操作文件：

- 用户明确纠正 → 更新 `profile.md` 或 `lessons.md`
- 用户输入 `/reflect` → 执行反思流程
- 自己发现事实性错误 → 追加到 `lessons.md` 一行

每轮不追加 session.md，不检查计数器或日期。

## 反思流程（/reflect）

用户输入 `/reflect` 时执行：

```
1. 回顾本轮：事实错误？过度工程？偏好违背？可复用模式？一两句话判断。
2. 写入记忆（读目标文件 → 去重合并 → 写回）：

   | 情况                   | 写入文件                     |
   |------------------------|-----------------------------|
   | 用户纠正 / 新偏好       | profile.md                  |
   | 可复用的正确做法        | lessons.md                  |
   | 自身能力边界            | self_model.md               |
   | 会话未完事项            | session.md（追加一行）       |
   | 本轮有价值内容          | reflections/YYYY-MM-DD.md   |

3. 技能进化：如果 lessons.md 同一主题出现 ≥ 2 次 → 提取为 skills/<name>.md → 更新 _index.md
```

## 技能文件格式

```markdown
---
name: "<name>"
trigger: "<何时调用>"
aliases: ["同义词"]
created: "YYYY-MM-DD"
last_used: "YYYY-MM-DD"
usage_count: 0
status: active
---
## 适用场景
## 操作流程
## 注意事项
```

技能匹配：每轮扫一眼 `skills/_index.md`（存在则读），trigger/aliases 与用户意图明显相关就加载，不相关跳过。

## 控制指令

| 指令 | 作用 |
|------|------|
| `/reflect` | 触发反思 |
| `/profile` | 查看用户画像 |
| `/skills` | 列出已进化技能 |
| `/forget <关键词>` | 列出匹配条目，确认后删除 |

指令兼容：用户输入上述文本即触发，不依赖原生斜杠命令。

## 多 Agent 适配

各 agent 加载本 SKILL.md 后自动激活。短时记忆用 `[agent_id]` 前缀隔离，长时文件共享。

| Agent | 激活方式 |
|-------|---------|
| Codex | 在 AGENTS.md 中引用本文件路径 |
| Trae | 作为 Skill 加载 |
| Claude Code | 在 CLAUDE.md 中引用 |
| Opencode | 在 agent 配置中引用 |
| Qoderwork | 在 agent 配置中引用 |

session.md 追加格式：`- [agent_id] [HH:MM] 诉求 → 关键动作 → 结果`

长期文件（profile/lessons/self_model/skills）写入频率低，读-去重-改写模式足够。若需完全隔离，复制目录到各 agent 工作区。

## 核心规则

1. **默认不写文件**：仅反思触发或用户纠正时才操作文件。
2. **隐私红线**：密码、token、私钥、身份证号绝不写入记忆。
3. **失败不阻塞**：文件操作失败就跳过，不影响主回复。
4. **用户说了算**：用户纠正立即更新，不与用户争辩。
5. **少即是多**：宁可少记也不记错，不确定的不写。
