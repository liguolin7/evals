from typing import Optional, Dict, Any, List, Union
from evals.api import CompletionFn
from evals.completion_fns.openai import OpenAIChatCompletionFn
from evals.eval import Eval
from evals.record import RecorderBase
from .metrics import FaithfulnessMetrics
from .report import FaithfulnessReport
import random
import logging
import os

logger = logging.getLogger(__name__)

class FaithfulnessEval(Eval):
    """Faithfulness Evaluation Framework
    
    This class implements the faithfulness evaluation framework for LLM responses.
    """
    
    # Define evaluation metrics
    METRICS = [
        "factual_accuracy",
        "logical_coherence",
        "context_relevance",
        "interpretative_reasoning",
        "information_completeness",
        "hallucination_score"
    ]
    
    # Define evaluation weights for different types
    TYPE_WEIGHTS = {
        "general": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "medical": {
            "factual_accuracy": 0.35,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "historical": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.2,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "scientific": {
            "factual_accuracy": 0.35,
            "logical_coherence": 0.2,
            "context_relevance": 0.1,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.1
        },
        "legal": {
            "factual_accuracy": 0.3,
            "logical_coherence": 0.25,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.1,
            "hallucination_score": 0.05
        }
    }

    def __init__(
        self,
        completion_fns: list[CompletionFn],
        eval_registry_path: str,
        samples_jsonl: str,
        seed: int = 20220722,
        report_dir: str = "reports",
        model_name: str = None,
        **kwargs,
    ):
        """Initialize evaluator
        
        Args:
            completion_fns: List of completion functions to evaluate
            eval_registry_path: Path to the evaluation registry
            samples_jsonl: Path to the samples JSONL file
            seed: Random seed for reproducibility
            report_dir: Directory to save the evaluation report
            model_name: Name of the model being evaluated
        """
        super().__init__(
            completion_fns=completion_fns,
            eval_registry_path=eval_registry_path,
            seed=seed,
            samples_jsonl=samples_jsonl,
            **kwargs
        )
        self.metrics_calculator = FaithfulnessMetrics()
        self.type_metrics = {}  # Store evaluation results for each type
        self.report_generator = FaithfulnessReport(output_dir=report_dir, model_name=model_name)
        
    def get_type_weights(self, sample_type: str) -> Dict[str, float]:
        """Get evaluation weights for specific type"""
        return self.TYPE_WEIGHTS.get(sample_type, self.TYPE_WEIGHTS["general"])

    def eval_sample(self, sample: Dict[str, Any], rng: Any) -> Optional[Dict[str, Any]]:
        """Evaluate a single sample"""
        # Get key information from sample
        context = sample.get("context", "")
        query = sample.get("query", "")
        reference = sample.get("reference", "")
        sample_type = sample.get("type", "general")  # Default to general type
        
        # Build prompt
        prompt = self._build_prompt(sample_type, context, query)
        
        # Get model response
        result = self.completion_fn(prompt=prompt)
        response = result.get_completions()[0]
        
        try:
            # Basic evaluation metrics
            metrics = {
                "factual_accuracy": self.metrics_calculator.calculate_factual_accuracy(response, reference),
                "logical_coherence": self.metrics_calculator.calculate_logical_coherence(response),
                "context_relevance": self.metrics_calculator.calculate_context_relevance(response, context)
            }
            
            # Advanced evaluation metrics
            advanced_metrics = {
                "interpretative_reasoning": self.metrics_calculator.calculate_interpretative_reasoning(response, context),
                "information_completeness": self.metrics_calculator.calculate_information_completeness(response, reference),
                "hallucination_score": self.metrics_calculator.calculate_hallucination_score(response, context)
            }
            
            # Merge all metrics
            metrics.update(advanced_metrics)
            
            # Calculate overall score using type-specific weights
            weights = self.get_type_weights(sample_type)
            overall_score = sum(metrics[metric] * weight for metric, weight in weights.items())
            metrics["overall_faithfulness"] = overall_score
            
            # Update type-specific metrics
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
            logger.error(f"Error occurred while evaluating the sample: {str(e)}")
            return None

    def _build_prompt(self, sample_type: str, context: str, query: str) -> Union[str, list[dict[str, str]]]:
        """Build prompt for model input"""
        if isinstance(self.completion_fn, OpenAIChatCompletionFn):
            # Use message format for chat models
            return [
                {"role": "system", "content": "You are a helpful AI assistant that provides accurate and faithful responses."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
            ]
        else:
            # Use text format for completion models
            return f"Context: {context}\n\nQuestion: {query}\n\nAnswer:"

    def run(self, recorder: RecorderBase, return_samples: bool = False) -> Union[Dict[str, float], Dict[str, Any]]:
        """Run evaluation and generate report"""
        # Load samples
        samples = self.get_samples()
        
        # Evaluate all samples
        sample_results = []
        self.type_metrics = {}  # Reset type metrics
        
        for i, sample in enumerate(samples):
            sample_type = sample.get("type", "general")
            
            # Use sample index as sample_id
            sample_id = f"sample_{i}"
            with recorder.as_default_recorder(sample_id):
                # Record original sample
                recorder.record_raw(sample)
                
                # Evaluate sample
                seed = f"{sample_id}:{self.seed}".encode("utf-8")
                rng = random.Random(seed)
                result = self.eval_sample(sample, rng)
                
                if result is not None:
                    # Record evaluation results
                    recorder.record_metrics(**result["metrics"])
                    sample_results.append(result)
                    
                    # Update type-specific metrics
                    if sample_type not in self.type_metrics:
                        self.type_metrics[sample_type] = []
                    self.type_metrics[sample_type].append(result["metrics"])
        
        # Calculate overall metrics and type-specific metrics
        final_metrics = self._calculate_final_metrics(sample_results)
        type_averages = self._calculate_type_averages()
        
        # Record final results with special sample_id
        with recorder.as_default_recorder("final_results"):
            recorder.record_metrics(**final_metrics)
        
        # Generate evaluation report
        report_path = self.report_generator.generate_report(
            final_metrics=final_metrics,
            type_metrics=type_averages,
            sample_results=sample_results
        )
        logger.info(f"Evaluation report generated: {report_path}")
        
        if return_samples:
            return {
                "sample_results": sample_results,
                "final_metrics": final_metrics,
                "type_metrics": type_averages,
                "report_path": report_path
            }
        else:
            return final_metrics

    def _calculate_final_metrics(self, sample_results: List[Dict]) -> Dict[str, float]:
        """Calculate final evaluation metrics"""
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
        """Calculate average metrics for each type"""
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
