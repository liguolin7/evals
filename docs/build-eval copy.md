# 构建评估

**重要提示：目前我们暂不接受包含自定义代码的评估！** 虽然我们暂时要求您不要提交此类评估，但您仍然可以使用自定义模型评分 YAML 文件提交模型评分评估。

本文档介绍了构建评估的端到端过程，评估包括数据集和评估类的选择。`examples` 文件夹中包含了遵循以下步骤构建几个学术评估的 Jupyter 笔记本，这有助于说明整个过程。

这个过程的步骤包括构建数据集、注册新的评估以及运行评估。重要的是，我们假设您正在使用现成的[现有评估模板](eval-templates.md)（如果不是这种情况，请参见[构建自定义评估的示例](custom-eval.md)）。如果您有兴趣公开贡献您的评估，我们在文末还包含了一些我们认为有趣的评估标准。

我们正在寻找以下类别的评估：

- 过度拒绝
- 安全性
- 系统消息可控性
- 实际场景中的幻觉
- 数学/逻辑/物理推理
- 真实世界用例（请在您的 PR 中描述这种能力如何在产品中使用）
- 其他基础能力

如果您有一个不属于这些类别但仍然是多样化示例的评估，也请贡献！

## 格式化数据

一旦您想好要实现的评估，您需要将样本转换为正确的 JSON lines (JSONL) 格式。JSONL 文件就是每行包含一个唯一 JSON 对象的 JSON 文件。

