# LLM Faithfulness Evaluation Framework

This project is developed based on the OpenAI Evals framework, focusing on evaluating the faithfulness of Large Language Model (LLM) outputs beyond simple context matching.

## Overview

As Large Language Models become increasingly sophisticated, ensuring the faithfulness of their responses becomes crucial. This framework provides a comprehensive evaluation system that assesses multiple dimensions of response faithfulness:

- Factual Accuracy
- Logical Coherence
- Context Relevance
- Interpretative Reasoning
- Information Completeness
- Hallucination Detection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-faithfulness-eval.git
cd llm-faithfulness-eval
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

1. Run a basic evaluation:
```bash
python scripts/run_faithfulness_eval.py --model gpt-3.5-turbo
```

2. Run comprehensive tests:
```bash
python evals/elsuite/faithfulness/run_tests.py
```

3. Generate evaluation report:
```bash
python evals/elsuite/faithfulness/report.py --output_dir reports
```

## Evaluation Metrics

### 1. Factual Accuracy (Weight: 25%)
Measures how accurately the response reflects facts from the reference:
- Semantic similarity
- Key fact matching
- Numerical accuracy

### 2. Logical Coherence (Weight: 15%)
Evaluates the internal logical structure:
- Inter-sentence coherence
- Argumentation structure
- Logical connector usage

### 3. Context Relevance (Weight: 15%)
Assesses how well the response relates to the given context:
- Semantic relevance
- Key information coverage
- Topic consistency

### 4. Interpretative Reasoning (Weight: 15%)
Evaluates the quality of reasoning and interpretation:
- Reasoning word usage
- Process completeness
- Context-based conclusion

### 5. Information Completeness (Weight: 15%)
Checks if all key information is covered:
- Keyword coverage
- Information depth
- Response comprehensiveness

### 6. Hallucination Score (Weight: 15%)
Detects potential hallucinations:
- Context alignment
- Fact verification
- Source tracing

## Usage Examples

### Basic Evaluation
```python
from evals.elsuite.faithfulness.eval import FaithfulnessEval
from evals.record import RecorderBase
from evals.eval import RunSpec

# Create evaluator instance
evaluator = FaithfulnessEval(
    completion_fns=[completion_fn],
    eval_registry_path="evals/registry/evals/faithfulness.yaml",
    samples_jsonl="evals/registry/data/faithfulness/samples.jsonl"
)

# Run evaluation
results = evaluator.run(recorder)
print(f"Overall Faithfulness Score: {results['final_metrics']['overall_faithfulness']:.4f}")
```

### Custom Sample Evaluation
```python
sample = {
    "type": "scientific_explanation",
    "context": "Recent studies show that quantum entanglement allows instantaneous correlation between particles regardless of distance.",
    "query": "Explain quantum entanglement and its implications.",
    "reference": "Quantum entanglement is a phenomenon where particles remain connected so that the quantum state of each particle cannot be described independently."
}

# Evaluate single sample
result = evaluator.evaluate_sample(sample)
print(f"Sample Evaluation Results:")
for metric, score in result.items():
    print(f"{metric}: {score:.4f}")
```

### Batch Processing
```python
import json

# Load custom samples
with open("your_samples.jsonl", "r") as f:
    samples = [json.loads(line) for line in f]

# Batch evaluation
results = evaluator.evaluate_batch(samples)
print(f"Batch Evaluation Complete. Average Score: {results['average_score']:.4f}")
```

## Advanced Features

### 1. Dynamic Weight Adjustment
The framework automatically adjusts metric weights based on evaluation results:
- Increases factual accuracy weight when accuracy is low
- Enhances hallucination detection weight when hallucinations are detected

### 2. Domain-Specific Evaluation
Supports various domains including:
- Scientific Explanations
- Medical Advice
- Technical Analysis
- Historical Analysis
- Current Events
- Economic Analysis
- Environmental Impact
- Policy Analysis

### 3. Visualization and Reporting
Generate comprehensive reports with:
- Performance metrics
- Domain-specific analysis
- Trend visualization
- Error analysis

## Contributing

We welcome contributions! Please see our contributing guidelines for more details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is built upon the OpenAI Evals framework. We thank the OpenAI team for providing the foundation for this evaluation system.

## Contact

For questions and feedback, please open an issue in the repository. 