<!-- 来源：改编自 Fable5res 的 fable-debug（AGPL-3.0）。原始文件为英文，本文为全面中文翻译与改编。
     许可：AGPL-3.0（copyleft 继承）。本文件随 cmchen-agent-thinking-guidance 整体受 AGPL-3.0 约束。 -->

# 调试流程

像 Fable 5 一样调试——自然推理流中的系统性根因分析。

## 何时使用

遇到报错、意外行为、失败的测试或任何不如预期的事情时使用。本流程是行轨（Act）在调试场景下的具体展开，与思轨（Think）的因果推理和审轨（Audit）的验证门禁配合运作。

## 核心原则

Fable 5 不猜——它**有条不紊地调查**，用流动的自然推理。37.4% 的报错轮次含当轮修复（实测验证）。调试流遵循：**OBSERVE → INVESTIGATE → HYPOTHESIZE → ROOT CAUSE → FIX → VERIFY**——全用自然段落，用 "because/since/therefore/thus" 连接。

**深度分析的量化事实：**

- 56.4% 的 CoT 含自我纠正——调试是 Fable 5 的自然状态
- "actually"（1,510 次）和 "however"（1,071 次）是主导修正标记
- 74.4% 的纠正**继续前进**，不后退
- 报错承认出现在每条 CoT 1.42 次（1,422% 密度）
- Edit→Bash(验证) 是 #1 调试循环模式（229 例）

## 自然调试流

**不要**用正式小节标题。遵循这个流动推理模式：

### 第 1 步：观察（OBSERVE）— "Alright, the [error/behavior] shows..."

精确说出哪里错了。对失败要具体。

> "Alright, the latest test run failed with `TypeError: buf.readUInt32BE is not a function`. The stack trace points to line 8 in `test/png.mjs`. The error tells me that `buf` is not a Node `Buffer` object because `Uint8Array` doesn't have `readUInt32BE`."

**要包括什么：**

- 反引号里的精确报错信息（不改写）——91.4% 的轨迹用反引号代码引用
- 发生的精确条件
- 什么 WORKS vs 什么 DOESN'T
- 你对报错含义的即时分析，带 "because"

### 第 2 步：调查（INVESTIGATE）— "I need to understand [什么]..."

> "I need to understand what `buf` actually is at runtime. I'll read `test/png.mjs` because the stack trace points there. I should also check how `buf` is created because the root cause might be upstream."

**来自真实轨迹的调查方法：**

- 读报错周围的源代码（82.8% 在 Read 前含 "because"）
- 检查失败点的变量类型和值
- 追踪数据流——"坏值从哪来的？"
- 检查 import 和依赖
- 跑诊断命令

### 第 3 步：假设（HYPOTHESIZE）— "Because [证据], the issue is likely..."

> "Because `buf` comes from Puppeteer's screenshot API which returns `Uint8Array`, the issue is likely a type mismatch. It could also be that the `Buffer` polyfill isn't loaded, but the type mismatch is more likely because the error specifically says `readUInt32BE is not a function` — that's a method that exists on `Buffer` but not `Uint8Array`."

**规则：**

- 生成具体、可测的假设
- 用 "because" 推理按可能性排序
- 用对冲词："likely"（1.22/CoT）、"perhaps"、"probably"
- 先别修——只假设
- 考虑：类型不匹配、缺依赖、逻辑错误、时序问题

### 第 4 步：定位根因（ROOT CAUSE）— "The root cause is [X] because [Y]"

> "The root cause is that Puppeteer returns `Uint8Array` while the code assumes `Buffer`. The `readUInt32BE` call is just a symptom of the underlying type mismatch. Since both types wrap `ArrayBuffer`, the fix is straightforward — use `DataView` which works on both."

**规则：**

- 区分症状和原因
- 根因在报错之外的文件/模块时，明说
- 解释链条：原因 → 中间效应 → 观察到的报错

### 第 5 步：修复（FIX）— "The next step is to fix [X] by [动作] because [理由]"

> "The next step is to replace the `Buffer` method calls with `DataView` equivalents because `DataView` works on any `ArrayBuffer` view. Because I only want to replace this specific occurrence, I'll target just the `readUInt32BE` call and the subsequent `readUInt32BE` calls. This should not affect other parts of the code because the rest of the module doesn't depend on `Buffer` methods."

**规则：**

- 修**根因**，不是症状
- 做解决**问题的最小改动**
- 永远用 "because" 论证
- 用精确编辑论证："because I only want to replace this specific occurrence"
- 考虑副作用

### 第 6 步：验证（VERIFY）— "The output should be [预期] to ensure the fix works"

> "The output should be a successful PNG validation with no `TypeError`. I should verify by re-running the playtest to ensure the fix works correctly. If the error persists, I'll need to check whether there are other `Buffer` method calls in the file because they might also fail with `Uint8Array` input."

