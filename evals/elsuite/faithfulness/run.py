#!/usr/bin/env python3
import os
import sys
import logging
import argparse
from evals.registry import Registry
import datetime
from evals.eval import Eval
from evals.record import RecorderBase
from evals.base import RunSpec
from .eval import FaithfulnessEval

def setup_logging():
    """Configure logging settings"""
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
    """Create run specification"""
    return RunSpec(
        completion_fns=[model_name],
        eval_name="faithfulness",
        base_eval="faithfulness",
        split="test",
        run_config={},
        created_by="faithfulness_eval"
    )

def create_recorder(run_spec: RunSpec) -> RecorderBase:
    """Create evaluation recorder"""
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
        # Set up evaluation parameters
        registry = Registry()
        
        # Set up output directory
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join("results", f"faithfulness_eval_{timestamp}")
        report_dir = os.path.join(output_path, "reports")
        os.makedirs(output_path, exist_ok=True)
        
        logger.info(f"Starting Faithfulness Evaluation - Model: {model_name}")
        logger.info(f"Output Directory: {output_path}")
        
        # Get model completion function
        completion_fn = registry.make_completion_fn(model_name)
        
        # Create run specification and recorder
        run_spec = create_run_spec(model_name)
        recorder = create_recorder(run_spec)
        
        # Create evaluator instance
        evaluator = FaithfulnessEval(
            completion_fns=[completion_fn],
            eval_registry_path="evals/registry/evals/faithfulness.yaml",
            samples_jsonl="evals/registry/data/faithfulness/samples.jsonl",
            report_dir=report_dir
        )
        
        # Run evaluation
        results = evaluator.run(recorder, return_samples=True)
        
        # Output evaluation results
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
    parser = argparse.ArgumentParser(description='Run faithfulness evaluation')
    parser.add_argument('--model', type=str, default="gpt-3.5-turbo",
                      help='Model to evaluate (e.g., gpt-4, gpt-4-1106-preview)')
    args = parser.parse_args()
    
    run_evaluation(model_name=args.model) 