您可以使用 `openai` CLI（通过 [OpenAI-Python](https://github.com/openai/openai-python) 获得）将一些常见文件类型转换为 JSONL：
```
openai tools fine_tunes.prepare_data -f data[.csv, .json, .txt, .xlsx or .tsv]
```

我们在 [registry/data/README.md](../evals/registry/data/README.md) 中包含了一些 JSONL 评估文件的示例。

每个 JSON 对象将代表您评估中的一个数据点。JSON 对象中需要的键取决于评估模板。所有模板都需要一个 `"input"` 键，这是提示，最好使用[聊天格式](https://platform.openai.com/docs/guides/chat/introduction)（也支持字符串）。即使您正在评估非聊天模型，我们也建议使用聊天格式。如果您同时评估聊天和非聊天模型，我们会处理聊天格式提示和原始字符串提示之间的转换（参见[这里](../evals/prompt/base.py)的转换逻辑）。

对于基本评估 `Match`、`Includes` 和 `FuzzyMatch`，另一个必需的键是 `"ideal"`，它是一个字符串（或字符串列表），指定正确的参考答案。对于模型评分评估，必需的键根据评估而变化，但由评估 `prompt` 中未被（可选的）`args` 覆盖的 `{key}` 决定。

我们为各种评估模板实现了 [CoQA](https://stanfordnlp.github.io/coqa/) 数据集的小子集，以说明数据应如何格式化。参见 [`coqa/match.jsonl`](../evals/registry/data/coqa/match.jsonl) 了解适用于 `Match` 基本评估模板的数据示例，以及 [`coqa/samples.jsonl`](../evals/registry/data/coqa/samples.jsonl) 了解适用于 `fact` 和 `closedqa` 模型评分评估的数据。请注意，即使这两个模型评分评估需要不同的键，我们也可以在数据中包含键的超集以支持两种评估。

如果数据集文件在您的本地机器上，将 `jsonl` 文件放在 `evals/registry/data/<eval_name>/samples.jsonl` 中。如果它在云对象存储中，我们支持主要云服务的路径式 URL（仅供您个人使用，我们不会接受包含云 URL 的 PR）。

## 注册评估

通过在 `evals/registry/evals/<eval_name>.yaml` 中添加文件来注册评估，使用 elsuite 注册表格式。例如，对于 `Match` 评估，它应该是：
```
<eval_name>:
  id: <eval_name>.dev.v0
  description: <description>
  metrics: [accuracy]

<eval_name>.dev.v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: <eval_name>/samples.jsonl
```

运行评估时，将在 `evals/registry/data` 中搜索数据。例如，如果提供的文件路径是 `test_match/samples.jsonl`，则数据应该位于 `evals/registry/data/test_match/samples.jsonl` 中。

评估的命名约定采用 `<eval_name>.<split>.<version>` 的形式。
- `<eval_name>` 是评估名称，用于对分数可比较的评估进行分组。
- `<split>` 是数据分割，用于进一步对同一 `<base_eval>` 下的评估进行分组。例如，"val"、"test" 或 "dev" 用于测试。
- `<version>` 是评估的版本，可以是您想使用的任何描述性文本（最好不要包含 `.`）。

通常，对同一模型运行相同的评估名称应该始终得到类似的结果，以便其他人可以复现。因此，当您更改评估时，应该更新版本。

## 运行评估

现在您可以从 CLI 使用您选择的模型或完成函数在您的数据上运行评估：
```
oaieval gpt-3.5-turbo <eval_name>
```
恭喜，您已经构建了您的评估！继续迭代直到您对结果有信心。

## 对于模型评分评估：逐步工作流程

我们预计现有的模型评分评估（如 `fact`、`closedqa` 和 `battle`）将适合许多用例。然而，其他用例可能需要更多定制，例如，不同的评估提示。对于这些情况，将需要更多工作，但通常仍然不需要编码！

1. 如果您不能使用现有的模型评分评估，在 `evals/registry/modelgraded` 中创建新的 YAML 或向现有 YAML 添加新条目，以指定评估的[参数](eval-templates.md#parameters-for-model-graded-evals)。参见 [`humor.yaml`](../evals/registry/modelgraded/humor.yaml) 作为示例。
    - 请注意，即使您正在创建新的 YAML，最简单的方法可能是复制现有的 YAML 作为起点。例如，检查模型完成输出是否符合评分标准的模型评分评估可以复制 `closedqa.yaml` 并只编辑 `args`。
2. 接下来，您将创建数据集并注册评估，如上所述。参见 [`joke_fruits_labeled.jsonl`](../evals/registry/data/test_metaeval/joke_fruits_labeled.jsonl) 和 [`joke-fruits`](../evals/registry/evals/test-modelgraded.yaml) 作为示例。
    - 请注意，建议在注册评估时指定 `eval_type`，而不是在步骤 1 中指定。
3. 运行您的评估，例如，`oaieval gpt-3.5-turbo joke-fruits`。
4. （推荐）为模型评分评估添加元评估！每个模型评分评估都有一些可调节的参数，主要是 `prompt` 但也包括 `eval_type`。为了确保评估质量高，我们建议每个模型评分评估贡献都附带"选择标签"，这基本上是人工提供的标签，指示模型应该做出哪种评估选择。作为示例（假设这些笑话确实很有趣），参见 [`joke_fruits_labeled.jsonl`](../evals/registry/data/test_metaeval/joke_fruits_labeled.jsonl) 中的 `"choice"` 键，这些键不被 `joke-fruits` 评估使用，但被其下方的 [`joke-fruits-meta`](../evals/registry/evals/test-modelgraded.yaml) 元评估使用。运行元评估后，例如 `oaieval gpt-3.5-turbo joke-fruits-meta`，报告将输出 `metascore/` 准确度，对于好的模型评分评估，这应该接近 "1.0"。

## 贡献评估的标准

重要提示：如果您要贡献代码，请确保在提交和推送之前运行 `pip install pre-commit; pre-commit install`，以确保运行 `black`、`isort` 和 `autoflake`。

我们有兴趣收集一组多样化和有趣的评估，以便未来改进我们的模型。以下是我们认为好的评估的一些标准：
- [ ] 评估应该主题一致。我们希望看到围绕相同用例、主题领域、失败模式等的多个提示。
- [ ] 评估应该具有挑战性。如果 GPT-4 或 GPT-3.5-Turbo 在所有提示上表现都很好，这就不太有趣。当然，评估也应该在模型的限制和约束范围内是可能的。通常，一个好的经验法则是人类（可能是主题专家）是否能在提示上表现良好。
- [ ] 评估应该方向明确。数据应该包含关于什么是正确行为的良好信号。这意味着，例如，高质量的参考答案或用于评估答案的详尽评分标准。
- [ ] 评估应该精心制作。在提交之前，您应该考虑是否已经为良好性能设计了提示，是否使用了最佳评估模板，是否已经抽查结果以确保准确性等。

一旦您准备好公开贡献您的评估，提交 PR，OpenAI 团队将很乐意审查。确保填写预填充到 PR 消息中的所有部分。请注意，提交 PR 并不保证 OpenAI 最终会合并它。我们将运行我们自己的检查，并在考虑跟进哪些评估时使用我们的最佳判断。
