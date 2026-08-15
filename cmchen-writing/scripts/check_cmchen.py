#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_cmchen.py — cmchen-writing v4.2 配套检查脚本

用法：python check_cmchen.py <稿件路径.md> [--blog]
    --blog  按博客稿件检查 frontmatter（description 必须留空、无 tags）

分层：
    FAIL  硬禁令，命中即必须修改
    WARN  语境判断，需要人工确认
    STAT  统计指标，对照语料基线看

只报警，不改文。屏蔽代码块、行内代码、图片与 frontmatter。
v4.2 新增重复密度红线（词级/骨架级/小句级），阈值与 SKILL.md 第四节一致。
"""
import re
import sys
import statistics

# ---------- 硬禁词（与 SKILL.md 四、字面命中清单一致，不得自行增加） ----------
FAIL_WORDS = [
    "在这个快节奏的时代", "总而言之", "综上所述", "值得注意的是", "不难发现",
    "让我们一起", "淋漓尽致", "仿佛置身于", "赋能", "闭环式成长",
    "我感到非常充实", "受益匪浅", "深深地震撼了我",
    "下面我来介绍一下", "首先需要了解的是", "我们可以从三个方面来分析",
    "希望对你有帮助", "如果你也喜欢请点赞",
    "属于是", "绝绝子", "yyds",
]

# ---------- 动作级禁令的可机检外衣（WARN，需人工确认语境） ----------
WARN_PATTERNS = [
    ("翻案抬价嫌疑", r"你以为[^，。]{1,20}(其实|实际上)"),
    ("翻案抬价嫌疑", r"看似[^，。]{1,20}(实则|其实)"),
    ("翻案抬价嫌疑", r"答案恰恰相反"),
    ("翻案抬价嫌疑", r"[^，。]{1,15}不重要，?重要的是"),
    ("名词化嫌疑", r"(进行|实现|完成)了[一]*[个]?[\u4e00-\u9fff]{2,4}"),
    ("三项排比嫌疑", r"为什么[^，。]{2,12}，为什么[^，。]{2,12}，为什么"),
    ("教科书开场白", r"首先.{0,40}其次.{0,40}最后"),
]

TIME_CONNECTORS = ("然后", "接着", "之后", "第二天", "随后", "接下来")

# ---------- 重复密度红线（v4.2，阈值与 SKILL.md 第四节一致） ----------
# 词级/骨架级检查的监控词表：连接词、转折词、口语高频实词。
WATCH_WORDS = [
    "但", "但是", "可是", "不过", "然而", "然后", "后来", "其实", "反正",
    "结果", "所以", "因为", "虽然", "而且", "还是", "就是", "真的", "直接",
    "知道", "觉得", "有点", "大概", "确实", "特别", "最后", "终于", "忽然",
    "突然", "原来", "居然", "竟然",
]
# 骨架级：连接词 + 主语/指示代词（"但我""然后我"这类同款句式开头）。
SKELETON_SUBJECTS = ("我", "她", "他", "你", "它", "这", "那")

# ---------- 语料基线（84 篇实测，详见 SKILL.md） ----------
BASELINE = {
    "sentence_cv": 0.825,       # 全库句长变异系数
    "dash_per_k": 0.55,         # 破折号/千字
    "excl_per_k": 0.075,        # 感叹号/千字
    "para_time_start_pct": 2.9,  # 段首时间连接词段落占比
    "word_per_k": 2.5,          # 重复密度红线·词级：单一实词/连接词密度上限（语料最高频实词 0.21/千字）
    "word_min": 4,              # 词级：低于该次数不看密度（千字以内短稿个位数出现不算病）
    "skeleton_per_k": 0.8,      # 重复密度红线·骨架级：同一"连接词+主语"开头上限
    "skeleton_min": 3,          # 骨架级：低于该次数不看密度
    "clause_repeat_warn": 3,    # 重复密度红线·小句级：相同小句复读黄灯
    "clause_repeat_fail": 6,    # 重复密度红线·小句级：相同小句复读红线
}


def strip_noise(text):
    """去掉 frontmatter、代码块、行内代码、图片，返回正文。"""
    fm = ""
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[:end + 3]
            text = text[end + 3:]
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    return fm, text


def split_paras(body):
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def sentences(body):
    lines = [l for l in body.split("\n")
             if l.strip() and not l.strip().startswith(("#", "|", ">", "-"))]
    prose = " ".join(lines)
    parts = [re.sub(r"\s", "", s) for s in re.split(r"[。！？!?]", prose)]
    return [len(p) for p in parts if 0 < len(p) <= 200]


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    args = [a for a in sys.argv[1:]]
    blog_mode = "--blog" in args
    args = [a for a in args if a != "--blog"]
    if not args:
        print(__doc__)
        sys.exit(2)
    raw = open(args[0], encoding="utf-8").read()
    fm, body = strip_noise(raw)
    n = len(re.sub(r"\s", "", body))
    if n == 0:
        print("正文为空（或全部是代码块/图片）。")
        sys.exit(0)

    fails, warns = [], []

    # ---- FAIL: 硬禁词（引号内命中降级为 WARN：引语或小说叙事道具合法） ----
    def in_quotes(pos):
        inside_curly = body.count('"', 0, pos) % 2 == 1
        inside_cn = (body.count("\u201c", 0, pos) > body.count("\u201d", 0, pos))
        opens = max(body.rfind("「", 0, pos), body.rfind("『", 0, pos))
        closes = max(body.rfind("」", 0, pos), body.rfind("』", 0, pos))
        return inside_curly or inside_cn or opens > closes

    def count_free_quoted(body, w):
        """统计 w 在引号内/外各出现几次。引号内是人物说话，不算作者复读。"""
        free = quoted = 0
        idx = body.find(w)
        while idx != -1:
            if in_quotes(idx):
                quoted += 1
            else:
                free += 1
            idx = body.find(w, idx + 1)
        return free, quoted

    for w in FAIL_WORDS:
        idx, free, quoted = body.find(w), 0, 0
        while idx != -1:
            if in_quotes(idx):
                quoted += 1
            else:
                free += 1
            idx = body.find(w, idx + 1)
        if free:
            fails.append(f"硬禁词「{w}」出现 {free} 次")
        if quoted:
            warns.append(f"硬禁词「{w}」在引号内出现 {quoted} 次——引语或小说叙事道具可保留，否则删除")

    # ---- FAIL: frontmatter ----
    if blog_mode and fm:
        m = re.search(r"^description:[ \t]*(\S.*)$", fm, flags=re.M)
        if m:
            fails.append(f"description 必须留空，当前值：{m.group(1).strip()}")
        if re.search(r"^tags:", fm, flags=re.M):
            fails.append("不使用 tags 字段")

    # ---- WARN: 动作级外衣 ----
    for name, pat in WARN_PATTERNS:
        ms = re.findall(pat, body)
        if ms:
            warns.append(f"{name}：命中 {len(ms)} 处（需人工判断是否抬价/套话）")

    # ---- WARN: 流水账接线 ----
    paras = split_paras(body)
    prose_paras = [p for p in paras if not p.startswith(("#", ">", "-", "*", "|"))]
    time_start = [p for p in prose_paras if p.startswith(TIME_CONNECTORS)]
    pct = len(time_start) / len(prose_paras) * 100 if prose_paras else 0
    if pct > 5:
        warns.append(f"流水账接线：段首时间连接词段落占 {pct:.1f}%（基线 {BASELINE['para_time_start_pct']}%，超 5% 即重写）")

    # ---- FAIL/WARN: 重复密度红线——词级（引号内豁免：那是人物说话） ----
    word_stats = []
    for w in WATCH_WORDS:
        free, quoted = count_free_quoted(body, w)
        if free:
            word_stats.append((w, free))
            if free >= BASELINE["word_min"] and free / n * 1000 > BASELINE["word_per_k"]:
                fails.append(
                    f"重复密度红线（词级）：「{w}」正文 {free} 次 = {free / n * 1000:.2f}/千字"
                    f"（上限 {BASELINE['word_per_k']}/千字且至少 {BASELINE['word_min']} 次，语料最高频实词仅 0.21），必须删改")

    # ---- FAIL: 重复密度红线——骨架级（连接词+主语，同款句式开头复读） ----
    for w in WATCH_WORDS:
        for subj in SKELETON_SUBJECTS:
            s = w + subj
            free, _ = count_free_quoted(body, s)
            if free >= BASELINE["skeleton_min"] and free / n * 1000 > BASELINE["skeleton_per_k"]:
                fails.append(
                    f"重复密度红线（骨架级）：「{s}」正文 {free} 次 = {free / n * 1000:.2f}/千字"
                    f"（上限 {BASELINE['skeleton_per_k']}/千字且至少 {BASELINE['skeleton_min']} 次），同款句式复读，必须改写一部分")

    # ---- WARN/FAIL: 重复密度红线——小句级（相同小句逐字复读） ----
    # 只数散文行：排除标题、引用块、列表、代码围栏等结构性行（与 sentences() 口径一致）。
    clause_counter = {}
    prose_clause_src = " ".join(
        l for l in body.split("\n")
        if l.strip() and not l.strip().startswith(("#", "|", ">", "-", "*", "`")))
    for c in re.split(r"[。！？!?；;，,、：:…\s]+", prose_clause_src):
        c = c.strip("\u201c\u201d\"'「」『』（）()")
        if 3 <= len(c) <= 12:
            clause_counter[c] = clause_counter.get(c, 0) + 1
    for c, cnt in sorted(clause_counter.items(), key=lambda kv: -kv[1]):
        if cnt >= BASELINE["clause_repeat_fail"]:
            fails.append(f"重复密度红线（小句级）：「{c}」复读 {cnt} 次，必须改写或删并")
        elif cnt >= BASELINE["clause_repeat_warn"]:
            warns.append(f"小句复读：「{c}」出现 {cnt} 次，注意口头禅化")

    # ---- WARN: 感叹号超发 ----
    excl = body.count("！") + body.count("!")
    excl_k = excl / n * 1000
    if excl_k > 0.5:
        warns.append(f"感叹号密度 {excl_k:.2f}/千字（基线 {BASELINE['excl_per_k']}/千字，情绪应走比喻和短句）")

    # ---- STAT ----
    sents = sentences(body)
    cv = statistics.pstdev(sents) / statistics.mean(sents) if sents else 0
    dash_k = body.count("——") / n * 1000
    single = sum(1 for p in prose_paras if "\n" not in p and len(re.sub(r"\s", "", p)) < 60)
    single_pct = single / len(prose_paras) * 100 if prose_paras else 0

    print("=" * 50)
    print("cmchen-writing 质检报告")
    print("=" * 50)
    print("\n【FAIL】硬禁令")
    if fails:
        for f in fails:
            print(f"  ✗ {f}")
    else:
        print("  ✓ 零命中")
    print("\n【WARN】语境判断")
    if warns:
        for w in warns:
            print(f"  ! {w}")
    else:
        print("  ✓ 无报警")
    print("\n【STAT】统计（基线对照）")
    print(f"  正文字数：{n}")
    print(f"  句长 CV：{cv:.3f}（人写基线 {BASELINE['sentence_cv']}，越高低差越大）")
    print(f"  破折号：{dash_k:.2f}/千字（基线 {BASELINE['dash_per_k']}，是他第一标点，别怕用）")
    print(f"  感叹号：{excl_k:.2f}/千字（基线 {BASELINE['excl_per_k']}）")
    print(f"  段首时间连接词：{pct:.1f}%（基线 {BASELINE['para_time_start_pct']}%）")
    print(f"  短单句段占比：{single_pct:.1f}%")
    top_words = sorted(word_stats, key=lambda kv: -kv[1])[:5]
    print("  高频连接词/实词：" + ("、".join(f"{w}×{c}" for w, c in top_words) if top_words else "（无）"))

    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