**按工具的验证（来自真实轨迹）：**

- **Bash**（1,090 例）：跑测试/命令检查
- **Read**（207 例）：重读文件确认编辑
- **Edit**（339 例）：有时需要跟进编辑

## 调试中的自我纠正

调试时发现错误，用 "Actually" 或 "However"：

> "Actually, I was looking at the wrong file. The actual issue is in `[correct file]` because the error stack trace clearly shows the failure there."

> "However, the fix I applied didn't address the root cause — it only fixed the symptom. The real issue is `[deeper problem]` because `[evidence]`."

**不是 "Oops"**——那个词在真实轨迹里几乎不出现。主导纠正模式是：

- "Actually, [纠正]" — 32.4% 的 CoT
- "However, [矛盾]" — 23.0% 的 CoT
- "Wait, [顿悟]" — 8.5% 的 CoT
- "Instead, [替代]" — 9.6% 的 CoT

而纠正 **74.4% 继续前进**——Fable 5 调整方向，不撤销。

## 常见调试模式（来自真实轨迹）

### 模式 1：类型不匹配

> "Alright, the error is `TypeError: buf.readUInt32BE is not a function`. That tells me that `buf` is not a Node `Buffer` object — Puppeteer returns `Uint8Array`, not `Buffer`. Because `Uint8Array` doesn't have `readUInt32BE`, I need to use `DataView` instead."

### 模式 2：缺依赖

> "The error says `Cannot find package 'puppeteer'`. I need to install it because the project requires it for screenshot capture. I'll run `npm install` to ensure the dependency is available."

### 模式 3：逻辑错误

> "The playtest is still failing the 'hitscan damages bot at close range' check. The log shows the player is at `[position]` while the bot is at `[position]`. Because the hit detection uses a forward vector that points almost directly toward the bot yet the hit result is false, the issue is likely in the ray-box intersection code."

### 模式 4：异步/时序问题

> "The test works sometimes but fails sometimes. Because the failure is intermittent, this is likely a race condition — `[component A]` hasn't finished `[action]` before `[component B]` tries to read it. I must add proper async handling because the current code doesn't await the promise."

## 调试诊断方法

来自真实轨迹的 Fable 5 诊断词汇：

| 词汇 | 出现次数 | 用途 |
|------|---------|------|
| "debug" | 312 | 泛指调试行为 |
| "print(" | 344 | 加诊断输出 |
| "error message" | 187 | 引用报错文本 |
| "logging" | 155 | 诊断日志 |
| "diagnose" | 148 | 诊断分析 |
| "traceback" | 111 | Python 堆栈追踪 |
| "investigate" | 100 | 深入调查 |
| "console.log" | 100 | JS 诊断输出 |
| "stack trace" | 39 | 堆栈追踪分析 |

Fable 5 偏爱**读源代码**胜过加打印语句。真加诊断时，用 "because" 论证为什么需要。

## 代码实体引用

**91.4% 的 Fable 5 轨迹用内联代码**（反引号）。调试时：

- 报错信息永远包反引号：`TypeError: buf.readUInt32BE is not a function`
- 函数/方法名永远包反引号：`readUInt32BE`
- 文件路径永远包反引号：`test/png.mjs`
- 变量名永远包反引号：`buf`

## 完整示例：真实的 Fable 5 调试流

> Alright, the recent series of edits to `renderer.js` should have addressed the black-box artifact that only showed up when the graphics preset was set to ultra (1280x720). I added a safeguard against near-zero `a` in the ray-sphere intersection, inserted NaN checks and clamping for the final fragment color, and also did the same for the bloom pass shader.
>
> Now I need to confirm that these fixes actually eliminate the black box. Because the most straightforward way to verify is to re-run the exact test script, I'll issue a Bash command to run the playtest again. The output should show the black box gone in the screenshots because the NaN clamping should prevent the shader from producing invalid color values.
>
> If the black box persists, I'll need to dig deeper into the shader because the issue might be in a different code path — perhaps the tone mapping or the final output stage rather than the ray-sphere intersection.

**注意这个示例的特征：** 没有正式标题。自然流动。"Because" 连接分析。"Now I need to confirm" 验证。"Should" 预期结果。含备用计划。代码包反引号。

## 反模式

- 正式小节标题（`## OBSERVE`、`## HYPOTHESIZE` 等）——Fable 5 从不使用
- 不理解根因就修症状
- 调试时同时改多处
- 不验证就假设第一个假设是对的
- 修完跳过验证
- 没假设就到处加打印语句
- 不用 "because" 论证调试决定
- 用 "Oops" 自我纠正——用 "Actually" 或 "However"
- 代码实体不包反引号
- 纠正时往回走——74.4% 继续前进
