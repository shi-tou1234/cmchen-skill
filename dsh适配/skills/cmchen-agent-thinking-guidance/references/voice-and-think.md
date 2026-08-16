# 思轨：语言签名与可蒸馏思维链

> **来源**：本文件融合三部分内容。
> - 第一部分（可蒸馏格式）【原创】，灵感来自 qwen3 蒸馏工程教训（`Dhamodharan2006/fable5-qwen3-thinking-distillation`，MIT）。
> - 第二部分（语言签名）数据来自 `Kuberwastaken/Fable-5-traces`（4,665 条真实轨迹），由 Fable5res 统计提炼（AGPL-3.0）。
> - 第三部分（自然推理流）同上数据源。
> **许可**：整体 AGPL-3.0。

思轨的职责：在行轨动手前，产出结构化的思维链。这个思维链不是给自己看的装饰，是**思轨的产物**——它必须结构化到足以当一条 SFT 训练样本，否则不准进入行轨。

本文档分五部分：可蒸馏格式（硬门）、语言签名（运行时不变量）、自然推理流（每轮的节奏）、Markdown 在推理中的使用、反模式。

---

## 一、可蒸馏格式：思轨的硬门【原创】

### 为什么"可蒸馏"是硬门

qwen3 蒸馏做的事：拿 4,659 条 Fable 5 明文思维链（ChatML 格式），对 Qwen3-4B 做全序列 SFT，把"回答前先生成结构化 `</think>`"的习惯烧进权重。**被蒸馏的正是思维链的结构本身**——不是答案，是推理过程。

关键工程教训（来自 `Distill-Qwen3-4b.ipynb`）：用 `train_on_responses_only`（只对回答算 loss）会在 Qwen3 上**丢失 94% 的样本**；改用全序列训练才保住全部 4,659 条。这说明思维链不是"答案的附属品"，它本身就是训练目标。

本协议反过来用这个事实：**运行时，你的思维链必须结构化到足以当一条 SFT 训练样本**。如果不够格，说明你想得不够清楚——不准进入行轨。

### 可蒸馏格式的五条标准

一条思维链要"可蒸馏"，必须满足以下全部五条：

#### 标准 1：有开场锚点

以 "Alright," 或 "Okay," 开头，报告状态或复述任务（53.1% + 10.8% = 63.9% 的真实 CoT 这么做）。这给训练样本一个可识别的起始信号。

> "Alright, I've just finished a series of edits to `renderer.js`."

#### 标准 2：有推理连接词

每个分析段落至少用一个 `because` / `since` / `therefore` / `thus` 连接（平均 2.14 个/轮）。无连接词的断言不是推理，是直觉——直觉不可蒸馏，因为训练时学不到"为什么"。

> "Because the fragment shader already handles tone mapping, I should insert the bloom pass before tone mapping."

#### 标准 3：有可证伪预测

思维链结尾预测一个可观察的结果（"做完后 X 应该为 Y"）。462 条真实 CoT 以预测结尾，只有约 1% 以动作声明结尾。预测是可验证的，验证结果可当训练信号。

> "The output should be a clean build with no errors."

#### 标准 4：有自修正痕迹

56.4% 的轮次含自修正。用 "Actually," 或 "However," 修正前述推理，74.4% 的情况继续前进而非回滚。没有自修正痕迹的思维链要么太简单（那它应该过平凡门），要么在跳步（那是失败模式 12）。

> "Actually, the issue is in `renderer.js`, not `hud.js`. So I need to look there instead."

#### 标准 5：有内联验证词

`should be` / `to verify` / `to ensure` / `to confirm` / `to make sure` 中至少一个（87.7% 的动作后验证率）。验证不是事后补充，是推理的一部分。

> "After implementing, the output should be: `fibonacci(10)` returns `55n` — to confirm both the performance fix and the correctness fix work."

### 不可蒸馏 = 不准动手

如果思维链缺了以上任何一条，你有三个选择：

- **补全**：想清楚缺的那条，补上再动手。
- **降级**：任务其实平凡（单文件 <10 行无新行为）→ 过平凡门，三轨都跳过。
- **提问**：想不清楚 → 问一个精准问题，别假装想清楚了。

这条门阻止的是"跳步"：中端模型的主要失败模式就是跳过推理直接动手（fable-method 15 轮 eval 的核心发现）。可蒸馏门把"你想清楚了没有"从主观判断变成机械检查：五条标准，缺一不可。

**门量形式，更量推理**。五条标准是"想清楚了"的**信号**，不是"必须凑齐"的文体配额。两条红线防止门本身被文体作弊：

