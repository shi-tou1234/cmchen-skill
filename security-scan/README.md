# security-scan

> Claude Code 安全审计 Skill，基于 OpenAI 开源的 [codex-security](https://github.com/openai/codex) 项目移植而来。

## 它是什么？

这是一个**自动化安全扫描与安全工程工具包**，专门设计在 Claude Code 环境中运行。它是一个技能包（bundle），提供 6 种能力：

1. **标准扫描**（standard）— 对整仓/指定路径做一次性安全审计
2. **Diff 审查**（diff）— 对 PR/commit/branch diff 做安全回归审查
3. **深度扫描**（deep）— 多轮独立发现 + 语义合并，降低漏报方差
4. **修复漏洞**（fix）— 把 finding 修成最小、已验证的改动
5. **加固方案**（hardening）— 产出结构性/架构性安全加固提案
6. **漏洞报告**（writeup）— 把漏洞素材写成可分发的研究级报告

以标准扫描为例，你给它一个代码仓库，它会：

1. 逐文件审查代码
2. 找出可能存在的安全漏洞（SQL 注入、路径穿越、未授权访问等）
3. 验证每个可疑点是否真实可被利用
4. 评估漏洞的严重程度
5. 生成一份密封的安全审计报告（Markdown + SARIF）

整个过程**只读扫描**，不会修改你的任何代码文件。无需任何云登录或第三方后端。

---

## 核心流程：5 个阶段（标准扫描）

| 阶段 | 名称 | 做什么 | 产出文件 |
|------|------|--------|----------|
| 0 | 预检与范围 | 确定扫描目标、读取仓库安全指引、创建工作目录 | `preflight.md` |
| 1 | 威胁建模 | 建立仓库级安全上下文：资产、信任边界、攻击面 | `threat_model.md` |
| 2 | 漏洞发现 | 逐文件审查，收集技术上可行的候选漏洞（source → control → sink） | `candidates.jsonl` |
| 3 | 验证 | 对每个候选用 PoC、测试或静态追踪核实真伪 | `validations.md` |
| 4 | 攻击路径分析 | 评估可达性与影响，套用严重度矩阵，确定优先级 P0–P3 | `attack_paths.md` |
| 5 | 定稿 | 生成密封报告 bundle | `report.md`、`exports/results.sarif` 等 |

每个阶段有严格的输入/输出契约，顺序执行，不允许跳步。

---

## 目录结构

```
security-scan/
│
├── SKILL.md                          ← 技能主入口：多模式路由 + 标准扫描 5 阶段流程
│
├── skills/                           ← 其余 5 种子技能（由顶层 SKILL.md 路由加载）
│   ├── security-diff-scan/           ← 模式 diff：Git 变更集安全审查
│   │   └── SKILL.md
│   ├── deep-security-scan/           ← 模式 deep：多轮独立发现 + 语义合并
│   │   └── SKILL.md
│   ├── fix-finding/                  ← 模式 fix：最小已验证修复
│   │   └── SKILL.md
│   ├── propose-security-hardening/   ← 模式 hardening：结构性加固提案
│   │   └── SKILL.md
│   └── vulnerability-writeup/        ← 模式 writeup：可分发漏洞报告
│       └── SKILL.md
│
├── references/                       ← 各阶段的参考规范文档
│   ├── candidate-contract.md         ← 阶段 2 规范：漏洞候选的输出格式与发现纪律
│   ├── validation-guidance.md        ← 阶段 3 规范：验证方法的优先级与置信度定义
│   ├── static-assessment.md          ← 静态评估方法：动态复现不可行时的纯代码分析兜底
│   ├── severity-matrix.md            ← 阶段 4 规范：严重度判断矩阵与硬压制规则
│   ├── report-contract.md            ← 阶段 5 规范：最终报告的结构与输出契约
│   ├── proposal-format.md            ← hardening 模式：加固提案的格式契约
│   └── report-format.md              ← writeup 模式：漏洞报告的格式契约
│
├── schemas/                          ← JSON Schema 定义，规定各产物的数据格式
│   ├── scan-manifest.schema.json     ← 扫描清单的 schema
│   ├── findings.schema.json          ← 漏洞发现的 schema
│   ├── coverage.schema.json          ← 覆盖率报告的 schema
│   └── definitions/                  ← 共享定义
│       ├── artifact-common.schema.json
│       └── discovery-candidate.schema.json
│
└── scripts/                          ← 自动化辅助脚本
    ├── build_scan_bundle.py          ← 主定稿脚本：从 bundle.json 生成密封产物
    ├── finalize_scan_contract.py     ← 定稿验证：校验 schema 合规性、填充指纹/ID/时间戳
    ├── report_projection.py          ← 报告投影：将结构化 JSON 渲染为 Markdown 报告
    ├── generate_in_scope_files.py    ← 枚举范围内文件清单
    ├── generate_diff_files.py        ← diff 模式：确定性地枚举 Git 变更的源文件
    ├── validate_report_format.py     ← 验证报告格式
    ├── windows_scan_local_files.py   ← Windows 平台文件描述符安全操作
    ├── normalize_candidates.py       ← 候选数据标准化
    └── __pycache__/                  ← Python 缓存（自动生成）
```

> **安装提示**：整个 `security-scan/` 目录作为一个 bundle 复制到 `~/.claude/skills/codex-security-scan/`（或项目内 `.claude/skills/codex-security-scan/`）。5 个子技能共享顶层的 references/scripts/schemas，**请整体复制**，不要只拷单个子技能目录。

---

## 每种能力怎么用

| 模式 | 触发说法 | 入口 |
|------|----------|------|
| standard | "帮我做个安全审计" / "这个项目有没有安全漏洞" | 顶层 SKILL.md 5 阶段 |
| diff | "帮我看看这个 PR/commit/branch 有没有安全问题" | `skills/security-diff-scan/` |
| deep | "深度/彻底/多轮地扫一遍" | `skills/deep-security-scan/` |
| fix | "把这个漏洞修掉并验证" / "修复这个 finding" | `skills/fix-finding/` |
| hardening | "怎么从架构上加固？" / "比单点补丁更好的方案" | `skills/propose-security-hardening/` |
| writeup | "把这份漏洞笔记写成报告" | `skills/vulnerability-writeup/` |

顶层 `SKILL.md` 会自动做模式路由：识别请求属于哪种能力，加载对应的子技能 SKILL.md 并严格执行。子技能通过 `<SKILL_DIR>/../..` 引用 bundle 根下的共享资源。

---

## 每个文件的作用

### 核心配置

| 文件 | 作用 |
|------|------|
| `SKILL.md` | 整个技能包的"总开关"。定义模式路由（6 种能力）与标准扫描的 5 阶段流程、每阶段的输入输出契约、全局铁律（只读不写、保留证据、不跳过阶段等）。Claude Code 读取此文件来决定执行哪个流程。 |
| `skills/<mode>/SKILL.md` | 各模式子技能。diff 聚焦改动代码与兄弟实例；deep 做多轮独立发现 + 语义合并；fix 遵循补丁契约与顺序验证门禁；hardening 产出选项/取舍/迁移计划；writeup 产出可分发漏洞报告。 |

### 参考规范（references/）

| 文件 | 作用 |
|------|------|
| `candidate-contract.md` | 阶段 2 的操作手册。规定了发现漏洞时的记录格式（anchor、instance、locations、source/control/sink 元组）和发现纪律（每个文件不因找到一个就停下、不泛化论断等）。 |
| `validation-guidance.md` | 阶段 3 的操作手册。规定了验证证据的优先级链（PoC > ASan > 调试器 > 单元测试 > 接口复现 > 静态追踪），以及置信度校准标准。 |
| `static-assessment.md` | 阶段 3 的兜底方案。当项目无法构建/运行时，用纯静态代码追踪来评估漏洞可行性。 |
| `severity-matrix.md` | 阶段 4 的操作手册。定义了严重度判断矩阵（影响 × 可能性）、critical 的严格标准、硬压制规则，以及 P0–P3 优先级映射。 |
| `report-contract.md` | 阶段 5 的操作手册。规定了最终报告的 JSON 结构（bundle.json）、覆盖率规则、以及定稿命令。报告不允许手写，必须由脚本从 JSON 投影生成。 |
| `proposal-format.md` | hardening 模式的格式契约。规定 `hardening.json`/`hardening.md`/`proposals/`/`diagrams/`/`implementation/` 的结构、写作语气、取舍维度与验收标准。 |
| `report-format.md` | writeup 模式的格式契约。规定漏洞报告的 7 个必需标题、证据与语气标准、源码与可利用性标准、验收检查项。 |

### Schema 定义（schemas/）

| 文件 | 作用 |
|------|------|
| `scan-manifest.schema.json` | 扫描清单的 JSON Schema，规定 manifest 中目标、范围、时间戳、产物引用的字段格式。 |
| `findings.schema.json` | 漏洞发现的 JSON Schema，规定每条 finding 的 findingId、指纹、severity、confidence、locations、remediation 等字段。 |
| `coverage.schema.json` | 覆盖率报告的 JSON Schema，规定 surface 级判定（reported / no_issue_found / rejected / not_applicable / needs_follow_up）的格式。 |
| `definitions/*` | 产物记录与发现候选的共享定义。 |

### 自动化脚本（scripts/）

| 文件 | 作用 |
|------|------|
| `build_scan_bundle.py` | **核心定稿脚本**。读取技能作者写的 bundle.json，自动填充 findingId、occurrenceId、指纹、时间戳，生成 findings.json、coverage.json、scan-manifest.json，然后调用 finalizer 生成 report.md 和 SARIF。 |
| `finalize_scan_contract.py` | **密封验证脚本**。验证所有产物是否符合 schema 契约、检测重复 finding、校验文件路径安全、生成 SARIF 格式结果。 |
| `report_projection.py` | **报告渲染脚本**。将结构化数据渲染为人类可读的 Markdown 报告。 |
| `generate_in_scope_files.py` | 文件枚举辅助脚本。使用 ripgrep 或 git 命令生成范围内文件清单，供阶段 2 逐文件审查使用。 |
| `generate_diff_files.py` | diff 模式专用。用 `git diff` 确定性地枚举 Git 变更的源文件（PR/commit/branch 用 `base...head`，本地补丁对比基线），过滤构建/生成目录并做字节序排序。 |
| `validate_report_format.py` | 报告格式验证脚本。 |
| `windows_scan_local_files.py` | Windows 平台兼容层。封装 Windows 下文件描述符的原子读写操作。 |
| `normalize_candidates.py` | 候选数据标准化脚本。 |

---

## 设计原则

1. **只读扫描** — 审计过程中绝不修改仓库源代码（修复模式除外，它由用户明确触发）
2. **保留证据** — 每个漏洞必须有可追溯的 source → control → sink 代码路径
3. **确定性输出** — 报告由脚本从规范 JSON 投影生成，不允许手写
4. **严格阶段边界** — 各阶段按顺序推进，每个阶段有明确的输入/输出契约
5. **反证优先** — 在判定为漏洞之前，先主动寻找"这可能不是问题"的证据
6. **覆盖率可追溯** — 每个被审查的表面（surface）必须有最终判定，不允许声称完整覆盖但留有未定论项
7. **多轮降方差** — 深度模式用多次独立发现暴露单遍漏掉的问题，但重复出现只是搜索证据，不是可报告性证明
8. **修复可验证** — 修复必须穿过顺序验证门禁（安全闭合 > 行为保留 > 仓库检查），证据缺口如实报告

---

## 使用方式

这是一个 Claude Code Skill，在 `.claude/settings.json` 中注册后，当用户提出以下需求时自动触发：

- "帮我做个安全审计"
- "这个项目有没有安全漏洞"
- "检查一下这段代码安不安全"
- "帮我看看这个 PR / commit / branch 有没有安全问题"
- "深度扫一遍，别漏"
- "把这个漏洞修掉并验证"
- "有什么架构层面的加固方案？"
- "把这份漏洞笔记写成报告"

触发后，Claude 会先做**模式路由**，再按对应流程执行；标准扫描的产物输出在 `.codex-scan/` 目录下。

---

## 来源

本 Skill 移植自 OpenAI 开源的 [codex-security](https://github.com/openai/codex) 项目，将其安全审计方法论（标准扫描 + diff 审查 + 深度扫描 + 修复 + 加固 + 漏洞报告）适配到 Claude Code 的 Skill 体系中。
