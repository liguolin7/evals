#!/usr/bin/env python3
import os
import sys
import logging
from evals.registry import Registry
import datetime
from evals.eval import Eval
from evals.record import RecorderBase
from evals.base import RunSpec
from .eval import FaithfulnessEval

def setup_logging():
    """设置日志配置"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(os.path.join(log_dir, f'faithfulness_eval_{timestamp}.log'))
        ]
    )

def create_run_spec(model_name: str) -> RunSpec:
    """创建运行规范"""
    return RunSpec(
        completion_fns=[model_name],
        eval_name="faithfulness",
        base_eval="faithfulness",
        split="test",
        run_config={},
        created_by="faithfulness_eval"
    )

def create_recorder(run_spec: RunSpec) -> RecorderBase:
    """创建记录器"""
    return RecorderBase(run_spec=run_spec)

def run_evaluation(
    model_name: str = "gpt-3.5-turbo",
    samples_path: str = "samples/faithfulness_samples.jsonl",
    report_dir: str = "reports"
) -> str:
    """Run faithfulness evaluation
    
    Args:
        model_name: Name of the model to evaluate
        samples_path: Path to samples file
        report_dir: Directory to save reports
        
    Returns:
        str: Path to the generated report
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # 设置评估参数
        registry = Registry()
        
        # 设置输出目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("results", f"faithfulness_eval_{timestamp}")
        report_dir = os.path.join(output_path, "reports")
        os.makedirs(output_path, exist_ok=True)
        
        logger.info(f"Starting Faithfulness Evaluation - Model: {model_name}")
        logger.info(f"Output Directory: {output_path}")
        
        # 获取模型completion function
        completion_fn = registry.make_completion_fn(model_name)
        
        # 创建运行规范和记录器
        run_spec = create_run_spec(model_name)
        recorder = create_recorder(run_spec)
        
        # 创建评估器实例
        evaluator = FaithfulnessEval(
            completion_fns=[completion_fn],
            eval_registry_path="evals/registry/evals/faithfulness.yaml",
            samples_jsonl="evals/registry/data/faithfulness/samples.jsonl",
            report_dir=report_dir
        )
        
        # 运行评估
        results = evaluator.run(recorder, return_samples=True)
        
        # 输出评估结果
        logger.info("\n=== Evaluation Complete ===")
        logger.info(f"Report Path: {results['report_path']}")
        
        logger.info("\nOverall Evaluation Results:")
        for metric, value in results["final_metrics"].items():
            logger.info(f"{metric}: {value:.4f}")
            
        logger.info("\nType-Specific Evaluation Results:")
        for type_name, metrics in results["type_metrics"].items():
            logger.info(f"\n{type_name}:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.4f}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}")
        raise e

if __name__ == "__main__":
    run_evaluation() 