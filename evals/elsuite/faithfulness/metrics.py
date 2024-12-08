from typing import List, Dict, Any
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
import re

class FaithfulnessMetrics:
    def __init__(self):
        # 加载预训练模型用于文本嵌入
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        # 初始化NLTK资源
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """初始化NLTK资源"""
        try:
            # 下载必要的NLTK数据
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Warning: Failed to download NLTK data: {str(e)}")
    
    def _split_sentences(self, text: str) -> List[str]:
        """分割文本为句子"""
        try:
            return sent_tokenize(text)
        except Exception:
            # 如果NLTK分句失败，使用简单的分句方法
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _get_stopwords(self) -> set:
        """获取停用词"""
        try:
            return set(stopwords.words('english'))
        except Exception:
            # 如果无法获取NLTK停用词，使用基本的停用词集合
            return {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
                   'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
                   'to', 'was', 'were', 'will', 'with'}

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
        sentences = self._split_sentences(response)
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
        
        评估响应与给定上下文的相关程度:
        1. 语义相关性
        2. 关键信息覆盖
        3. 主题一致性
        """
        # 语义相关性评分
        response_emb = self.get_embeddings(response)
        context_emb = self.get_embeddings(context)
        semantic_relevance = cosine_similarity(response_emb, context_emb)[0][0]
        
        # 关键信息覆盖评分
        def extract_key_info(text):
            # 提取命名实体、数字和关键词
            entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)
            numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
            # 提取可能的关键词（大写字母开头的词）
            keywords = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
            return set(entities + numbers + keywords)
        
        context_info = extract_key_info(context)
        response_info = extract_key_info(response)
        
        coverage_score = len(context_info.intersection(response_info)) / len(context_info) if context_info else 1.0
        
        # 主题一致性评分
        def get_topic_words(text):
            # 获取文本中最重要的词（非停用词）
            words = text.lower().split()
            stop_words = self._get_stopwords()
            return set(word for word in words if word not in stop_words)
        
        context_topics = get_topic_words(context)
        response_topics = get_topic_words(response)
        
        topic_score = len(context_topics.intersection(response_topics)) / len(context_topics) if context_topics else 1.0
        
        # 综合评分
        final_score = (
            semantic_relevance * 0.4 +
            coverage_score * 0.3 +
            topic_score * 0.3
        )
        
        return float(final_score)

    def calculate_interpretative_reasoning(self, response: str, context: str) -> float:
        """评估解释性推理能力
        
        评估模型是否能基于上下文进行合理的推理和解释
        """
        # 推理性词汇列表
        reasoning_words = ['because', 'therefore', 'thus', 'since', 'as a result', 
                         'consequently', 'hence', 'so', 'due to', 'indicates']
        
        # 计算推理性词汇的使用情况
        reasoning_word_count = sum(1 for word in reasoning_words if word.lower() in response.lower())
        reasoning_word_score = min(reasoning_word_count / 3, 1.0)  # 最多计算3个推理词
        
        # 评估推理过程的完整性
        sentences = self._split_sentences(response)
        if len(sentences) < 2:  # 至少需要两个句子才能构成推理
            process_score = 0.0
        else:
            process_score = min((len(sentences) - 1) / 3, 1.0)  # 最多计算4个句子
        
        # 检查结论是否基于上下文
        context_based_score = self.calculate_context_relevance(sentences[-1], context)
        
        # 综合得分
        final_score = (reasoning_word_score * 0.3 + 
                      process_score * 0.3 + 
                      context_based_score * 0.4)
        
        return float(final_score)

    def calculate_information_completeness(self, response: str, reference: str) -> float:
        """评估信息完整性
        
        检查响应是否包含了参考答案中的所有关键信息点
        """
        # 获取停用词
        stop_words = self._get_stopwords()
        
        # 提取关键词（去除停用词和标点符号）
        def extract_keywords(text: str) -> set:
            # 移除标点符号
            text = re.sub(r'[^\w\s]', '', text.lower())
            # 分词并去除停用词
            words = set(word for word in text.split() if word not in stop_words)
            return words
        
        reference_keywords = extract_keywords(reference)
        response_keywords = extract_keywords(response)
        
        if not reference_keywords:
            return 0.0
        
        # 计算关键词覆盖率
        coverage = len(response_keywords.intersection(reference_keywords)) / len(reference_keywords)
        
        # 评估信息深度（通过比较句子数量）
        ref_sent_count = len(self._split_sentences(reference))
        resp_sent_count = len(self._split_sentences(response))
        depth_score = min(resp_sent_count / ref_sent_count, 1.0) if ref_sent_count > 0 else 0.0
        
        # 综合得分
        final_score = coverage * 0.7 + depth_score * 0.3
        
        return float(final_score)

    def calculate_hallucination_score(self, response: str, context: str) -> float:
        """评估幻觉程度（返回无幻觉的置信度，越高越好）
        
        检测响应中是否包含上下文中不存在的信息
        """
        response_sentences = self._split_sentences(response)
        
        # 计算每个句子与上下文的相关性
        sentence_scores = []
        for sentence in response_sentences:
            if not sentence.strip():
                continue
            
            # 计算句子与上下文的相似度
            sentence_emb = self.get_embeddings(sentence)
            context_emb = self.get_embeddings(context)
            similarity = cosine_similarity(sentence_emb, context_emb)[0][0]
            sentence_scores.append(similarity)
        
        if not sentence_scores:
            return 0.0
        
        # 计算无幻觉置信度
        min_similarity = min(sentence_scores)
        avg_similarity = np.mean(sentence_scores)
        final_score = min_similarity * 0.6 + avg_similarity * 0.4
        
        return float(final_score)

    def calculate_overall_faithfulness(self, metrics: Dict[str, float]) -> float:
        """计算综合忠实度分数
        
        根据不同场景类型调整权重
        """
        # 基础权重
        base_weights = {
            "factual_accuracy": 0.25,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.15,
            "hallucination_score": 0.15
        }
        
        # 根据评分情况动态调整权重
        if metrics.get("factual_accuracy", 0) < 0.5:
            # 如果事实准确性较低，增加其权重
            base_weights["factual_accuracy"] = 0.35
            base_weights["hallucination_score"] = 0.20
            # 相应减少其他权重
            for k in base_weights:
                if k not in ["factual_accuracy", "hallucination_score"]:
                    base_weights[k] = (1 - 0.55) / 4
        
        elif metrics.get("hallucination_score", 0) < 0.5:
            # 如果存在严重幻觉，增加幻觉分数的权重
            base_weights["hallucination_score"] = 0.25
            base_weights["factual_accuracy"] = 0.30
            # 相应减少其他权重
            for k in base_weights:
                if k not in ["hallucination_score", "factual_accuracy"]:
                    base_weights[k] = (1 - 0.55) / 4
        
        # 计算加权平均分
        overall_score = sum(
            metrics[metric] * weight 
            for metric, weight in base_weights.items() 
            if metric in metrics
        )
        
        return float(overall_score)
