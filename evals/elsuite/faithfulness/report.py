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
        # 生成报告时间戳
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
        
        # 2. 总体评估结果
        content.append("## 1. Overall Evaluation Results")
        content.append("\n### 1.1 Main Metrics")
        content.append("| Metric | Score |")
        content.append("|--------|--------|")
        for metric in ["factual_accuracy", "logical_coherence", "context_relevance", 
                      "interpretative_reasoning", "information_completeness", "hallucination_score"]:
            if metric in final_metrics:
                content.append(f"| {metric} | {final_metrics[metric]:.4f} |")
        
        # 添加可视化图表引用
        content.append("\n### 1.2 Visualization Analysis")
        content.append("\n#### 1.2.1 Overall Metrics Radar")
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
            for metric in ["factual_accuracy", "logical_coherence", "context_relevance", 
                         "interpretative_reasoning", "information_completeness", "hallucination_score"]:
                if metric in metrics:
                    content.append(f"| {metric} | {metrics[metric]:.4f} |")
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

def create_type_comparison_chart(results: Dict[str, Dict[str, float]], output_path: str):
    """创建优化后的类型比较图表
    
    Args:
        results: 评估结果字典
        output_path: 输出文件路径
    """
    # 设置图表样式
    plt.style.use('default')
    
    # 创建图表和子图
    fig = plt.figure(figsize=(18, 8))  # 增加总宽度以容纳类型列表
    gs = fig.add_gridspec(1, 2, width_ratios=[3, 1])  # 3:1 的宽度比
    ax1 = fig.add_subplot(gs[0])  # 主图表
    ax2 = fig.add_subplot(gs[1])  # 类型列表
    
    # 准备数据
    types = list(results.keys())
    type_indices = list(range(1, len(types) + 1))  # 创建序号列表
    metrics = ['factual_accuracy', 'logical_coherence', 'context_relevance',
              'interpretative_reasoning', 'information_completeness', 
              'hallucination_score', 'overall_faithfulness']
    
    # 设置颜色
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    # 设置柱状图参数
    x = np.arange(len(types))
    width = 0.11
    
    # 绘制柱状图
    for i, (metric, color) in enumerate(zip(metrics, colors)):
        values = [results[t][metric] for t in types]
        ax1.bar(x + i * width, values, width, label=metric, color=color)
    
    # 设置主图表的标题和标签
    ax1.set_title('Type-Specific Metrics Comparison', fontsize=14, pad=20)
    ax1.set_xlabel('Sample Type Index', fontsize=12, labelpad=10)
    ax1.set_ylabel('Score', fontsize=12)
    
    # 设置x轴为序号
    ax1.set_xticks(x + width * 3)
    ax1.set_xticklabels(type_indices)
    
    # 设置图例
    ax1.legend(bbox_to_anchor=(1.02, 1),
              loc='upper left',
              fontsize=10,
              frameon=True)
    
    # 设置网格线
    ax1.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # 设置y轴范围
    ax1.set_ylim(0, 1.0)
    
    # 创建类型对照表
    ax2.axis('off')  # 关闭坐标轴
    cell_text = [[f"{i+1}. {t}"] for i, t in enumerate(types)]
    table = ax2.table(cellText=cell_text,
                     loc='center right',
                     cellLoc='left',
                     edges='open')  # 移除单元格边框
    
    # 设置表格样式
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.2, 1.8)  # 调整单元格大小
    
    # 为表格添加标题
    ax2.text(0.5, 1.02, 'Sample Types',
             horizontalalignment='center',
             fontsize=12,
             transform=ax2.transAxes)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(output_path,
                bbox_inches='tight',
                dpi=300,
                facecolor='white',
                edgecolor='none')
    
    # 关闭图表
    plt.close()

