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
    """忠实度评估报告生成器"""
    
    def __init__(self, output_dir: str = "reports"):
        """初始化报告生成器
        
        Args:
            output_dir: 报告输出目录
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
    def generate_report(self, 
                       final_metrics: Dict[str, float],
                       type_metrics: Dict[str, Dict[str, float]],
                       sample_results: List[Dict[str, Any]]) -> str:
        """生成评估报告
        
        Args:
            final_metrics: 总体评估指标
            type_metrics: 类型特定的评估指标
            sample_results: 样本评估结果
            
        Returns:
            str: 报告文件路径
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
        """生成报告内容
        
        Args:
            final_metrics: 总体评估指标
            type_metrics: 类型特定的评估指标
            sample_results: 样本评估结果
        """
        content = []
        
        # 1. 报告标题
        content.append("# 忠实度评估报告")
        content.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 2. 总体评估结果
        content.append("## 1. 总体评估结果")
        content.append("\n### 1.1 主要指标")
        content.append("| 指标 | 得分 |")
        content.append("|------|------|")
        for metric, score in final_metrics.items():
            content.append(f"| {metric} | {score:.4f} |")
        
        # 添加可视化图表引用
        content.append("\n### 1.2 可视化分析")
        content.append("\n#### 1.2.1 总体评估雷达图")
        content.append("![总体评估雷达图](overall_metrics_radar.png)")
        
        content.append("\n#### 1.2.2 评估指标热力图")
        content.append("![评估指标热力图](metrics_heatmap.png)")
        
        content.append("\n#### 1.2.3 评估指标分布")
        content.append("![评估指标箱线图](metrics_boxplot.png)")
        
        content.append("\n#### 1.2.4 评估指标趋势")
        content.append("![评估指标趋势图](metrics_trend.png)")
        
        content.append("\n#### 1.2.5 评估指标构成")
        content.append("![评估指标堆叠柱状图](metrics_stacked_bar.png)")
            
        # 3. 类型特定评估结果
        content.append("\n## 2. 类型特定评估结果")
        for sample_type, metrics in type_metrics.items():
            content.append(f"\n### 2.{len(content)} {sample_type}")
            content.append("| 指标 | 得分 |")
            content.append("|------|------|")
            for metric, score in metrics.items():
                content.append(f"| {metric} | {score:.4f} |")
            content.append(f"\n![{sample_type}雷达图]({sample_type}_radar.png)")
                
        # 4. 样本分析
        content.append("\n## 3. 样本分析")
        content.append(f"\n总样本数: {len(sample_results)}")
        
        # 统计每种类型的样本数量
        type_counts = {}
        for result in sample_results:
            sample_type = result["type"]
            type_counts[sample_type] = type_counts.get(sample_type, 0) + 1
            
        content.append("\n### 3.1 样本类型分布")
        content.append("| 类型 | 数量 | 占比 |")
        content.append("|------|------|------|")
        for sample_type, count in type_counts.items():
            percentage = count / len(sample_results) * 100
            content.append(f"| {sample_type} | {count} | {percentage:.2f}% |")
            
        # 5. 详细样本评估
        content.append("\n## 4. 详细样本评估")
        for i, result in enumerate(sample_results[:5], 1):  # 只显示前5个样本
            content.append(f"\n### 4.{i} 样本 {i}")
            content.append(f"- 类型: {result['type']}")
            content.append(f"- 上下文: {result['sample']['context']}")
            content.append(f"- 问题: {result['sample']['query']}")
            content.append(f"- 参考答案: {result['sample']['reference']}")
            content.append(f"- 模型响应: {result['response']}")
            content.append("\n评估指标:")
            content.append("| 指标 | 得分 |")
            content.append("|------|------|")
            for metric, score in result["metrics"].items():
                content.append(f"| {metric} | {score:.4f} |")
                
        return "\n".join(content)
    
    def _generate_visualizations(self,
                               final_metrics: Dict[str, float],
                               type_metrics: Dict[str, Dict[str, float]],
                               report_dir: str):
        """生成可视化图表
        
        Args:
            final_metrics: 总体评估指标
            type_metrics: 类型特定的评估指标
            report_dir: 报告目录
        """
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 对于macOS
        plt.rcParams['axes.unicode_minus'] = False
        
        # 1. 总体指标雷达图
        self._plot_radar_chart(final_metrics, "总体评估指标", 
                             os.path.join(report_dir, "overall_metrics_radar.png"))
        
        # 2. 类型对比条形图
        self._plot_type_comparison(type_metrics,
                                 os.path.join(report_dir, "type_comparison.png"))
        
        # 3. 每种类型的指标雷达图
        for sample_type, metrics in type_metrics.items():
            self._plot_radar_chart(metrics, f"{sample_type}评估指标",
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
        """绘制雷达图"""
        # 准备数据
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # 计算角度
        angles = [n / float(len(categories)) * 2 * 3.14159 for n in range(len(categories))]
        values += values[:1]
        angles += angles[:1]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        ax.plot(angles, values)
        ax.fill(angles, values, alpha=0.25)
        
        # 设置刻度
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        
        # 设置标题
        plt.title(title)
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _plot_type_comparison(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """绘制类型对比条形图"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(15, 8))
        df.plot(kind='bar', width=0.8)
        
        # 设置标题和标签
        plt.title("各类型评估指标对比")
        plt.xlabel("样本类型")
        plt.ylabel("得分")
        
        # 调整布局
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _plot_heatmap(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """绘制热力图"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(12, 8))
        sns.heatmap(df, annot=True, cmap='YlOrRd', fmt='.2f', cbar_kws={'label': '得分'})
        
        # 设置标题和标签
        plt.title("各类型评估指标热力图")
        plt.xlabel("评估指标")
        plt.ylabel("样本类型")
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _plot_boxplot(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """绘制箱线图"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        df.boxplot()
        
        # 设置标题和标签
        plt.title("评估指标分布箱线图")
        plt.xlabel("评估指标")
        plt.ylabel("得分")
        
        # 调整布局
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _plot_trend(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """绘制趋势图"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        for column in df.columns:
            plt.plot(df.index, df[column], marker='o', label=column)
        
        # 设置标题和标签
        plt.title("各类型评估指标趋势")
        plt.xlabel("样本类型")
        plt.ylabel("得分")
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 调整布局
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _plot_stacked_bar(self, type_metrics: Dict[str, Dict[str, float]], save_path: str):
        """绘制堆叠柱状图"""
        # 准备数据
        df = pd.DataFrame(type_metrics).T
        
        # 创建图表
        plt.figure(figsize=(12, 6))
        df.plot(kind='bar', stacked=True)
        
        # 设置标题和标签
        plt.title("各类型评估指标构成")
        plt.xlabel("样本类型")
        plt.ylabel("得分")
        
        # 添加图例
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # 调整布局
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        plt.savefig(save_path)
        plt.close()
    
    def _save_raw_data(self,
                      final_metrics: Dict[str, float],
                      type_metrics: Dict[str, Dict[str, float]],
                      sample_results: List[Dict[str, Any]],
                      report_dir: str):
        """保存原始数据"""
        # 保存总体指标
        with open(os.path.join(report_dir, "final_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(final_metrics, f, ensure_ascii=False, indent=2)
            
        # 保存类型指标
        with open(os.path.join(report_dir, "type_metrics.json"), "w", encoding="utf-8") as f:
            json.dump(type_metrics, f, ensure_ascii=False, indent=2)
            
        # 保存样本结果
        with open(os.path.join(report_dir, "sample_results.json"), "w", encoding="utf-8") as f:
            json.dump(sample_results, f, ensure_ascii=False, indent=2) 