# 如何运行评估

我们提供了两个命令行界面(CLI)：`oaieval` 用于运行单个评估，`oaievalset` 用于运行一组评估。

## 运行评估

使用 `oaieval` 命令时，你需要提供要评估的完成函数以及要运行的评估。例如：
```sh
oaieval gpt-3.5-turbo test-match
```

有效的评估名称在 `evals/registry/evals` 下的 YAML 文件中指定，其对应的实现可以在 `evals/elsuite` 中找到。

在这个例子中，`gpt-3.5-turbo` 是一个 OpenAI 模型，我们使用 `OpenAIChatCompletionFn(model=gpt-3.5-turbo)` 动态实例化为一个完成函数。任何实现了 `CompletionFn` 协议的函数都可以通过 `oaieval` 运行。默认情况下，我们支持使用 OpenAI API 上可用的任何模型或 [`evals/registry/completion_fns`](../evals/registry/completion_fns/) 中可用的完成函数来调用 `oaieval`。我们一直在寻求添加更多的完成函数，我们鼓励你实现自己的函数以反映特定用例。

更多关于 `CompletionFn` 的详细信息可以在这里找到：[`completion-fns.md`](completion-fns.md)

这些 CLI 可以接受各种标志来修改其默认行为。例如：
- 如果你希望记录到 Snowflake 数据库（你已经按照 [README](../README.md) 中的描述设置好了），添加 `--no-local-run`。
- 默认情况下，本地或 Snowflake 的日志会写入 `tmp/evallogs`，你可以通过设置不同的 `--record_path` 来更改这一点。

你可以运行 `oaieval --help` 来查看完整的 CLI 选项列表。

## 运行评估集

```sh
oaievalset gpt-3.5-turbo test
```

同样，`oaievalset` 也需要一个模型名称和一个评估集名称，有效选项在 `evals/registry/eval_sets` 下的 YAML 文件中指定。

默认情况下，我们使用 10 个线程运行，每个线程在 40 秒后超时并重启。你可以配置这些参数，例如：

```sh
EVALS_THREADS=42 EVALS_THREAD_TIMEOUT=600 oaievalset gpt-3.5-turbo test
```

使用更多线程会使评估更快，不过要注意成本和你的[速率限制](https://platform.openai.com/docs/guides/rate-limits/overview)。如果你预计每个样本需要很长时间，例如数据包含会引发模型长回复的长提示，可能需要设置更高的线程超时时间。

如果你必须停止运行或运行崩溃，我们也考虑到了！`oaievalset` 会在 `/tmp/oaievalset/{model}.{eval_set}.progress.txt` 中记录已完成的评估。你只需重新运行命令就可以从中断处继续。如果你想从头开始运行评估集，删除这个进度文件即可。

不幸的是，你不能从单个评估的中间位置恢复。你必须从头开始，所以尽量保持单个评估的运行时间较短。

## 日志记录

默认情况下，`oaieval` [记录事件](/evals/record.py) 到本地的 JSONL 日志中，这些日志可以使用文本编辑器查看或通过编程方式分析。第三方工具如 [naimenz/logviz](https://github.com/naimenz/logviz) 可能有助于可视化日志，但我们不为其使用提供支持或保证。
