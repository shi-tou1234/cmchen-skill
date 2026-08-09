#!/usr/bin/env python3
"""把技能作者写的一个简单 JSON 打包成密封的 Codex Security 扫描包，
然后调用随附的定稿脚本生成 report.md + SARIF。

技能作者写一个 `bundle.json`，结构如下：

{
  "target": {
    "kind": "git_worktree" | "directory_snapshot" | "git_revision",
    "displayName": "...",            // 可选；默认用源码根目录名
    "targetId": "...",               // 可选；默认用源码根目录路径
    "revision": "..."                // 仅 git_revision 需要
  },
  "scope": {
    "summary": "...",                // 一句话描述审了什么、怎么审的
    "includePaths": ["."],
    "excludePaths": [],
    "artifactsReviewed": [...],      // 可选
    "validationMode": "dynamic|static|mixed"   // 可选：动态|静态|混合
  },
  "threatModel": { "summary": "...", "assets": [...], "trustBoundaries": [...], "attackers": [...] },
  "findings": [
    {
      "title": "...",
      "ruleId": "sql-injection",     // 小写漏洞族 slug
      "severity": "critical|high|medium|low|informational",
      "confidence": "high|medium|low",
      "severityRationale": "...",    // 为什么是这个严重度
      "confidenceRationale": "...",  // 为什么是这个置信度
      "category": "SQL injection",   // 具体漏洞类别
      "cwe": ["CWE-89"],
      "anchor": "path/to/file",      // 稳定小写 slug（路径风格）
      "instance": "route:file:line", // 稳定小写 slug，每个独立 bug 唯一
      "summary": "...",
      "locations": [
        {"path": "src/x.py", "startLine": 42, "endLine": 45, "role": "sink"},
        {"path": "src/routes.py", "startLine": 10, "endLine": 12, "role": "entrypoint"}
      ],
      "rootCause": "...",
      "validation": {"method": "static_trace|poc|test|...", "disposition": "reportable", "notes": "..."},
      "attackPath": {"reachability": "...", "dataflow": "source -> control -> sink", "severity": "..."},
      "remediation": "..."
    }
  ],
  "coverage": {
    "completeness": "complete|partial|unknown",    // 完整|部分|未知
    "mode": "repository|scoped_path|diff",
    "surfaces": [{"label": "...", "disposition": "reported|no_issue_found|rejected|not_applicable|needs_follow_up", "riskArea": "...", "notes": "..."}],
    "explicitExclusions": [],
    "deferred": [],
    "openQuestions": []
  }
}

运行：  python build_scan_bundle.py --bundle bundle.json --scan-dir <out> --source-root <repo>
输出（在 <out> 下）：scan-manifest.json（密封）、findings.json、coverage.json、report.md、
                     exports/results.sarif
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1.0"
FINGERPRINT_ALGORITHM = "codex-security/v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _slug(value: str, fallback: str) -> str:
    value = re.sub(r"[^a-z0-9._/-]", "-", value.lower())
    value = re.sub(r"-+", "-", value).strip("-").rstrip("/")
    return value or fallback


def _normalize_surfaces(surfaces: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, s in enumerate(surfaces):
        if not isinstance(s, dict):
            continue
        item: dict[str, Any] = {
            "id": _slug(str(s.get("id") or f"surface-{i}"), f"surface-{i}"),
            "label": str(s.get("label") or f"Surface {i}"),
            "disposition": s.get("disposition") or "no_issue_found",
            "receiptRefs": s.get("receiptRefs") or [],
            "notes": str(s.get("notes") or "Reviewed as part of the scan."),
        }
        if s.get("riskArea"):
            item["riskArea"] = str(s["riskArea"])
        out.append(item)
    return out


def _target_coordinate(target: dict[str, Any], source_root: Path) -> dict[str, Any]:
    coord: dict[str, Any] = {}
    if target.get("revision"):
        coord["revision"] = str(target["revision"])
    digest = target.get("snapshotDigest")
    if not isinstance(digest, str) or not digest.startswith(
        "codex-security-snapshot/v1:sha256:"
    ):
        digest = None
    if target.get("kind") != "git_revision" and not digest:
        digest = "codex-security-snapshot/v1:sha256:" + hashlib.sha256(
            str(source_root).encode()
        ).hexdigest()
    if digest:
        coord["snapshotDigest"] = digest
    return coord


def make_finding(i: int, f: dict[str, Any]) -> dict[str, Any]:
    locs = f.get("locations", [])
    anchor = _slug(str(f.get("anchor") or (locs[0]["path"] if locs else f"finding-{i}")),
                   f"finding-{i}")
    instance = _slug(str(f.get("instance") or f.get("instanceKey") or f"finding-{i}"),
                     f"finding-{i}")
    identity_src = f"{anchor}:{instance}"
    primary = FINGERPRINT_ALGORITHM + ":sha256:" + hashlib.sha256(
        identity_src.encode()
    ).hexdigest()

    finding: dict[str, Any] = {
        "findingId": f.get("findingId") or f"F-{i:04d}",
        "occurrenceId": f.get("occurrenceId") or f"O-{i:04d}",
        "ruleId": str(f.get("ruleId") or f.get("category") or "security-finding"),
        "identity": {"anchor": anchor, "instance": instance},
        "fingerprints": {
            "algorithm": FINGERPRINT_ALGORITHM,
            "primary": primary,
        },
        "title": str(f["title"]),
        "summary": str(f.get("summary", "")),
        "severity": {
            "level": f.get("severity", "medium"),
            "rationale": str(f.get("severityRationale", "")),
            "changeConditions": str(
                f.get("changeConditions")
                or f.get("severityRationale")
                or "No material change in conditions identified."
            ),
        },
        "confidence": {
            "level": f.get("confidence", "medium"),
            "rationale": str(f.get("confidenceRationale", "")),
        },
        "taxonomy": {
            "category": str(f.get("category") or f["title"]),
            "cwe": [str(c) for c in (f.get("cwe") or [])],
        },
        "locations": [
            {
                "path": str(loc["path"]),
                "startLine": int(loc.get("startLine", 1)),
                "endLine": int(loc["endLine"]) if loc.get("endLine") else None,
                "role": str(loc.get("role", "sink")),
            }
            for loc in locs
            if isinstance(loc, dict) and loc.get("path")
        ],
        "remediation": str(f.get("remediation", "")),
        "provenance": {"source": str(f.get("provenanceSource", "local_plugin"))},
    }
    for key in ("validation", "attackPath"):
        if f.get(key):
            finding[key] = f[key]
    if f.get("rootCause"):
        finding["rootCause"] = str(f["rootCause"])
    return finding


def build(scan_dir: Path, source_root: Path, bundle: dict[str, Any]) -> None:
    scan_dir.mkdir(parents=True, exist_ok=True)
    scan_id = bundle.get("scanId") or str(uuid.uuid4())
    target = bundle.get("target", {})
    scope = bundle.get("scope", {})
    coverage = bundle.get("coverage", {})
    findings = bundle.get("findings", [])
    ts_start = now()

    findings_json = {
        "documentType": "codex-security.findings",
        "schemaVersion": SCHEMA_VERSION,
        "scanId": scan_id,
        "findings": [make_finding(i, f) for i, f in enumerate(findings) if isinstance(f, dict)],
    }
    coverage_json = {
        "documentType": "codex-security.coverage",
        "schemaVersion": SCHEMA_VERSION,
        "scanId": scan_id,
        "mode": coverage.get("mode", "repository"),
        "completeness": coverage.get("completeness", "complete"),
        "inventoryStrategy": coverage.get("inventoryStrategy", "repository"),
        "includePaths": coverage.get("includePaths", scope.get("includePaths", ["."])),
        "excludePaths": coverage.get("excludePaths", scope.get("excludePaths", [])),
        "surfaces": _normalize_surfaces(coverage.get("surfaces", [])),
        "explicitExclusions": coverage.get("explicitExclusions", []),
        "deferred": coverage.get("deferred", []),
        "openQuestions": coverage.get("openQuestions", []),
    }
    threat_model = bundle.get("threatModel") or {}
    manifest = {
        "documentType": "codex-security.scan-manifest",
        "schemaVersion": SCHEMA_VERSION,
        "scan": {
            "id": scan_id,
            "producer": {"name": "codex-security-claude-skill", "version": "0.1.0"},
            "status": "completed",
            "startedAt": ts_start,
            "completedAt": ts_start,
            "target": {
                "kind": target.get("kind", "git_worktree"),
                "targetId": target.get("targetId") or str(source_root),
                "displayName": target.get("displayName") or source_root.name,
                **_target_coordinate(target, source_root),
            },
            "scope": {
                "includePaths": scope.get("includePaths", ["."]),
                "excludePaths": scope.get("excludePaths", []),
                **{
                    k: scope[k]
                    for k in ("summary", "artifactsReviewed", "runtimeStatus", "validationMode")
                    if scope.get(k) is not None
                },
            },
            "coverageRef": "coverage.json",
            "findingsRef": "findings.json",
            "threatModel": {
                "summary": threat_model.get("summary")
                or scope.get("summary")
                or "No explicit threat model was recorded for this scan.",
                **{k: threat_model[k] for k in ("assets", "trustBoundaries", "attackers")
                   if threat_model.get(k)},
            },
        },
    }
    (scan_dir / "findings.json").write_text(json.dumps(findings_json, indent=2), encoding="utf-8")
    (scan_dir / "coverage.json").write_text(json.dumps(coverage_json, indent=2), encoding="utf-8")
    (scan_dir / "scan-manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path, help="bundle.json authored by the skill")
    parser.add_argument("--scan-dir", required=True, type=Path, help="output scan directory")
    parser.add_argument("--source-root", required=True, type=Path, help="repository root")
    parser.add_argument("--schema-dir", type=Path, help="schemas dir (defaults to ../schemas)")
    parser.add_argument("--finalizer", type=Path, help="finalize_scan_contract.py (defaults to sibling)")
    parser.add_argument("--no-finalize", action="store_true", help="write bundle only, skip finalizer")
    args = parser.parse_args()

    bundle = json.loads(args.bundle.read_text(encoding="utf-8"))
    build(args.scan_dir, args.source_root, bundle)
    if args.no_finalize:
        return 0
    finalizer = args.finalizer or (Path(__file__).resolve().parent / "finalize_scan_contract.py")
    cmd = [
        sys.executable,
        str(finalizer),
        "--scan-dir",
        str(args.scan_dir),
        "--source-root",
        str(args.source_root),
    ]
    if args.schema_dir:
        cmd += ["--schema-dir", str(args.schema_dir)]
    subprocess.run(cmd, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
