"""
RAG (Retrieval Augmented Generation) Pipeline
Implements vector storage and LLM-based question answering
"""
import json
import numpy as np
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator
        
        Args:
            model_name: Name of the sentence-transformer model
        """
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded embedding model: {model_name}")
        except ImportError:
            logger.warning("sentence-transformers not installed. Install with: pip install sentence-transformers")
            self.model = None
    
    def generate_embeddings(self, texts: List[str]) -> Optional[np.ndarray]:
        """
        Generate embeddings for list of texts
        
        Returns:
            NumPy array of shape (len(texts), embedding_dim) or None if model not available
        """
        if self.model is None:
            logger.warning("Embedding model not loaded - returning None")
            return None
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return np.array(embeddings)
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
    
    def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for a single text - returns None if model not available"""
        if self.model is None:
            logger.warning("Embedding model not loaded - returning None")
            return None
        
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return np.array(embedding)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None


class SimpleVectorStore:
    """Simple FAISS-like vector store for demonstration"""
    
    def __init__(self):
        self.texts = []
        self.embeddings = []
        self.metadata = []
    
    def add_documents(self, texts: List[str], embeddings: np.ndarray, metadata: List[Dict] = None):
        """
        Add documents and their embeddings to the store
        
        Args:
            texts: List of text chunks
            embeddings: NumPy array of embeddings
            metadata: Optional list of metadata dictionaries
        """
        if metadata is None:
            metadata = [{"index": i} for i in range(len(texts))]
        
        self.texts.extend(texts)
        self.embeddings.extend(embeddings)
        self.metadata.extend(metadata)
        
        logger.info(f"Added {len(texts)} documents to vector store")
    
    def similarity_search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict]:
        """
        Find top-k most similar documents to query
        
        Returns:
            List of dictionaries with text, score, and metadata
        """
        if not self.embeddings:
            return []
        
        embeddings_array = np.array(self.embeddings)
        
        # Calculate cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        similarities = []
        
        for emb in embeddings_array:
            emb_norm = emb / np.linalg.norm(emb)
            similarity = np.dot(query_norm, emb_norm)
            similarities.append(similarity)
        
        # Get top-k indices
        similarities = np.array(similarities)
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            results.append({
                "text": self.texts[idx],
                "score": float(similarities[idx]),
                "metadata": self.metadata[idx]
            })
        
        return results
    
    def save(self, path: str):
        """Save vector store to disk"""
        data = {
            "texts": self.texts,
            "embeddings": [emb.tolist() if isinstance(emb, np.ndarray) else emb 
                          for emb in self.embeddings],
            "metadata": self.metadata
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f)
        logger.info(f"Saved vector store to {path}")
    
    def load(self, path: str):
        """Load vector store from disk"""
        with open(path, 'r') as f:
            data = json.load(f)
        
        self.texts = data["texts"]
        self.embeddings = [np.array(emb) for emb in data["embeddings"]]
        self.metadata = data["metadata"]
        logger.info(f"Loaded vector store from {path}")


class RAGPipeline:
    """End-to-end RAG pipeline for financial QA"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize RAG pipeline"""
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        self.vector_store = SimpleVectorStore()
        self.context_k = 5  # Number of context documents to retrieve
    
    def index_documents(self, chunks: List[str], metadata: List[Dict] = None):
        """
        Index document chunks for retrieval
        
        Args:
            chunks: List of text chunks
            metadata: Optional metadata for each chunk
        """
        logger.info(f"Indexing {len(chunks)} document chunks...")
        
        embeddings = self.embedding_generator.generate_embeddings(chunks)
        
        # If embeddings not available, create placeholder embeddings
        if embeddings is None:
            logger.warning("Embeddings not available - using placeholder embeddings")
            embeddings = np.zeros((len(chunks), 384))  # 384-dim placeholder
        
        self.vector_store.add_documents(chunks, embeddings, metadata)
        
        logger.info("Indexing complete")
    
    def retrieve_context(self, query: str, k: int = None) -> List[Dict]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            k: Number of documents to retrieve (uses self.context_k if not specified)
        
        Returns:
            List of relevant document chunks with metadata
        """
        if k is None:
            k = self.context_k
        
        query_embedding = self.embedding_generator.generate_embedding(query)
        
        # If embeddings not available, return first k chunks
        if query_embedding is None:
            logger.warning("Query embedding not available - returning first k chunks")
            results = []
            for i in range(min(k, len(self.vector_store.texts))):
                results.append({
                    "text": self.vector_store.texts[i],
                    "score": 0.0,
                    "metadata": self.vector_store.metadata[i] if i < len(self.vector_store.metadata) else {}
                })
            return results
        
        results = self.vector_store.similarity_search(query_embedding, k=k)
        
        return results
    
    def generate_prompt(self, query: str, context: List[Dict]) -> str:
        """
        Generate LLM prompt with retrieved context
        
        Args:
            query: User query
            context: Retrieved context documents
        
        Returns:
            Formatted prompt for LLM
        """
        context_text = "\n".join([f"[Context {i+1}]\n{doc['text'][:300]}" 
                                 for i, doc in enumerate(context)])
        
        prompt = f"""You are a financial analyst AI assistant. Answer the following question based on the provided financial document context.

QUESTION: {query}

FINANCIAL DOCUMENT CONTEXT:
{context_text}

ANSWER:"""
        
        return prompt
    
    def answer_question(self, query: str, use_openai: bool = False) -> Dict:
        """
        Answer a question using retrieved context and LLM
        
        Args:
            query: User query
            use_openai: Whether to use OpenAI API (requires API key)
        
        Returns:
            Dictionary with answer and source documents
        """
        # Retrieve context
        context = self.retrieve_context(query)
        
        if not context:
            return {
                "query": query,
                "answer": "No relevant information found in the documents.",
                "sources": [],
                "confidence": 0
            }
        
        # Generate prompt
        prompt = self.generate_prompt(query, context)
        
        # Generate answer
        if use_openai:
            try:
                answer = self._call_openai_api(prompt)
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                answer = self._generate_simple_answer(query, context)
        else:
            answer = self._generate_simple_answer(query, context)
        
        return {
            "query": query,
            "answer": answer,
            "sources": [{"text": doc["text"][:100], "score": doc["score"]} 
                       for doc in context],
            "confidence": float(np.mean([doc["score"] for doc in context]))
        }
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API for answer generation"""
        try:
            import openai
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")
            
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a financial analyst AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _generate_simple_answer(self, query: str, context: List[Dict]) -> str:
        """
        Generate simple answer from context (fallback)
        """
        query_lower = query.lower()
        
        # Simple keyword matching for common questions
        if "revenue" in query_lower:
            return f"Based on the financial documents, the relevant revenue information is found in the retrieved context above. This appears to be the most relevant information about {query}."
        elif "risk" in query_lower:
            return f"The financial documents highlight several risks. Based on the retrieved context, here are the key risks mentioned related to {query}."
        elif "debt" in query_lower or "liquidity" in query_lower:
            return f"Regarding {query}, the documents indicate the following based on the retrieved financial information."
        else:
            return f"Based on the retrieved financial document context, {query} can be analyzed as follows from the provided information."
    
    def save_index(self, path: str):
        """Save the vector index to disk"""
        self.vector_store.save(path)
    
    def load_index(self, path: str):
        """Load the vector index from disk"""
        self.vector_store.load(path)
