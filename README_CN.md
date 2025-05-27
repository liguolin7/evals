# LLM忠实度评估框架

基于OpenAI Evals框架开发的大语言模型（LLM）忠实度评估系统，专注于评估LLM输出的忠实度，超越简单的上下文匹配，提供多维度的响应质量评估。

## 🎯 项目概述

随着大语言模型变得越来越复杂，确保其响应的忠实度变得至关重要。本框架提供了一个全面的评估系统，从多个维度评估响应的忠实度：

### 核心评估维度
- **事实准确性** - 评估响应与参考答案的事实一致性
- **逻辑连贯性** - 分析响应内部的逻辑结构和连贯性
- **上下文相关性** - 评估响应与给定上下文的相关程度
- **解释推理** - 评估模型的推理和解释能力
- **信息完整性** - 检查是否涵盖了所有关键信息点
- **幻觉检测** - 识别和量化潜在的虚假信息

### 🌟 核心特性

- **智能权重调整** - 根据评估结果动态调整指标权重
- **类型特化评估** - 针对不同领域（科学、医疗、技术等）使用专门的评估策略
- **多模型支持** - 兼容OpenAI GPT系列及其他主流模型
- **丰富可视化** - 生成详细的雷达图、热力图、趋势分析等
- **完整报告系统** - 自动生成Markdown格式的详细评估报告

## 📁 项目结构

```
evals/
├── elsuite/faithfulness/         # 核心评估模块
│   ├── eval.py                  # 主评估逻辑
│   ├── metrics.py               # 指标计算算法
│   ├── report.py                # 报告生成器
│   ├── run.py                   # 命令行接口
│   └── utils.py                 # 工具函数
├── registry/
│   ├── data/faithfulness/       # 评估数据集
│   │   └── samples.jsonl        # 标准测试样本
│   └── evals/                   # 评估配置文件
├── scripts/
│   └── generate_visualization.py # 可视化工具
├── results/                     # 评估结果存储
├── logs/                        # 评估日志
└── visualizations/              # 生成的图表
```

## 🚀 快速开始

### 环境要求
- **操作系统**: macOS (Apple Silicon优化) / Linux / Windows
- **Python**: 3.9+
- **内存**: 推荐16GB+
- **依赖管理**: Anaconda/Miniconda

### 安装步骤

1. **克隆仓库**
```bash
git clone https://github.com/liguolin7/evals.git
cd evals
```

2. **创建conda环境**
```bash
# 从配置文件创建环境
conda env create -n evals -f environment.yml

# 激活环境
conda activate evals

# 安装SpaCy语言模型
python -m spacy download en_core_web_sm
```

3. **安装额外依赖**（如需要）
```bash
# 基础依赖
pip install blobfile lz4 openai backoff pyyaml tiktoken

# 机器学习相关
pip install transformers torch

# NLP处理
pip install nltk
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# 数据处理和可视化
pip install pandas matplotlib seaborn
```

4. **配置API密钥**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 基础使用

1. **运行标准评估**
```bash
# 使用GPT-3.5 Turbo
python -m evals.elsuite.faithfulness.run --model gpt-3.5-turbo

# 使用GPT-4
python -m evals.elsuite.faithfulness.run --model gpt-4

# 使用GPT-4 Turbo
python -m evals.elsuite.faithfulness.run --model gpt-4-turbo
```

2. **生成可视化图表**
```bash
# 为所有可用模型生成图表
python scripts/generate_visualization.py

# 为特定模型生成图表
python scripts/generate_visualization.py --models gpt-3.5-turbo gpt-4-turbo gpt-4
```

## 📊 评估指标详解

### 1. 事实准确性 (权重: 25%)
评估响应与参考答案的事实一致性
- **语义相似度**: 使用sentence-transformers计算语义相似性
- **关键事实匹配**: 识别和匹配关键事实点
- **数值准确性**: 验证数字和统计数据的准确性

### 2. 逻辑连贯性 (权重: 15%)
评估响应内部的逻辑结构
- **句间连贯性**: 分析相邻句子的逻辑关联
- **论证结构**: 评估论证的完整性和合理性
- **逻辑连接词**: 检查逻辑连接词的使用

