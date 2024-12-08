### 完成函数协议

以下是实现完成函数协议所需的接口。任何实现了这个接口的代码都可以在 `oaieval` 中使用。

参考实现：
- [OpenAICompletionFn](../evals/completion_fns/openai.py)
- [LangChainLLMCompletionFn](../evals/completion_fns/langchain_llm.py)

#### CompletionFn
完成函数应该实现 `CompletionFn` 接口：
```python
class CompletionFn(Protocol):
    def __call__(
        self,
        prompt: Union[str, list[dict[str, str]]],
        **kwargs,
    ) -> CompletionResult:
```

我们接收一个 `prompt` 参数，它代表评估中的单个样本。这些提示可以表示为文本字符串或[OpenAI 聊天格式](https://platform.openai.com/docs/guides/chat/introduction)的消息列表。为了与现有的评估一起工作，完成函数实现需要处理这两种类型的输入，但如果您的程序更喜欢文本字符串输入，我们提供了辅助功能将聊天格式的消息转换为文本字符串：
```python
from evals.prompt.base import CompletionPrompt

# chat_prompt: list[dict[str, str]] -> text_prompt: str
text_prompt = CompletionPrompt(chat_prompt).to_formatted_prompt()
```

#### CompletionResult
完成函数应该返回一个实现了 `CompletionResult` 接口的对象：
```python
class CompletionResult(ABC):
    @abstractmethod
    def get_completions(self) -> list[str]:
        pass
```
`get_completions` 方法返回一个字符串完成列表。每个元素都应该被视为一个唯一的完成（在大多数情况下，这将是一个长度为 1 的列表）。

#### 使用您的 CompletionFn
这就是实现一个可以与我们现有评估一起工作的完成函数所需的全部内容，让您能够更轻松地在任务上评估您的端到端逻辑。

查看 [completion-fns.md](completion-fns.md) 了解如何注册您的完成函数并与 `oaieval` 一起使用。
