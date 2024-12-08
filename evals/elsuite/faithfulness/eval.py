from typing import Optional, Dict, Any, List, Union
from evals.api import CompletionFn
from evals.eval import Eval
from evals.record import RecorderBase
from .metrics import FaithfulnessMetrics
import random

class FaithfulnessEval(Eval):
    def __init__(
        self,
        completion_fns: list[CompletionFn],
        eval_registry_path: str,
        samples_jsonl: str,
        seed: int = 20220722,
        **kwargs,
    ):
        super().__init__(
            completion_fns=completion_fns,
            eval_registry_path=eval_registry_path,
            seed=seed,
            samples_jsonl=samples_jsonl,
            **kwargs
        )
        self.metrics_calculator = FaithfulnessMetrics()

    def eval_sample(self, sample: Dict[str, Any], rng: Any) -> Optional[Dict[str, Any]]:
        """评估单个样本"""
        # 获取样本中的关键信息
        context = sample.get("context", "")
        query = sample.get("query", "")
        reference = sample.get("reference", "")
        
        # 构建提示词
        prompt = f"Context: {context}\nQuestion: {query}"
        
        # 获取模���响应
        result = self.completion_fn(prompt=prompt)
        response = result.get_completions()[0]
        
        # 基础评估指标
        metrics = {
            "factual_accuracy": self.metrics_calculator.calculate_factual_accuracy(response, reference),
            "logical_coherence": self.metrics_calculator.calculate_logical_coherence(response),
            "context_relevance": self.metrics_calculator.calculate_context_relevance(response, context)
        }
        
        # 高级评估指标
        advanced_metrics = {
            "interpretative_reasoning": self.metrics_calculator.calculate_interpretative_reasoning(response, context),
            "information_completeness": self.metrics_calculator.calculate_information_completeness(response, reference),
            "hallucination_score": self.metrics_calculator.calculate_hallucination_score(response, context)
        }
        
        # 合并所有指标
        metrics.update(advanced_metrics)
        
        # 计算综合分数
        metrics["overall_faithfulness"] = self.metrics_calculator.calculate_overall_faithfulness(metrics)
        
        return {
            "sample": sample,
            "response": response,
            "metrics": metrics,
            "prompt": prompt  # 添加提示词以便分析
        }

    def run(self, recorder: RecorderBase, return_samples: bool = False) -> Union[Dict[str, float], Dict[str, Any]]:
        """运行评估"""
        # 加载样本
        samples = self.get_samples()
        
        # 评估所有样本
        sample_results = []
        for i, sample in enumerate(samples):
            # 使用样本索引作为sample_id
            sample_id = f"sample_{i}"
            with recorder.as_default_recorder(sample_id):
                # 记录原始样本
                recorder.record_raw(sample)
                
                # 评估样本
                seed = f"{sample_id}:{self.seed}".encode("utf-8")
                rng = random.Random(seed)
                result = self.eval_sample(sample, rng)
                
                if result is not None:
                    # 记录样本的评估结果
                    recorder.record_metrics(**result["metrics"])
                    sample_results.append(result)
        
        # 计算平均分数
        metric_names = [
            "factual_accuracy",
            "logical_coherence", 
            "context_relevance",
            "interpretative_reasoning",
            "information_completeness",
            "hallucination_score",
            "overall_faithfulness"
        ]
        
        final_metrics = {}
        for metric in metric_names:
            scores = [r["metrics"][metric] for r in sample_results if r is not None and metric in r["metrics"]]
            if scores:
                final_metrics[metric] = sum(scores) / len(scores)
            else:
                final_metrics[metric] = 0.0
        
        # 使用特殊的sample_id记录最终结果
        with recorder.as_default_recorder("final_results"):
            recorder.record_metrics(**final_metrics)
        
        if return_samples:
            return {
                "sample_results": sample_results,
                "final_metrics": final_metrics
            }
        else:
            return final_metrics
