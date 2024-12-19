import json
import os
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
import numpy as np

logger = logging.getLogger(__name__)

class FaithfulnessReport:
    """Faithfulness Evaluation Report Generator"""
    
    def __init__(self, output_dir: str = "reports", model_name: str = None):
        """Initialize report generator
        
        Args:
            output_dir: Output directory for reports
            model_name: Name of the model being evaluated
        """
        self.output_dir = output_dir
        self.model_name = model_name
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_report(self, 
                       final_metrics: Dict[str, float],
                       type_metrics: Dict[str, Dict[str, float]],
                       sample_results: List[Dict[str, Any]]) -> str:
        """Generate evaluation report
        
        Args:
            final_metrics: Overall evaluation metrics
            type_metrics: Type-specific evaluation metrics
            sample_results: Sample evaluation results
            
        Returns:
            str: Report file path
        """
        # Generate report timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Add model name to report directory if provided
        report_dir_name = f"report_{timestamp}"
        if self.model_name:
            report_dir_name = f"report_{timestamp}_{self.model_name}"
            
        report_dir = os.path.join(self.output_dir, report_dir_name)
        os.makedirs(report_dir, exist_ok=True)
        
        # Generate report content
        report_content = self._generate_report_content(final_metrics, type_metrics, sample_results)
        
        # Generate visualizations
        self._generate_visualizations(final_metrics, type_metrics, report_dir)
        
        # Save report with model name suffix
        report_name = "report.md"
        if self.model_name:
            report_name = f"report_{self.model_name}.md"
        report_path = os.path.join(report_dir, report_name)
        
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        # Save raw data with model name
        self._save_raw_data(final_metrics, type_metrics, sample_results, report_dir)
        
        return report_path
    
    def _generate_report_content(self,
                               final_metrics: Dict[str, float],
                               type_metrics: Dict[str, Dict[str, float]],
                               sample_results: List[Dict[str, Any]]) -> str:
        """Generate report content"""
        # Define suffix for file names
        suffix = f"_{self.model_name}" if self.model_name else ""
        
        content = []
        
        # 1. Report title
        content.append("# Faithfulness Evaluation Report")
        content.append(f"\nGeneration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 2. Overall evaluation results
        content.append("## 1. Overall Evaluation Results")
        content.append("\n### 1.1 Main Metrics")
        content.append("| Metric | Score |")
        content.append("|--------|--------|")
        for metric in ["factual_accuracy", "logical_coherence", "context_relevance", 
                      "interpretative_reasoning", "information_completeness", "hallucination_score"]:
            if metric in final_metrics:
                content.append(f"| {metric} | {final_metrics[metric]:.4f} |")
        
        # Add visualization references
        content.append("\n### 1.2 Visualization Analysis")
        content.append("\n#### 1.2.1 Overall Metrics Radar")
        content.append(f"![Overall Metrics Radar](overall_metrics_radar{suffix}.png)")
        
        content.append("\n#### 1.2.2 Metrics Heatmap")
        content.append(f"![Metrics Heatmap](metrics_heatmap{suffix}.png)")
        
        content.append("\n#### 1.2.3 Metrics Distribution")
        content.append(f"![Metrics Boxplot](metrics_boxplot{suffix}.png)")
        
        content.append("\n#### 1.2.4 Metrics Trend")
        content.append(f"![Metrics Trend](metrics_trend{suffix}.png)")
        
        content.append("\n#### 1.2.5 Metrics Composition")
        content.append(f"![Metrics Stacked Bar](metrics_stacked_bar{suffix}.png)")
            
        # 3. Type-specific evaluation results
        content.append("\n## 2. Type-Specific Evaluation Results")
        for sample_type, metrics in type_metrics.items():
            content.append(f"\n### 2.{len(content)} {sample_type}")
            content.append("| Metric | Score |")
            content.append("|--------|--------|")
            for metric in ["factual_accuracy", "logical_coherence", "context_relevance", 
                         "interpretative_reasoning", "information_completeness", "hallucination_score"]:
                if metric in metrics:
                    content.append(f"| {metric} | {metrics[metric]:.4f} |")
            content.append(f"\n![{sample_type} Radar]({sample_type}_radar{suffix}.png)")
                
        # 4. Sample analysis
        content.append("\n## 3. Sample Analysis")
        content.append(f"\nTotal Samples: {len(sample_results)}")
        
        # Count samples by type
        type_counts = {}
        for result in sample_results:
            sample_type = result["type"]
            type_counts[sample_type] = type_counts.get(sample_type, 0) + 1
            
        content.append("\n### 3.1 Sample Type Distribution")
        content.append("| Type | Count | Percentage |")
        content.append("|------|--------|------------|")
        for sample_type, count in type_counts.items():
            percentage = count / len(sample_results) * 100
            content.append(f"| {sample_type} | {count} | {percentage:.2f}% |")
            
        # 5. Detailed sample evaluation
        content.append("\n## 4. Detailed Sample Evaluation")
        for i, result in enumerate(sample_results[:5], 1):  # Show only first 5 samples
            content.append(f"\n### 4.{i} Sample {i}")
            content.append(f"- Type: {result['type']}")
            content.append(f"- Context: {result['sample']['context']}")
            content.append(f"- Question: {result['sample']['query']}")
            content.append(f"- Reference: {result['sample']['reference']}")
            content.append(f"- Model Response: {result['response']}")
            content.append("\nEvaluation Metrics:")
            content.append("| Metric | Score |")
            content.append("|--------|--------|")
            for metric in ["factual_accuracy", "logical_coherence", "context_relevance", 
                         "interpretative_reasoning", "information_completeness", "hallucination_score"]:
                if metric in result["metrics"]:
                    content.append(f"| {metric} | {result['metrics'][metric]:.4f} |")
                
        return "\n".join(content)
    
    def _generate_visualizations(self,
                               final_metrics: Dict[str, float],
                               type_metrics: Dict[str, Dict[str, float]],
                               report_dir: str):
        """Generate visualization charts"""
        # Set font for non-ASCII characters
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # For macOS
        plt.rcParams['axes.unicode_minus'] = False
        
        # Add model name suffix to file names if provided
        suffix = f"_{self.model_name}" if self.model_name else ""
        
        # 1. Overall metrics radar chart
        self._plot_radar_chart(final_metrics, "Overall Evaluation Metrics", 
                             os.path.join(report_dir, f"overall_metrics_radar{suffix}.png"))
        
        # 2. Type comparison bar chart
        self._plot_type_comparison(type_metrics,
                                 os.path.join(report_dir, f"type_comparison{suffix}.png"))
        
        # 3. Radar chart for each type
        for sample_type, metrics in type_metrics.items():
            self._plot_radar_chart(metrics, f"{sample_type} Evaluation Metrics",
                                 os.path.join(report_dir, f"{sample_type}_radar{suffix}.png"))
        
        # 4. Heatmap
        self._plot_heatmap(type_metrics,
                          os.path.join(report_dir, f"metrics_heatmap{suffix}.png"))
        
        # 5. Box plot
        self._plot_boxplot(type_metrics,
                          os.path.join(report_dir, f"metrics_boxplot{suffix}.png"))
        
        # 6. Trend chart
        self._plot_trend(type_metrics,
                        os.path.join(report_dir, f"metrics_trend{suffix}.png"))
        
        # 7. Stacked bar chart
        self._plot_stacked_bar(type_metrics,
                             os.path.join(report_dir, f"metrics_stacked_bar{suffix}.png"))
    
    def _plot_radar_chart(self, metrics: Dict[str, float], title: str, save_path: str):
        """Generate radar chart"""
        # Prepare data
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # Calculate angles
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]
        
        # Create chart
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'), dpi=300)
        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # Set ticks
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        
        # Set title
        plt.title(title, fontsize=14, pad=20)
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_type_comparison(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate type comparison bar chart"""
        # Prepare data
        df = pd.DataFrame(type_metrics).T
        
        # Create chart
        plt.figure(figsize=(16, 10), dpi=300)
        df.plot(kind='bar', width=0.8)
        
        # Set title and labels
        plt.title("Type-Specific Metrics Comparison", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # Adjust layout
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_heatmap(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate heatmap"""
        # Prepare data
        df = pd.DataFrame(type_metrics).T
        
        # Create chart
        plt.figure(figsize=(14, 10), dpi=300)
        sns.heatmap(df, annot=True, cmap='YlOrRd', fmt='.2f', 
                   cbar_kws={'label': 'Score'}, 
                   annot_kws={'size': 10})
        
        # Set title and labels
        plt.title("Type-Specific Metrics Heatmap", fontsize=14, pad=20)
        plt.xlabel("Metrics", fontsize=12)
        plt.ylabel("Sample Types", fontsize=12)
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_boxplot(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate box plot"""
        # Prepare data
        df = pd.DataFrame(type_metrics).T
        
        # Create chart
        plt.figure(figsize=(14, 10), dpi=300)
        df.boxplot()
        
        # Set title and labels
        plt.title("Metrics Distribution", fontsize=14, pad=20)
        plt.xlabel("Metrics", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # Adjust layout
        plt.xticks(rotation=45)
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_trend(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate trend chart"""
        # Prepare data
        df = pd.DataFrame(type_metrics).T
        
        # Create chart
        plt.figure(figsize=(14, 10), dpi=300)
        for column in df.columns:
            plt.plot(df.index, df[column], marker='o', label=column)
        
        # Set title and labels
        plt.title("Metrics Trend Across Types", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # Adjust layout
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_stacked_bar(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate stacked bar chart"""
        # Prepare data
        df = pd.DataFrame(type_metrics).T
        
        # Create chart
        plt.figure(figsize=(14, 10), dpi=300)
        df.plot(kind='bar', stacked=True)
        
        # Set title and labels
        plt.title("Metrics Composition by Type", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # Adjust layout
        plt.xticks(rotation=45)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Save chart
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _save_raw_data(self,
                      final_metrics: Dict[str, float],
                      type_metrics: Dict[str, Dict[str, float]],
                      sample_results: List[Dict[str, Any]],
                      report_dir: str):
        """Save raw data for future analysis"""
        # Add model name suffix to all file names
        suffix = ""
        if self.model_name:
            suffix = f"_{self.model_name}"
            
        # Save final metrics
        final_metrics_path = os.path.join(report_dir, f"final_metrics{suffix}.json")
        with open(final_metrics_path, "w", encoding="utf-8") as f:
            json.dump(final_metrics, f, indent=2, ensure_ascii=False)
            
        # Save type metrics
        type_metrics_path = os.path.join(report_dir, f"type_metrics{suffix}.json")
        with open(type_metrics_path, "w", encoding="utf-8") as f:
            json.dump(type_metrics, f, indent=2, ensure_ascii=False)
            
        # Save sample results
        sample_results_path = os.path.join(report_dir, f"sample_results{suffix}.json")
        with open(sample_results_path, "w", encoding="utf-8") as f:
            json.dump(sample_results, f, indent=2, ensure_ascii=False) 