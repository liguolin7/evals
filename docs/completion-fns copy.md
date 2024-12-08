# 完成函数

## 什么是完成函数
在 [run-evals.md](run-evals.md) 中，我们学习了如何使用 `oaieval` 命令对完成函数运行评估。完成函数是模型完成的泛化，其中"完成"是对提示的某种文本输出答案。例如，如果"谁在霍比特人中扮演精灵女孩？"是我们的提示，正确的完成是"Evangeline Lilly"。虽然我们可以直接测试模型是否生成"Evangeline Lilly"，但我们可以想象在回答之前在底层执行许多其他操作来提高我们回答这个问题的能力，比如让模型访问浏览器来查找答案。让这种底层操作在响应之前易于实现是构建完成函数的动机。

## 如何实现完成函数
完成函数需要实现一些使其在 Evals 中可用的接口。从本质上讲，它只是将输入标准化为文本字符串或[聊天对话](https://platform.openai.com/docs/guides/chat)，输出标准化为文本字符串列表。实现这个接口将允许您针对 Evals 中的任何评估运行您的完成函。

具体需要的接口在 [completion-fn-protocol.md](completion-fn-protocol.md) 中有详细描。

我们在 `evals/completion_fns` 中包含了一些示例实现。例如，[`LangChainLLMCompletionFn`](../evals/completion_fns/langchain_llm.py) 实现了一种从 [LangChain LLMs](https://python.langchain.com/en/latest/modules/models/llms/getting_started.html) 生成完成的方法。然后我们可以将这些完成函数与 `oaieval` 一起使用：
```
oaieval langchain/llm/flan-t5-xl test-match
```

## 注册完成函数
一旦您编写了完成函数，我们需要使该类对 `oaieval` CLI 可见。与注册评估类似，我们也在 `evals/registry/completion_fns` 中将完成函数注册为 `yaml` 文件。以下是我们的 langchain LLM 完成函数的注册：
```yaml
langchain/llm/flan-t5-xl:
  class: evals.completion_fns.langchain_llm:LangChainLLMCompletionFn
  args:
    llm: HuggingFaceHub
    llm_kwargs:
      repo_id: google/flan-t5-xl
```
以下是它的分解说明：
`langchain/llm/flan-t5-xl`：这是用于通过 `oaieval` 访问此完成函数的顶级键。
`class`：这是完成函数协议实现的路径。此类需要在您的 Python 环境中可导入。
`args`：这些是在实例化完成函数时传递给它的参数。


### 在 Evals 之外开发完成函数
可以使用 `--registry_path` 参数在不直接修改 `Evals` 中的注册表或代码的情况下注册完成函数。例如，假设我想使用位于 `~/my_project/` 中的 `MyCompletionFn`：
```
my_project
├── my_completion_fn.py
└── completion_fns
    └── my_completion_fn.yaml
```

如果 `my_project` 在 Python 环境中可导入（通过 PYTHONPATH 访问），我们可以将 `my_completion_fn.yaml` 结构化为：
```
my_completion_fn:
  class: my_project.my_completion_fn:MyCompletionFn
```
然后，我们可以使用以下命令调用 `oaieval`：
```
oaieval my_completion_fn test-match --registry_path ~/my_project
```
