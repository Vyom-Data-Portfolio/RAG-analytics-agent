"""
RAG Retrieval Module
Handles semantic search and context retrieval from knowledge base
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json


class RAGRetriever:
    """Retrieves relevant context from knowledge base for SQL generation"""
    
    def __init__(
        self,
        db_path: str = "chroma_db",
        collection_name: str = "saas_analytics_kb",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize RAG retriever
        
        Args:
            db_path: Path to ChromaDB storage
            collection_name: Name of collection to query
            embedding_model: Sentence transformer model name
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Load embedding model
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Connect to ChromaDB
        try:
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Connected to ChromaDB collection: {collection_name}")
        except Exception as e:
            print(f"❌ Error connecting to ChromaDB: {e}")
            print("Run 'python embed_knowledge_base.py' first to create the database.")
            raise
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        filter_category: Optional[str] = None,
        similarity_threshold: float = 0.3
    ) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: User's natural language question
            k: Number of documents to retrieve
            filter_category: Optional category filter (e.g., "Revenue Metrics")
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of retrieved documents with metadata and scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Build filter if category specified
        where_filter = None
        if filter_category:
            where_filter = {"category": filter_category}
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            where=where_filter
        )
        
        # Format results
        retrieved_docs = []
        for doc, metadata, distance in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            # Convert distance to similarity (1 - cosine distance)
            similarity = 1 - distance
            
            # Filter by similarity threshold
            if similarity < similarity_threshold:
                continue
            
            retrieved_docs.append({
                'text': doc,
                'metadata': metadata,
                'similarity': similarity,
                'distance': distance
            })
        
        return retrieved_docs
    
    def format_context_for_prompt(
        self,
        retrieved_docs: List[Dict],
        max_context_length: int = 3000
    ) -> str:
        """
        Format retrieved documents into a context string for the LLM prompt
        
        Args:
            retrieved_docs: List of retrieved documents
            max_context_length: Maximum characters for context
            
        Returns:
            Formatted context string
        """
        if not retrieved_docs:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, doc in enumerate(retrieved_docs):
            # Create section header
            header = f"\n{'='*60}\n"
            header += f"RETRIEVED CONTEXT {i+1}\n"
            header += f"Source: {doc['metadata']['filename']}\n"
            header += f"Category: {doc['metadata']['category']}\n"
            header += f"Relevance: {doc['similarity']:.2f}\n"
            header += f"{'='*60}\n\n"
            
            # Add document text
            doc_text = doc['text']
            
            section = header + doc_text
            
            # Check if adding this section exceeds max length
            if current_length + len(section) > max_context_length:
                # Truncate if this is the first doc, otherwise stop
                if i == 0:
                    remaining = max_context_length - current_length - len(header)
                    truncated_text = doc_text[:remaining] + "\n...[truncated]"
                    context_parts.append(header + truncated_text)
                break
            
            context_parts.append(section)
            current_length += len(section)
        
        return "\n".join(context_parts)
    
    def retrieve_for_sql_generation(
        self,
        question: str,
        k: int = 5,
        include_examples: bool = True,
        include_metrics: bool = True,
        include_schema: bool = True,
        include_business_logic: bool = True
    ) -> str:
        """
        Retrieve context specifically for SQL generation
        
        Args:
            question: User's natural language question
            k: Total number of documents to retrieve
            include_examples: Include example query pairs
            include_metrics: Include metric definitions
            include_schema: Include schema documentation
            include_business_logic: Include business logic rules
            
        Returns:
            Formatted context string for LLM prompt
        """
        # Determine what to search for based on question
        all_docs = []
        
        # Always search general collection
        general_docs = self.retrieve(query=question, k=k)
        all_docs.extend(general_docs)
        
        # Optional: Add category-specific searches
        # This ensures we get diverse relevant content
        
        # Remove duplicates (same chunk retrieved multiple times)
        seen_ids = set()
        unique_docs = []
        for doc in all_docs:
            doc_id = doc['metadata'].get('filepath', '') + str(doc['text'][:100])
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_docs.append(doc)
        
        # Sort by similarity
        unique_docs.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Take top k
        top_docs = unique_docs[:k]
        
        # Format for prompt
        context = self.format_context_for_prompt(top_docs)
        
        return context
    
    def get_statistics(self) -> Dict:
        """Get statistics about the knowledge base"""
        try:
            count = self.collection.count()
            
            # Get sample to analyze categories
            sample = self.collection.get(limit=1000)
            
            categories = {}
            file_types = {}
            
            for metadata in sample['metadatas']:
                # Count by category
                cat = metadata.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
                
                # Count by file type
                ftype = metadata.get('file_type', 'Unknown')
                file_types[ftype] = file_types.get(ftype, 0) + 1
            
            return {
                'total_chunks': count,
                'categories': categories,
                'file_types': file_types,
                'collection_name': self.collection_name,
                'db_path': self.db_path
            }
        except Exception as e:
            return {'error': str(e)}


def test_retriever():
    """Test the RAG retriever"""
    print("\n" + "="*60)
    print("TESTING RAG RETRIEVER")
    print("="*60 + "\n")
    
    # Initialize retriever
    retriever = RAGRetriever()
    
    # Get statistics
    stats = retriever.get_statistics()
    print("Knowledge Base Statistics:")
    print(f"  Total chunks: {stats['total_chunks']}")
    print(f"  Categories: {stats['categories']}")
    print(f"  File types: {stats['file_types']}")
    print()
    
    # Test queries
    test_queries = [
        "What is MRR and how do I calculate it?",
        "Show me revenue by plan tier",
        "How do I calculate churn rate?",
        "Which customers are at high risk of churning?",
        "What's the best way to join users and subscriptions?"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {query}")
        print("="*60)
        
        # Retrieve documents
        docs = retriever.retrieve(query, k=3)
        
        print(f"\nRetrieved {len(docs)} documents:\n")
        
        for i, doc in enumerate(docs):
            print(f"{i+1}. {doc['metadata']['filename']} - {doc['metadata']['category']}")
            print(f"   Similarity: {doc['similarity']:.3f}")
            print(f"   Preview: {doc['text'][:150]}...")
            print()
        
        # Show formatted context
        print("\n--- FORMATTED CONTEXT FOR LLM ---\n")
        context = retriever.retrieve_for_sql_generation(query, k=3)
        print(context[:500] + "...\n")
        
        input("Press Enter for next query...")


if __name__ == "__main__":
    test_retriever()
