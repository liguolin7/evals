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

## Project Structure

```
project_root/
├── evals/
│   └── elsuite/
│       └── faithfulness/
│           ├── __init__.py
│           ├── eval.py           # Core evaluation implementation
│           ├── metrics.py        # Metric calculation functions
│           ├── report.py         # Report generation
│           ├── run.py           # CLI interface
│           ├── utils.py         # Utility functions
│           ├── run_tests.py     # Test runner
│           ├── test_eval.py     # Unit tests
│           └── test_report.py   # Report tests
├── scripts/
│   └── generate_visualization.py  # Visualization tools
├── requirements.txt              # Project dependencies
```

## Environment Setup

### Prerequisites
- Anaconda or Miniconda
- Python 3.9+
- PS: I use Apple Silicon Mac (M1) to run this project.

### Installation Steps

1. Clone the repository:
```bash
git clone <https://github.com/liguolin7/evals.git>
cd evals
```

2. Create and activate conda environment:
```bash
# Create new environment from environment.yml
conda env create -n evals -f environment.yml

# Activate the environment
conda activate evals

# Install SpaCy language model
python -m spacy download en_core_web_sm
```

3. Install additional dependencies if needed:
```bash
# Basic dependencies
pip install blobfile lz4 openai backoff pyyaml tiktoken

# Machine learning related
pip install transformers torch

# NLP related
pip install nltk
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet')"

# Data processing and visualization
pip install pandas matplotlib seaborn
```

4. Set up OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

1. Run a basic evaluation:
```bash
python -m evals.elsuite.faithfulness.run --model gpt-3.5-turbo
```
You can replace gpt-3.5-turbo with other model names, such as gpt-4 or gpt-4-turbo.

2. Generate visualization:
```bash
# Generate charts for all available models
python scripts/generate_visualization.py

# Or generate charts for specific models
python scripts/generate_visualization.py --models gpt-3.5-turbo gpt-4-turbo gpt-4
```
The script will automatically:
1. Search for evaluation results in the logs directory
2. Generate model comparison charts in the `visualizations` directory:
   - `model_comparison.png`: Overall performance comparison
   - `type_comparison.png`: Sample type comparison (requires exactly 3 models)

## Output Directory Structure

After running the evaluation, results will be organized in the following directories:

```
project_root/
├── logs/                          # Evaluation logs
│   └── faithfulness_eval_*.log    # Timestamped evaluation logs
│
├── results/                       # Detailed evaluation results
│   └── faithfulness_eval_*/       # Timestamped evaluation results
│       └── reports/               # Generated reports
│           └── report_*/          # Timestamped report directory
│               ├── final_metrics.json     # Overall evaluation metrics
│               ├── type_metrics.json      # Type-specific metrics
│               ├── sample_results.json    # Individual sample results
│               ├── report.md              # Detailed evaluation report
│               │
                ── overall_metrics_radar.png  # Overall metrics visualization
│               ├── type_comparison.png        # Sample type comparison
│               ├── metrics_heatmap.png        # Metrics correlation heatmap
│               ├── metrics_boxplot.png        # Metrics distribution
│               ├── metrics_trend.png          # Metrics trend analysis
│               ├── metrics_stacked_bar.png    # Metrics composition
│               │
│               └── *_radar.png               # Type-specific radar charts
│                   ├── scientific_explanation_radar.png
│                   ├── medical_advice_radar.png
│                   ├── technical_analysis_radar.png
│                   ├── historical_analysis_radar.png
│                   └── current_events_radar.png
│
└── visualizations/               # Generated model comparison charts
    ├── model_comparison.png     # Model performance comparison
    └── type_comparison.png      # Sample type performance comparison
```

### Logs Directory
- Contains detailed evaluation logs with timestamps
- Includes model responses, error messages, and evaluation progress
- Useful for debugging and tracking evaluation process

### Results Directory
- Organized by evaluation timestamp
- Contains detailed JSON files with evaluation metrics:
  * `final_metrics.json`: Overall performance metrics
  * `type_metrics.json`: Performance metrics by sample type
  * `sample_results.json`: Detailed results for each evaluated sample
- Includes comprehensive markdown report (`report.md`)
- Generates various visualization charts:
  * Overall performance visualizations
  * Type-specific radar charts
  * Metrics analysis charts (heatmap, boxplot, trend, etc.)

