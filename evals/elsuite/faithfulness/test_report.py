import unittest
import os
import shutil
from unittest.mock import Mock
from .report import FaithfulnessReport

class TestFaithfulnessReport(unittest.TestCase):
    def setUp(self):
        """测试初始化"""
        self.test_dir = "test_reports"
        self.report_generator = FaithfulnessReport(output_dir=self.test_dir)
        
        # 准备测试数据
        self.final_metrics = {
            "factual_accuracy": 0.85,
            "logical_coherence": 0.78,
            "context_relevance": 0.92,
            "interpretative_reasoning": 0.76,
            "information_completeness": 0.81,
            "hallucination_score": 0.95,
            "overall_faithfulness": 0.845
        }
        
        self.type_metrics = {
            "medical_advice": {
                "factual_accuracy": 0.88,
                "logical_coherence": 0.82,
                "context_relevance": 0.90,
                "interpretative_reasoning": 0.75,
                "information_completeness": 0.85,
                "hallucination_score": 0.93,
                "overall_faithfulness": 0.855
            },
            "economic_analysis": {
                "factual_accuracy": 0.82,
                "logical_coherence": 0.75,
                "context_relevance": 0.88,
                "interpretative_reasoning": 0.79,
                "information_completeness": 0.77,
                "hallucination_score": 0.91,
                "overall_faithfulness": 0.82
            }
        }
        
        self.sample_results = [
            {
                "type": "medical_advice",
                "sample": {
                    "context": "患者出现发烧症状",
                    "query": "应该采取什么措施？",
                    "reference": "建议卧床休息，多喝水。"
                },
                "response": "需要卧床休息，多补充水分，必要时服用退烧药。",
                "metrics": {
                    "factual_accuracy": 0.88,
                    "logical_coherence": 0.82,
                    "context_relevance": 0.90,
                    "interpretative_reasoning": 0.75,
                    "information_completeness": 0.85,
                    "hallucination_score": 0.93,
                    "overall_faithfulness": 0.855
                }
            },
            {
                "type": "economic_analysis",
                "sample": {
                    "context": "GDP增长率下降",
                    "query": "这对市场有什么影响？",
                    "reference": "可能导致市场信心下降。"
                },
                "response": "GDP增长率下降可能导致市场信心受挫，投资者态度趋于谨慎。",
                "metrics": {
                    "factual_accuracy": 0.82,
                    "logical_coherence": 0.75,
                    "context_relevance": 0.88,
                    "interpretative_reasoning": 0.79,
                    "information_completeness": 0.77,
                    "hallucination_score": 0.91,
                    "overall_faithfulness": 0.82
                }
            }
        ]
    
    def tearDown(self):
        """清理测试目录"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_report_generation(self):
        """测试报告生成"""
        report_path = self.report_generator.generate_report(
            final_metrics=self.final_metrics,
            type_metrics=self.type_metrics,
            sample_results=self.sample_results
        )
        
        # 验证报告文件是否生成
        self.assertTrue(os.path.exists(report_path))
        
        # ���证报告内容
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # 验证报告各个部分
        self.assertIn("# 忠实度评估报告", content)
        self.assertIn("## 1. 总体评估结果", content)
        self.assertIn("## 2. 类型特定评估结果", content)
        self.assertIn("## 3. 样本分析", content)
        self.assertIn("## 4. 详细样本评估", content)
        
        # 验证指标值
        self.assertIn("0.85", content)  # factual_accuracy
        self.assertIn("0.78", content)  # logical_coherence
        
        # 验证样本类型
        self.assertIn("medical_advice", content)
        self.assertIn("economic_analysis", content)
    
    def test_visualization_generation(self):
        """测试可视化生成"""
        report_path = self.report_generator.generate_report(
            final_metrics=self.final_metrics,
            type_metrics=self.type_metrics,
            sample_results=self.sample_results
        )
        
        report_dir = os.path.dirname(report_path)
        
        # 验证可视化文件是否生成
        self.assertTrue(os.path.exists(os.path.join(report_dir, "overall_metrics_radar.png")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "type_comparison.png")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "medical_advice_radar.png")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "economic_analysis_radar.png")))
    
    def test_raw_data_saving(self):
        """测试原始数据保存"""
        report_path = self.report_generator.generate_report(
            final_metrics=self.final_metrics,
            type_metrics=self.type_metrics,
            sample_results=self.sample_results
        )
        
        report_dir = os.path.dirname(report_path)
        
        # 验证原始数据文件是否生成
        self.assertTrue(os.path.exists(os.path.join(report_dir, "final_metrics.json")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "type_metrics.json")))
        self.assertTrue(os.path.exists(os.path.join(report_dir, "sample_results.json")))

def run_tests():
    """运行所有测试"""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests() 