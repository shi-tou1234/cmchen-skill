# 安全加固提案格式（Security Hardening Proposal Format）

本格式用于基于漏洞披露、已有 findings、事件/评估文档、源码证据、一次已完成的安全扫描或它们混合的**派生加固分析**。该分析是设计产物：不是其源证据的一部分，也不证明任何 finding 已被修复。

## 产物集（Artifact Set）

在一个分析目录下写以下文件：

```text
<analysis_dir>/
├── context.md
├── hardening.json
├── hardening.md
├── proposals/
│   └── <opportunity-id>.md
├── diagrams/
│   ├── <opportunity-id>-before.mmd
│   └── <opportunity-id>-<option-id>-after.mmd
└── implementation/
    └── <option-id>.md
```

`context.md` 是本地工作上下文，可含本地源码根路径。其余产物必须可分发，只用仓库相对源码路径与分析相对产物链接。

`implementation/` 只在用户选定选项或明确要求实施规划后创建。

## 写作语气与叙述（Writing Voice And Narrative）

写给技术强但可能不熟悉该子系统或原始扫描的安全工程师与软件工程师。文档要像资深安全工程师平静地带同行走一个设计问题：专业温和、精确、对不确定坦诚、乐于听取意见。不要机械、危言耸听、官僚或过于亲昵。

把第一人称当作设计评审声音的组成部分：

- 实质走查全程用第一人称复数引导共享推理："我们能看到当前归属边界为何漂移"、"如果我们保住快路径"、"只有在旧代次排空时我们才会付这笔内存成本"
- 第一人称单数要真实且克制，用于建立作者实际完成的工作与所提建议："我核对了这些调用者"、"我测了"、"我没能验证设备暴露"、"在当前约束下我建议选项 2"
- 依据是源码核对、提供的证据、类比或假设时，绝不暗示代码被运行、性能被测量或行为被观察。用平实语言说出用的是哪种依据。

这不是代词配额。不要用孤立的 "we"/"I" 装饰机械散文。第一人称应暴露推理、把读者请进设计选择、让作者的证据基础可审计。只有首尾两句第一人称的提案仍不合格。

让专业判断显出来。解释选项吸引人之处、让作者犹豫之处、哪个取舍看似相称、哪个未知阻止了更强结论。"让我犹豫的是…"、"这选项的吸引点在于…"、"我们该诚实面对…"、"如果…我会舒服一些"这类短语示意语气，但不是脚本。用贴合实际设计的语言，避免在 portfolio 里重复套句。

构建连贯技术论证，而不是填模板。耐心连接相关角色与边界、观察到的失败、允许它的结构条件、期望不变量与可用设计选择。保留必需表格，并在确切增量、覆盖映射或跨选项比较适合紧凑视图时善用它们。把表格当第二层供扫描与引用，不是替代"教读者为何比较要紧"的散文。先介绍图与源码引用，再用文字解释重要边。

平静清楚地讨论选项。给每个严肃替代它最强合理情形、成本、残余风险与它应当胜出的条件。给出建议但不推销、不搞选项表演。优先用"在当前约束下我建议选项 1"与"如果…则选项 2 更可取"。局部修复相称时照直说，不要硬造架构项目。

Portfolio 要简洁，但提案不应读成短促的分诊笔记或拼凑的子弹。给 portfolio 足够散文解释为何这些机会构成连贯的决策集。给每个提案足够讨论，让工程师能质疑诊断、比较选项、在无需重建论证的情况下开始实施。用段落做推理，用列表放真正列表形状的材料。保持散文自然节奏；终端友好换行在不伤害清晰度、链接、表格、代码引用或技术语言时受欢迎。

接受某提案前，确保叙述本身（不靠表格）做到以下全部：

- 把观察证据连接到推断的结构条件，并解释该推断为何合理
- 给每个严肃选项它最强情形，包括它保留什么、改什么、控制如何运作、风险留在哪里
- 解释物质安全、性能、内存、可靠性、运维与迁移效应背后的机制
- 让作者深思熟虑的观点可见，包括每选项吸引人之处、主要顾虑、什么证据能解决它
- 介绍每个图与表，然后解释读者应从中取出的决策相关边或比较
- 提供有条件建议，点名会让另一选项更可取的事实、约束或优先级

拒绝并重写以下散文：无人情味、机械镜像标题结构、把选项压缩成图+增量表+一个短段。深度跟随决策复杂度；不要为凑人工长度目标而填充简单点。