### 3. 上下文相关性 (权重: 15%)
评估响应与给定上下文的相关程度
- **语义相关性** (40%): 计算响应与上下文的语义相似度
- **关键信息覆盖** (30%): 检查是否涵盖上下文中的关键信息
- **主题一致性** (30%): 评估主题的一致性

### 4. 解释推理 (权重: 15%)
评估推理和解释的质量
- **推理词汇使用**: 检查推理关键词的使用频率
- **推理过程完整性**: 评估推理步骤的完整性
- **基于上下文的结论**: 验证结论是否基于给定上下文

### 5. 信息完整性 (权重: 15%)
检查是否涵盖所有关键信息
- **关键词覆盖**: 计算关键词的覆盖率
- **信息深度**: 比较响应与参考答案的信息深度
- **响应全面性**: 评估响应的全面程度

### 6. 幻觉检测 (权重: 15%)
检测潜在的虚假信息
- **上下文对齐**: 验证信息是否与上下文一致
- **事实验证**: 检查事实的准确性
- **来源追踪**: 验证信息来源的可靠性

## ⚖️ 动态权重调整

框架会根据评估结果自动调整指标权重：

### 场景1: 事实准确性较低 (< 0.5)
- 事实准确性权重 → 35%
- 幻觉检测权重 → 20%
- 其他指标平分剩余45%

### 场景2: 严重幻觉问题 (< 0.5)
- 幻觉检测权重 → 25%
- 事实准确性权重 → 30%
- 其他指标平分剩余45%

## 📈 输出结果结构

评估完成后，结果将按以下结构组织：

```
project_root/
├── logs/                          # 评估日志
│   └── faithfulness_eval_*.log    # 带时间戳的评估日志
│
├── results/                       # 详细评估结果
│   └── faithfulness_eval_*/       # 带时间戳的评估结果
│       └── reports/               # 生成的报告
│           └── report_*/          # 带时间戳的报告目录
│               ├── final_metrics.json         # 总体评估指标
│               ├── type_metrics.json          # 类型特定指标
│               ├── sample_results.json        # 单个样本结果
│               ├── report.md                  # 详细评估报告
│               ├── overall_metrics_radar.png  # 总体指标雷达图
│               ├── type_comparison.png        # 样本类型对比
│               ├── metrics_heatmap.png        # 指标相关性热力图
│               ├── metrics_boxplot.png        # 指标分布箱线图
│               ├── metrics_trend.png          # 指标趋势分析
│               ├── metrics_stacked_bar.png    # 指标组成堆叠图
│               └── [type]_radar.png          # 各类型专门雷达图
│
└── visualizations/               # 模型对比图表
    ├── model_comparison.png     # 模型性能对比
    └── type_comparison.png      # 样本类型性能对比
```

## 💻 编程接口使用

### 基础评估示例
```python
from evals.elsuite.faithfulness.eval import FaithfulnessEval
from evals.record import RecorderBase
from evals.completion_fns.openai import OpenAIChatCompletionFn

# 创建完成函数
completion_fn = OpenAIChatCompletionFn(model="gpt-3.5-turbo")

# 创建评估器实例
evaluator = FaithfulnessEval(
    completion_fns=[completion_fn],
    eval_registry_path="evals/registry/evals/faithfulness.yaml",
    samples_jsonl="evals/registry/data/faithfulness/samples.jsonl",
    report_dir="reports"
)

# 创建记录器
recorder = RecorderBase()

# 运行评估
results = evaluator.run(recorder)
print(f"总体忠实度分数: {results['overall_faithfulness']:.4f}")
```

### 自定义样本评估
```python
# 准备样本
sample = {
    "type": "scientific_explanation",
    "context": "最近的研究表明，量子纠缠允许粒子之间无论距离多远都能保持瞬时关联。",
    "query": "解释量子纠缠的概念及其意义。",
    "reference": "量子纠缠是一种现象，其中两个或多个粒子以某种方式连接，使得每个粒子的量子态不能独立描述。"
}

# 评估单个样本
result = evaluator.eval_sample(sample, random.Random(42))
if result:
    print("样本评估结果:")
    for metric, score in result["metrics"].items():
        print(f"{metric}: {score:.4f}")
```

