# 候选契约（漏洞发现阶段）

用于发现阶段。发现阶段只找技术上**可行**的候选并保留证据；它**不校准最终严重度**——那是攻击路径分析的职责。

## 候选元组

每个候选在 `references/report-contract.md` 的 bundle 表单中记录：

- `anchor`：根文件/行位置的稳定小写 slug（路径风格，`^[a-z0-9][a-z0-9._/-]*$`）。
- `instance`：区分共享同一位置的不同独立 bug 的稳定小写 slug（例如 `create:route:10`、`delete:route:10`）。语义为 `<family>:<file>:<line>`。
- `cwe`：`CWE-<正整数>` 数组，可为空。不要臆造分类。
- `locations`：`{path, startLine, endLine?, role}` 数组，其中 role 为 `entrypoint`、`entrypoint/wrapper`、`source`、`root_control`、`sink`、`concrete_implementation`、`evidence` 之一。至少保留根"被破坏的控制"或 sink 行；若入口/包装器与之不同，也保留使其可达的入口行。
- `summary` + `rootCause`：对该可能 bug 与所违反不变量的简明解释。
- 需要时，把攻击者输入/sink 上下文嵌入 `summary`/`rootCause`。

## 发现纪律

- 审查**每个**范围内文件。不要因为一个文件找到 bug 就停下。
- 枚举具体实例。绝不要写"所有 X 都受影响"；要列出使该论断成立的具体导出函数、路由、解析器模式、sink 语句、处理器或受保护动作，每个独立可触发的都单独成候选。
- 每个独立可达的 source/control/sink/impact 元组保持为**单独**候选。不要把兄弟路由、模板、查询构造器、解析器操作、认证端点或共享辅助函数的调用方折叠成一个代表性候选。
- 危险 sink 有多个调用点时，为每个调用点枚举自己的 source 与最近控制。
- 证据跨包装器进入共享 sink/控制辅助函数时，两个位置都保留，这样验证可以测可达性而不丢失根脆弱行。
- 对共享解析器/反序列化/模板/认证控制，保留 resolver、filter、白/黑名单、guard 或工厂设置行——而不只是那个"戏剧性"的传输层。
- 对反序列化/对象构造族，枚举具体 codec、converter、handler 与容器辅助函数（array/collection/map/bean/enum/generic-object），包括恶意输入能到达的底层 `to*Array`、`getObject`、数值转换、迭代器与分配循环。
- 对结构化 patch/edit/apply API（JSON Patch、Graph Patch、配置变更），枚举请求选择的操作（add/remove/replace/move/copy/test）及其路径变换或绑定行。
- 对外发请求面，枚举每个攻击者可控的目的地来源及其最近 allow/deny/filter/redirect 控制。空或由操作者配置的过滤器不是压制证据。
- 对归档解压 / 恢复 / 导入流程，保留成员名解码、目的 join、包含检查与解压/写入调用行。仅"标准库会规范化路径"这种说法不够；要展示解压/写入前对每个条目的包含检查。
- 对认证/授权面，单独枚举公开 webhook/status/callback/API 端点与改变状态的受保护动作（create/delete/reset/admin/job）。对 admin/restore/login 命名的路由，先核实精确的中间件/装饰器语义，再假定需要认证。
- 建议种子行保持打开，直到本地代码证据关闭它；相邻同族发现不算满足该种子行，除非它覆盖同一控制+效果。
- 对 diff 扫描，锚定变更本身；只有变更依赖的文件才纳入支撑。未变更的兄弟文件是上下文，不是扩大扫描的借口。

## 发现门槛（Finding bar）

优先技术上可行的候选：授权绕过、confused deputy（混淆代理）、SSRF、路径穿越、有真实 sink 的注入、跨租户数据泄露、缺少正确强制时的敏感状态变更、沙箱/信任边界逃逸。

避免：没有利用路径的泛泛"需要更多验证"评论、可维护性抱怨、同一根因的重复变体。

## 输出契约

若无可行候选，记录空 findings 列表。否则每个候选包含：受影响位置（带标签）、instance key、攻击者可控 source、脆弱 sink/被破坏控制、影响、为什么从当前代码看可行、最近的表观控制及其为何缺失/被绕过/错配/不完整、是否建议验证、已知时给出 CWE ID，以及足够让后续审查者理解该候选（验证前）的证据。