对复杂架构替代，图与表周围一个引言段一个结论段通常不够。用能独立成立的连贯散文展开选项：先给最强情形并解释机制；再推演安全与残余风险；然后真正关注可能改变决策的资源、可靠性与迁移效应。解释该选项可信的引入与回滚姿态，而不仅是最终建议。真正中性或简单的点可压缩，不要制造等长章节。

## 结构化分析（Structured Analysis）

`hardening.json` 为 UTF-8 JSON，形状如下。允许携带有意义语义的额外字段，但不要把 `extensions` 当成应放进提案的散文的垃圾桶。

扫描背书的第一例：

```json
{
  "documentType": "security-scan.hardening-analysis",
  "schemaVersion": "1.0",
  "analysisId": "hardening_20260619_example",
  "sourceScan": {
    "scanDir": ".codex-scan/scan_xxx",
    "targetRevision": "deadbeef",
    "sourceDrift": "none"
  },
  "assessment": {
    "outcome": "opportunities_identified",
    "summary": "扫描支撑一个跨切面的遏制机会。"
  },
  "constraints": {
    "profile": "balanced",
    "changeHorizons": ["incremental", "medium_term", "foundational"],
    "nonNegotiables": [],
    "assumptions": ["未提供测量延迟或内存预算。"]
  },
  "opportunities": [
    {
      "opportunityId": "centralize-archive-containment",
      "title": "集中归档目标遏制",
      "summary": "把目标派生与遏制放到一个专属提取边界之后。",
      "diagnosis": "多个提取路径可独立构造文件系统目标。",
      "evidence": [
        {
          "claimType": "observed",
          "sourceKind": "finding",
          "findingId": "csf_852f90d6e1177502ff113d4a",
          "path": "src/extract.py",
          "claim": "归档条目路径在无遏制校验时到达文件系统写入。"
        }
      ],
      "desiredInvariants": ["每个提取写入都使用被证明仍处于调用方输出根之下的目标。"],
      "proposalPath": "proposals/centralize-archive-containment.md",
      "options": [
        {
          "optionId": "local-guards",
          "title": "强化局部守卫",
          "kind": "baseline",
          "summary": "给每个既有提取路径打补丁并加共享回归用例。",
          "findingCoverage": [
            {
              "findingId": "csf_852f90d6e1177502ff113d4a",
              "effect": "addresses",
              "tacticalFixRequired": true,
              "rationale": "局部遏制检查本身就是战术修复。"
            }
          ],
          "tradeoffs": [
            {
              "dimension": "security",
              "direction": "improves",
              "confidence": "high",
              "basis": "source-derived",
              "assessment": "观察到的写入路径拒绝逃逸条目，但未来调用者仍可能省略守卫。",
              "validationPlan": "重跑原始穿越 PoC 并搜索每个提取写入路径。"
            },
            {
              "dimension": "performance",
              "direction": "neutral",
              "confidence": "medium",
              "basis": "source-derived",
              "assessment": "局部词法遏制检查不引入 I/O 或进程边界。",
              "validationPlan": "守卫前后基准测试代表性归档提取。"
            }
          ],
          "residualRisks": ["遏制策略可能在调用点之间漂移。"],
          "implementationReadiness": {
            "affectedComponents": ["src/extract.py"],
            "workPackages": ["添加遏制强制与回归覆盖。"],
            "acceptanceCriteria": ["原始穿越 PoC 无法写到输出根之外。"],
            "migrationNotes": [],
            "rollback": "回滚聚焦守卫与测试改动。"
          }
        }
      ],
      "recommendedOptionId": "local-guards",
      "recommendation": "仅当交付时间主导复发风险时用基线。"
    }
  ],
  "openQuestions": []
}
```

对披露、提供的 findings 或其它非扫描集合，用完整性记录的证据身份替换 `sourceScan`：

```json
{
  "sourceEvidence": {
    "kind": "document_collection",
    "label": "内核漏洞披露文档",
    "collectionSha256": "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
    "artifactCount": 12,
    "sourceDrift": "unknown"
  }
}
```

选项映射到披露文档而非规范扫描 findings 时，用 `evidenceCoverage` 替代 `findingCoverage`：

```json
{
  "evidenceCoverage": [
    {
      "evidenceId": "evidence-001",
      "effect": "mitigates",
      "tacticalFixRequired": true,
      "rationale": "结构边界收窄复发风险，而受影响路径仍需要其直接生命周期修复。"
    }
  ]
}
```

### 必需语义（Required Semantics）

