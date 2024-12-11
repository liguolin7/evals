import json
from typing import List, Dict, Any
import numpy as np

def load_samples(jsonl_path: str) -> List[Dict[str, Any]]:
    """Load evaluation sample data"""
    samples = []
    with open(jsonl_path, 'r') as f:
        for line in f:
            samples.append(json.loads(line))
    return samples

def format_metrics_report(metrics: Dict[str, float]) -> str:
    """Format evaluation metrics report"""
    report = "Faithfulness Evaluation Report\n"
    report += "=" * 30 + "\n"
    
    for metric, score in metrics.items():
        report += f"{metric.replace('_', ' ').title()}: {score:.3f}\n"
    
    return report

def normalize_score(score: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Normalize score to specified range"""
    return np.clip(score, min_val, max_val)

def extract_key_points(text: str) -> List[str]:
    """Extract key points from text"""
    sentences = text.split('.')
    return [s.strip() for s in sentences if s.strip()]

def compare_key_points(source_points: List[str], target_points: List[str]) -> float:
    """Compare similarity between two sets of key points"""
    if not source_points or not target_points:
        return 0.0
    
    common_points = set(source_points) & set(target_points)
    return len(common_points) / max(len(source_points), len(target_points))