### 批量评估与完整结果
```python
import json

# 加载自定义样本
with open("your_samples.jsonl", "r") as f:
    samples = [json.loads(line) for line in f]

# 运行评估并获取完整结果
results = evaluator.run(recorder, return_samples=True)

# 访问不同类型的结果
print("最终指标:", results["final_metrics"])
print("类型特定指标:", results["type_metrics"])
print("报告路径:", results["report_path"])

# 访问单个样本结果
for sample_result in results["sample_results"]:
    print(f"\n样本类型: {sample_result['type']}")
    print(f"响应: {sample_result['response']}")
    print("指标:", sample_result["metrics"])
```

## 📊 可视化功能

框架提供两种主要的可视化类型：

### 1. 模型性能对比
- 对比多个模型（GPT-3.5 Turbo、GPT-4 Turbo、GPT-4）在所有评估指标上的表现
- 包含的指标：
  * 事实准确性
  * 逻辑连贯性
  * 上下文相关性
  * 解释推理
  * 信息完整性
  * 幻觉检测
  * 总体忠实度

### 2. 样本类型性能分析
- 展示模型在不同类型样本上的表现：
  * 科学解释
  * 技术分析
  * 医疗建议
  * 历史分析
  * 时事分析
- 对比各样本类型的总体忠实度分数
- 帮助识别模型在特定领域的优势和劣势

## 📋 评估样本类型

当前支持的样本类型及其特点：

### 科学解释 (Scientific Explanation)
- **特点**: 需要准确的科学知识和清晰的解释
- **权重调整**: 提高事实准确性权重(35%)
- **示例**: 量子纠缠、CRISPR基因编辑

### 技术分析 (Technical Analysis)
- **特点**: 需要技术深度和实用性分析
- **权重调整**: 平衡逻辑连贯性和解释推理
- **示例**: 编程语言特性、云计算平台

### 医疗建议 (Medical Advice)
- **特点**: 要求极高的准确性和安全性
- **权重调整**: 最高事实准确性权重(35%)
- **示例**: 运动建议、睡眠研究

### 历史分析 (Historical Analysis)
- **特点**: 需要准确的历史知识和分析能力
- **权重调整**: 平衡事实准确性和逻辑连贯性
- **示例**: 大萧条分析、工业革命影响

### 时事分析 (Current Events)
- **特点**: 需要及时性和准确性
- **权重调整**: 标准权重配置
- **示例**: 半导体短缺、气候变化

## 🔧 高级配置

### 自定义权重配置
```python
# 自定义类型权重
custom_weights = {
    "factual_accuracy": 0.4,
    "logical_coherence": 0.2,
    "context_relevance": 0.1,
    "interpretative_reasoning": 0.1,
    "information_completeness": 0.1,
    "hallucination_score": 0.1
}

evaluator = FaithfulnessEval(
    completion_fns=[completion_fn],
    eval_registry_path="evals/registry/evals/faithfulness.yaml",
    samples_jsonl="evals/registry/data/faithfulness/samples.jsonl",
    custom_weights=custom_weights
)
```

### 性能优化建议
- **批量处理**: 对大量样本使用批量评估
- **缓存机制**: 启用模型嵌入缓存
- **并行处理**: 使用多进程加速评估
- **资源监控**: 监控内存和GPU使用情况

## 🤝 贡献指南

我们欢迎社区贡献！请参考以下指南：

### 贡献类型
- **新评估指标**: 添加新的评估维度
- **样本数据**: 贡献高质量的评估样本
- **性能优化**: 改进算法效率
- **文档改进**: 完善文档和示例
- **Bug修复**: 报告和修复问题

### 开发流程
1. Fork项目仓库
2. 创建功能分支
3. 编写测试用例
4. 提交Pull Request
5. 代码审查和合并

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE.md)文件。

## 🙏 致谢

本项目基于OpenAI Evals框架构建。感谢OpenAI团队为评估系统提供的基础框架。

## 📞 联系方式

- **问题反馈**: 请在GitHub仓库中创建Issue
- **功能建议**: 欢迎通过Issue或Discussion提出
- **技术交流**: 欢迎参与项目讨论

## 🔗 相关链接

- [OpenAI Evals](https://github.com/openai/evals) - 基础评估框架
- [Sentence Transformers](https://www.sbert.net/) - 文本嵌入模型
- [NLTK](https://www.nltk.org/) - 自然语言处理工具包

---

**注意**: 本项目专为研究和评估目的设计，请确保在使用时遵循相关的API使用条款和数据隐私规定。 