def create_radar_chart(metrics: Dict[str, float], output_path: str):
    """创建雷达图展示各项指标的得分
    
    Args:
        metrics: 评估指标和得分
        output_path: 输出文件路径
    """
    # 准备数据
    categories = list(metrics.keys())
    values = list(metrics.values())
    
    # 计算角度
    angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
    
    # 闭合图形
    values = np.concatenate((values, [values[0]]))
    angles = np.concatenate((angles, [angles[0]]))
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # 绘制雷达图
    ax.plot(angles, values)
    ax.fill(angles, values, alpha=0.25)
    
    # 设置刻度标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # 设置标题
    plt.title('Faithfulness Metrics Radar Chart', pad=20)
    
    # 保存图表
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def create_heatmap(type_metrics: Dict[str, Dict[str, float]], output_path: str):
    """创建热力图展示不同类型的评估结果
    
    Args:
        type_metrics: 各类型的评估指标和得分
        output_path: 输出文件路径
    """
    # 准备数据
    types = list(type_metrics.keys())
    metrics = ['factual_accuracy', 'logical_coherence', 'context_relevance',
              'interpretative_reasoning', 'information_completeness', 
              'hallucination_score', 'overall_faithfulness']
    
    # 创建数据矩阵
    data = np.zeros((len(metrics), len(types)))
    for i, metric in enumerate(metrics):
        for j, type_name in enumerate(types):
            data[i, j] = type_metrics[type_name][metric]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 绘制热力图
    im = ax.imshow(data, cmap='YlOrRd')
    
    # 设置刻度标签
    ax.set_xticks(np.arange(len(types)))
    ax.set_yticks(np.arange(len(metrics)))
    ax.set_xticklabels(types)
    ax.set_yticklabels(metrics)
    
    # 旋转x轴标签
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    
    # 添加颜色条
    plt.colorbar(im)
    
    # 在每个单元格中添加数值
    for i in range(len(metrics)):
        for j in range(len(types)):
            text = ax.text(j, i, f"{data[i, j]:.2f}",
                         ha="center", va="center", color="black")
    
    # 设置标题
    plt.title('Type-Specific Metrics Heatmap')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def create_trend_analysis(results: Dict[str, Any], output_path: str):
    """创建趋势分析图，展示不同类型的整体表现趋势
    
    Args:
        results: 评估结果
        output_path: 输出文件路径
    """
    # 准备数据
    type_metrics = results['type_metrics']
    types = list(type_metrics.keys())
    metrics = ['factual_accuracy', 'logical_coherence', 'context_relevance',
              'interpretative_reasoning', 'information_completeness', 
              'hallucination_score', 'overall_faithfulness']
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # 为每个指标绘制一条线
    for metric in metrics:
        values = [type_metrics[t][metric] for t in types]
        plt.plot(types, values, marker='o', label=metric, linewidth=2)
    
    # 设置标签和标题
    plt.xlabel('Sample Types')
    plt.ylabel('Score')
    plt.title('Metrics Trend Across Sample Types')
    
    # 旋转x轴标签
    plt.xticks(rotation=45, ha='right')
    
    # 添加图例
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 添加网格
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图表
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

def generate_report(results: Dict[str, Any], report_dir: str):
    """生成评估报告
    
    Args:
        results: 评估结果
        report_dir: 报告输出目录
    """
    os.makedirs(report_dir, exist_ok=True)
    
    # 生成各种可视化
    # 1. 类型比较图
    type_comparison_path = os.path.join(report_dir, 'type_comparison.png')
    create_type_comparison_chart(results['type_metrics'], type_comparison_path)
    
    # 2. 雷达图
    radar_path = os.path.join(report_dir, 'metrics_radar.png')
    create_radar_chart(results['final_metrics'], radar_path)
    
    # 3. 热力图
    heatmap_path = os.path.join(report_dir, 'type_metrics_heatmap.png')
    create_heatmap(results['type_metrics'], heatmap_path)
    
    # 4. 趋势分析图
    trend_path = os.path.join(report_dir, 'metrics_trend.png')
    create_trend_analysis(results, trend_path)
    
    # 保存详细结果
    with open(os.path.join(report_dir, "detailed_results.json"), "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    logger.info(f"Report generated successfully in {report_dir}") 