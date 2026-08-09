# 报告契约（bundle.json → report.md + SARIF）

验证与攻击路径分析之后，组装一个 `bundle.json`，用随附的确定性管道定稿。**不要**手写 `report.md`；定稿脚本从规范 JSON 投影生成它，以保证一致与可密封。

## 定稿命令

```bash
python <SKILL_DIR>/scripts/build_scan_bundle.py \
  --bundle <scan_dir>/bundle.json \
  --scan-dir <scan_dir>/final \
  --source-root <repository_root>
```

输出在 `<scan_dir>/final/` 下：`scan-manifest.json`（密封）、`findings.json`、`coverage.json`、`report.md`、`exports/results.sarif`。可安全重跑；若定稿脚本拒绝 bundle，修正指出的字段后重跑（有界重试，不要循环）。

`<SKILL_DIR>` 是本技能所在目录——通常是 `~/.claude/skills/cmchen-security-scan/`（若是项目级则是 `.claude/skills/cmchen-security-scan/`）。通过查找 `scripts/finalize_scan_contract.py` 来定位。

## bundle.json 结构

```jsonc
{
  "target": {                       // kind + 可选 revision/snapshotDigest
    "kind": "git_worktree"          // 或 directory_snapshot / git_revision
  },
  "scope": {
    "summary": "一句话描述审了什么、怎么审的",
    "validationMode": "dynamic|static|mixed"   // 动态|静态|混合
  },
  "threatModel": {
    "summary": "浓缩威胁模型：资产、信任边界、攻击者输入、不变量"
  },
  "findings": [                     // 每个独立可达元组一条
    {
      "title": "简明漏洞标题",
      "ruleId": "lowercase-vuln-family",          // 如 "sql-injection"、"ssti"、"path-traversal"
      "severity": "high",                          // critical|high|medium|low|informational
      "confidence": "medium",                      // high|medium|low
      "severityRationale": "为什么是这个严重度，基于可达性+影响",
      "confidenceRationale": "为什么是这个置信度，基于验证方法/证据",
      "category": "SQL injection",                 // 具体类别，不是占位符
      "cwe": ["CWE-89"],                           // 精确 CWE id；未知则 []
      "anchor": "path/to/file",                    // 根位置的稳定 slug
      "instance": "create:path/to/file:42",        // 稳定 slug，每个独立 bug 唯一
      "summary": "是什么 bug、为什么现有控制不够",
      "rootCause": "违反的不变量 + 脆弱调用路径走查",
      "locations": [                               // 包含根控制/sink 行 + 入口
        {"path": "src/routes.py", "startLine": 10, "endLine": 12, "role": "entrypoint"},
        {"path": "src/db.py", "startLine": 42, "endLine": 42, "role": "sink"}
      ],
      "validation": {"method": "static_trace", "disposition": "reportable", "notes": "..."},
      "attackPath": {"reachability": "谁能在哪触发它", "dataflow": "source -> control -> sink", "severity": "high"},
      "remediation": "具体最小修复 + 测试 + 预防控制"
    }
  ],
  "coverage": {
    "completeness": "complete|partial|unknown",   // 完整|部分|未知
    "surfaces": [
      {"label": "HTTP 路由", "disposition": "reported", "riskArea": "injection", "notes": "..."}
    ]
  }
}
```

builder 会填充派生值（finding id、指纹、快照摘要、时间戳、密封），你不需要自己写。

## 覆盖规则

- surface 的 `disposition`：`reported`（已报告）| `no_issue_found`（未发现问题）| `rejected`（被否决）| `not_applicable`（不适用）| `needs_follow_up`（需跟进）。
- 当存在任何暂缓项或 `needs_follow_up` surface 时，`completeness` 标记为 `partial`；在 `notes` 保留其真实原因。
- 确定性映射：
  - 验证 `reportable` 且攻击路径 `reportable` → finding（surface 为 `reported`）。
  - 任一阶段 `deferred` → surface 为 `needs_follow_up` + 暂缓条目（带证据缺口）。
  - 验证 `not_applicable` → surface 为 `not_applicable`。
  - 验证 `suppressed` 或攻击路径 `ignore` → surface 为 `rejected`。
- 每个范围内文件/surface 都必须有交代。有文件或候选未定论时，不要声称完整覆盖。

## 报告预期（由定稿脚本投影生成）

- 结构：`# Security Review: <repo>` → `## Scope`（含 Scan Summary 表）→ `## Threat Model` → `## Findings`（汇总表、Confidence Scale、每条 finding 的小节：Summary / Root Cause / Validation / Dataflow / Reachability / Severity / Remediation）→ `## Reviewed Surfaces`（部分覆盖时还有 `## Open Questions And Follow Up`）。
- finding 按严重度从高到低排列（critical → high → medium → low）。
- 无存活发现时出现 `### No findings`。
- 每条 finding 的受影响行必须包含根"被破坏的控制"或 sink 行，而不只是可达的包装器。
- 在最终对话小结里报告严重度 → 优先级：critical=P0、high=P1、medium=P2、low=P3。
- 把生成的 `report.md` 和 `exports/results.sarif` 作为主要产出链接。
