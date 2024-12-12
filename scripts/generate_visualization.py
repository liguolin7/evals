#!/usr/bin/env python3
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple
import glob
import re
import argparse

def create_model_comparison_chart(model_results: Dict[str, Dict[str, float]], output_path: str, model_order: List[str] = None):
    """Create model comparison chart
    
    Args:
        model_results: Dictionary containing evaluation results for different models
        output_path: Output file path
        model_order: List of model names in desired order
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
    
    # If model_order is provided, use it to sort the models
    if model_order:
        sorted_models = [(name, model_results[name]) for name in model_order if name in model_results]
    else:
        sorted_models = model_results.items()
    
    # Create bars for each model
    for i, (model_name, results) in enumerate(sorted_models):
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

def create_type_comparison_chart(model_type_results: Dict[str, Dict[str, Dict[str, float]]], 
                               output_path: str,
                               model_order: List[str] = None):
    """Create type comparison chart
    
    Args:
        model_type_results: Dictionary containing type results for different models
        output_path: Output file path
        model_order: List of model names in desired order
    """
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Get all unique types
    types = set()
    for model_results in model_type_results.values():
        types.update(model_results.keys())
    types = sorted(list(types))
    
    x = np.arange(len(types))
    width = 0.25  # Reduced width to accommodate three bars
    
    # Set colors
    colors = ['#2ecc71', '#3498db', '#e74c3c']  # Green, Blue, Red
    
    # If model_order is provided, use it to sort the models
    if model_order:
        sorted_models = [(name, model_type_results[name]) for name in model_order if name in model_type_results]
    else:
        sorted_models = model_type_results.items()
    
    # Plot bars for each model
    for i, (model_name, results) in enumerate(sorted_models):
        values = [results[t]['overall_faithfulness'] if t in results else 0 for t in types]
        ax.bar(x + i * width, values, width, label=model_name, color=colors[i], alpha=0.8)
    
    # Set chart title and labels
    ax.set_title('Model Performance Comparison by Sample Type', fontsize=14, pad=20)
    ax.set_xlabel('Sample Type', fontsize=12)
    ax.set_ylabel('Overall Faithfulness Score', fontsize=12)
    
    # Set x-axis labels
    ax.set_xticks(x + width)
    plt.xticks(x + width, [t.replace('_', ' ').title() for t in types], rotation=45, ha='right')
    
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
                path_match = re.search(r"Report Path: (.*?)(?:/report_[^/]+)?(?:/report\.md)?$", line.strip())
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
    
    # Convert target models to standardized names if specified
    target_model_names = None
    if target_models:
        target_model_names = [get_model_name_from_id(m) for m in target_models]
    
    # First, find all evaluation directories
    eval_dirs = glob.glob("results/faithfulness_eval_*")
    
    for eval_dir in eval_dirs:
        # Find report directories
        report_dirs = glob.glob(os.path.join(eval_dir, "reports/report_*"))
        
        for report_dir in report_dirs:
            # Look for final_metrics files
            metric_files = glob.glob(os.path.join(report_dir, "final_metrics_*.json"))
            
            for metric_file in metric_files:
                # Extract model name from filename
                model_id = os.path.basename(metric_file).replace("final_metrics_", "").replace(".json", "")
                model_name = get_model_name_from_id(model_id)
                
                # Skip if not in target models
                if target_model_names and model_name not in target_model_names:
                    continue
                
                # Check if type metrics file exists
                type_metrics_file = os.path.join(report_dir, f"type_metrics_{model_id}.json")
                if not os.path.exists(type_metrics_file):
                    print(f"Warning: Type metrics file not found for {model_name}: {type_metrics_file}")
                    continue
                
                results.append((model_name, report_dir))
                print(f"Found results for {model_name} in {report_dir}")
    
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
    
    # Store the original model order from command line
    model_order = [get_model_name_from_id(m) for m in args.models] if args.models else None
    
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
        # Get model id
        model_id = model_name.lower().replace(" ", "-")
        if model_id == "gpt-3.5-turbo":
            model_id = "gpt-3.5-turbo"
        elif model_id == "gpt-4-turbo":
            model_id = "gpt-4-turbo"
        elif model_id == "gpt-4":
            model_id = "gpt-4"
        
        # Read final_metrics.json
        metrics_file = os.path.join(result_path, f"final_metrics_{model_id}.json")
        try:
            with open(metrics_file, "r") as f:
                model_results[model_name] = json.load(f)
        except Exception as e:
            print(f"Error reading {metrics_file}: {str(e)}")
            continue
        
        # Read type_metrics.json
        type_metrics_file = os.path.join(result_path, f"type_metrics_{model_id}.json")
        try:
            with open(type_metrics_file, "r") as f:
                model_type_results[model_name] = json.load(f)
        except Exception as e:
            print(f"Error reading {type_metrics_file}: {str(e)}")
            continue
    
    # Generate model comparison chart
    if len(model_results) > 0:
        model_comparison_path = os.path.join(output_dir, "model_comparison.png")
        create_model_comparison_chart(model_results, model_comparison_path, model_order)
        print(f"Model comparison chart generated: {model_comparison_path}")
    
    # Generate type comparison chart
    if len(model_type_results) >= 3:
        type_comparison_path = os.path.join(output_dir, "type_comparison.png")
        create_type_comparison_chart(model_type_results, type_comparison_path, model_order)
        print(f"Type comparison chart generated: {type_comparison_path}")
    else:
        print("Not enough model data to generate type comparison chart (requires 3 models)")

if __name__ == "__main__":
    main() 