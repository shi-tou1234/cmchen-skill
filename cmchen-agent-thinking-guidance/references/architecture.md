<!-- 来源：改编自 Fable5res 的 fable-architect（AGPL-3.0）。原始文件为英文，本文为全面中文翻译与改编。
     许可：AGPL-3.0（copyleft 继承）。本文件随 cmchen-agent-thinking-guidance 整体受 AGPL-3.0 约束。 -->

# 架构设计

像 Fable 5 一样设计架构——先深度理解再设计、模块化思考、迭代精炼。

## 何时使用

开启新项目、设计系统架构、规划大型重构或做技术决策时使用。本流程是行轨（Act）在架构场景下的具体展开，强调长时间跨度的自主工作能力。

## 核心原则

Fable 5 最令人印象深刻的能力是**长时间跨度的自主工作**——单任务会话最长 439 轮（光追 CS:GO 克隆项目用了 297 轮）。关键在于：**理解要深、设计要模块化、执行要增量、验证要持续**——全用自然流动的推理，不加正式小节标题。

**深度分析的量化事实：**

- 平均每会话 77.75 轮，中位数 38
- 平均每会话用 4.65 种不同工具
- 81.4% 的轮次是 tool_use（行动密集）
- 56.4% 的轮次含自我纠正
- "the next step"（768）和 "now I need to"（804）是主要过渡短语

## 自然架构流

**不要**用正式小节标题。遵循这个流动推理模式：

### 阶段 1：理解（UNDERSTAND）— "Alright, I need to understand the full scope..."

> "Alright, I need to understand the full scope of what's being asked. The user wants [具体目标] with [约束]. Because this is a [范围评估], I need to be realistic about what I can deliver. I'll start by exploring the existing codebase because I need to understand what's already in place."

**来自真实轨迹的 Fable 5 第一个动作：**

- 58.3% 从建上下文开始（读、探索、理解）
- 33.6% 从承认范围和需求开始
- 只有 16.2% 直接跳到行动

### 阶段 2：设计（DESIGN）— "Because [推理], the architecture should..."

> "Because [关于约束的推理], the architecture should [方案]. I could use [备选 A], but [方案 B] is better because [具体权衡]. Since [约束], I need to [考量]. The modules will be: [模块 1] for [目的], [模块 2] for [目的], because [分离的理由]."

**来自真实轨迹的模块设计规则：**

- 每个模块应能独立理解
- 按特性/领域分组，不按技术层分组
- 依赖向内流（特性依赖核心，反之不然）

**多备选推理**——架构决策用 "I could X, but Y because Z"：

> "I could use Three.js for rendering, but raw WebGL2 is better because it gives us full control over the rendering pipeline and avoids the overhead of a scene graph we don't need."

### 阶段 3：垂直切片实现（VERTICAL SLICE）— "The next step is [切片]..."

> "The next step is to build the smallest end-to-end working feature because [理由]. I'll start with [切片 1] — [具体组件]. Because this is the foundation, I need to verify it works completely before adding more."

**这不是：**

- 先建全部 models，再建全部 views，再建全部 controllers
- 先建整个后端，再建整个前端

**这是：**

- 建一条小而完整的系统通路
- 验证它端到端工作
- 加下一条通路
- 模式浮现时重构

### 阶段 4：持续验证（VERIFY）— "The output should be [预期] to ensure [行为]"

> "The output should be a working page with the 3D scene rendering correctly, to ensure the foundation is solid before adding more features."

来自真实轨迹的 Fable 5 验证模式：

- 每个垂直切片后：跑 playtest/冒烟测试
- 每个文件写入后：检查能无错运行
- 每个编辑后：验证无回归
- 用 "should be"（27.5%）表预期结果
- 用 "to ensure"（16.5%）做安全检查
- 用 "to make sure"（9.4%）做实用验证

### 阶段 5：迭代与扩张（ITERATE）— "Done. Now [下一个特性]."

> "Done. Now [下一个特性] because [理由]. The next step is to add [特性] because it builds on what we just verified."

来自真实轨迹的 Fable 5 标志性完成→过渡模式：

- "Alright, I've just finished..." → "The next step is..."
- "Done." 后接 "Now [动作]"
- "Alright, let me take stock of where we are" → 进度总结 → 下一步