### Visualizations Directory
- Contains generated model comparison charts
- Provides comparative analysis between different models
- Updated when running `generate_visualization.py`

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
- Semantic relevance (40%)
- Key information coverage (30%)
- Topic consistency (30%)

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

## Dynamic Weight Adjustment

The framework automatically adjusts metric weights based on evaluation results:

1. When factual accuracy is low (< 0.5):
   - Factual accuracy weight increases to 35%
   - Hallucination score weight increases to 20%
   - Other metrics share the remaining 45%

2. When hallucination is severe (score < 0.5):
   - Hallucination score weight increases to 25%
   - Factual accuracy weight increases to 30%
   - Other metrics share the remaining 45%

## Usage Examples

### Basic Evaluation
```python
from evals.elsuite.faithfulness.eval import FaithfulnessEval
from evals.record import RecorderBase
from evals.completion_fns.openai import OpenAIChatCompletionFn

# Create completion function
completion_fn = OpenAIChatCompletionFn(model="gpt-3.5-turbo")

# Create evaluator instance
evaluator = FaithfulnessEval(
    completion_fns=[completion_fn],
    eval_registry_path="evals/registry/evals/faithfulness.yaml",
    samples_jsonl="evals/registry/data/faithfulness/samples.jsonl",
    report_dir="reports"
)

# Create recorder
recorder = RecorderBase()

# Run evaluation
results = evaluator.run(recorder)
print(f"Overall Faithfulness Score: {results['overall_faithfulness']:.4f}")
```

### Custom Sample Evaluation
```python
# Prepare a sample
sample = {
    "type": "scientific_explanation",
    "context": "Recent studies show that quantum entanglement allows instantaneous correlation between particles regardless of distance.",
    "query": "Explain quantum entanglement and its implications.",
    "reference": "Quantum entanglement is a phenomenon where particles remain connected so that the quantum state of each particle cannot be described independently."
}

# Evaluate single sample
result = evaluator.eval_sample(sample, random.Random(42))
if result:
    print("Sample Evaluation Results:")
    for metric, score in result["metrics"].items():
        print(f"{metric}: {score:.4f}")
```

### Batch Evaluation with Full Results
```python
import json

# Load custom samples
with open("your_samples.jsonl", "r") as f:
    samples = [json.loads(line) for line in f]

# Run evaluation with full results
results = evaluator.run(recorder, return_samples=True)

# Access different types of results
print("Final Metrics:", results["final_metrics"])
print("Type-specific Metrics:", results["type_metrics"])
print("Report Path:", results["report_path"])

# Access individual sample results
for sample_result in results["sample_results"]:
    print(f"\nSample Type: {sample_result['type']}")
    print(f"Response: {sample_result['response']}")
    print("Metrics:", sample_result["metrics"])
```

## Visualization Features

The framework provides two main visualization types:

1. Model Performance Comparison
   - Compares multiple models (GPT-3.5 Turbo, GPT-4 Turbo, GPT-4) across all evaluation metrics
   - Metrics include:
     * Factual Accuracy
     * Logical Coherence
     * Context Relevance
     * Interpretative Reasoning
     * Information Completeness
     * Hallucination Score
     * Overall Faithfulness

2. Sample Type Performance Analysis
   - Shows model performance across different types of samples:
     * Scientific Explanation
     * Technical Analysis
     * Medical Advice
     * Historical Analysis
     * Current Events
   - Compares overall faithfulness scores for each sample type
   - Helps identify model strengths and weaknesses in specific domains

## Report Generation

The framework generates comprehensive evaluation reports including:

1. Overall Evaluation Results
   - Main metrics with scores
   - Visualization analysis
   - Metrics radar charts
   - Metrics heatmaps
   - Distribution analysis

2. Type-Specific Results
   - Performance by sample type
   - Type-specific radar charts
   - Comparative analysis

3. Sample Analysis
   - Sample type distribution
   - Detailed sample evaluations
   - Performance breakdowns

## Contributing

We welcome contributions! Please see our contributing guidelines for more details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

This project is built upon the OpenAI Evals framework. We thank the OpenAI team for providing the foundation for this evaluation system.

## Contact

For questions and feedback, please open an issue in the repository.

