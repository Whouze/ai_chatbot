import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

from utils.knowledge_loader import load_knowledge_base
from utils.logger import logger


def sigmoid(x: float | np.ndarray):
    """Converts raw CrossEncoder logits into a normalized 0.0 - 1.0 probability score."""
    return 1 / (1 + np.exp(-x))


class RagService:
    """RAG Service combining Hybrid Search (Semantic + TF-IDF) and CrossEncoder Reranking."""

    def __init__(self, knowledge_file_path=None):
        logger.info("Initializing RagService (Loading SentenceTransformer & CrossEncoder models)...")
        self.model_emb = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-base"
        )

        self.kb_texts = load_knowledge_base(knowledge_file_path)

        if self.kb_texts:
            self.doc_embeddings = self.model_emb.encode(self.kb_texts)
        else:
            self.doc_embeddings = np.array([])

    def retrieve_with_rerank(self, query: str, top_k: int = 10, threshold: float = 0.6, normalize: bool = True):
        """
        Retrieves relevant context using hybrid search (Semantic + TF-IDF)
        and reranks candidates using CrossEncoder.
        
        - If normalize=True (default): returns a normalized score between 0.0 and 1.0 (recommended threshold ~0.6).
        - If normalize=False: returns raw logits score (recommended threshold ~2.5).
        """
        if not self.kb_texts or len(self.doc_embeddings) == 0:
            logger.warning("Knowledge base is empty. Skipping RAG retrieval.")
            return None, 0.0

        query_emb = self.model_emb.encode([query])
        semantic_scores = cosine_similarity(query_emb, self.doc_embeddings)[0]

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(self.kb_texts + [query])
        keyword_scores = cosine_similarity(
            tfidf_matrix[-1:], 
            tfidf_matrix[:-1]
        )[0]

        # Ubah dari 0.5 & 0.5 menjadi 0.85 Semantic (Multilingual) & 0.15 TF-IDF
        combined_scores = 0.85 * semantic_scores + 0.15 * keyword_scores

        top_k_indices = np.argsort(combined_scores)[-top_k:][::-1]
        candidates = [self.kb_texts[i] for i in top_k_indices]

        pairs = [(query, doc) for doc in candidates]
        raw_rerank_scores = self.reranker.predict(pairs)

        best_idx = int(np.argmax(raw_rerank_scores))
        raw_score = float(raw_rerank_scores[best_idx])

        # Normalize raw logits (-inf to +inf) into a probability score (0.0 to 1.0) using Sigmoid
        final_score = float(sigmoid(raw_score)) if normalize else raw_score

        if final_score >= threshold:
            logger.info(f"RAG match found with score {final_score:.4f} (Raw Logit: {raw_score:.4f})")
            return candidates[best_idx], final_score

        logger.info(f"No RAG match met threshold {threshold} (Best score: {final_score:.4f}, Raw Logit: {raw_score:.4f})")
        return None, final_score