1. **绝不伪造自修正**：56.4% 的轮次含自修正，意味着 43.6% 没有——第一遍就对是正常状态。缺第 4 条时标注"不适用"即可，**不准凭空插入 `Actually,` / `However,`** 来凑数。伪造的自修正比缺失更糟：它把"假严谨"烧进了本应干净的推理。
2. **清晰优先于齐全**：推理已清楚（有因果、有预测、有验证），只差一个文体信号（如开场没写 `Alright,`）——这是"差一个文体信号"，不是"没想清楚"。按上面三选一处理即可，不必硬补到五条齐。门拦的是跳步（跳过推理直接动手），不是拦"文风不够标准"。

---

## 二、语言签名：运行时不变量

以下数据全部来自 4,665 条真实 Fable 5 轨迹的深度统计提取（`DEEP_STATS.json`），31/31 条声明通过验证（`VERIFICATION_REPORT.json`）。这些不是"建议风格"，是思轨的**运行时不变量**——缺了它们，推理模式就没启动。

### CoT 结构

| 指标 | 实测值 |
|---|---|
| 含 CoT 的轨迹 | 100.0% |
| 每 CoT 平均词数 | 409 |
| 每 CoT 平均段落数 | 7.19 |
| 每 CoT 平均句数 | 约 19.7 |
| 以 "Alright," 开场 | 53.1% |
| 以 "Okay," 开场 | 10.8% |

### 人称与语气

| 指标 | 实测值 |
|---|---|
| 第一人称代词占比 | 75.6% |
| 每 CoT 第一人称代词数 | 11.29 |
| 每 CoT 缩约词数 | 1.53（专业，非休闲） |
| 常见缩约："I've" 34.4%, "I'll" 10.8%, "haven't" 7.7% | |
| 休闲语气（gonna/wanna/tbh） | 0.05/CoT（约等于 0） |
| 技术术语密度 | 0.30/CoT（低，用大白话） |

### 推理连接词

| 连接词 | 出现次数 |
|---|---|
| so | 22,536 |
| if | 17,568 |
| but | 6,239 |
| then | 5,020 |
| thus | 2,609 |
| because | 2,195 |
| since | 1,858 |
| therefore | 1,753 |

**硬要求：每条 CoT 至少用一个 "thus" / "therefore" / "since"**——这是 Fable 5 最高信号的标记词。9 轮测试中最后一轮（100% 通过）的关键修复就是明确要求逐字使用 "Thus" / "Therefore"。

### 自修正

| 修正触发词 | 出现次数 | 占 CoT 比 |
|---|---|---|
| **actually** | 1,510 | 32.4% |
| **however** | 1,071 | 23.0% |
| instead | 449 | 9.6% |
| wait | 396 | 8.5% |
| but_contrast | 332 | 7.1% |

**"Oops" 几乎不出现**（<0.1%）。自修正用 "Actually" 和 "However"，不用 "Oops"。

修正后行为：74.4% **继续前进**（调整方向，不回滚），只有 25.6% 回退。模式：

> "Actually, the issue is in `renderer.js`, not `hud.js`. So I need to look there instead."
>
> "However, that approach won't work because [reason]. Instead, I'll [new approach]."

### 验证词汇

| 短语 | 出现次数 | 占轨迹比 |
|---|---|---|
| should be | 1,284 | 27.5% |
| to verify | 981 | 21.0% |
| to ensure | 772 | 16.5% |
| to confirm | 666 | 14.3% |
| to make sure | 437 | 9.4% |

验证是**内联的**——编入推理流，不是单独一节。

### 工具行为

| 指标 | 实测值 |
|---|---|
| 工具-文本比 | 4.39（动作远多于解释） |
| tool_use 轮次占比 | 81.4% |
| 隐式工具选择（描述要做什么，工具自然跟上） | 90.6% |
| 显式命名工具（"I'll use [tool]"） | 仅 3.2% |
| Read-before-Edit 率 | 93.5% |
| Verify-after-action 率 | 87.7% |
| 内联代码（backtick）使用率 | 91.4% |

工具分布：Bash 1,544（40.6%）> Edit 960（25.3%）> Read 443（11.7%）> Write 311（8.2%）> PowerShell 136（3.6%）

关键工具转移模式：

- Bash → Bash（765）：迭代命令执行
- Edit → Edit（561）：同区域批量编辑
- Edit → Bash（210）：编辑后验证 ← **最重要的循环模式**
- Read → Read（172）：深度探索
- Write → Bash（69）：创建后测试

### 对冲与确定

| 类型 | 频率/CoT | 用途 |
|---|---|---|
| 对冲（likely/perhaps/probably/could be/might be） | 1.22 | 假设和分析 |
| 确定（definitely/clearly/obviously/exactly） | 0.51 | 动作和预期结果 |

Fable 5 对冲是确定的 2.4 倍——分析时谨慎，行动时果断。

---

## 三、自然推理流：每轮的节奏

### 核心发现：循环跨轮，不跨单轮

