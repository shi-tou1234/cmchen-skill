# references 导读

> **来源**：本目录由 `cmchen-agent-thinking-guidance` 项目维护。
> **许可**：整体 AGPL-3.0（见根目录 `LICENSE`）。方法类文件改编自 MIT 的 fable-method，训练类文件改编自 MIT 的 qwen3 蒸馏笔记；二者并入 AGPL 作品后随作品整体受 AGPL 约束。

本目录是 `cmchen-agent-thinking-guidance` 的深度参考资料。主入口 `SKILL.md` 已给出三轨融合的完整行为规范；需要**方法全量规则**、**思轨语言签名与可蒸馏标准**、**审轨门禁细节**、**对抗验证流程**、**编排执行策略**或**场景适配**时再翻这里。

## 三个来源

| 来源 | 贡献 | 许可 |
|---|---|---|
| `Kuberwastaken/Fable-5-traces`（4,665 条真实 Claude Fable 5 思维链） | 全部量化数据（百分比/次数/频率），由 Fable5res 统计提炼并逐条校验（31/31 通过） | AGPL-3.0 |
| `Sahir619/fable-method`（15 轮对抗评测、260+ 次运行） | 7 步方法、硬门禁、对抗验证、编排循环、失败模式 | MIT |
| `Dhamodharan2006/fable5-qwen3-thinking-distillation` | `<think>` 结构、训练路线、蒸馏工程教训 | MIT |

## 方法类（改编自 fable-method，MIT）

| 文件 | 内容 | 什么时候看 |
|---|---|---|
| `method.md` | 7 步方法全量规则：平凡性门、适配门、Step 0-6 每步规则与 tie-break、意图/召回/授权/双生/工件门细节、验证失败路由、报告规范、审计模式、诊断词汇 | 主入口"完整流程"想深挖，或做审计 |
| `judge.md` | 对抗式验证：把"完成"当声明集、重跑验证、猎捕六类欺诈、VERIFIED/CAVEATS/REFUTED 判决、suite 模式 | 交付前自检，核验他人声称的完成 |
| `loop.md` | 编排式执行：四阶段（PLAN/EXECUTE/VERIFY/AUDIT）、并行证据子代理、攻击者验证、模型经济、子代理分工 | 大任务、无人值守、会扇出子代理时 |

## 思轨类（融合 Fable5res 语言签名与 qwen3 蒸馏教训）

| 文件 | 内容 | 什么时候看 |
|---|---|---|
| `voice-and-think.md` | 可蒸馏格式五条标准（硬门）、语言签名运行时不变量（CoT 结构/人称/连接词/自修正/验证词/工具行为/对冲与确定）、自然推理流每轮节奏、Markdown 使用、反模式 | 想深入了解"怎么想"，或检查思维链是否可蒸馏 |

## 审轨类（改编自 fable-method，MIT）

| 文件 | 内容 | 什么时候看 |
|---|---|---|
| `gates.md` | 全部 8 个门禁（平凡/适配/分类/意图/召回/授权/双生/工件）和 3 个硬上限（3 次失败/外部阻塞/取证轮次），每个附带触发条件、通过标准、不通过路由、阻止的失败模式；门禁速查表 | 查某个门的具体规则，或审计时定位跳步风险 |
| `failure-modes.md` | 18 种失败模式表（症状 → 由哪步防住，含 done/skipped/faked 审计口径） | 审计 agent 记录，或当复查清单 |

## 场景类

| 文件 | 内容 | 什么时候看 |
|---|---|---|
| `coding.md` | 编码流程：Read → Understand → Plan → Write → Verify → Iterate | 写/改代码时想深挖 |
| `debugging.md` | 调试流程：OBSERVE → INVESTIGATE → HYPOTHESIZE → ROOT CAUSE → FIX → VERIFY | 排查 bug 时 |
| `architecture.md` | 架构设计：UNDERSTAND → DESIGN → 垂直切片 → VERIFY → ITERATE | 做架构决策时 |
| `verification.md` | 验证词汇层级：5 个验证短语织进推理 | 想深挖验证行为时 |
| `examples.md` | 六种任务形状的完整示例（三轨并行 + 门禁痕迹） | 想看完整跑通的例子时 |
| `flowcharts.md` | 8 张决策流程图（含第 8 张【原创】三轨交汇图） | 想跟着箭头走时 |
| `domains/TEMPLATE.md` | 领域适配器 schema | 想造新适配器时 |
| `domains/coding.md` 等 9 个 | 各领域适配器（研究/数据/营销/运维/设计/业务/财务/法务） | 非编码领域适配 |

## 训练类（改编自 qwen3 蒸馏笔记，MIT）

| 文件 | 内容 | 什么时候看 |
|---|---|---|
| `training-notes.md` | 训练路线：QLoRA 配置、`<think>` 模板、复现步骤 | 想微调自己的小模型内化这套思维 |
| `distillation.md` | 权重蒸馏核心工程教训 + 可蒸馏门理论依据 | 想理解"为什么思维链是训练目标" |

## 许可提醒

本 Skill **整体按 AGPL-3.0 发布**（见根目录 `LICENSE`）：派生自 AGPL-3.0 数据集与 Fable5res 包，copyleft 继承。

- **方法类文件**（`method.md`、`gates.md`、`judge.md`、`loop.md`）改编自 MIT 的 fable-method，其内容在并入 AGPL 作品后随作品整体受 AGPL 约束。
- **训练类文件**改编自 MIT 的 qwen3 蒸馏笔记，同样在并入后受 AGPL 约束。
- **思轨类文件**（`voice-and-think.md`）融合了 AGPL-3.0 数据集的量化签名与 MIT 蒸馏笔记的工程教训，其中可蒸馏格式五条标准为【原创】。

分发或改造时请遵守 AGPL copyleft 条款。
