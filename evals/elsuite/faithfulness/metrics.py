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
        # Load pre-trained model for text embedding
        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        self.model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        
        # Initialize NLTK resources
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """Initialize NLTK resources"""
        try:
            # Download necessary NLTK data
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
        except Exception as e:
            print(f"Warning: Failed to download NLTK data: {str(e)}")
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        try:
            return sent_tokenize(text)
        except Exception:
            # If NLTK sentence splitting fails, use simple method
            return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    
    def _get_stopwords(self) -> set:
        """Get stopwords"""
        try:
            return set(stopwords.words('english'))
        except Exception:
            # If unable to get NLTK stopwords, use basic stopword set
            return {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 
                   'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 
                   'to', 'was', 'were', 'will', 'with'}

    def get_embeddings(self, text: str) -> np.ndarray:
        """Get text embeddings"""
        inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state.mean(dim=1).detach().numpy()
        return embeddings

    def calculate_factual_accuracy(self, response: str, reference: str) -> float:
        """Calculate factual accuracy score
        
        Use semantic similarity to evaluate factual consistency between response and reference
        """
        response_emb = self.get_embeddings(response)
        reference_emb = self.get_embeddings(reference)
        
        similarity = cosine_similarity(response_emb, reference_emb)[0][0]
        return float(similarity)

    def calculate_logical_coherence(self, response: str) -> float:
        """Calculate logical coherence score
        
        Evaluate the internal logical structure of the response
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
        """Calculate context relevance score
        
        Evaluate the relevance of response to given context:
        1. Semantic relevance
        2. Key information coverage
        3. Topic consistency
        """
        # Semantic relevance score
        response_emb = self.get_embeddings(response)
        context_emb = self.get_embeddings(context)
        semantic_relevance = cosine_similarity(response_emb, context_emb)[0][0]
        
        # Key information coverage score
        def extract_key_info(text):
            # Extract named entities, numbers, and keywords
            entities = re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', text)
            numbers = re.findall(r'\d+(?:\.\d+)?%?', text)
            # Extract potential keywords (words starting with capital letters)
            keywords = re.findall(r'\b[A-Z][a-zA-Z]*\b', text)
            return set(entities + numbers + keywords)
        
        context_info = extract_key_info(context)
        response_info = extract_key_info(response)
        
        coverage_score = len(context_info.intersection(response_info)) / len(context_info) if context_info else 1.0
        
        # Topic consistency score
        def get_topic_words(text):
            # Get most important words (non-stopwords)
            words = text.lower().split()
            stop_words = self._get_stopwords()
            return set(word for word in words if word not in stop_words)
        
        context_topics = get_topic_words(context)
        response_topics = get_topic_words(response)
        
        topic_score = len(context_topics.intersection(response_topics)) / len(context_topics) if context_topics else 1.0
        
        # Final score
        final_score = (
            semantic_relevance * 0.4 +
            coverage_score * 0.3 +
            topic_score * 0.3
        )
        
        return float(final_score)

    def calculate_interpretative_reasoning(self, response: str, context: str) -> float:
        """Evaluate interpretative reasoning ability
        
        Assess if the model can make reasonable inferences and explanations based on context
        """
        # List of reasoning words
        reasoning_words = ['because', 'therefore', 'thus', 'since', 'as a result', 
                         'consequently', 'hence', 'so', 'due to', 'indicates']
        
        # Calculate usage of reasoning words
        reasoning_word_count = sum(1 for word in reasoning_words if word.lower() in response.lower())
        reasoning_word_score = min(reasoning_word_count / 3, 1.0)  # Count max 3 reasoning words
        
        # Evaluate completeness of reasoning process
        sentences = self._split_sentences(response)
        if len(sentences) < 2:  # Need at least 2 sentences for reasoning
            process_score = 0.0
        else:
            process_score = min((len(sentences) - 1) / 3, 1.0)  # Count max 4 sentences
        
        # Check if conclusion is based on context
        context_based_score = self.calculate_context_relevance(sentences[-1], context)
        
        # Final score
        final_score = (reasoning_word_score * 0.3 + 
                      process_score * 0.3 + 
                      context_based_score * 0.4)
        
        return float(final_score)

    def calculate_information_completeness(self, response: str, reference: str) -> float:
        """Evaluate information completeness
        
        Check if response contains all key information points from reference
        """
        # Get stopwords
        stop_words = self._get_stopwords()
        
        # Extract keywords (remove stopwords and punctuation)
        def extract_keywords(text: str) -> set:
            # Remove punctuation
            text = re.sub(r'[^\w\s]', '', text.lower())
            # Tokenize and remove stopwords
            words = set(word for word in text.split() if word not in stop_words)
            return words
        
        reference_keywords = extract_keywords(reference)
        response_keywords = extract_keywords(response)
        
        if not reference_keywords:
            return 0.0
        
        # Calculate keyword coverage
        coverage = len(response_keywords.intersection(reference_keywords)) / len(reference_keywords)
        
        # Evaluate information depth (by comparing sentence count)
        ref_sent_count = len(self._split_sentences(reference))
        resp_sent_count = len(self._split_sentences(response))
        depth_score = min(resp_sent_count / ref_sent_count, 1.0) if ref_sent_count > 0 else 0.0
        
        # Final score
        final_score = coverage * 0.7 + depth_score * 0.3
        
        return float(final_score)

    def calculate_hallucination_score(self, response: str, context: str) -> float:
        """Evaluate hallucination level (returns confidence score of no hallucination, higher is better)
        
        Detect if response contains information not present in context
        """
        response_sentences = self._split_sentences(response)
        
        # Calculate relevance of each sentence to context
        sentence_scores = []
        for sentence in response_sentences:
            if not sentence.strip():
                continue
            
            # Calculate similarity between sentence and context
            sentence_emb = self.get_embeddings(sentence)
            context_emb = self.get_embeddings(context)
            similarity = cosine_similarity(sentence_emb, context_emb)[0][0]
            sentence_scores.append(similarity)
        
        if not sentence_scores:
            return 0.0
        
        # Calculate no-hallucination confidence
        min_similarity = min(sentence_scores)
        avg_similarity = np.mean(sentence_scores)
        final_score = min_similarity * 0.6 + avg_similarity * 0.4
        
        return float(final_score)

    def calculate_overall_faithfulness(self, metrics: Dict[str, float]) -> float:
        """Calculate overall faithfulness score
        
        Adjust weights based on different scenario types
        """
        # Base weights
        base_weights = {
            "factual_accuracy": 0.25,
            "logical_coherence": 0.15,
            "context_relevance": 0.15,
            "interpretative_reasoning": 0.15,
            "information_completeness": 0.15,
            "hallucination_score": 0.15
        }
        
        # Dynamically adjust weights based on scores
        if metrics.get("factual_accuracy", 0) < 0.5:
            # If factual accuracy is low, increase its weight
            base_weights["factual_accuracy"] = 0.35
            base_weights["hallucination_score"] = 0.20
            # Reduce other weights accordingly
            for k in base_weights:
                if k not in ["factual_accuracy", "hallucination_score"]:
                    base_weights[k] = (1 - 0.55) / 4
        
        elif metrics.get("hallucination_score", 0) < 0.5:
            # If serious hallucination exists, increase hallucination score weight
            base_weights["hallucination_score"] = 0.25
            base_weights["factual_accuracy"] = 0.30
            # Reduce other weights accordingly
            for k in base_weights:
                if k not in ["hallucination_score", "factual_accuracy"]:
                    base_weights[k] = (1 - 0.55) / 4
        
        # Calculate weighted average score
        overall_score = sum(
            metrics[metric] * weight 
            for metric, weight in base_weights.items() 
            if metric in metrics
        )
        
        return float(overall_score)
