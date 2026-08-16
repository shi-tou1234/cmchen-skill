<!-- 来源：改编自 Fable5res 的 fable-verify（AGPL-3.0）。原始文件为英文，本文为全面中文翻译与改编。
     许可：AGPL-3.0（copyleft 继承）。本文件随 cmchen-agent-thinking-guidance 整体受 AGPL-3.0 约束。 -->

# 验证词汇层级

像 Fable 5 一样验证——把执着、系统、基于证据的质量保证织进你的推理。

## 何时使用

刚写完或改完代码、需要确认某东西能用、在跑测试、或需要对照需求校验输出时使用。本流程是审轨（Audit）在日常编码中的具体展开——验证不是事后检查，而是推理流的一部分。

## 核心原则

Fable 5 在 **87.7% 的动作后**验证，但它**不用**正式验证小节。验证**自然织进**推理流，用丰富的验证短语词汇。最常见的验证工具是 **Bash**（3,410 个验证实例里的 1,090 个）——意思是 Fable 5 通过**跑代码**验证，不是通过写关于验证的文字。

**关键——Fable 5 在几乎每个验证轮次里用全部五个验证短语。你至少要用每个中的一个：**

- `"should be"`（27.5% 的 CoT）——预期结果
- `"to verify"`（21.0% 的 CoT）——显式验证意图
- `"to ensure"`（16.5% 的 CoT）——安全/质量检查
- `"to confirm"`（14.3% 的 CoT）——确认正确
- `"to make sure"`（9.4% 的 CoT）——实用日常检查

**深度分析的量化事实：**

- 49.8% 的轨迹显式提到测试
- Edit→Bash(验证) 是 #1 验证循环模式（229 例）
- "should be" 是 #1 验证短语（27.5% 的轨迹）
- Fable 5 对冲是确定的 2.4 倍
- 56.4% 的轮次含自我纠正——验证失败立即触发修复

## 完整验证短语层级表

来自 4,665 条真实轨迹的 Fable 5 完整验证短语层级：

| 短语 | 次数 | 占轨迹比 | 用途 |
|------|------|---------|------|
| "should be" | 1,284 | 27.5% | 预期结果 |
| "to verify" | 981 | 21.0% | 显式验证意图 |
| "to ensure" | 772 | 16.5% | 安全/质量检查 |
| "to confirm" | 666 | 14.3% | 确认正确 |
| "to make sure" | 437 | 9.4% | 实用日常检查 |
| "I need to verify" | 396 | 8.5% | 行动导向验证 |
| "the expected" | 289 | 6.2% | 引用预期结果 |
| "assert" | 261 | 5.6% | 测试断言 |
| "validate" | 227 | 4.9% | 验证流程 |
| "I should verify" | 197 | 4.2% | 自我提醒验证 |
| "sanity check" | 153 | 3.3% | 快速合理性检查 |
| "playtest" | 142 | 3.0% | 游戏/应用测试 |
| "smoke test" | 119 | 2.6% | 基本功能测试 |

这些**不是**小节标题。它们自然出现在句子里：

> "I'll run the test script **to ensure** the fix doesn't break existing behavior."
> "The output **should be** a clean build with no errors."
> "Now I need **to confirm** this works **by** [方法]."
> "I should **make sure** the API returns the expected format."

## 按工具的验证（来自真实轨迹）

| 工具 | 次数 | 何时用 |
|------|------|--------|
| Bash | 1,090 | 跑测试、查输出、验证行为 |
| Edit | 339 | 验证暴露问题后的跟进修复 |
| Read | 207 | 回读文件确认内容 |
| Write | 155 | 有时重写就是修复 |
| PowerShell | 105 | Windows 专属验证 |

## 验证触发（来自真实轨迹）

| 触发 | 次数 | 模式 |
|------|------|------|
| 输出检查 | 1,871 | "The output should be [预期]" |
| 改动后 | 1,255 | "to ensure the change doesn't break [其他部分]" |
| 继续前 | 458 | "Before I move on, I should confirm [检查]" |
| 回归检查 | 67 | "to ensure no regressions" |
| 边界检查 | 36 | "I should test [边界情况] because [理由]" |

## 自然验证流（4 种场景）

### 场景 1：写码后

> "Alright, I've created `game.js`. I should verify that the game loop runs correctly by running the playtest. The output should be a rendering of the 3D scene with player movement because the game loop handles input, physics, and rendering."

### 场景 2：改码后

> "Now I've edited the `toneMap()` function in `renderer.js`. I need to confirm this change works correctly and doesn't break the existing rendering because the tone mapper affects every pixel on screen. I'll run the playtest to ensure the scene still renders correctly."

### 场景 3：跑码后

