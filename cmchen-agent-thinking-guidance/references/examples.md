# 完整三轨示例：每种问题形状一个

> **来源**：改编自 [fable-method](https://github.com/Sahir619/fable-method) 的 `references/examples.md`（MIT 许可）。原始内容为英文，本文件已全面汉化改编，融入三轨一门协议的行轨/思轨/审轨框架，并入 AGPL-3.0 作品后随整体受 AGPL 约束。
>
> **用途**：6 种任务形状各一个完整示例，每个展示三轨协议跑完整循环——行轨（七步循环做改动）、思轨（可蒸馏思维链想清楚）、审轨（门禁 + 对抗自审守住质量）同时推进。弱模型最容易伪造的两步（Step 1 的完成定义和 Step 5 的观察式验证）在每个示例中具体写出。

这些示例不是缩略图，是完整跑通。每个示例展示三轨怎么并行推进，以及门禁痕迹（`INTENT:` / `AUTH:` / `TWINS:` / `PENDING:`）在什么时机出现。示例中的思轨推理用英文原文保留——因为可蒸馏门的语言签名（`Alright,` 开场、`because/since/thus` 连接、`Actually,` 自修正）是统计自真实 Fable 5 思维链的，翻译会丢失签名特征。

6 种任务形状覆盖了协议的所有路由路径：

| 编号 | 形状 | 平凡门 | 适配门路由 | 循环 |
|---|---|---|---|---|
| 1 | 平凡（改名） | 通过 | — | 跳过 |
| 2 | 评估/提问 | 不过 | 编码源 | 诊断，不改 |
| 3 | 任务（简单修复） | 不过 | 编码源 | 完整循环，1 轮 |
| 4 | 任务（多步骤调试） | 不过 | 编码源 | 完整循环，含自修正和双生发现 |
| 5 | 计划优先 | 不过 | 编码源 | Step 3 停，等批准 |
| 6 | 评估（非编码领域） | 不过 | 研究适配器 | 诊断，不改 |

---

## 1. 平凡（门，无循环）

**请求**："把 `api.ts` 里的 `getUsrData` 改名成 `getUserData`。"

一个文件，不到 10 行，无新行为，不搜索就知道改哪——平凡门通过。改名（定义加同文件调用点），跑项目已用的 typecheck 或 build，报告。

**执行**：
1. 读 `api.ts`，找到 `getUsrData` 的定义和同文件内的调用点。
2. 全部改成 `getUserData`。
3. 跑 `tsc --noEmit`（或项目已有的 typecheck 命令）。

**报告**：
> 已改名，3 处调用点更新，`tsc` 通过。

三句搞定。无分类表，无计划，无门禁痕迹（未改行为——改名不改语义，不触发意图门）。

**追溯失败条件**：如果改名跨文件了（搜索显示 6 个文件 14 个调用点），平凡门**追溯失败**——说出来，退出平凡路径，进全循环 Step 1 带清单。

**三轨痕迹**：
- **行轨**：一处编辑（同文件内改名），一个验证（typecheck）。
- **思轨**：跳过（平凡门通过，三轨都跳过）。
- **审轨**：跳过（未改行为、无对外动作、未修缺陷、无规定跟进——四条门禁痕迹都不触发）。

---

## 2. 评估/提问

**请求**："为什么仪表板慢？"

- **Step 0（分类）**：评估。交付物是诊断。不改任何东西。
- **Step 1（定义完成）**：完成 = 一个有观测支撑的原因；每条声明可溯源到文件行或测量。
  - **思轨**："Alright, the user reports the dashboard is slow. Because the symptom is overall sluggishness rather than a specific operation being slow, the cause is likely in data fetching or the rendering path. Thus, I should investigate both the query layer and the render layer."
  - **可证伪预测**：慢的原因应该在数据获取或渲染路径，因为用户描述的症状是整体卡顿而非某个操作慢。
- **Step 2（取证）**：一批并行——数据获取 hook、渲染路径、实际触发的网络请求（跑应用或读 query 配置）。
  - **思轨**："Alright, the data-fetching hook at `useDashboard.ts:41` has no debounce and the query cache key includes the raw search string. Because every keystroke triggers a refetch of all 12 widgets, the dashboard is slow — but this doesn't explain why the initial load is also slow. Actually, let me check the initial query configuration too."
  - **行轨**：发现两个问题——每次按键重取所有 12 个 widget；初始加载也有性能问题。
  - **审轨**：开最低证据集（代码 + 实际运行观测）。惊喜检查：慢在你假设的地方吗？——部分是，但初始加载慢是额外的发现，不匹配预测。
- **Step 3（决策）**：一个原因，一条推荐修。"可能是几个问题"不是发现——必须点名主因。
- **Step 6（报告）**：
  > 仪表板每次按键重取全部 12 个 widget：`useDashboard.ts:41` 无 debounce 且 query cache key 含原始搜索串。修法是 300ms debounce 加 normalized cache key。初始加载也慢，可能是 query 配置问题（`dashboardQueries.ts:23` 的 `staleTime: 0`），但这需要单独确认。要我改吗？

  没碰文件。结尾的"要我改吗？"是从评估到任务的唯一桥梁——不跨这条桥，不改任何东西。

**三轨痕迹**：
- **行轨**：未碰文件，只取证和诊断。
- **思轨**：`Alright,` 开场，`because` 连接（"Because every keystroke triggers..."），`Actually,` 自修正（从"只看 hook"转向"也要看 query 配置"），`should` 预测（"I should investigate both"）——五条可蒸馏门标准命中四条（无验证词，因为没执行动作不需要验证）。
- **审轨**：无 `INTENT:`（未改行为），无 `AUTH:`（无对外动作），无 `TWINS:`（未修缺陷），无 `PENDING:`（无规定跟进）。

---

## 3. 任务（简单修复）

**请求**："修挂掉的日期测试。"

- **Step 0（分类）**：任务。交付物是修好的代码，已验证。
- **Step 1（定义完成）**：完成 = 全套测试过，含 `test_format_date`。验证 = 套件运行输出。
  - **思轨**："Alright, the user wants me to fix a failing date test. Because the test is failing, I need to understand what it expects vs what the function does. Thus, after the fix, `test_format_date` should pass and the other 41 tests should remain unaffected."
  - **可证伪预测**：修完后 `test_format_date` 应该过，且其他 41 个测试不受影响。
- **Step 2（取证）**：一批读测试和它调的函数。
  - **思轨**："Alright, I need to understand what the test expects vs what the function does. Because the test checks `2024-01-15T10:00:00Z` formats to `Jan 15, 2024 10:00 AM UTC`, but the function returns `Jan 15, 2024 10:00 AM` — it drops the timezone. The test is correct because the spec in the docstring says 'preserve timezone offset'. Thus, the function is the broken part, not the test."
  - **行轨**：读 `dates.ts:27`，确认 `formatDate` 丢了 `Z` 后缀。
  - **审轨（意图门）**：`INTENT: 代码做 <formatDate 丢时区偏移>; 检查期望 <保留时区>; 规范(docstring)说 <preserve timezone offset>`。三者不一致（代码 vs 检查 + 规范）→ 修代码侧。因为改变用户所求（不只是修代码，是确认测试对还是代码对），报给用户。
- **Step 4（执行）**：`formatDate` 一处编辑。不碰别的。
- **Step 5（验证）**：全套运行——42 passed。
  - **两半**：半 1（靶向——`test_format_date` 过了），半 2（周围系统——其余 41 个测试仍过）。
  - **审轨（双生门）**：`TWINS: searched "formatDate.*drop|format.*timezone" - found 0 other sites: none`（函数只在 `dates.ts` 出现一次）。硬上限未触发（一次修过）。
- **Step 6（报告）**：
  > 测试是对的：`formatDate` 丢了时区偏移（`dates.ts:27`）。一行修好；全部 42 测试过（输出如下）。
  >
  > `INTENT: 代码做 <formatDate 丢时区偏移>; 检查期望 <保留时区>; 规范(docstring)说 <preserve timezone offset>`
  >
  > `TWINS: searched "formatDate" - found 0 other sites: none`

**三轨痕迹**：
- **行轨**：一处编辑，全套验证。
- **思轨**：`Alright,` 开场，`because`/`thus` 连接（"Because the test checks..." / "Thus, the function is the broken part"），可证伪预测（"42 passed"）。无 `Actually,`——一路清晰，没有自修正。验证词：`should pass`（预测中隐含）。
- **审轨**：`INTENT:` 行（行为变了——`formatDate` 的输出从丢时区变成保留时区），`TWINS:` 行（修了缺陷，搜了全项目确认无孪生）。无 `AUTH:`（可逆编辑），无 `PENDING:`（无规定跟进）。

---

## 4. 任务（多步骤调试）

**请求**："API 返回 500，日志显示 `TypeError: Cannot read property 'map' of undefined`。"

- **Step 0（分类）**：任务。
- **Step 1（定义完成）**：完成 = API 返回 200，错误消失，现有测试仍过。
  - **思轨**："Alright, the API is returning a 500 with `TypeError: Cannot read property 'map' of undefined`. Because this error means something is undefined when `.map()` is called on it, I need to trace the data flow. Since the error is in the orders endpoint, the issue is likely that the database query returned null instead of an array. Thus, the fix should make the data layer return an empty array when there are no results."
  - **可证伪预测**：错误应该在某个 middleware 或 controller 里对 undefined 做了 `.map()` 调用。
- **Step 2（取证）**：定向——列 `src/` 目录。一批并行——grep `.map(` 找所有调用点、读错误栈指向的文件、检查最近的改动。
  - **思轨**："Alright, the error is `Cannot read property 'map' of undefined`. Because this means something is undefined when `.map()` is called on it, I need to trace the data flow. The stack trace points to `orderController.js:45`. Since the error is in the orders endpoint, the issue is likely that the database query returned null instead of an array. Actually, let me check the query function too — the root cause might be there."
  - **行轨**：读 `orderController.js:45` → `orders.map(formatOrder)`。读 `getOrders()` → 返回 `null` 当无订单时（而不是 `[]`）。
  - **审轨（意图门）**：`INTENT: 代码做 <getOrders() 返回 null 当无订单>; 检查期望 <formatOrder 不被调用于 null>; 规范(API doc)说 <GET /orders 返回 [] 空数组>`。
- **Step 3（决策）**：一个推荐——在 `getOrders()` 里把 `null` 改成 `[]`。替代方案（在 controller 里加 null check）一行落选："因为根因在数据层，controller 加 check 只是治症状。"
- **Step 4（执行）**：`getOrders()` 一处编辑：`return result || []`。
  - **审轨（召回门）**：`||` 语法和 `[]` 行为是 JavaScript 基础，本会话已确认，不需要额外开源头。
- **Step 5（验证）**：跑 API——返回 `[]` 和 200。跑现有测试——全过。
  - **审轨（双生门）**：`TWINS: searched "return.*null|return null" in src/ - found 2 other sites: userController.js:31, productController.js:58`。这两个也有同样的 null 返回模式——列出来，问用户要不要一起修。
  - **硬上限**：未触发（一次修过）。
- **Step 6（报告）**：
  > 根因是 `getOrders()` 在无订单时返回 `null` 而非 `[]`，导致 `orderController.js:45` 的 `.map()` 炸了。一行修好；API 现在返回 `[]` 和 200，现有测试全过。
  >
  > `INTENT: 代码做 <getOrders() 返回 null>; 检查期望 <不炸>; 规范(API doc)说 <返回 []>`
  >
  > `TWINS: searched "return null" in src/ - found 2 other sites: userController.js:31, productController.js:58 — 同样模式, 未修, 要一起修吗？`

**三轨痕迹**：
- **行轨**：一处编辑，API + 测试验证。
- **思轨**：`Alright,` 开场，`because`/`since`/`thus` 连接（"Because this means..." / "Since the error is in..." / "Thus, the fix should..."），`Actually,` 自修正（从 controller 转向 query 函数——这是最重要的思轨痕迹，它表明 agent 不是一条路走到底），可证伪预测（"API 返回 200"）。验证词：`should` / `to verify`（隐含在预测中）。
- **审轨**：`INTENT:` 行（行为变了），`TWINS:` 行（发现了 2 个双生，列出未修，问用户——这是双生检查最有价值的场景：不仅确认修了的地方，还主动发现同类问题）。无 `AUTH:`（可逆编辑），无 `PENDING:`（无规定跟进）。

---

## 5. 计划优先

**请求**："分析我的项目怎么配置 X，提一个全局标准。"

- **Step 0（分类）**：计划优先——用户说"提"，且跨项目应用标准是大影响范围。交付物是计划；呈现后停。
- **Step 1（定义完成）**：完成 = 用户可批准的计划；每个计划步骤命名自己的验证（配置文件的文件存在、每项目文件仍 lint/build、每项目 diff 摘要）。
  - **思轨**："Alright, the user wants a global standard across projects. Because each project may have different conventions, I need to see what they actually do before proposing. Since the user named X as the config, I should find every instance and tabulate. Thus, the evidence is the frequency table of current practices."
- **Step 2（取证）**：并行——找每个配置实例，一批读全部，fetch 用户命名的任何外部参考。制表项目实际怎么做；频率表是证据。
- **Step 3（决策）**：一个提名的标准。项目间的冲突命名，每个带推荐解决方案，不静默平均。
- **交付计划。停。**

Step 4-6 只在批准后发生。然后执行是外科手术式的：每项目精确编辑、测量的 before/after、报告包括故意没碰的及为什么。

**三轨痕迹**：
- **行轨**：未碰文件，只取证和交付计划。
- **思轨**：`Alright,` 开场，`because`/`since`/`thus` 连接（"Because each project may have..." / "Since the user named X..." / "Thus, the evidence is..."），可证伪预测（"the evidence is the frequency table"——计划交付后用户可以验证频率表是否存在）。无 `Actually,`——取证阶段没有与预期相悖的发现。验证词：`should`（"I should find every instance"）。
- **审轨**：无 `INTENT:`（未改行为），无 `AUTH:`（无对外动作），无 `TWINS:`（未修缺陷），无 `PENDING:`（无规定跟进）——计划优先在 Step 3 停，工件门在计划上跑，不欠任何工件。

---

## 6. 评估（非编码领域：研究）

**请求**："竞品 A 和竞品 B 的定价策略有什么区别？"

- **Step 0（分类）**：评估。加载 `references/domains/research.md` 适配器。交付物是发现和推荐。不改任何东西。
- **Step 1（定义完成）**：完成 = 每条声明可溯源到抓取的页面或文档；两个竞品的定价模型对比清晰。
  - **思轨**："Alright, I need to compare pricing strategies. Because pricing changes frequently, I must fetch current pages — memory is not evidence. Since both competitors have public pricing pages, I'll fetch both in parallel. Thus, the comparison will be grounded in what they actually charge today, not what I remember."
- **Step 2（取证）**：适配器的最低证据集（绑定的）：
  1. **两个竞品的实际定价页面**：现在抓取，不凭记忆。
  2. **各自的定价文档/FAQ**：如果存在。
  3. **一个活的第三方参考**：行业报告或评测，现在抓取。
  - **行轨**：一批并行抓取两个定价页面 + 一个行业报告。
  - **审轨（召回门）**：任何价格数字必须从抓取的页面写，不从记忆。适配器定义多少算够（三个源）。
- **Step 3（决策）**：一个推荐（哪个策略适合什么场景）。
- **Step 6（报告）**：
  > 竞品 A 用分层定价（3 档，$10/$50/$200），竞品 B 用用量定价（$0.01/API call）。A 适合预算固定的小团队，B 适合用量波动大的项目。
  >
  > [来源：各自定价页面，抓取于 2026-08-11；行业报告 X，同日]

**三轨痕迹**：
- **行轨**：未碰文件，只取证。
- **思轨**：`Alright,` 开场，`because`/`since`/`thus` 连接（"Because pricing changes frequently..." / "Since both competitors have..." / "Thus, the comparison will be grounded..."），可证伪预测（"grounded in what they actually charge today"——用户可以打开链接验证）。无 `Actually,`——取证阶段没有与预期相悖的发现。验证词：`must` / `to verify`（隐含在"memory is not evidence"的态度中）。
- **审轨**：召回门触发（价格数字从抓取页面写，不从记忆），领域适配器加载（`research.md`）。无 `INTENT:`/`AUTH:`/`TWINS:`/`PENDING:`。

---

## 示例的共同模式

从 6 个示例中可以提取出 5 条贯穿始终的模式。这些模式不是巧合，是三轨一门协议的结构性后果——理解它们就能理解协议为什么这样设计。

### 1. 思轨先行

每个非平凡示例的 `<think>` 块都有 `Alright,` 开场 + `because`/`thus` 连接 + 可证伪预测。这是可蒸馏门的五条标准中的三条。另外两条（自修正痕迹和验证词）在非平凡示例中出现——示例 2 和 4 有 `Actually,` 自修正，示例 3、4、5、6 有 `should`/`to verify` 验证词。

思轨不是"先想后做"的前置步骤，是和行轨并行推进的实时推理。它在每一步都产出——Step 1 产出预测，Step 2 产出惊喜检查，Step 5 产出验证预期。思轨的质量被可蒸馏门硬性约束：不达标不准进入行轨。

### 2. 审轨在决策点触发

审轨不是全程跑，是在特定时机触发：
- 行为变更 → 意图门（`INTENT:`）
- 对外动作 → 授权门（`AUTH:`）
- 修缺陷 → 双生门（`TWINS:`）
- 未做规定后续 → 待办线（`PENDING:`）
- 用记忆 → 召回门

门禁痕迹留在报告里，是审计的证据。示例 3 有 `INTENT:` + `TWINS:`，示例 4 有 `INTENT:` + `TWINS:`（且发现了 2 个双生），示例 6 有召回门触发。示例 1（平凡）和示例 2、5（评估/计划，未改行为）无门禁痕迹——因为门禁只在需要时触发，不是为了留痕而留痕。

### 3. 行轨的结构不出现在报告里

报告没有 "Step 0:" / "Step 1:" / "Step 2:"——只有结果、证据、坑、和欠的方法工件（`INTENT:`/`AUTH:`/`TWINS:`/`PENDING:`）。

这是刻意的设计：结构服务于工作，不服务于展示。用户看到的是"发生了什么"和"凭什么相信它"，不是"我跑了七步循环"。步号和轨名是内部坐标，不是输出格式。唯一例外是方法工件行——它们出现是因为它们是审计需要的证据，不是因为 agent 想展示流程。

### 4. 惊喜改变方向

示例 2 和 4 都有惊喜：
- 示例 2：慢的地方和假设的不同（预测是数据获取或渲染路径，实际发现初始加载也有独立问题）。
- 示例 4：根因在 query 函数不在 controller（预测是 controller 里的 `.map()`，实际根因在 `getOrders()` 返回 null）。

惊喜说出来，改变"完成"的含义或用户所求。示例 4 的 `Actually,` 自修正就是惊喜的思轨痕迹——它表明 agent 不是一条路走到底，而是在取证中发现与预期相悖的证据后主动调整方向。这是三轨并行比线性流程更强的关键：线性流程遇到意外只能"强行穿过"（失败模式 9），三轨并行允许在任意步骤重路由。

### 5. 验证是观察式的

不是"should work now"（应该能行了），是"42 passed"（42 个通过）或"API 返回 200"。不能验证的明说"未验证"或 `UNVERIFIABLE`。

示例 3 的验证是"42 passed"——具体数字，可复核。示例 4 的验证是"API 返回 `[]` 和 200，现有测试全过"——具体输出，可复核。示例 2 的"诊断"不涉及验证（未改行为），但每条声明都"可溯源到文件行或测量"——这是评估类任务的等价物。

观察式验证防的是失败模式 14（验证表演）。"应该能行了"是表演——它假设改动会按预期工作，但假设不是证据。跑出真实输出是证据。两个半边都看（靶向 + 周围系统）是完整证据。

---

## 来源

- 原始来源：[fable-method](https://github.com/Sahir619/fable-method) `references/examples.md`（MIT）
- 本文件为中文改编版，融入了三轨一门协议的行轨/思轨/审轨框架标注。思轨推理保留英文原文以保持语言签名的可蒸馏特征。
- 6 种任务形状覆盖了协议的所有路由路径，是从 fable-method 的 15 轮对抗评测和 260+ 次运行中提炼的典型场景。
