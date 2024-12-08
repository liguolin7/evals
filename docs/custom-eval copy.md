# 如何添加自定义评估

**重要提示：目前我们暂不接受包含自定义代码的评估！** 虽然我们暂时要求您不要提交此类评估，但您仍然可以使用自定义模型评分 YAML 文件提交模型评分评估。

本教程将通过一个简单的示例来指导您编写和添加自定义评估。这个示例评估将测试模型进行基本算术运算的能力。我们假设您已经按照 [README](../README.md) 中的设置说明进行了操作，并已阅读了有关如何运行和构建评估的其他文档。

在编写自己的评估时，主要需要关注以下文件：
- `evals/api.py`，它提供了评估创建者用于从模型采样和处理结果的通用接口和实用工具，
- `evals/record.py`，它定义了以不同方式记录评估结果的记录器类，例如记录到本地 JSON 文件或远程 Snowflake 数据库，以及
- `evals/metrics.py`，它定义了各种常用的感兴趣指标。

这些文件提供了一套用于编写新评估的工具。完成本教程后，您可以在[机器翻译](../evals/elsuite/translate.py)[评估示例](../examples/lafand-mt.ipynb)中看到这些工具在实际应用中的更多示例，该示例也实现了自定义评估逻辑而不是使用现有模板。

## 创建数据集

第一步是为您的评估创建数据集。在这里，我们将分别创建只包含两个示例的玩具训练集和测试集。测试示例是我们将用来评估模型的，而我们会将训练示例作为少量示例包含在模型的提示中。

