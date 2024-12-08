import unittest
from unittest.mock import Mock, patch
from .eval import FaithfulnessEval
import json
import os

class TestFaithfulnessEval(unittest.TestCase):
    def setUp(self):
        """测试初始化"""
        self.mock_completion_fn = Mock()
        self.mock_completion_fn.return_value = Mock(
            get_completions=lambda: ["这是一个测试响应"]
        )
        
        self.eval = FaithfulnessEval(
            completion_fns=[self.mock_completion_fn],
            eval_registry_path="test_registry",
            samples_jsonl="test_samples.jsonl",
            seed=42
        )

    def test_type_weights(self):
        """测试类型权重计算"""
        # 测试医疗建议类型的权重
        medical_weights = self.eval.get_type_weights("medical_advice")
        self.assertEqual(medical_weights["factual_accuracy"], 0.35)
        self.assertEqual(medical_weights["logical_coherence"], 0.15)
        
        # 测试经济分析类型的权重
        economic_weights = self.eval.get_type_weights("economic_analysis")
        self.assertEqual(economic_weights["factual_accuracy"], 0.3)
        self.assertEqual(economic_weights["logical_coherence"], 0.2)

    def test_prompt_generation(self):
        """测试提示词生成"""
        # 测试医疗建议类型的提示词
        medical_prompt = self.eval._build_prompt(
            "medical_advice",
            "患者出现发烧症状",
            "应该采取什么措施？"
        )
        self.assertIn("medical_advice", medical_prompt)
        self.assertIn("evidence-based medical information", medical_prompt)
        
        # 测试经济分析类型的提示词
        economic_prompt = self.eval._build_prompt(
            "economic_analysis",
            "GDP增长率下降",
            "这对市场有什么影响？"
        )
        self.assertIn("economic_analysis", economic_prompt)
        self.assertIn("implications", economic_prompt)

    def test_eval_sample(self):
        """测试样本评估"""
        sample = {
            "type": "medical_advice",
            "context": "患者出现发烧症状",
            "query": "应该采取什么措施？",
            "reference": "建议卧床休息，多喝水，必要时服用退烧药。"
        }
        
        result = self.eval.eval_sample(sample, None)
        
        # 验证结果结构
        self.assertIn("metrics", result)
        self.assertIn("type", result)
        self.assertIn("overall_faithfulness", result["metrics"])
        
        # 验证医疗类型特定的评分权重是否正确应用
        metrics = result["metrics"]
        self.assertTrue(0 <= metrics["overall_faithfulness"] <= 1)

    def test_type_specific_evaluation(self):
        """测试类型特定的评估"""
        # 创建不同类型的测试样本
        samples = [
            {
                "type": "medical_advice",
                "context": "患者出现发烧症状",
                "query": "应该采取什么措施？",
                "reference": "建议卧床休息，多喝水。"
            },
            {
                "type": "economic_analysis",
                "context": "GDP增长率下降",
                "query": "这对市场有什么影响？",
                "reference": "可能导致市场信心下降。"
            }
        ]
        
        # 模拟样本加载
        self.eval.get_samples = Mock(return_value=samples)
        
        # 创建模拟记录器
        mock_recorder = Mock()
        mock_recorder.as_default_recorder = Mock(return_value=Mock(__enter__=Mock(), __exit__=Mock()))
        
        # 运行评估
        results = self.eval.run(mock_recorder, return_samples=True)
        
        # 验证类型特定的结果
        self.assertIn("type_metrics", results)
        self.assertIn("final_metrics", results)
        
        # 验证是否包含所有样本类型的结果
        type_metrics = results["type_metrics"]
        self.assertIn("medical_advice", type_metrics)
        self.assertIn("economic_analysis", type_metrics)

    def test_edge_cases(self):
        """测试边界情况"""
        # 测试未知类型
        unknown_weights = self.eval.get_type_weights("unknown_type")
        self.assertIsNotNone(unknown_weights)
        
        # 测试空样本
        empty_sample = {
            "type": "medical_advice",
            "context": "",
            "query": "",
            "reference": ""
        }
        result = self.eval.eval_sample(empty_sample, None)
        self.assertIsNotNone(result)
        
        # 测试缺失字段的样本
        incomplete_sample = {
            "type": "medical_advice"
        }
        result = self.eval.eval_sample(incomplete_sample, None)
        self.assertIsNotNone(result)

def run_tests():
    """运行所有测试"""
    unittest.main(argv=[''], verbosity=2, exit=False)

if __name__ == '__main__':
    run_tests() 