- 至少记录 `sourceScan` 或 `sourceEvidence` 之一。扫描加外部证据时可两者都在。
- 非扫描分析：`sourceEvidence.collectionSha256` 把分析绑定到盘点的输入集合。记录其 `kind`、读者向 `label` 与正 `artifactCount`。目标修订或快照摘要可选，因为普通披露可能不识别。
- `sourceDrift` 是 `none` / `present` / `unknown` 之一。
- `assessment.outcome` 是 `opportunities_identified` 或 `local_remediation_preferred`。
- `assessment.summary` 是报告索引用的简洁读者向结论。不得声称提议工作已实现。
- `opportunities_identified` 要求至少一个完整机会。`local_remediation_preferred` 要求空机会列表 + 解释战术修复为何相称的 portfolio。
- `claimType` 是 `observed` 或 `inferred`。提议行为属于选项文本，不进证据数组。
- `sourceKind` 是 `finding` / `disclosure` / `document` / `source` / `coverage` / `threat_model` / `poc` / `experiment`。披露、文档、PoC 或实验证据用 `evidenceId`，规范 finding 用 `findingId`。
- `kind` 是 `baseline` / `incremental` / `structural` / `isolation` / `foundational`。
- 每个选项必须至少有一个 `findingCoverage` 或 `evidenceCoverage` 映射。其 `effect` 是 `addresses` / `mitigates` / `unaffected` / `unknown`。
- `direction` 是 `improves` / `regresses` / `neutral` / `unknown`。`confidence` 是 `high` / `medium` / `low`。`basis` 是 `measured` / `source-derived` / `analogous` / `hypothetical`。
- `recommendedOptionId` 在约束不支持明确建议时可为 `null`；否则必须命名同一机会里的一个选项。
- 每个机会与选项 ID 在分析内唯一，只用小写字母、数字、点、下划线或连字符。
- 每个选项必须评估 `security` / `performance` / `memory` / `reliability` / `operability` / `migration`。用诚实的 `neutral` 或 `unknown` 条目，而不要省略不便的维度。

## Portfolio 格式（Portfolio Format）

`hardening.md` 按此顺序包含标题。普通或混合集合用 `Evidence Basis`；仅派生自扫描时 `Source Scan` 也可接受。

```markdown
# Security Hardening Review: <target>

## Evidence Basis
## Constraints
## Opportunity Portfolio
## Recommendation Summary
## Next Decisions
```

`Opportunity Portfolio` 下用紧凑表：

| Opportunity | Evidence | Options | Recommendation | Proposal |
| --- | --- | --- | --- | --- |

用其确切 `proposalPath` 链接每个提案。让建议对记录的约束保持有条件。此文档要易扫读；完整技术论证放提案文件。开头用足够散文给没参与扫描的读者定向，建议摘要用温暖的评审声音解释推理，而非复述表格。

`Evidence` 单元格离开 `context.md` 也必须有意义。用简短 finding 或文档标题（可选加 ID）、或链接到提案的清晰读者向组标签。不要写 `E021, E022, E031` 这类裸列表或不透明 canonical finding hash。例如优先 `Netlink 长度与 scratch 失败（E021, E031）`，或链接 `6 个解码边界 finding` 这样定义了全部六者的紧凑标签。

`local_remediation_preferred` 评估保留全部必需 portfolio 标题。`Opportunity Portfolio` 下说明无结构机会合格；`Recommendation Summary` 下解释局部修复结论。不要为虚构选项创建提案或图文件。

## 提案格式（Proposal Format）

每个提案命名为 `proposals/<opportunity-id>.md`，按此顺序用标题：

```markdown
# Security Hardening Proposal: <title>

## Decision
## Executive Recommendation
## Evidence
## Current Design And Failure Mode
## Desired Invariants
## Constraints And Non-Goals
## Before Architecture
## Options
### Option 1: <baseline, when useful>
### Option 2: <first alternative>
## Comparison
## Recommendation
## Evidence Coverage And Residual Risk
## Migration And Rollout
## Validation Plan
## Implementation Work Packages
## Open Questions
```

要求：