我们将使用[这里](https://platform.openai.com/docs/guides/chat/introduction)描述的新聊天格式。默认情况下，如果您想评估我们的新模型，我们鼓励所有评估都使用聊天格式编写。在底层，我们会将聊天格式的数据[转换](../evals/prompt/base.py)为原始字符串，以供较旧的非聊天模型使用。

要创建玩具数据集，在终端中输入：
```bash
echo -e '{"problem": "2+2=", "answer": "4"}\n{"problem": "4*4=", "answer": "16"}' > /tmp/train.jsonl
echo -e '{"problem": "48+2=", "answer": "50"}\n{"problem": "5*20=", "answer": "100"}' > /tmp/test.jsonl
```

## 创建评估

下一步是编写一个代表实际评估的 Python 类。这个类使用您的数据集创建提示，这些提示会传递给模型以生成完成。评估类通常会继承自 `evals.Eval` 基类（在 `evals/eval.py` 中定义）并重写两个方法：`eval_sample` 和 `run`。

让我们在 `evals/elsuite` 文件夹下创建一个名为 `arithmetic.py` 的文件。我们先定义评估类。它的 `__init__` 方法将接收我们需要的参数（训练集和测试集的引用）以及其他将由基类处理的 `kwargs`。我们还将定义 `run` 方法，它接收一个 `recorder` 并返回最终的感兴趣指标。

```python
import random
import textwrap

import evals
import evals.metrics

class Arithmetic(evals.Eval):
    def __init__(self, train_jsonl, test_jsonl, train_samples_per_prompt=2, **kwargs):
        super().__init__(**kwargs)
        self.train_jsonl = train_jsonl
        self.test_jsonl = test_jsonl
        self.train_samples_per_prompt = train_samples_per_prompt

    def run(self, recorder):
        """
        由 `oaieval` CLI 调用以运行评估。`eval_all_samples` 方法调用 `eval_sample`。
        """
        self.train_samples = evals.get_jsonl(self.train_jsonl)
        test_samples = evals.get_jsonl(self.test_jsonl)
        self.eval_all_samples(recorder, test_samples)

        # 记录整体指标
        return {
            "accuracy": evals.metrics.get_accuracy(recorder.get_events("match")),
        }
```

通常，大多数 `run` 方法都会遵循这里显示的相同模式：加载数据，调用 `eval_all_samples`，并聚合结果（在本例中，使用 `evals/metrics.py` 中的 `get_accuracy` 函数）。`eval_all_samples` 接收 `recorder` 和 `test_samples`，并在底层对 `test_samples` 中的每个样本调用 `eval_sample` 方法。所以让我们现在编写 `eval_sample` 方法：

```python
    def eval_sample(self, test_sample, rng: random.Random):
        """
        由 `eval_all_samples` 方法调用以评估单个样本。

        参数
        ====
        `test_sample`：来自 JSONL 测试文件的一行
        `rng`：应该用于评估过程中需要的任何随机性

        此方法执行以下操作：
        1. 生成包含任务说明、几个示例和测试问题的提示。
        2. 从模型生成完成。
        3. 检查生成的答案是否正确。
        """
        stuffing = rng.sample(self.train_samples, self.train_samples_per_prompt)

        prompt = [
            {"role": "system", "content": "Solve the following math problems"},
        ]

        for i, sample in enumerate(stuffing + [test_sample]):
            if i < len(stuffing):
                prompt += [
                    {"role": "system", "content": sample["problem"], "name": "example_user"},
                    {"role": "system", "content": sample["answer"], "name": "example_assistant"},
                ]
            else:
                prompt += [{"role": "user", "content": sample["problem"]}]


        result = self.completion_fn(prompt=prompt, temperature=0.0, max_tokens=1)
        sampled = result.get_completions()[0]

        evals.record_and_check_match(prompt=prompt, sampled=sampled, expected=test_sample["answer"])
```
您会注意到 `eval_sample` 不接收 `recorder` 作为参数。这是因为 `eval_all_samples` 在调用 `eval_sample` 之前将其设置为默认记录器，而 `evals/record.py` 中定义的记录实用工具使用默认记录器。在这个示例中，`eval_sample` 方法将大量繁重工作交给了 `evals.record_and_check_match` 实用函数，该函数在 `evals/api.py` 中定义。这个实用函数使用给定的 `prompt` 查询由 `self.model_spec` 定义的模型，并检查结果是否与 `expected` 答案匹配（如果给定列表，则与其中之一匹配）。然后，它使用默认记录器记录这些匹配（或不匹配）。

`eval_sample` 方法可能会根据您的用例有很大的不同。如果您正在构建自定义评估，最好熟悉 `evals/record.py`、`evals/metrics.py` 和特别是 `evals/api.py` 中可用的函数。

## 注册评估

下一步是在注册表中注册您的评估，以便可以使用 `oaieval` CLI 运行它。

让我们在 `evals/registry/evals` 文件夹下创建一个名为 `arithmetic.yaml` 的文件，并为我们的评估添加一个条目，如下所示：

```yaml
# 定义基础评估
arithmetic:
  # id 指定此评估是其别名的评估
  # 在这种情况下，arithmetic 是 arithmetic.dev.match-v1 的别名
  # 当您运行 `oaieval davinci arithmetic` 时，实际上是在运行 `oaieval davinci arithmetic.dev.match-v1`
  id: arithmetic.dev.match-v1
  # 此评估记录的指标
  # 第一个指标将被视为主要指标
  metrics: [accuracy]
  description: 评估算术能力
# 定义评估
arithmetic.dev.match-v1:
  # 将类名指定为模块和类的点分路径
  class: evals.elsuite.arithmetic:Arithmetic
  # 将参数指定为 JSONL URI 的字典
  # 这些参数可以是您想传递给类构造函数的任何内容
  args:
    train_jsonl: /tmp/train.jsonl
    test_jsonl: /tmp/test.jsonl
```

`args` 字段应该与您的评估类 `__init__` 方法期望的参数匹配。

## 运行评估

最后一步是运行您的评估并查看结果。

```sh
pip install .  # 如果您使用 `pip install -e .` 安装，可以省略这一步
oaieval gpt-3.5-turbo arithmetic
```

如果您使用 `gpt-3.5-turbo` 模型运行，您应该看到类似这样的输出（我们在这里稍微整理了输出以提高可读性）：

```
% oaieval gpt-3.5-turbo arithmetic
... [registry.py:147] 从 .../evals/registry/evals 加载注册表
... [registry.py:147] 从 .../.evals/evals 加载注册表
... [oaieval.py:139] 运行开始：<run_id>
... [eval.py:32] 评估 2 个样本
... [eval.py:138] 在线程模式下运行，使用 1 个线程！
100%|██████████████████████████████████████████| 2/2 [00:00<00:00,  3.35it/s]
... [record.py:320] 最终报告：{'accuracy': 1.0}。已记录到 /tmp/evallogs/<run_id>_gpt-3.5-turbo_arithmetic.jsonl
... [oaieval.py:170] 最终报告：
... [oaieval.py:172] accuracy: 1.0
... [record.py:309] 已将 6 行事件记录到 /tmp/evallogs/<run_id>_gpt-3.5-turbo_arithmetic.jsonl：insert_time=2.038ms
```
