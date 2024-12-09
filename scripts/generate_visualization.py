#!/usr/bin/env python3
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def create_model_comparison_chart(model_results: Dict[str, Dict[str, float]], output_path: str):
    """Create model comparison chart
    
    Args:
        model_results: Dictionary containing evaluation results for different models
        output_path: Output file path
    """
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(14, 7))
    
    metrics = ['factual_accuracy', 'logical_coherence', 'context_relevance',
              'interpretative_reasoning', 'information_completeness', 
              'hallucination_score', 'overall_faithfulness']
    
    x = np.arange(len(metrics))
    width = 0.25  # Reduced width to accommodate three bars
    
    # Set colors
    colors = ['#2ecc71', '#3498db', '#e74c3c']  # Green, Blue, Red
    
    # Create bars for each model
    for i, (model_name, results) in enumerate(model_results.items()):
        values = [results[metric] for metric in metrics]
        ax.bar(x + i * width, values, width, label=model_name, color=colors[i], alpha=0.8)
    
    # Set chart title and labels
    ax.set_title('Model Performance Comparison', fontsize=14, pad=20)
    ax.set_xlabel('Metrics', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    
    # Set x-axis labels
    ax.set_xticks(x + width)
    plt.xticks(x + width, metrics, rotation=45, ha='right')
    
    # Set legend
    ax.legend()
    
    # Set grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis range
    ax.set_ylim(0, 1.0)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save chart
    plt.savefig(output_path,
                bbox_inches='tight',
                dpi=300,
                facecolor='white',
                edgecolor='none')
    
    # Close figure
    plt.close()

def create_type_comparison_chart(gpt35_results: Dict[str, Dict[str, float]], 
                               gpt4_turbo_results: Dict[str, Dict[str, float]],
                               gpt4_results: Dict[str, Dict[str, float]], 
                               output_path: str):
    """Create type comparison chart
    
    Args:
        gpt35_results: Type evaluation results for GPT-3.5
        gpt4_turbo_results: Type evaluation results for GPT-4 Turbo
        gpt4_results: Type evaluation results for GPT-4
        output_path: Output file path
    """
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(15, 8))
    
    types = list(gpt35_results.keys())
    x = np.arange(len(types))
    width = 0.25  # Reduced width to accommodate three bars
    
    # Set colors
    colors = ['#2ecc71', '#3498db', '#e74c3c']  # Green, Blue, Red
    
    # Plot GPT-3.5 results
    gpt35_values = [gpt35_results[t]['overall_faithfulness'] for t in types]
    ax.bar(x - width, gpt35_values, width, label='GPT-3.5 Turbo', color=colors[0], alpha=0.8)
    
    # Plot GPT-4 Turbo results
    gpt4_turbo_values = [gpt4_turbo_results[t]['overall_faithfulness'] for t in types]
    ax.bar(x, gpt4_turbo_values, width, label='GPT-4 Turbo', color=colors[1], alpha=0.8)
    
    # Plot GPT-4 results
    gpt4_values = [gpt4_results[t]['overall_faithfulness'] for t in types]
    ax.bar(x + width, gpt4_values, width, label='GPT-4', color=colors[2], alpha=0.8)
    
    # Set chart title and labels
    ax.set_title('Model Performance Comparison by Sample Type', fontsize=14, pad=20)
    ax.set_xlabel('Sample Type', fontsize=12)
    ax.set_ylabel('Overall Faithfulness Score', fontsize=12)
    
    # Set x-axis labels
    ax.set_xticks(x)
    plt.xticks(x, [t.replace('_', ' ').title() for t in types], rotation=45, ha='right')
    
    # Set legend
    ax.legend()
    
    # Set grid
    ax.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Set y-axis range
    ax.set_ylim(0, 1.0)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save chart
    plt.savefig(output_path,
                bbox_inches='tight',
                dpi=300,
                facecolor='white',
                edgecolor='none')
    
    # Close figure
    plt.close()

def main():
    # Set input and output paths
    gpt35_base = "results/faithfulness_eval_20241209_024454/reports/report_20241209_024534"
    gpt4_turbo_base = "results/faithfulness_eval_20241209_024611/reports/report_20241209_024906"
    gpt4_base = "results/faithfulness_eval_20241209_025136/reports/report_20241209_025338"
    output_dir = "visualizations"
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Read final metrics data
    with open(os.path.join(gpt35_base, "final_metrics.json"), "r") as f:
        gpt35_final = json.load(f)
    with open(os.path.join(gpt4_turbo_base, "final_metrics.json"), "r") as f:
        gpt4_turbo_final = json.load(f)
    with open(os.path.join(gpt4_base, "final_metrics.json"), "r") as f:
        gpt4_final = json.load(f)
    
    # Prepare model comparison data
    model_results = {
        "GPT-3.5 Turbo": gpt35_final,
        "GPT-4 Turbo": gpt4_turbo_final,
        "GPT-4": gpt4_final
    }
    
    # Generate model comparison chart
    model_comparison_path = os.path.join(output_dir, "model_comparison.png")
    create_model_comparison_chart(model_results, model_comparison_path)
    print(f"Model comparison chart generated: {model_comparison_path}")
    
    # Read type metrics data
    with open(os.path.join(gpt35_base, "type_metrics.json"), "r") as f:
        gpt35_types = json.load(f)
    with open(os.path.join(gpt4_turbo_base, "type_metrics.json"), "r") as f:
        gpt4_turbo_types = json.load(f)
    with open(os.path.join(gpt4_base, "type_metrics.json"), "r") as f:
        gpt4_types = json.load(f)
    
    # Generate type comparison chart
    type_comparison_path = os.path.join(output_dir, "type_comparison.png")
    create_type_comparison_chart(gpt35_types, gpt4_turbo_types, gpt4_types, type_comparison_path)
    print(f"Type comparison chart generated: {type_comparison_path}")

if __name__ == "__main__":
    main() 