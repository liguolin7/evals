from typing import Optional, Dict, Any, List, Union
from evals.api import CompletionFn
from evals.eval import Eval
from evals.record import RecorderBase
from .metrics import FaithfulnessMetrics
import random
import logging

logger = logging.getLogger(__name__)

class FaithfulnessEval(Eval):
    # 定义不同类型的评估权重
    TYPE_WEIGHTS = {
        "general": {  # 添加通用类型的权重配置
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "economic_analysis": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.1,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "current_events": {
            "factual_accuracy": 0.35,
            "logical_coherence": 0.15,
            "context_relevance": 0.2,
            "interpretative_reasoning": 0.1,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "medical_advice": {
            "factual_accuracy": 0.35,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "scientific_explanation": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.1,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "technical_analysis": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.1,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "historical_analysis": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "environmental_impact": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "policy_analysis": {
            "factual_accuracy": 0.25,
            "logical_coherence": 0.2,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.2,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        }
    }

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
        self.type_metrics = {}  # 用于存储每种类型的评估结果

    def get_type_weights(self, sample_type: str) -> Dict[str, float]:
        """获取特定类型的评估权重"""
        return self.TYPE_WEIGHTS.get(sample_type, self.TYPE_WEIGHTS["general"])

    def eval_sample(self, sample: Dict[str, Any], rng: Any) -> Optional[Dict[str, Any]]:
        """评估单个样本"""
        # 获取样本中的关键信息
        context = sample.get("context", "")
        query = sample.get("query", "")
        reference = sample.get("reference", "")
        sample_type = sample.get("type", "general")  # 默认使用general类型
        
        # 构建提示词
        prompt = self._build_prompt(sample_type, context, query)
        
        # 获取模型响应
        result = self.completion_fn(prompt=prompt)
        response = result.get_completions()[0]
        
        try:
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
            
            # 使用类型特定的权重计算综合分数
            weights = self.get_type_weights(sample_type)
            overall_score = sum(metrics[metric] * weight for metric, weight in weights.items())
            metrics["overall_faithfulness"] = overall_score
            
            # 更新类型特定的指标
            if sample_type not in self.type_metrics:
                self.type_metrics[sample_type] = []
            self.type_metrics[sample_type].append(metrics)
            
            return {
                "sample": sample,
                "response": response,
                "metrics": metrics,
                "prompt": prompt,
                "type": sample_type
            }
            
        except Exception as e:
            logger.error(f"评估样本时发生错误: {str(e)}")
            return None

    def _build_prompt(self, sample_type: str, context: str, query: str) -> str:
        """根据样本类型构建特定的提示词"""
        type_specific_instructions = {
            "economic_analysis": "Analyze the economic data and implications. Consider both direct and indirect effects.",
            "current_events": "Provide a factual summary focusing on key events and their immediate implications.",
            "medical_advice": "Provide evidence-based medical information. Be clear about the research context.",
            "scientific_explanation": "Explain the scientific concept clearly and accurately. Use appropriate terminology.",
            "technical_analysis": "Analyze the technical aspects and their practical implications.",
            "historical_analysis": "Analyze historical events considering causes, effects, and broader context.",
            "environmental_impact": "Assess environmental impacts considering both immediate and long-term effects.",
            "policy_analysis": "Evaluate policy implications considering benefits, drawbacks, and implementation challenges."
        }
        
        instruction = type_specific_instructions.get(sample_type, "")
        return f"Type: {sample_type}\nInstruction: {instruction}\nContext: {context}\nQuestion: {query}"

    def run(self, recorder: RecorderBase, return_samples: bool = False) -> Union[Dict[str, float], Dict[str, Any]]:
        """运行评估"""
        # 加载样本
        samples = self.get_samples()
        
        # 评估所有样本
        sample_results = []
        self.type_metrics = {}  # 重置类型指标
        
        for i, sample in enumerate(samples):
            sample_type = sample.get("type", "general")
            
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
                    
                    # 更新类型特定的指标
                    if sample_type not in self.type_metrics:
                        self.type_metrics[sample_type] = []
                    self.type_metrics[sample_type].append(result["metrics"])
        
        # 计算总体指标和类型特定指标
        final_metrics = self._calculate_final_metrics(sample_results)
        
        # 使用特殊的sample_id记录最终结果
        with recorder.as_default_recorder("final_results"):
            recorder.record_metrics(**final_metrics)
        
        if return_samples:
            return {
                "sample_results": sample_results,
                "final_metrics": final_metrics,
                "type_metrics": self._calculate_type_averages()
            }
        else:
            return final_metrics

    def _calculate_final_metrics(self, sample_results: List[Dict]) -> Dict[str, float]:
        """计算最终的评估指标"""
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
        
        return final_metrics

    def _calculate_type_averages(self) -> Dict[str, Dict[str, float]]:
        """计算每种类型的平均指标"""
        type_averages = {}
        
        for sample_type, metrics_list in self.type_metrics.items():
            if not metrics_list:
                continue
                
            type_averages[sample_type] = {}
            for metric in metrics_list[0].keys():
                scores = [m[metric] for m in metrics_list if metric in m]
                if scores:
                    type_averages[sample_type][metric] = sum(scores) / len(scores)
                else:
                    type_averages[sample_type][metric] = 0.0
        
        return type_averages
