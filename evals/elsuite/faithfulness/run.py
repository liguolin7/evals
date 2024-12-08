import argparse
import os
import logging
from evals.api import CompletionFn
from evals.registry import Registry
from evals.eval import Eval
from evals.record import RecorderBase
from evals.base import RunSpec
from .eval import FaithfulnessEval

logger = logging.getLogger(__name__)

def create_run_spec(model_name: str) -> RunSpec:
    """创建运行规范"""
    return RunSpec(
        completion_fns=[model_name],
        eval_name="faithfulness_eval",
        base_eval="faithfulness",
        split="test",
        run_config={},
        created_by="faithfulness_eval"
    )

def create_recorder(run_spec: RunSpec) -> RecorderBase:
    """创建记录器"""
    return RecorderBase(run_spec=run_spec)

def format_sample_result(sample: dict, response: str, metrics: dict) -> str:
    """格式化单个样本的评估结果"""
    result = "\n" + "="*50 + "\n"
    result += "Context: " + sample["context"] + "\n"
    result += "Question: " + sample["query"] + "\n"
    result += "Reference: " + sample["reference"] + "\n"
    result += "Model Response: " + response + "\n"
    result += "\nMetrics:\n"
    for metric, value in metrics.items():
        result += f"  {metric}: {value:.3f}\n"
    return result

def run_faithfulness_eval(model_name: str = "gpt-3.5-turbo", 
                         samples_path: str = "evals/registry/data/faithfulness/samples.jsonl",
                         verbose: bool = True):
    """运行忠实度评估的主函数"""
    # 设置必要的环境变量
    os.environ["EVALS_REGISTRY_PATH"] = "evals/registry"
    
    try:
        # 创建评估器
        registry = Registry()
        
        # 获取模型completion function
        completion_fn = registry.make_completion_fn(model_name)
        
        # 创建运行规范和记录器
        run_spec = create_run_spec(model_name)
        recorder = create_recorder(run_spec)
        
        # 创建评估实例
        evaluator = FaithfulnessEval(
            completion_fns=[completion_fn],
            eval_registry_path=os.path.join(os.getcwd(), "evals/registry"),
            samples_jsonl=samples_path
        )
        
        # 运行评估
        results = evaluator.run(recorder, return_samples=True)  # 添加return_samples参数
        
        if verbose:
            print("\n=== Detailed Evaluation Results ===")
            for sample_result in results["sample_results"]:
                print(format_sample_result(
                    sample_result["sample"],
                    sample_result["response"],
                    sample_result["metrics"]
                ))
            
            print("\n=== Overall Metrics ===")
            for metric, value in results["final_metrics"].items():
                print(f"{metric}: {value:.3f}")
        
        return results["final_metrics"]
        
    except Exception as e:
        logger.error(f"Error in evaluation: {str(e)}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Run LLM Faithfulness Evaluation")
    parser.add_argument("--model", type=str, default="gpt-3.5-turbo",
                      help="Name of the model to evaluate")
    parser.add_argument("--samples", type=str, 
                      default="evals/registry/data/faithfulness/samples.jsonl",
                      help="Path to test samples file")
    parser.add_argument("--verbose", action="store_true",
                      help="Show detailed evaluation results")
    
    args = parser.parse_args()
    
    try:
        # 运行评估
        results = run_faithfulness_eval(args.model, args.samples, args.verbose)
        
        if not args.verbose:
            # 只在非详细模式下打印总体结果
            print("\n=== Evaluation Results ===")
            for metric, value in results.items():
                print(f"{metric}: {value:.3f}")
                
    except Exception as e:
        logger.error(f"Error running evaluation: {str(e)}")
        raise

if __name__ == "__main__":
    main() 