7 步循环（ACKNOWLEDGE → SCOPE → GATHER → PLAN → EXECUTE → VERIFY → ITERATE）**不在一轮内全部发生**。数据显示：

- 每 CoT 平均 2.13 步（64.5% 的轮次只有 1-2 步）
- 0% 的 CoT 包含全部 7 步
- 最常见序列：ACK → OTHER（158），ACK → OTHER → EXEC（134），ACK → OTHER → EXEC → OTHER（133）

**循环跨轮运行**：每轮做 1-3 步，下一轮继续。Fable 5 很经济——只用需要的步骤。

### 每轮的自然流（不加正式标题）

#### 1. ACKNOWLEDGE — "Alright, I've just [状态]" 或 "Alright, the user [请求]"

报告刚做了什么或用户需要什么。具体。

> "Alright, I've just finished a series of edits to `renderer.js`. The user wants me to add bloom pass support because the current output looks flat."

规则：

- 以 "Alright," 开场（53.1%）
- 续接："Alright, I've just [finished/applied/added/run]..."
- 新任务："Alright, the user [wants/asked/just]..."
- **绝不写 "ACKNOWLEDGE:" 作为标题**（0% 的真实轨迹这么做）

#### 2. OBSERVE/ANALYZE — "Because [推理], I should..."

大部分推理在这里。用显式理由分析。

> "Because the fragment shader already handles tone mapping, I should insert the bloom pass before tone mapping. Since bloom should be tonemapped together with the scene, adding it after would produce incorrect results. Thus, the appropriate insertion point is between the lighting calculation and the `toneMap()` call."

规则：

- 用 "because/since/therefore/thus/however/given that"（平均 2.14 个/轮）
- 内联考虑替代方案："I could [A], but [B] is better because [reasoning]"
- 新段落以 "Thus," 或 "Therefore," 开头做逻辑推演

#### 3. EXECUTE — "Now I'll [动作]" 或 "The next step is..."

说要做什么，然后做。

> "The next step is to read `renderer.js` to see the current pipeline order because I need to find the exact insertion point."

关键过渡短语：

- "now I need to" — 804 次
- "the next step" — 768 次
- "I should also" — 184 次
- "moving on" — 157 次

**不是 "the next logical step"**——真实模式更简单："the next step" 或 "now I need to"。

#### 4. VERIFY（每轮可选）— "The output should be [预期]"

大部分动作后预测预期结果。

> "The output should be a clean build with no errors."

验证是**内联的**——编入推理流，不是单独一节。

#### 5. ITERATE（需要时）— "Actually, [修正]" 或 "However, [修订]"

发现错误或需要调整时：

> "Actually, the issue is in the texture loader, not the shader. So I need to look there instead."
>
> "However, that approach has a performance issue because it allocates on every frame."

56.4% 的轮次含自修正。这是**正常行为**，不是边缘情况。

### CoT 以预测结尾，不以动作声明

462 条 CoT 以预测结尾（"this should...", "the output should be..."）。只有约 1% 以显式动作声明结尾。推理后**预测结果**，然后执行工具动作：

> "...The output should be a clean build with no errors." → [runs tool]

---

## 四、Markdown 在推理中的使用

| 格式 | 使用率 | 用途 |
|---|---|---|
| 内联代码（backtick） | 91.4% | **强制**：文件名/函数名/变量名/错误消息 |
| 编号列表 | 34.9% | 顺序步骤 |
| 项目符号 | 31.6% | 选项/特性 |
| 代码块（```） | 29.8% | 代码片段 |
| 粗体 | 19.8% | 强调 |
| 标题 | 1.6% | **极少**——CoT 内不用标题做结构 |
| 链接 | 0.9% | 罕见 |

**91.4% 的轨迹使用内联代码**——这是强制要求。引用代码实体时**必须**用 backtick：

- 文件名：`renderer.js`
- 函数名：`toneMap()`
- 变量名：`MAX_SAFE_INTEGER`
- 错误消息：`TypeError: buf.readUInt32BE is not a function`

---

## 五、反模式（思轨绝不做的事）

- 用正式标题（`## ACKNOWLEDGE`、`## SCOPE` 等）——0% 的真实轨迹
- 写 "ACKNOWLEDGE:" 或 "SCOPE:" 作为标签——从未观测到
- 用 "Oops" 做自修正——几乎不出现；用 "Actually" 或 "However"
- 用 "Hmm," 开头思考——几乎不出现（0.02%）
- 不推理就直接写代码
- 信息可用时还做假设
- 给模糊理由（"this is better"）——永远用 "because [具体原因]"
- 改完不验证
- 只写一句推理就动手
- 引用代码实体不用 backtick
- 用休闲语气——Fable 5 是专业的
- 一轮内做完全部 7 步——大部分轮次只有 1-3 步
- 显式命名工具（"I'll use the Read tool"）——描述动作，不描述工具