> "The output shows 4 failed, 92 passed in 3.15s. Because there are still failures, I need to investigate. The test failures are likely in the new module because the existing tests all passed before my changes."

### 场景 4：复杂特性后

> "I should do a sanity check on the full feature because the bloom pass touches every shader. I'll verify that basic rendering works, that bloom appears on bright areas, and that the FPS counter is still visible to ensure everything works end-to-end."

## 验证层级（5 级，自然应用）

### 第 1 级：语法验证（总是）

写完/改完后："The file should compile without syntax errors because [理由]."

### 第 2 级：执行验证（通常）

创建可运行代码后："Now I'll run [命令] to verify it executes without errors. The output should be [预期]."

### 第 3 级：行为验证（重要改动）

实现特性后："I should verify that [具体行为] works because [理由]. I'll test by [方法]. The result should be [预期]."

### 第 4 级：集成验证（重大改动）

影响多组件的改动后："I need to verify that [特性 A] still works with [特性 B] because they share the [组件]."

### 第 5 级：回归验证（关键改动）

改了核心/共享代码后："Because this change affects [共享组件], I should ensure [所有依赖特性] still work. I'll run the full test suite to make sure nothing broke."

## 标志性验证模式（5 种）

### 1. 合理性检查（3.0% 的轨迹）

> "I should do a sanity check because the change affects the core rendering pipeline."

### 2. 冒烟测试（2.6% 的轨迹）

> "I'll run a quick smoke test to ensure the basic functionality still works after the refactor."

### 3. Playtest（3.0% 的轨迹）

> "Now I need to playtest because the user reported a visual bug. I'll run [playtest 脚本] to verify [预期行为]."

### 4. 端到端检查

> "I need to verify this works end-to-end because the feature spans three modules."

### 5. 测试套件（49.8% 提到测试）

> "I'll run the test suite to make sure all existing tests still pass after these changes."

## 验证失败时

Fable 5 不只记录失败——它立刻诊断和修复。37.4% 的报错轮次含当轮修复。

验证失败时，用 "Actually" 或 "However"——**不是** "Oops"：

> "Actually, the test still fails because [根因]. I need to [修复] because [理由]. After fixing, I should verify again to ensure [预期结果]."

> "However, the output shows a different error — [新报错]. This means [修订诊断] because [证据]."

**失败响应循环（自然的，不是正式的）：**

1. **观察**："The output shows [失败]" 或 "Actually, [什么出了错]"
2. **诊断**："Because [推理], the root cause is [原因]"
3. **修复**："The next step is to fix [动作] because [理由]"
4. **重验**："The output should be [预期] to ensure the fix works correctly"

## "Should Be" 用法详解

"Should be" 出现在 27.5% 的轨迹里，是 Fable 5 的主导验证表达。用它表达：

- **预期结果**："The output should be a clean build with no errors."
- **预期状态**："After this change, the page should render the 3D scene correctly."
- **预期值**："The function should return `true` for valid inputs."
- **预期行为**："The game should start the round when all players are ready."

"Should be" 不是模糊猜测——它是基于代码逻辑的具体预测。如果说 "should be" 却无法说出具体预期，说明还没理解清楚，需要先回到定向阶段。

## 验证中的代码实体引用

**91.4% 的 Fable 5 轨迹用内联代码**（反引号）。验证时：

- 预期值包反引号："should return `0n`"
- 报错信息包反引号："should not show `TypeError`"
- 测试名包反引号："should pass `test_fibonacci`"
- 文件名包反引号："should compile `renderer.js` without errors"

## 完整示例：真实的 Fable 5 验证流

> Alright, the recent edits should have addressed the rendering artifact. I added NaN checks and clamping because invalid color values could cause the black box. Now I need to confirm that these fixes actually eliminate the issue.
>
> Because the most straightforward way to verify is to re-run the playtest, I'll issue the Bash command. The output should show the black box gone in the screenshots because the NaN clamping prevents invalid values. If the artifact persists, I'll need to dig deeper because the issue might be in a different code path — perhaps the tone mapping stage rather than the ray-sphere intersection.

**注意这个示例的特征：** 没有正式标题。"Because" 无处不在。"Should" 表预期结果。内联验证。含备用计划。"If X persists, I'll need to Y because Z." 代码包反引号。

## 反模式

- 正式小节标题（`## VERIFY`、`## CHECKLIST` 等）——Fable 5 从不使用
- 因为"看起来对"就假设代码能用
- "简单"改动跳过验证
- 只验证快乐路径
- 改动后不查回归
- 看到报错立刻整体重写
- 应用修复后不重验
- 只写验证文字而不真跑代码
- 只用 "to ensure"——用 "should be"、"to make sure"、"to confirm" 交替
- 代码实体不包反引号
- 验证失败用 "Oops"——用 "Actually" 或 "However"
