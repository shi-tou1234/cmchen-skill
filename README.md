# cmchen-skill

个人使用的 AI agent 技能（Skill）集合，按用途分为三个独立技能包。

## 技能包

### cmchen-writing（v3.1）

个人写作风格生成器。基于博客全部 84 篇文章的全量语料分析重建，核心是**四轨声音系统**：

| 轨道 | 用途 |
|------|------|
| A1 冷峻小说腔 | 虚构小说、叙事写作 |
| A2 温热日记腔 | 日记体情感记录 |
| B 冷面博客腔 | 技术随笔、踩坑记录、工具测评 |
| C 学习笔记腔 | 教科书骨架 + 讲课口语的笔记 |

配套 15 个签名技法、口语词库与四层自检流程，写作时拿不准的句子可到 EXAMPLES.md 逐段比对。

### 反思skill（self-evolving-agent v3.0）

轻量自我进化框架，基于文件读写实现跨会话记忆与反思。每次会话加载历史记忆，仅在反思触发时写入——只做必要记录，不做过度积累。

- 用户画像（profile）——记录偏好与技术背景
- 经验教训（lessons）——沉淀可复用工作模式
- 自我模型（self_model）——记录能力边界与易错点
- 技能进化（skills）——从教训中提取可复用的技能片段
- 控制指令：`/reflect`、`/profile`、`/skills`、`/forget <关键词>`

### security-scan（codex-security-scan）

基于 OpenAI 开源的 [codex-security](https://github.com/openai/codex) 项目移植的自动化安全审计工具包，在 Claude Code 环境中运行，提供 6 种能力：标准扫描、Diff 审查、深度扫描、漏洞修复、加固方案、漏洞报告。整个过程只读扫描，不修改代码，无需云登录或第三方后端。

## 目录结构

```
cmchen-skill/
├── cmchen-writing/        # 写作风格生成器（SKILL.md + EXAMPLES.md）
├── 反思skill/             # 自我进化框架（README.md + 反思skill具体描述/）
└── security-scan/         # 安全审计工具包（SKILL.md + references/schemas/scripts/skills）
```

## 使用方式

每个技能包即一个 Skill 目录，将对应目录放入 agent 的 skills 目录（如 `~/.claude/skills/`）后即可按各自的触发词调用。具体安装方式与调用约定见各技能包内的 README/SKILL.md。
