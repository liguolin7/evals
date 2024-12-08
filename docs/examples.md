# Usage Examples

This document provides detailed examples of using the LLM Faithfulness Evaluation Framework in various scenarios.

## Basic Usage Examples

### 1. Simple Evaluation

```python
from evals.elsuite.faithfulness.eval import FaithfulnessEval
from evals.record import RecorderBase

# Initialize evaluator
evaluator = FaithfulnessEval(
    completion_fns=[completion_fn],
    eval_registry_path="evals/registry/evals/faithfulness.yaml",
    samples_jsonl="evals/registry/data/faithfulness/samples.jsonl"
)

# Run evaluation
results = evaluator.run(recorder)
print(f"Overall Score: {results['final_metrics']['overall_faithfulness']:.4f}")
```

### 2. Custom Sample Evaluation

```python
# Define a custom sample
sample = {
    "type": "scientific_explanation",
    "context": "The James Webb Space Telescope has detected water vapor and methane in the atmosphere of exoplanet K2-18b.",
    "query": "What has been discovered about K2-18b?",
    "reference": "The James Webb Space Telescope has found water vapor and methane in K2-18b's atmosphere, suggesting potential habitability conditions."
}

# Evaluate single sample
result = evaluator.evaluate_sample(sample)

# Print detailed results
for metric, score in result.items():
    print(f"{metric}: {score:.4f}")
```

## Advanced Usage Examples

### 1. Domain-Specific Evaluation

```python
# Medical domain evaluation
medical_samples = [
    {
        "type": "medical_advice",
        "context": "Recent studies show that regular exercise reduces the risk of cardiovascular disease by 30%.",
        "query": "What are the benefits of regular exercise for heart health?",
        "reference": "Regular exercise significantly reduces cardiovascular disease risk by 30% through improved heart function and circulation."
    },
    # Add more medical samples...
]

# Run domain-specific evaluation
medical_results = evaluator.evaluate_batch(medical_samples)
print("\nMedical Domain Results:")
print(f"Average Score: {medical_results['average_score']:.4f}")
```

### 2. Comparative Analysis

```python
def compare_models(samples, models):
    results = {}
    for model in models:
        evaluator = FaithfulnessEval(
            completion_fns=[model],
            eval_registry_path="evals/registry/evals/faithfulness.yaml",
            samples_jsonl="evals/registry/data/faithfulness/samples.jsonl"
        )
        results[model.name] = evaluator.evaluate_batch(samples)
    
    return results

# Compare different models
models = [model1, model2, model3]
comparison_results = compare_models(test_samples, models)

# Print comparison
for model_name, result in comparison_results.items():
    print(f"\n{model_name}:")
    print(f"Overall Score: {result['average_score']:.4f}")
```

### 3. Custom Metric Weights

```python
# Define custom weights
custom_weights = {
    "factual_accuracy": 0.3,
    "logical_coherence": 0.2,
    "context_relevance": 0.2,
    "interpretative_reasoning": 0.1,
    "information_completeness": 0.1,
    "hallucination_score": 0.1
}

# Evaluate with custom weights
results = evaluator.run(recorder, weights=custom_weights)
```

## Real-World Applications

### 1. News Article Fact-Checking

```python
news_sample = {
    "type": "current_events",
    "context": """
    Original Article: The global average temperature in 2023 reached 1.1°C above pre-industrial levels, 
    with Arctic regions warming at twice the global rate. Climate scientists warn of potential tipping points.
    """,
    "query": "Summarize the key points about global warming in 2023.",
    "reference": "In 2023, global temperatures rose to 1.1°C above pre-industrial levels, with Arctic warming occurring at double the global rate."
}

# Evaluate news article
news_result = evaluator.evaluate_sample(news_sample)
print("\nNews Article Evaluation:")
print(f"Factual Accuracy: {news_result['factual_accuracy']:.4f}")
print(f"Hallucination Score: {news_result['hallucination_score']:.4f}")
```

### 2. Technical Documentation Review

```python
tech_sample = {
    "type": "technical_analysis",
    "context": """
    The new API uses OAuth 2.0 for authentication and supports REST endpoints for CRUD operations. 
    Response time has improved by 40% compared to the previous version.
    """,
    "query": "Describe the key features of the new API.",
    "reference": "The API implements OAuth 2.0 authentication and REST endpoints for CRUD operations, achieving 40% faster response times."
}

# Evaluate technical documentation
tech_result = evaluator.evaluate_sample(tech_sample)
print("\nTechnical Documentation Evaluation:")
print(f"Information Completeness: {tech_result['information_completeness']:.4f}")
print(f"Logical Coherence: {tech_result['logical_coherence']:.4f}")
```

### 3. Research Paper Analysis

```python
research_sample = {
    "type": "scientific_explanation",
    "context": """
    Research findings: CRISPR-Cas9 gene editing showed 90% efficiency in correcting the mutation 
    responsible for sickle cell disease in laboratory trials. Side effects were minimal.
    """,
    "query": "What are the results of the CRISPR-Cas9 trials for sickle cell disease?",
    "reference": "CRISPR-Cas9 demonstrated 90% efficiency in correcting sickle cell disease mutations with minimal side effects in lab trials."
}

# Evaluate research paper
research_result = evaluator.evaluate_sample(research_sample)
print("\nResearch Paper Evaluation:")
print(f"Factual Accuracy: {research_result['factual_accuracy']:.4f}")
print(f"Context Relevance: {research_result['context_relevance']:.4f}")
```

## Batch Processing Examples

### 1. Large-Scale Evaluation

```python
def process_large_dataset(file_path, batch_size=32):
    # Load samples
    with open(file_path, 'r') as f:
        samples = [json.loads(line) for line in f]
    
    # Process in batches
    total_samples = len(samples)
    processed = 0
    results = []
    
    for i in range(0, total_samples, batch_size):
        batch = samples[i:i + batch_size]
        batch_results = evaluator.evaluate_batch(batch)
        results.extend(batch_results)
        
        processed += len(batch)
        print(f"Processed {processed}/{total_samples} samples")
    
    return results

# Run large-scale evaluation
results = process_large_dataset("large_dataset.jsonl")
```

### 2. Continuous Monitoring

```python
def monitor_model_performance(interval_hours=24):
    while True:
        # Run evaluation
        results = evaluator.run(recorder)
        
        # Log results
        log_results(results)
        
        # Alert if scores drop below threshold
        if results['final_metrics']['overall_faithfulness'] < 0.7:
            send_alert("Model performance degradation detected!")
        
        # Wait for next evaluation
        time.sleep(interval_hours * 3600)

# Start monitoring
monitor_model_performance()
```

## Visualization Examples

### 1. Performance Dashboard

```python
def create_dashboard(results):
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Create metrics visualization
    plt.figure(figsize=(12, 6))
    metrics = results['final_metrics']
    sns.barplot(x=list(metrics.keys()), y=list(metrics.values()))
    plt.title("Faithfulness Metrics Overview")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("metrics_overview.png")
    
    # Create domain-specific analysis
    plt.figure(figsize=(12, 6))
    domain_scores = results['type_metrics']
    sns.heatmap(pd.DataFrame(domain_scores), annot=True, cmap='YlOrRd')
    plt.title("Domain-Specific Performance")
    plt.tight_layout()
    plt.savefig("domain_analysis.png")

# Generate visualizations
create_dashboard(evaluation_results)
``` 