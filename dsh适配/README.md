# cmchen-skills (DSH Bundle)

DeepSeek Harness bundle that packages the cmchen personal skills for installation via `dsh`.

## 包含的技能

| 技能 | 一句话 |
|------|--------|
| `cmchen-writing` | cmchen 个人写作风格生成器，六模式路由 |
| `cmchen-learning` | 回合制交互式教学助手 |
| `cmchen-blog-writing` | PPT/PDF/讲义 → 博客 Markdown 文章 |
| `cmchen-self-evolving-agent` | 跨会话记忆与自我进化 |
| `cmchen-security-scan` | 自动化安全审计（只读扫描，无云依赖） |
| `cmchen-agent-thinking-guidance` | 三轨一门协议：像 Claude 一样思考与做事 |
| `cmchen-political-writing` | 高校政治类论文写作，五类型路由 |

## 安装

```bash
dsh install ./dsh适配
```

## 重新生成元数据

```bash
cd dsh适配 && npm run extract
```