#!/usr/bin/env python3
import json
import os
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

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

def main():
    # 设置输入输出路径
    results_dir = "results/faithfulness_eval_20241209_020856/reports/report_20241209_021054"
    output_dir = "visualizations"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取类型指标数据
    with open(os.path.join(results_dir, "type_metrics.json"), "r") as f:
        type_metrics = json.load(f)
    
    # 生成图表
    output_path = os.path.join(output_dir, "type_comparison.png")
    create_type_comparison_chart(type_metrics, output_path)
    print(f"图表已生成: {output_path}")

if __name__ == "__main__":
    main() 