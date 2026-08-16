<!-- 来源：改编自 fable5-qwen3-thinking-distillation（MIT）。原始文件为英文，本文为全面中文翻译与改编。
     许可：原始训练笔记本源码为 MIT；本文件并入 cmchen-agent-thinking-guidance 后随整体受 AGPL-3.0 约束。 -->

# 训练路线：把 Fable 5 思维蒸馏进 Qwen3-4B

本笔记从 `Distill-Qwen3-4b.ipynb`（原样留档）提炼。它描述的是**进阶路径**：不满足于用提示词规范让任意 agent 模仿，而是真正**微调一个轻量小模型**，让它自己"内化" Fable 5 的思考习惯。**普通使用本协议不需要这步——提示词方案已能达到同样的行为效果。**

## 一句话路线

用 4,659 条真实 Fable 5 智能体会话 trace，通过 QLoRA SFT 微调 Qwen3-4B，让模型在回答前自动生成结构化的 `<think>` 推理块。训练约 45 分钟（实际跑 304 分钟），loss 从约 2.0 降到约 0.9–1.1。

## 数据

| 项 | 值 |
|---|---|
| 数据集 | `lordx64/agentic-distill-fable-5-sft` |
| 条数 | 4,659（与主协议的 4,665 trace 同源） |
| 格式 | ChatML（`<|im_start|>system/user/assistant`） |

**关键取舍**：全序列训练，不开 `train_on_responses_only`——后者在 Qwen3 上会造成约 94% 样本被过滤掉，全序列训练保留全部 4,659 条。

> 为什么这个取舍重要：`train_on_responses_only` 通常只训练 assistant 回复部分，忽略 system 和 user 部分。但在 Qwen3 的 ChatML 格式下，大量 trace 的结构使得该模式误过滤掉绝大多数样本。全序列训练虽然也让模型"看到" user 指令，但保留了完整上下文，让模型学会在给定任务描述后如何生成正确的推理过程。

## 训练配置（QLoRA，Kaggle T4 / 15GB VRAM）

| 项 | 值 |
|---|---|
| 基座模型 | `unsloth/Qwen3-4B-bnb-4bit` |
| 量化 | 4-bit QLoRA（NF4） |
| LoRA | r=16, alpha=32, dropout=0.05 |
| LoRA 模块 | q, k, v, o, gate, up（6/7，保留 SwiGLU 相关） |
| 序列长度 | 2048 tokens |
| batch | 1 × grad_accum 8 = 有效 8 |
| 学习率 | 5e-5，cosine 调度 |
| epoch | 1（loss 仍在下降） |

> 关于 LoRA 模块的选择：覆盖了 attention 的 q/k/v/o 和 FFN 的 gate/up，共 6 个模块。唯一未覆盖的是 SwiGLU 的 down 投影——保留它不动是一个经过验证的取舍，既能控制参数量，又不损失太多表达力。

## `<think>` 块与提示词模板

推理时用的系统提示词（微调数据里也以此为基底）：

```
<|im_start|>system
You are a helpful coding assistant that thinks carefully before responding.<|im_end|>
<|im_start|>user
{问题}<|im_end|>
<|im_start|>assistant
```

模型被训练成：先输出 `<think>...</think>` 块（规划步骤、考虑边界与错误处理、论证多方案权衡、以"行动 + 预期结果"收尾），再输出正式回答。

这与本协议思轨（Think）的可蒸馏门标准一致——思维链必须结构化到足以当一条 SFT 训练样本。微调后的模型不需要外部提示词来强制这个结构，它已经内化了。

## 训练后的可测差异（vs 原版 Qwen3-4B）

1. **生成 `<think>` 块，先规划再回答**——原版 Qwen3-4B 不会自动生成结构化推理块，微调后会
2. **把调试问题拆成有序的调查步骤**——不再是跳跃式猜测，而是 OBSERVE → INVESTIGATE → HYPOTHESIZE 的系统流程
3. **代码评审时能指出多个失败模式**——不只指出一个，而是系统性枚举（对应本协议审轨的对抗式自检）
4. **主动考虑边界情况、错误处理、安全问题**——不再需要提示词提醒
5. **先结构化地给出架构建议，再展开细节**——对应本协议行轨的"先理解全貌再垂直切片"

## 复现步骤（Kaggle T4）

1. 在 Kaggle 建 Notebook，加速器选 **T4 x 1**，联网开启。
2. 上传 `Distill-Qwen3-4b.ipynb` 按序运行（它已含依赖安装、torch shim）。
3. 训练结束后产物：`fable5-qwen3-4b-lora-adapter.zip`（约 93 MB）。
4. 可选：推送到 HuggingFace Hub 或导出 GGUF（笔记本第 13 个 cell 有模板，注意笔记本中间有个 cell 因版本问题报错，跳过即可，主体训练 cell 可正常完成）。

> 关于硬件：Kaggle 的免费 T4（15GB VRAM）足以完成训练。本地推理只需约 3GB VRAM（4-bit 量化后）。如果没有 GPU，主协议的提示词方案已能达到同样的行为效果，成本为零。

## 注意

- **许可**：本协议整体为 AGPL-3.0。若基于此再训练/分发模型，请遵守 AGPL 派生条款；训练笔记本源码为 MIT（`Dhamodharan2006/fable5-qwen3-thinking-distillation`）。
- **成本**：训练需 GPU（本地 4-bit 推理约 3GB VRAM；训练建议 >=15GB）。无 GPU 时，主协议的提示词方案已能达到同样的行为效果，成本为零。
- **数据来源**：4,659 条 trace 来自 `Kuberwastaken/Fable-5-traces` 数据集（AGPL-3.0），由 `lordx64/agentic-distill-fable-5-sft` 整理为 SFT 格式。
- **不是必需步骤**：本协议的核心价值在提示词规范（三轨一门），微调只是进阶选项。大多数使用场景下，加载 `SKILL.md` 即可获得完整的 Fable 5 思维行为。
