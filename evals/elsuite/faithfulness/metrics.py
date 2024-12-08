from typing import List, Dict, Any
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity

class FaithfulnessMetrics:
    def __init__(self):
        # 加载预训练模型用于文本嵌入
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    
    def get_embeddings(self, text: str) -> np.ndarray:
        """获取文本的嵌入向量"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings

    def calculate_factual_accuracy(self, response: str, reference: str) -> float:
        """计算事实准确性分数
        
        使用语义相似度来评估响应与参考之间的事实一致性
        """
        response_emb = self.get_embeddings(response)
        reference_emb = self.get_embeddings(reference)
        
        similarity = cosine_similarity(response_emb, reference_emb)[0][0]
        return float(similarity)

    def calculate_logical_coherence(self, response: str) -> float:
        """计算逻辑连贯性分数
        
        评估响应内部的逻辑结构
        """
        sentences = response.split('.')
        if len(sentences) <= 1:
            return 1.0
        
        coherence_scores = []
        for i in range(len(sentences)-1):
            if not sentences[i].strip() or not sentences[i+1].strip():
                continue
            emb1 = self.get_embeddings(sentences[i])
            emb2 = self.get_embeddings(sentences[i+1])
            score = cosine_similarity(emb1, emb2)[0][0]
            coherence_scores.append(score)
        
        return float(np.mean(coherence_scores)) if coherence_scores else 0.0

    def calculate_context_relevance(self, response: str, context: str) -> float:
        """计算上下文相关性分数
        
        评估响应与给定上下文的相关程度
        """
        response_emb = self.get_embeddings(response)
        context_emb = self.get_embeddings(context)
        
        similarity = cosine_similarity(response_emb, context_emb)[0][0]
        return float(similarity)

    def calculate_overall_faithfulness(self, metrics: Dict[str, float]) -> float:
        """计算综合忠实度分数"""
        weights = {
            "factual_accuracy": 0.4,
            "logical_coherence": 0.3,
            "context_relevance": 0.3
        }
        
        overall_score = sum(
            metrics[metric] * weight 
            for metric, weight in weights.items() 
            if metric in metrics
        )
        
        return float(overall_score)
