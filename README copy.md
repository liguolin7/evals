# OpenAI Evals

Evals提供了一个用于评估大型语言模型(LLMs)或基于LLMs构建的系统的框架。我们提供了一个现有的评估注册表，用于测试OpenAI模型的不同维度，并且您可以编写自己的自定义评估用于您关心的用例。您还可以使用自己的数据构建私有评估，这些评估代表了您工作流程中常见的LLMs模式，而无需公开暴露任何数据。

如果您正在使用LLMs进行开发，创建高质量的评估是您能做的最有影响力的事情之一。没有评估，要理解不同模型版本如何影响您的用例可能会非常困难且耗时。用[OpenAI总裁Greg Brockman](https://twitter.com/gdb/status/1733553161884127435)的话说：

<img width="596" alt="https://x.com/gdb/status/1733553161884127435?s=20" src="https://github.com/openai/evals/assets/35577566/ce7840ff-43a8-4d88-bb2f-6b207410333b">

## 设置

要运行评估，您需要设置并指定您的[OpenAI API密钥](https://platform.openai.com/account/api-keys)。获取API密钥后，使用[`OPENAI_API_KEY`环境变量](https://platform.openai.com/docs/quickstart/step-2-setup-your-api-key)指定它。运行评估时，请注意使用API相关的[成本](https://openai.com/pricing)。您还可以使用[Weights & Biases](https://wandb.ai/wandb_fc/openai-evals/reports/OpenAI-Evals-Demo-Using-W-B-Prompts-to-Run-Evaluations--Vmlldzo0MTI4ODA3)运行和创建评估。

**最低要求版本：Python 3.9**

### 下载评估

我们的评估注册表使用[Git-LFS](https://git-lfs.com/)存储。一旦您下载并安装了LFS，您可以从您的本地evals仓库中获取评估：
```sh
cd evals
git lfs fetch --all
git lfs pull
```

这将填充`evals/registry/data`下的所有指针文件。

如果您只想获取特定评估的数据，可以通过以下方式实现：
```sh
git lfs fetch --include=evals/registry/data/${your eval}
git lfs pull
```

### 创建评估

如果您要创建评估，我们建议直接从GitHub克隆此仓库，并使用以下命令安装要求：

```sh
pip install -e .
```

使用`-e`，您对评估所做的更改将立即生效，无需重新安装。

可选地，您可以通过以下命令安装预提交的格式化工具：

```sh
pip install -e .[formatters]
```

然后运行`pre-commit install`将pre-commit安装到您的git钩子中。pre-commit现在将在每次提交时运行。

如果您想手动在仓库上运行所有pre-commit钩子，运行`pre-commit run --all-files`。要运行单个钩子，使用`pre-commit run <hook_id>`。

## 运行评估

如果您不想贡献新的评估，而只是想在本地运行它们，您可以通过pip安装evals包：

```sh
pip install evals
```

您可以在[`run-evals.md`](docs/run-evals.md)中找到运行现有评估的完整说明，在[`eval-templates.md`](docs/eval-templates.md)中找到我们现有的评估模板。对于更高级的用例，如提示链或工具使用代理，您可以使用我们的[完成函数协议](docs/completion-fns.md)。

我们提供了将评估结果记录到Snowflake数据库的选项，如果您有数据库或希望设置一个。对于此选项，您还需要指定`SNOWFLAKE_ACCOUNT`、`SNOWFLAKE_DATABASE`、`SNOWFLAKE_USERNAME`和`SNOWFLAKE_PASSWORD`环境变量。

## 编写评估

我们建议从以下方面开始：

- 了解构建评估的过程：[`build-eval.md`](docs/build-eval.md)
- 探索实现自定义评估逻辑的示例：[`custom-eval.md`](docs/custom-eval.md)
- 编写您自己的完成函数：[`completion-fns.md`](docs/completion-fns.md)
- 查看我们的评估编写入门指南：[OpenAI Evals入门](https://cookbook.openai.com/examples/evaluation/getting_started_with_openai_evals)

请注意，我们目前不接受带有自定义代码的评估！虽然我们暂时要求您不要提交此类评估，但您仍然可以使用自定义模型评分YAML文件提交模型评分评估。

如果您认为您有一个有趣的评估，请提交包含您贡献的拉取请求。OpenAI员工在考虑改进即将推出的模型时会积极审查这些评估。

## 常见问题

您有从头到尾构建评估的示例吗？

- 是的！这些在`examples`文件夹中。我们建议您也阅读[`build-eval.md`](docs/build-eval.md)，以便更深入地理解这些示例中发生的事情。

您有以多种不同方式实现的评估示例吗？

- 是的！特别是，请参见`evals/registry/evals/coqa.yaml`。我们已经为各种评估模板实现了[CoQA](https://stanfordnlp.github.io/coqa/)数据集的小子集，以帮助说明差异。

当我运行评估时，它有时在最后（最终报告之后）会挂起。这是怎么回事？

- 这是一个已知问题，但您应该能够安全地中断它，评估应该在之后立即完成。

代码太多了，我只想快速启动一个评估。帮帮我？或者，

我是一位世界级的提示工程师。我选择不编码。我如何贡献我的智慧？

- 如果您遵循现有的[评估模板](docs/eval-templates.md)来构建基本或模型评分评估，您根本不需要编写任何评估代码！只需以JSON格式提供您的数据并在YAML中指定您的评估参数。[build-eval.md](docs/build-eval.md)将指导您完成这些步骤，您可以结合`examples`文件夹中的Jupyter笔记本来帮助您快速入门。但请记住，一个好的评估inevitably需要仔细的思考和严格的实验！

## 免责声明

通过贡献评估，您同意使您的评估逻辑和数据遵循与本仓库相同的MIT许可证。您必须拥有上传评估中使用的任何数据的充分权利。OpenAI保留在未来产品服务改进中使用这些数据的权利。对OpenAI评估的贡献将受我们通常的使用政策约束：https://platform.openai.com/docs/usage-policies。
