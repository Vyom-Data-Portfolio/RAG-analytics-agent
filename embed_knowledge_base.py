"""
Vector Embedding Script for RAG Analytics Agent
Embeds knowledge base documents into ChromaDB for semantic search
"""

import os
import json
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import tiktoken

class KnowledgeBaseEmbedder:
    """Handles embedding and storage of knowledge base documents"""
    
    def __init__(
        self,
        kb_path: str = "knowledge_base",
        db_path: str = "chroma_db",
        collection_name: str = "saas_analytics_kb",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500,
        chunk_overlap: int = 50
    ):
        """
        Initialize the embedder
        
        Args:
            kb_path: Path to knowledge base directory
            db_path: Path to ChromaDB storage
            collection_name: Name of ChromaDB collection
            embedding_model: Sentence transformer model name
            chunk_size: Max tokens per chunk
            chunk_overlap: Overlapping tokens between chunks
        """
        self.kb_path = Path(kb_path)
        self.db_path = db_path
        self.collection_name = collection_name
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding model
        print(f"Loading embedding model: {embedding_model}...")
        self.embedding_model = SentenceTransformer(embedding_model)
        
        # Initialize ChromaDB client
        print(f"Initializing ChromaDB at {db_path}...")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "SaaS Analytics Knowledge Base"}
        )
        
        # Initialize tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))
    
    def chunk_text(self, text: str, metadata: Dict) -> List[Dict]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            metadata: Metadata to attach to each chunk
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Split by lines first
        lines = text.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for line in lines:
            line_tokens = self.count_tokens(line)
            
            # If single line exceeds chunk size, split it
            if line_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append({
                        'text': '\n'.join(current_chunk),
                        'metadata': metadata.copy()
                    })
                    current_chunk = []
                    current_tokens = 0
                
                # Split long line by sentences or words
                words = line.split()
                temp_chunk = []
                temp_tokens = 0
                
                for word in words:
                    word_tokens = self.count_tokens(word)
                    if temp_tokens + word_tokens > self.chunk_size:
                        chunks.append({
                            'text': ' '.join(temp_chunk),
                            'metadata': metadata.copy()
                        })
                        # Keep overlap
                        overlap_words = temp_chunk[-10:] if len(temp_chunk) > 10 else temp_chunk
                        temp_chunk = overlap_words + [word]
                        temp_tokens = self.count_tokens(' '.join(temp_chunk))
                    else:
                        temp_chunk.append(word)
                        temp_tokens += word_tokens
                
                if temp_chunk:
                    chunks.append({
                        'text': ' '.join(temp_chunk),
                        'metadata': metadata.copy()
                    })
                continue
            
            # Check if adding this line exceeds chunk size
            if current_tokens + line_tokens > self.chunk_size:
                # Save current chunk
                chunks.append({
                    'text': '\n'.join(current_chunk),
                    'metadata': metadata.copy()
                })
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-3:] if len(current_chunk) > 3 else current_chunk
                current_chunk = overlap_lines + [line]
                current_tokens = self.count_tokens('\n'.join(current_chunk))
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
        
        # Add final chunk
        if current_chunk:
            chunks.append({
                'text': '\n'.join(current_chunk),
                'metadata': metadata.copy()
            })
        
        return chunks
    
    def load_markdown_file(self, filepath: Path) -> List[Dict]:
        """Load and chunk a markdown file"""
        print(f"  Loading {filepath.name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract file category from name
        category = filepath.stem.replace('_', ' ').title()
        
        metadata = {
            'filename': filepath.name,
            'filepath': str(filepath),
            'category': category,
            'file_type': 'markdown'
        }
        
        chunks = self.chunk_text(content, metadata)
        print(f"    Created {len(chunks)} chunks")
        
        return chunks
    
    def load_json_file(self, filepath: Path) -> List[Dict]:
        """Load and process JSON example queries"""
        print(f"  Loading {filepath.name}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            examples = json.load(f)
        
        chunks = []
        for example in examples:
            # Create searchable text combining question, SQL, and context
            text = f"""Question: {example['question']}
SQL: {example['sql']}
Explanation: {example['explanation']}
Business Context: {example['business_context']}
Category: {example['category']}"""
            
            metadata = {
                'filename': filepath.name,
                'filepath': str(filepath),
                'category': example['category'],
                'file_type': 'example',
                'example_id': example['id'],
                'question': example['question']
            }
            
            chunks.append({
                'text': text,
                'metadata': metadata
            })
        
        print(f"    Created {len(chunks)} example chunks")
        return chunks
    
    def embed_knowledge_base(self):
        """Embed all knowledge base files into ChromaDB"""
        print(f"\n{'='*60}")
        print("EMBEDDING KNOWLEDGE BASE")
        print(f"{'='*60}\n")
        
        all_chunks = []
        
        # Load markdown files
        markdown_files = [
            'metrics.md',
            'schema_docs.md', 
            'business_logic.md',
            'README.md'
        ]
        
        for filename in markdown_files:
            filepath = self.kb_path / filename
            if filepath.exists():
                chunks = self.load_markdown_file(filepath)
                all_chunks.extend(chunks)
            else:
                print(f"  WARNING: {filename} not found")
        
        # Load JSON examples
        json_file = self.kb_path / 'examples.json'
        if json_file.exists():
            chunks = self.load_json_file(json_file)
            all_chunks.extend(chunks)
        else:
            print(f"  WARNING: examples.json not found")
        
        print(f"\n{'='*60}")
        print(f"TOTAL CHUNKS: {len(all_chunks)}")
        print(f"{'='*60}\n")
        
        if not all_chunks:
            print("ERROR: No chunks created. Check knowledge_base directory.")
            return
        
        # Prepare data for ChromaDB
        print("Generating embeddings...")
        texts = [chunk['text'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        ids = [f"chunk_{i}" for i in range(len(all_chunks))]
        
        # Generate embeddings (batch processing for efficiency)
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            embeddings = self.embedding_model.encode(
                batch,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            all_embeddings.extend(embeddings.tolist())
            print(f"  Embedded {min(i+batch_size, len(texts))}/{len(texts)} chunks")
        
        # Clear existing collection
        print("\nClearing existing collection...")
        existing_ids = self.collection.get()['ids']
        if existing_ids:
            self.collection.delete(ids=existing_ids)
            print(f"  Deleted {len(existing_ids)} existing chunks")
        
        # Add to ChromaDB
        print("\nAdding to ChromaDB...")
        self.collection.add(
            ids=ids,
            embeddings=all_embeddings,
            documents=texts,
            metadatas=metadatas
        )
        
        print(f"\n{'='*60}")
        print("✅ EMBEDDING COMPLETE")
        print(f"{'='*60}")
        print(f"Collection: {self.collection_name}")
        print(f"Total chunks: {len(all_chunks)}")
        print(f"Database path: {self.db_path}")
        print(f"{'='*60}\n")
        
        # Print summary by category
        from collections import Counter
        categories = [chunk['metadata']['category'] for chunk in all_chunks]
        category_counts = Counter(categories)
        
        print("Chunks by category:")
        for category, count in category_counts.most_common():
            print(f"  {category}: {count} chunks")
    
    def test_retrieval(self, query: str, k: int = 3):
        """Test retrieval with a sample query"""
        print(f"\n{'='*60}")
        print(f"TEST QUERY: '{query}'")
        print(f"{'='*60}\n")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Display results
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"Result {i+1}:")
            print(f"  Category: {metadata['category']}")
            print(f"  File: {metadata['filename']}")
            print(f"  Similarity: {1 - distance:.3f}")
            print(f"  Preview: {doc[:200]}...")
            print()


def main():
    """Main execution"""
    # Initialize embedder
    embedder = KnowledgeBaseEmbedder(
        kb_path="knowledge_base",
        db_path="chroma_db",
        collection_name="saas_analytics_kb",
        chunk_size=500,
        chunk_overlap=50
    )
    
    # Embed knowledge base
    embedder.embed_knowledge_base()
    
    # Test retrieval with sample queries
    test_queries = [
        "What is MRR and how do I calculate it?",
        "Show me customers by industry",
        "How do I join users and subscriptions tables?",
        "What's the churn rate formula?",
        "Show me high-value customers at risk"
    ]
    
    print("\n" + "="*60)
    print("TESTING RETRIEVAL")
    print("="*60)
    
    for query in test_queries:
        embedder.test_retrieval(query, k=3)
        input("Press Enter for next test query...")


if __name__ == "__main__":
    main()