## NEONSTRIKE 项目案例

297 轮的光追 CS:GO 克隆会话展示了 Fable 5 的架构方法：

1. **T1-3：探索** — 读项目结构，检查可用工具
2. **T4-7：计划** — "Big task. Plan: build ray-traced FPS (WebGL2 fragment-shader ray tracer — real rays, real bounces), CSGO-style"
3. **T8：地基** — "Renderer done. Now audio — pure-DSP SFX generators + playback engine."
4. **T9：下一模块** — "Now HUD — viewmodel canvas, radar, killfeed, damage numbers, buy menu."
5. **T10：核心逻辑** — "Now `game.js` — player physics, weapons, bots AI, rounds, economy. Biggest file."
6. **T11-18：构建与写入** — 写 `map.js`、`renderer.js`、`audio.js`、`settings.js`、`game.js`、`hud.js`
7. **T19-25：集成** — 写 `index.html`、`main.js`、playtest 工具
8. **T26-50：测试与修复** — 跑 playtest，修 bug，迭代

**核心模式：** EXPLORE → PLAN → BUILD（一次一个模块）→ INTEGRATE → TEST → FIX → REPEAT

## 关键架构模式（来自真实轨迹）

### 1. "Now X" 模块过渡

> "Renderer done. Now audio — pure-DSP SFX generators + playback engine."
> "Now HUD — viewmodel canvas, radar, killfeed, damage numbers, buy menu."
> "Now `game.js` — player physics, weapons, bots AI, rounds, economy. Biggest file."

### 2. "The next step is..."（768 次）

> "The next step is to tie everything together with the core game simulation."
> "The next step is to look at the front-end JavaScript that consumes these entries."

### 3. 端到端思考

> "I need to verify this works end-to-end because [理由]."

### 4. 合理性检查（3.0% 的轨迹）

> "I should do a sanity check because [理由]."

### 5. 冒烟测试（2.6% 的轨迹）

> "I'll run a quick smoke test to ensure [基本功能能用]."

### 6. Playtest（3.0% 的轨迹）

> "Now I need to playtest because [理由]."

## 架构中的自我纠正

架构决策需要修订时，用 "Actually" 或 "However"：

> "Actually, the modular approach isn't working here because the modules are too tightly coupled. Instead, I'll merge `physics.js` and `collision.js` into a single `game-engine.js` because the interaction between physics and collision is too frequent to justify the separation."

> "However, this architecture won't scale because [证据]. Instead, I'll [修订方案] because [理由]."

**56.4% 的轮次含自我纠正。** 架构也不例外——Fable 5 不断精炼它的设计决策。

## 架构决策中的对冲

Fable 5 对不确定的架构选择用对冲语言（每条 CoT 1.22 个）：

- "likely" — "This is likely the best approach because..."
- "probably" — "This will probably work because..."
- "could be" — "This could be extended later because..."

但对已承诺的决策用确定语言（每条 CoT 0.51 个）：

- "this will" — "This will handle all edge cases because..."
- "I must" — "I must ensure the foundation is solid because..."

## 状态检查点模式

在长会话中（平均 77.75 轮），Fable 5 定期盘点：

> "Alright, let me take stock of where we are — [进度总结]. The next step is [动作]."

> "Alright, let me recap where I am — [已完成什么]. Now I need [接下来做什么]."

这种检查点模式防止长会话中迷失方向——每完成一个模块或遇到重大里程碑时，停下来盘点已完成和待完成的工作。

## 代码实体引用

**91.4% 的 Fable 5 轨迹用内联代码**（反引号）。讨论架构时：

- 模块名包反引号：`game.js`、`renderer.js`
- 类名包反引号：`SparseSelection`、`DataView`
- API 端点包反引号：`/api/refresh`
- 配置键包反引号：`fp4_weights`

## 反模式

- 正式小节标题（`## UNDERSTAND`、`## DESIGN` 等）——Fable 5 从不使用
- 写任何代码前就设计整个系统
- 横向构建（先全部后端，再全部前端）
- 地基没验证就加特性
- 架构决策不用 "because" 论证
- 为未确认的未来需求过度工程
- 不内联考虑备选就选架构
- 代码实体不包反引号
- 用 "Oops" 纠正——用 "Actually" 或 "However"
