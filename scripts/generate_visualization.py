#!/usr/bin/env python3
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
import glob
import re
import argparse

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

def parse_log_file(log_path: str) -> Tuple[str, str]:
    """
    Parse model information and result path from log file
    
    Args:
        log_path: Path to log file
    
    Returns:
        Tuple containing (model_name, result_path)
    """
    model_name = None
    result_path = None
    
    with open(log_path, 'r') as f:
        for line in f:
            # Get model name
            if "Starting Faithfulness Evaluation - Model:" in line:
                model_match = re.search(r"Model: (.*?)$", line.strip())
                if model_match:
                    model = model_match.group(1)
                    if "gpt-4-turbo" in model.lower():
                        model_name = "GPT-4 Turbo"
                    elif "gpt-4" in model.lower():
                        model_name = "GPT-4"
                    elif "gpt-3.5" in model.lower() or "gpt35" in model.lower():
                        model_name = "GPT-3.5 Turbo"
            
            # Get report path
            if "Report Path:" in line:
                path_match = re.search(r"Report Path: (.*?)/report\.md", line.strip())
                if path_match:
                    result_path = path_match.group(1)
                    break
    
    return model_name, result_path

def get_model_name_from_id(model_id: str) -> str:
    """
    Convert model ID to display name
    
    Args:
        model_id: Model ID (e.g., gpt-3.5-turbo)
    
    Returns:
        Display name (e.g., GPT-3.5 Turbo)
    """
    model_id = model_id.lower()
    if "gpt-4-turbo" in model_id:
        return "GPT-4 Turbo"
    elif "gpt-4" in model_id:
        return "GPT-4"
    elif "gpt-3.5" in model_id or "gpt35" in model_id:
        return "GPT-3.5 Turbo"
    return model_id.upper()

def find_model_results(target_models: List[str] = None) -> List[Tuple[str, str]]:
    """
    Find model evaluation results from logs directory
    
    Args:
        target_models: List of target models to find, if None returns all models
    
    Returns:
        List of tuples containing (model_name, result_path)
    """
    results = []
    log_files = glob.glob("logs/faithfulness_eval_*.log")
    
    if not log_files:
        print("Warning: No log files found")
        return results
    
    # Convert target models to standardized names if specified
    target_model_names = None
    if target_models:
        target_model_names = [get_model_name_from_id(m) for m in target_models]
        
    for log_file in log_files:
        model_name, result_path = parse_log_file(log_file)
        if model_name and result_path:
            # Only process target models if specified
            if target_model_names and model_name not in target_model_names:
                continue
                
            # Check if result files exist
            if (os.path.exists(os.path.join(result_path, "final_metrics.json")) and 
                os.path.exists(os.path.join(result_path, "type_metrics.json"))):
                results.append((model_name, result_path))
            else:
                print(f"Warning: Result files not found: {result_path}")
        else:
            print(f"Warning: Could not parse information from log file: {log_file}")
    
    # Check if all target models were found
    if target_model_names:
        found_models = {r[0] for r in results}
        missing_models = set(target_model_names) - found_models
        if missing_models:
            print(f"Warning: No evaluation results found for the following models: {', '.join(missing_models)}")
    
    return results

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Generate visualization charts for model evaluation results')
    parser.add_argument('--models', nargs='+', help='List of models to compare (e.g., gpt-3.5-turbo gpt-4-turbo gpt-4)')
    args = parser.parse_args()
    
    # Find model results
    model_results_paths = find_model_results(args.models)
    
    if len(model_results_paths) < 1:
        print("No model results found. Please ensure:")
        print("1. Log files exist in the logs directory")
        print("2. Corresponding results exist in the results directory")
        return
    
    print(f"Found the following model results:")
    for model_name, path in model_results_paths:
        print(f"- {model_name}: {path}")
    
    output_dir = "visualizations"
    os.makedirs(output_dir, exist_ok=True)
    
    # Read metrics data for all models
    model_results = {}
    model_type_results = {}
    
    for model_name, result_path in model_results_paths:
        # Read final_metrics.json
        with open(os.path.join(result_path, "final_metrics.json"), "r") as f:
            model_results[model_name] = json.load(f)
        
        # Read type_metrics.json
        with open(os.path.join(result_path, "type_metrics.json"), "r") as f:
            model_type_results[model_name] = json.load(f)
    
    # Generate model comparison chart
    if len(model_results) > 0:
        model_comparison_path = os.path.join(output_dir, "model_comparison.png")
        create_model_comparison_chart(model_results, model_comparison_path)
        print(f"Model comparison chart generated: {model_comparison_path}")
    
    # Generate type comparison chart
    if len(model_type_results) >= 3:  # Ensure enough models for comparison
        gpt35_types = model_type_results.get("GPT-3.5 Turbo", {})
        gpt4_turbo_types = model_type_results.get("GPT-4 Turbo", {})
        gpt4_types = model_type_results.get("GPT-4", {})
        
        if gpt35_types and gpt4_turbo_types and gpt4_types:
            type_comparison_path = os.path.join(output_dir, "type_comparison.png")
            create_type_comparison_chart(gpt35_types, gpt4_turbo_types, gpt4_types, type_comparison_path)
            print(f"Type comparison chart generated: {type_comparison_path}")
    else:
        print("Not enough model data to generate type comparison chart (requires 3 models)")

if __name__ == "__main__":
    main() 