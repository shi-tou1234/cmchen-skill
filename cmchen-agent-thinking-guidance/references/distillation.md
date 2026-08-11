# 权重蒸馏精髓：工程教训与可蒸馏格式

> **【原创】** 本文件为本协议原创，解释权重层蒸馏的工程教训和"可蒸馏格式"概念，以及它如何反过来成为运行时思维质量的硬门（可蒸馏门）。
>
> **来源**：训练配置信息提取自 `cmchen-claude-thinking-mode`（本机衍生 skill）的 `references/training-notes.md`，后者改编自 [Dhamodharan2006/fable5-qwen3-thinking-distillation](https://github.com/Dhamodharan2006/fable5-qwen3-thinking-distillation) 的 `Distill-Qwen3-4b.ipynb`（MIT 许可）。训练笔记本源码为 MIT，本文件并入 AGPL-3.0 作品后随整体受 AGPL 约束。
>
> **用途**：本文件不是训练教程（训练复现步骤见 `training-notes.md`），而是提炼权重蒸馏的**核心工程教训**，并解释这些教训如何反过来定义了运行时的"可蒸馏门"——本协议思轨的硬门。

---

## 一句话路线

用 4,659 条真实 Fable 5 智能体会话 trace，通过 QLoRA SFT 微调 Qwen3-4B，让模型在回答前自动生成结构化的 `<think>` 推理块。训练约 45 分钟（实际跑 304 分钟），loss 从约 2.0 降到约 0.9–1.1。

这不是"教模型写代码"——Qwen3-4B 已经会写代码。这是教模型**像 Fable 5 一样思考**：先规划再行动、主动考虑边界、自我纠正、验证结果。被蒸馏的不是答案，是推理过程本身。

---

## 数据

| 项 | 值 |
|---|---|
| 数据集 | `lordx64/agentic-distill-fable-5-sft` |
| 条数 | 4,659（与主 Skill 的 4,665 条 trace 同源，差 6 条是格式过滤） |
| 格式 | ChatML（`<|im_start|>system/user/assistant`） |
| 来源 | Fable 5（Claude）在真实 agentic 任务中的完整工具调用转录 |

数据集样本长这样（**示意，非原文**——用户消息与 `<think>` 内容为按真实模式编造的示例，只用于展示结构）：

```
<|im_start|>system
You are a helpful coding assistant that thinks carefully before responding.<|im_end|>
<|im_start|>user
把 api.ts 里的 getUsrData 改名成 getUserData<|im_end|>
<|im_start|>assistant
<think>
Alright, the user wants to rename getUsrData to getUserData. Because this is a single-file rename,
I need to find the definition and all call sites within api.ts. Since the user specified one file,
I should check if there are cross-file references too. Thus, I'll grep the project first to be safe.
</think>

我来先搜索项目里所有引用 `getUsrData` 的地方...<|im_end|>
```

注意：`<think>` 块里有 `Alright,` 开场、`because`/`since`/`thus` 连接、可证伪预测——这正是可蒸馏门的五条标准。训练数据本身就是这些标准的具象化。

---

## 关键取舍：全序列训练 vs train_on_responses_only

这是整个蒸馏过程中最重要的工程决策，也是本文件最想传递的教训。

| 方案 | 效果 | 为什么 |
|---|---|---|
| **全序列训练**（采用） | 保留全部 4,659 条 | 模型学习完整对话流——包括用户输入、工具输出、assistant 推理和回答 |
| `train_on_responses_only`（放弃） | 约 94% 样本被过滤掉 | Qwen3 的 chat template 在 `train_on_responses_only` 模式下会因模板标记匹配问题大量过滤 |

**为什么这个取舍重要**：如果开 `train_on_responses_only`，只剩下约 6%（约 280 条）样本可训练——数据量不足以让 4B 模型学到稳定的思维模式。全序列训练虽然连用户输入和工具输出一起学了（理论上浪费），但保留了完整数据量，模型能从 4,659 条样本中提取稳定的推理模式。

**教训**：工具链的默认选项不总是对的。`train_on_responses_only` 在大多数 SFT 场景是推荐做法（只学 assistant 部分，不学 user 部分），但在 Qwen3 + ChatML + 这个特定数据集上，它会造成灾难性数据损失。这个发现不是理论推演，是实际跑起来看到 94% 过滤率后被迫切换的。

---

## 训练配置

以下配置在 Kaggle T4（15GB VRAM）上跑通，loss 从约 2.0 降到约 0.9–1.1。

| 项 | 值 | 说明 |
|---|---|---|
| 基座模型 | `unsloth/Qwen3-4B-bnb-4bit` | 4-bit 预量化版本，省 VRAM |
| 量化 | 4-bit QLoRA（NF4） | QLoRA = 量化基座 + LoRA 微调，15GB 够用 |
| LoRA rank | r=16 | 低秩适配的维度 |
| LoRA alpha | alpha=32 | 缩放因子，通常 alpha = 2 × r |
| LoRA dropout | 0.05 | 正则化，防过拟合 |
| LoRA 模块 | q, k, v, o, gate, up（6/7） | 保留 SwiGLU 相关模块，跳过 down 投影 |
| 序列长度 | 2048 tokens | 覆盖大多数 agentic trace |
| batch | 1 × grad_accum 8 = 有效 8 | T4 显存只够 batch=1，用梯度累积模拟大 batch |
| 学习率 | 5e-5，cosine 调度 | QLoRA 典型学习率 |
| epoch | 1 | loss 仍在下降，但 1 epoch 已足够看到行为差异 |

**为什么只跑 1 epoch**：loss 在 1 epoch 结束时仍在下降，理论上可以继续。但 1 epoch 已经产生了可测的行为差异（见下节），且更多 epoch 有过拟合风险——模型可能开始记忆特定 trace 而非学习通用模式。这是工程判断而非理论最优。

**LoRA 模块选择**：6/7 模块（q, k, v, o, gate, up）覆盖了注意力和 SwiGLU 前馈的主体，只跳过 down 投影。这个选择来自 Unsloth 的默认推荐，在本数据集上效果良好。

---

## think 块与提示词模板

推理时用的系统提示词（微调数据里也以此为基底）：

```
<|im_start|>system
You are a helpful coding assistant that thinks carefully before responding.<|im_end|>
<|im_start|>user
{问题}<|im_end|>
<|im_start|>assistant
```

模型被训练成：先输出 `<think>...</think>` 块（规划、考虑边界），再输出正式回答。

### think 块的结构

训练数据中的 `<think>` 块不是随意流意识，而是有结构的。从 4,659 条 trace 的统计中可以提取出以下模式：

1. **开场锚点**：以 `Alright,` 或 `Okay,` 开头（63.9% 的真实 CoT 这么做）
2. **推理连接词**：每段至少用一个 `because`/`since`/`therefore`/`thus`（平均 2.14 个/轮）
3. **可证伪预测**：结尾预测一个可观察的结果（462 条真实 CoT 以预测结尾）
4. **自修正痕迹**（56.4% 的轮次）：用 `Actually,` 或 `However,` 修正
5. **内联验证词**：`should be` / `to verify` / `to ensure` / `to confirm` / `to make sure` 中至少一个（87.7% 的动作后验证率）

这五条不是事后总结——它们是训练数据本身的统计特征。模型通过 SFT 学到的正是这些特征。

### 提示词模板的极简性

注意系统提示词只有一句话："You are a helpful coding assistant that thinks carefully before responding." 没有长篇行为规范，没有 18 条规则，没有流程图。模型的行为来自权重，不是来自提示词。这是权重蒸馏与提示词方案的根本区别：提示词方案靠每次推理时注入规范，权重蒸馏把规范烧进权重。

---

## 训练后的可测差异

训练前后的 Qwen3-4B 在以下方面有可观测的行为差异（vs 原版 Qwen3-4B）：

| 维度 | 原版 Qwen3-4B | 微调后 |
|---|---|---|
| `<think>` 块 | 不生成或无结构 | 自动生成结构化 `<think>` 块，先规划再回答 |
| 调试方法 | 直接猜原因或逐个试 | 拆成有序的调查步骤 |
| 代码评审 | 指出一个问题 | 指出**多个**失败模式 |
| 边界考虑 | 不主动想 | 主动考虑边界情况、错误处理、安全问题 |
| 架构建议 | 直接给细节 | 先结构化地给架构建议，再展开细节 |

**这些差异怎么测**：不是靠主观感受，是靠可观测的行为指标。比如"指出多个失败模式"——给模型一段有 3 个 bug 的代码，原版通常只找到 1 个，微调后平均找到 2-3 个。"先规划再回答"——检查输出中 `<think>` 块是否出现在正式回答之前，以及块内是否有规划步骤。

---

## 核心洞察：思维链本身就是训练目标

这是本文件最重要的部分，也是本协议原创的"可蒸馏门"的理论基础。

### 传统 SFT 的直觉

传统 SFT 的直觉是：训练数据 = 输入 + 正确输出，模型学习从输入映射到正确输出。在这种直觉下，`<think>` 块是"中间过程"——它帮助模型推理，但训练目标仍然是最终答案的正确性。

### 这个直觉在这里是错的

在 agentic 蒸馏场景中，训练数据 = 输入 + **推理过程** + 输出。被蒸馏的不是"给定这个问题，正确答案是什么"，而是"给定这个问题，**该怎么想**才能得到正确答案"。

具体来说：
- 如果只训练最终答案（`train_on_responses_only` 且去掉 think 块），模型学到的只是"输入 → 输出"的映射。但 agentic 任务的输出空间太大（可能的代码改动无穷多），4B 模型记不住。
- 如果训练完整序列（包括 think 块），模型学到的是"输入 → 推理 → 输出"的映射。推理过程约束了输出空间——先想清楚要改什么、为什么改、改完怎么验证，然后改。模型不需要记住所有可能的输出，只需要学会推理模式。

**这就是为什么全序列训练比 `train_on_responses_only` 更重要**——不只是因为数据量（94% vs 100%），更是因为 think 块本身就是训练信号。丢掉 think 块的训练等于丢掉了一半的训练信息。

### 推论：思维链不是答案的附属品

传统观点：思维链是帮助模型得到答案的脚手架，答案是目标。

这里的发现：思维链本身就是目标。答案是思维链的副产品——如果你想了正确的步骤，答案自然正确；如果你想错了步骤，答案大概率错。

这个发现不是哲学，是工程事实：4,659 条 trace 的 SFT 让 4B 模型学会了 Fable 5 的推理模式，而这个推理模式（不是任何具体的代码答案）是可迁移到新任务的。

---

## 这个事实的运行时应用：可蒸馏门

上面的核心洞察反过来定义了本协议的运行时硬门——可蒸馏门。

### 逻辑链

1. **训练事实**：Qwen3 蒸馏的训练数据是 Fable 5 的明文思维链。被蒸馏的是推理过程，不是答案。
2. **推理**：如果推理过程是训练目标，那么"好的推理过程"就是"像训练数据一样的推理过程"。
3. **训练数据的特征**：开场锚点、连接词、可证伪预测、自修正痕迹、验证词——五条统计特征。
4. **运行时硬门**：你的思维链必须满足这五条标准。不满足意味着你的推理过程不够格当训练数据——也就是不够格当 Fable 5 的推理过程——也就是不够格进入行轨。

### 可蒸馏门的五条标准

一条思维链要"可蒸馏"，必须满足（缺一不可）：

1. **有开场锚点**：以 `Alright,` 或 `Okay,` 开头
2. **有推理连接词**：每段至少用一个 `because`/`since`/`therefore`/`thus`
3. **有可证伪预测**：结尾预测一个可观察的结果
4. **有自修正痕迹**：用 `Actually,` 或 `However,` 修正
5. **有内联验证词**：`should be` / `to verify` / `to ensure` / `to confirm` / `to make sure` 中至少一个

不满足时有三个选择：
- **补全**：想清楚补上再动手
- **降级**：过平凡门（单文件 <10 行无新行为——不需要复杂推理）
- **提问**：问一个精准问题（想不清楚就问，不要硬猜）

### 为什么这是"硬门"而不是"建议"

因为它阻止的是中端模型的主要失败模式——跳步。一个不满足可蒸馏门的思维链，通常意味着以下之一：
- 没有开场锚点 → agent 没有复述需求就开始动手（失败模式 1 的前兆）
- 没有连接词 → agent 在叙述而非推理（没有因果链，下一步可能是猜的）
- 没有可证伪预测 → agent 不知道做完后怎么验证（失败模式 4 的前兆）
- 没有自修正痕迹 → agent 一条路走到底（失败模式 9 的前兆——强行穿过意外）
- 没有验证词 → agent 不打算验证（失败模式 14 的前兆——验证表演）

每一条缺失都对应一种具体的失败模式。可蒸馏门把它们拦在行轨入口之前。

同时注意，门量的是"跳步"而不是"文体"：第一遍就对、无需修正时不伪造自修正（该条标"不适用"）；只差一个文体信号（如没写 `Alright,`）时按三选一处理，不必硬凑五条。伪造的自修正比缺失更糟——它把假严谨写进了本来干净的推理。完整豁免规则见 `voice-and-think.md` 的"不可蒸馏 = 不准动手"节。

### 与 voice-and-think.md 的关系

可蒸馏门的深度规则、五条标准的统计来源、不满足时的处理流程，详见 `voice-and-think.md`。本文件解释的是**为什么**有这扇门——因为权重蒸馏的核心教训告诉我们，思维链本身就是训练目标。`voice-and-think.md` 解释的是**怎么**执行这扇门。

### 与 flowcharts.md 第 8 张图的关系

`flowcharts.md` 的第 8 张图（三轨交汇，本协议原创）把可蒸馏门放在行轨入口之前。思轨的思维链不达标，不准进入行轨。这张图可视化了权重蒸馏教训如何变成运行时架构——不是"先想后做"的线性流程，而是"思轨质量不达标就不准动手"的硬约束。

---

## 两种使用路径的对比

本协议提供两条路径让 agent 获得 Fable 5 的思维能力：

| 路径 | 机制 | 成本 | 效果 |
|---|---|---|---|
| **提示词路径**（默认） | 加载 SKILL.md，用提示词规范行为 | 零成本，任何 agent 可用 | 依赖模型遵守规范的能力；强模型效果好，弱模型可能跳步 |
| **权重蒸馏路径**（进阶） | 微调 Qwen3-4B，把思维模式烧进权重 | 需 GPU（训练 15GB，推理 3GB） | 行为内化，不依赖提示词遵守；4B 模型也能稳定生成结构化思维链 |

**重要**：普通使用本协议不需要微调。提示词路径已能达到同样的行为效果——可蒸馏门在运行时用提示词强制执行，不需要权重层面的微调。权重蒸馏路径是为那些想要一个**自带** Fable 5 思维习惯的轻量模型的用户准备的。

两条路径不互斥：你可以用微调后的 Qwen3-4B 加载本协议的 SKILL.md——权重提供默认的思维习惯，提示词提供场景化的门禁规则。这是叠加而非替代。

---

## 来源声明

- **训练配置与数据信息**：提取自 `cmchen-claude-thinking-mode`（本机衍生 skill）的 `references/training-notes.md`，后者改编自 [Dhamodharan2006/fable5-qwen3-thinking-distillation](https://github.com/Dhamodharan2006/fable5-qwen3-thinking-distillation) 的 `Distill-Qwen3-4b.ipynb`（MIT 许可）。
- **训练笔记本源码**：MIT 许可。若基于此再训练或分发模型，请遵守 MIT 条款。
- **本协议整体**：AGPL-3.0。本文件作为 AGPL 作品的一部分，随整体受 AGPL 约束。
- **数据集**：`lordx64/agentic-distill-fable-5-sft`，源自 [Kuberwastaken](https://huggingface.co/Kuberwastaken) 发布的 `Fable-5-traces` 数据集（AGPL-3.0）。
- **【原创】内容**：本文件的"核心洞察"和"可蒸馏门"部分为本协议原创贡献——把权重蒸馏的工程教训反过来当运行时思维质量硬门。这不是 fable5-qwen3-thinking-distillation 项目的内容，而是本协议对其训练结果的解读和应用。
- **Claude、Fable 5、Anthropic** 为 Anthropic PBC 商标。本项目与 Anthropic 无关联或背书。
