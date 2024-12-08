import json
import os
from typing import Dict, List, Any
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class FaithfulnessReport:
    """Faithfulness Evaluation Report Generator"""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize report generator
        
        Args:
            output_dir: Output directory for reports
        """
        self.output_dir = output_dir
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
        # 生成报告���间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(self.output_dir, f"report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # 生成报告内容
        report_content = self._generate_report_content(final_metrics, type_metrics, sample_results)
        
        # 生成可视化
        self._generate_visualizations(final_metrics, type_metrics, report_dir)
        
        # 保存报告
        report_path = os.path.join(report_dir, "report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        # 保存原始数据
        self._save_raw_data(final_metrics, type_metrics, sample_results, report_dir)
        
        return report_path
    
    def _generate_report_content(self,
                               final_metrics: Dict[str, float],
                               type_metrics: Dict[str, Dict[str, float]],
                               sample_results: List[Dict[str, Any]]) -> str:
        """Generate report content"""
        content = []
        
        # 1. 报告标题
        content.append("# Faithfulness Evaluation Report")
        content.append(f"\nGeneration Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 2. ���体评估结果
        content.append("## 1. Overall Evaluation Results")
        content.append("\n### 1.1 Main Metrics")
        content.append("| Metric | Score |")
        content.append("|--------|--------|")
        for metric, score in final_metrics.items():
            content.append(f"| {metric} | {score:.4f} |")
        
        # 添加可视化图表引用
        content.append("\n### 1.2 Visualization Analysis")
        content.append("\n#### 1.2.1 Overall Metrics Radar Chart")
        content.append("![Overall Metrics Radar](overall_metrics_radar.png)")
        
        content.append("\n#### 1.2.2 Metrics Heatmap")
        content.append("![Metrics Heatmap](metrics_heatmap.png)")
        
        content.append("\n#### 1.2.3 Metrics Distribution")
        content.append("![Metrics Boxplot](metrics_boxplot.png)")
        
        content.append("\n#### 1.2.4 Metrics Trend")
        content.append("![Metrics Trend](metrics_trend.png)")
        
        content.append("\n#### 1.2.5 Metrics Composition")
        content.append("![Metrics Stacked Bar](metrics_stacked_bar.png)")
            
        # 3. 类型特定评估结果
        content.append("\n## 2. Type-Specific Evaluation Results")
        for sample_type, metrics in type_metrics.items():
            content.append(f"\n### 2.{len(content)} {sample_type}")
            content.append("| Metric | Score |")
            content.append("|--------|--------|")
            for metric, score in metrics.items():
                content.append(f"| {metric} | {score:.4f} |")
            content.append(f"\n![{sample_type} Radar]({sample_type}_radar.png)")
                
        # 4. 样本分析
        content.append("\n## 3. Sample Analysis")
        content.append(f"\nTotal Samples: {len(sample_results)}")
        
        # 统计每种类型的样本数量
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
            
        # 5. 详细样本评估
        content.append("\n## 4. Detailed Sample Evaluation")
        for i, result in enumerate(sample_results[:5], 1):  # 只显示前5个样本
            content.append(f"\n### 4.{i} Sample {i}")
            content.append(f"- Type: {result['type']}")
            content.append(f"- Context: {result['sample']['context']}")
            content.append(f"- Question: {result['sample']['query']}")
            content.append(f"- Reference: {result['sample']['reference']}")
            content.append(f"- Model Response: {result['response']}")
            content.append("\nEvaluation Metrics:")
            content.append("| Metric | Score |")
            content.append("|--------|--------|")
            for metric, score in result["metrics"].items():
                content.append(f"| {metric} | {score:.4f} |")
                
        return "\n".join(content)
    
    def _generate_visualizations(self,
                               final_metrics: Dict[str, float],
                               type_metrics: Dict[str, Dict[str, float]],
                               report_dir: str):
        """Generate visualization charts"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 对于macOS
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 总体指标雷达图
        self._plot_radar_chart(final_metrics, "Overall Evaluation Metrics", 
                             os.path.join(report_dir, "overall_metrics_radar.png"))
        
        # 2. 类型对比条形图
        self._plot_type_comparison(type_metrics,
                                 os.path.join(report_dir, "type_comparison.png"))
        
        # 3. 每种类型的指标雷达图
        for sample_type, metrics in type_metrics.items():
            self._plot_radar_chart(metrics, f"{sample_type} Evaluation Metrics",
                                 os.path.join(report_dir, f"{sample_type}_radar.png"))
        
        # 4. 热力图
        self._plot_heatmap(type_metrics,
                          os.path.join(report_dir, "metrics_heatmap.png"))
        
        # 5. 箱线图
        self._plot_boxplot(type_metrics,
                          os.path.join(report_dir, "metrics_boxplot.png"))
        
        # 6. 趋势图
        self._plot_trend(type_metrics,
                        os.path.join(report_dir, "metrics_trend.png"))
        
        # 7. 堆叠柱状图
        self._plot_stacked_bar(type_metrics,
                             os.path.join(report_dir, "metrics_stacked_bar.png"))
    
    def _plot_radar_chart(self, metrics: Dict[str, float], title: str, save_path: str):
        """Generate radar chart"""
        # 准备数据
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # 计算角度
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(12, 12), subplot_kw=dict(projection='polar'), dpi=300)
        ax.plot(angles, values, linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        
        # 设置刻度
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10)
        
        # 设置标题
        plt.title(title, fontsize=14, pad=20)
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_type_comparison(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate type comparison bar chart"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(16, 10), dpi=300)
        df.plot(kind='bar', width=0.8)
        
        # 设置标题和标签
        plt.title("Type-Specific Metrics Comparison", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # 调整布局
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.legend(fontsize=10, bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_heatmap(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate heatmap"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(14, 10), dpi=300)
        sns.heatmap(df, annot=True, cmap='YlOrRd', fmt='.2f', 
                   cbar_kws={'label': 'Score'}, 
                   annot_kws={'size': 10})
        
        # 设置标题和标签
        plt.title("Type-Specific Metrics Heatmap", fontsize=14, pad=20)
        plt.xlabel("Metrics", fontsize=12)
        plt.ylabel("Sample Types", fontsize=12)
        
        # 调整布局
        plt.xticks(fontsize=10, rotation=45)
        plt.yticks(fontsize=10, rotation=0)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_boxplot(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate boxplot"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(14, 8), dpi=300)
        df.boxplot()
        
        # 设置标题和标签
        plt.title("Metrics Distribution Boxplot", fontsize=14, pad=20)
        plt.xlabel("Metrics", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # 调整布局
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_trend(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate trend chart"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(14, 8), dpi=300)
        for column in df.columns:
            plt.plot(df.index, df[column], marker='o', label=column, linewidth=2, markersize=8)
        
        # 设置标题和标签
        plt.title("Type-Specific Metrics Trend", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        # 调整布局
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _plot_stacked_bar(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """Generate stacked bar chart"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(14, 8), dpi=300)
        df.plot(kind='bar', stacked=True)
        
        # 设置标题和标签
        plt.title("Type-Specific Metrics Composition", fontsize=14, pad=20)
        plt.xlabel("Sample Types", fontsize=12)
        plt.ylabel("Score", fontsize=12)
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        
        # 调整布局
        plt.xticks(rotation=45, fontsize=10)
        plt.yticks(fontsize=10)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path, dpi=300, bbox_inches='tight', pad_inches=0.5)
        plt.close()
    
    def _save_raw_data(self,
                       final_metrics: Dict[str, float],
                       type_metrics: Dict[str, Dict[str, float]],
                       sample_results: List[Dict[str, Any]],
                       report_dir: str):
        """Save raw data"""
        # 保存总体指标
        with open(os.path.join(report_dir, "final_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(final_metrics, f, ensure_ascii=False, indent=2)
            
        # 保存类型指标
        with open(os.path.join(report_dir, "type_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(type_metrics, f, ensure_ascii=False, indent=2)
            
        # 保存样本结果
        with open(os.path.join(report_dir, "sample_results.json"), "w", encoding="utf-8") as f:
            json.dump(sample_results, f, ensure_ascii=False, indent=2) 