- 读者向选项编号从 1 开始，包括选项 1 是基线时；绝不把零基实现索引暴露成 "Option 0"
- 结构化 `optionId` 保持语义化且独立于显示顺序，使选项可重排而无需重命名机器向身份
- 在 `Executive Recommendation` 里先按编号与简短描述性标题引入每个选项，之后才只按编号引用
- 推荐子集前让完整选项集可见，避免会被误当成编号选项的编号步骤列表
- 在 `Evidence` 里显式标识 observed 与 inferred 论断
- 在使用处定义每个不透明 finding/证据 ID；配上简洁标题与一句"它确立了什么"，多项贡献时用紧凑证据映射
- 真核对过源码或产物时，用真实第一人称陈述该依据，并说明哪些证据最影响结构诊断
- 有源码时引用 finding/证据 ID 与仓库相对源码位置
- 解释结构条件，而不只是易受攻击行
- 提议组件前先陈述期望不变量
- 每个选项都含 before 图与一张 after 图
- 每对图后跟含 `Change` / `Before` / `After` / `Security consequence` / `Cost` 的 delta 表
- 含无捏造综合分数的取舍比较表
- 在依赖其图或 delta 表之前，用连贯散文解释每个选项，包括控制机制、最强情形、物质成本、残余风险、发布与回滚
- 解释当前假设下的建议，有支撑时用第一人称陈述，并说出另一选项何时应胜出
- 保留迁移期间需要的战术修复
- 列出具体验证、基准、发布、回滚与验收工作

多个 finding 或文档贡献时，`Evidence` 用此形状：

| Evidence | Finding or document | What it establishes |
| --- | --- | --- |
| `E021` | Netlink 多路径 scratch 耗尽 | 攻击者可控嵌套可耗尽未检查的解析器 scratch 空间。 |

可得时把 finding 或文档标题链接到其报告（分发的相对路径）。标题可为可读性缩短，但必须足够具体让新读者理解引用。在提案里定义一次 ID 后，后续散文在重复会笨拙时可直接用 ID。`Evidence Coverage And Residual Risk` 里每行同时标 ID 与短标题，例如 `E021 — Netlink scratch 耗尽`。规范扫描 finding ID 同样处理。`context.md` 里的完整登记支持审计，但不能让裸 ID 在另一文档中自解释。

提案要读成一个连贯讨论。特别地：

- 请读者选择选项前，先确立组件、相关角色、信任或生命周期边界与证据依据
- 让证据引用局部可懂；不要逼读者跑去 `context.md` 解码标识符
- 从观察到的事实自然过渡到推断的结构条件，显式说明认知状态变化，不把节降为标签
- 用散文引入每个选项，解释它保留什么、请项目改什么、改变后的边界如何产生安全效果，再用图或表锐化要点
- 每个图与比较表后回到散文，解释重要边、成本机制与剩余不确定
- 避免每个选项/提案重复同一开头、过渡与结论公式；让真实工程关注塑造讨论
- 公平比较替代，包括教人重要约束时有用的被拒或暂缓设计
- 有支撑时用第一人称陈述建议，解释为何它适合当前约束，点名会改变建议的证据或优先级
- 避免通用结尾。给审阅者留下具体决策、开放问题与细化或实现设计的舒适路径

## 图规则（Diagram Rules）

用 Mermaid `flowchart` 源码写进 `.mmd` 文件。图保持紧凑且只含安全相关：

- 前后视图复用组件名与抽象层
- 显示信任边界、攻击者可控入口点、控制归属、危险能力或 sink、故障遏制
- 清楚标注被改的控制或权限边
- 除非提议改动本身就是调用边界，避免代码级调用图
- 没有源码或部署证据支撑 before 视图时，不要暗示存在进程、服务、队列或沙箱
- 支撑细节放散文，别用段落塞满节点

## 取舍规则（Tradeoff Rules）

对每个选项评估以下维度：

| 维度 | 问题 |
| --- | --- |
| 安全 | 哪些攻击路径消失、收窄或保留？出现什么新可信组件？ |
| 性能 | 关键路径是否增加跳数、复制、序列化、锁或缓存缺失？ |
| 内存 | 是否有新进程、缓冲区、索引、队列、缓存或保留对象？ |
| 可靠性 | 故障隔离、重试、背压、恢复与可用性如何变化？ |
| 可运维性 | 出现什么新部署、可观测性、告警或事件响应负担？ |
| 迁移 | 需要哪些兼容、数据、协议、发布与回滚工作？ |

未测量效应要说出可能的机制与测量计划。有用计划要识别工作负载、指标、基线、候选设计与决策阈值。不要把类比或直觉当基准数据。

## 实施交接（Implementation Handoff）

选定后写 `implementation/<option-id>.md`：

```markdown
# Implementation Plan: <option title>

## Selected Design And Constraints
## Source Revision And Drift Check
## Affected Components
## Ordered Work Packages
## Compatibility And Migration
## Tactical Protections During Migration
## Tests And Security Validation
## Performance And Resource Benchmarks
## Rollout And Rollback
## Acceptance Criteria
## Open Decisions
```

把计划锚定到扫描 manifest 摘要或证据集合摘要，可得时锚定到刷新后的实施修订。源码漂移改变相关边界时，回到设计评审，而不是在编码时悄悄改提案。
