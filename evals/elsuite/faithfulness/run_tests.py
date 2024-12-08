#!/usr/bin/env python3
import os
import sys
from .test_eval import run_tests
import logging

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('faithfulness_test.log')
        ]
    )

def main():
    """主函数"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("开始运行忠实度评估框架测试...")
    
    try:
        # 运行测试
        run_tests()
        logger.info("测试完成")
        
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 