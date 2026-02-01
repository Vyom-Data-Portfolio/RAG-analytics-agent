"""
Enhanced RAG Analytics Agent
Integrates retrieval-augmented generation for improved SQL accuracy
Compatible with LangChain 0.1.x+
"""

import os
import sqlite3
from typing import Dict, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Import RAG retriever
try:
    from rag_retriever import RAGRetriever
    RAG_AVAILABLE = True
except ImportError:
    print("⚠️  RAG retriever not available. Run without RAG enhancement.")
    RAG_AVAILABLE = False


class RAGAnalyticsAgent:
    """Text-to-SQL agent with RAG enhancement - Simplified version"""
    
    def __init__(
        self,
        db_path: str,
        use_rag: bool = True,
        rag_k: int = 5,
        model_name: str = "claude-sonnet-4-20250514"
    ):
        """
        Initialize the agent
        
        Args:
            db_path: Path to SQLite database
            use_rag: Whether to use RAG enhancement
            rag_k: Number of documents to retrieve
            model_name: Claude model to use
        """
        load_dotenv()
        
        self.db_path = db_path
        self.use_rag = use_rag and RAG_AVAILABLE
        self.rag_k = rag_k
        
        # Initialize RAG retriever if enabled
        if self.use_rag:
            try:
                self.retriever = RAGRetriever()
                print("✅ RAG enhancement enabled")
            except Exception as e:
                print(f"⚠️  RAG initialization failed: {e}")
                print("   Falling back to standard mode")
                self.use_rag = False
        else:
            self.retriever = None
            print("ℹ️  Running in standard mode (no RAG)")
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            model=model_name,
            temperature=0,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Get database schema
        self.schema = self._get_schema()
    
    def _get_schema(self) -> str:
        """Get database schema as string"""
        # For now, return a sample schema since we don't have the DB yet
        return """
DATABASE SCHEMA:

users:
  - user_id (INTEGER, PRIMARY KEY)
  - email (TEXT)
  - company_name (TEXT)
  - industry (TEXT)
  - company_size (TEXT)
  - signup_date (DATE)
  - country (TEXT)
  - status (TEXT)

subscriptions:
  - subscription_id (INTEGER, PRIMARY KEY)
  - user_id (INTEGER, FOREIGN KEY)
  - plan_id (INTEGER, FOREIGN KEY)
  - status (TEXT)
  - start_date (DATE)
  - end_date (DATE)
  - billing_cycle (TEXT)
  - amount (DECIMAL)
  - cancellation_reason (TEXT)

plans:
  - plan_id (INTEGER, PRIMARY KEY)
  - plan_name (TEXT)
  - plan_tier (TEXT)
  - monthly_price (DECIMAL)
  - annual_price (DECIMAL)
"""
    
    def _generate_sql(self, question: str) -> str:
        """Generate SQL from natural language question"""
        
        # Retrieve context if RAG enabled
        rag_context = ""
        if self.use_rag and self.retriever:
            rag_context = self.retriever.retrieve_for_sql_generation(
                question,
                k=self.rag_k
            )
        
        prompt = f"""You are a SQL expert. Generate a SQL query for this question.

{rag_context}

DATABASE SCHEMA:
{self.schema}

QUESTION: {question}

IMPORTANT RULES:
1. Only use tables and columns from the schema above
2. For revenue metrics, normalize billing cycles (annual/12, quarterly/3)
3. Filter for active subscriptions unless otherwise specified
4. Use DISTINCT for user counts to avoid double-counting
5. Follow any business logic rules from the retrieved context

Generate ONLY the SQL query, no explanations:
"""
        
        response = self.llm.invoke(prompt)
        sql = response.content.strip()
        
        # Clean up SQL (remove markdown code blocks if present)
        if sql.startswith("```sql"):
            sql = sql.split("```sql")[1].split("```")[0].strip()
        elif sql.startswith("```"):
            sql = sql.split("```")[1].split("```")[0].strip()
        
        return sql
    
    def _execute_query(self, sql: str) -> str:
        """Execute SQL query and return results"""
        if not os.path.exists(self.db_path):
            return f"Database not found at {self.db_path}. Please create it first with generate_data.py"
        
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if df.empty:
                return "Query executed successfully but returned no results."
            
            # Format results
            result = f"Query Results ({len(df)} rows):\n\n"
            result += df.to_string(index=False)
            
            return result
            
        except Exception as e:
            return f"Error executing query: {str(e)}"
    
    def query(self, question: str) -> Dict:
        """
        Process a natural language query
        
        Args:
            question: User's question
            
        Returns:
            Dict with results, SQL, and metadata
        """
        print(f"\n{'='*60}")
        print(f"QUERY: {question}")
        print('='*60)
        
        # Get RAG context if enabled
        retrieved_docs = []
        
        if self.use_rag and self.retriever:
            retrieved_docs = self.retriever.retrieve(question, k=self.rag_k)
            if retrieved_docs:
                print(f"📚 Retrieved {len(retrieved_docs)} relevant documents")
                print(f"   Sources: {', '.join(set(doc['metadata']['filename'] for doc in retrieved_docs[:3]))}")
        
        try:
            # Generate SQL
            print("\n🔨 Generating SQL...")
            sql = self._generate_sql(question)
            print(f"\n📝 Generated SQL:")
            print(f"   {sql}\n")
            
            # Execute SQL
            print("⚙️  Executing query...")
            results = self._execute_query(sql)
            print(f"\n✅ Results:")
            print(results)
            
            return {
                "success": True,
                "sql": sql,
                "results": results,
                "rag_enabled": self.use_rag,
                "retrieved_docs": len(retrieved_docs),
                "rag_sources": [doc['metadata']['filename'] for doc in retrieved_docs[:3]]
            }
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "rag_enabled": self.use_rag
            }


def main():
    """Test the agent"""
    print("\n" + "="*60)
    print("RAG ANALYTICS AGENT - TEST")
    print("="*60 + "\n")
    
    # Check for database
    db_path = "saas_analytics.db"
    if not os.path.exists(db_path):
        print("⚠️  Database not found!")
        print(f"   Expected location: {db_path}")
        print("\nTo create the database:")
        print("1. You'll need to generate synthetic data (Phase 3)")
        print("2. Or create a simple test database")
        print("\nFor now, the agent will generate SQL but won't execute queries.")
        print("\n" + "="*60)
        db_path = "test.db"  # Use dummy path
    
    # Initialize agent
    agent = RAGAnalyticsAgent(
        db_path=db_path,
        use_rag=True,
        rag_k=5
    )
    
    # Test queries
    test_queries = [
        "What is our current MRR?",
        "Show me revenue by plan tier",
        "How many active customers do we have?",
        "What's our churn rate this month?"
    ]
    
    for query in test_queries:
        result = agent.query(query)
        
        print("\n" + "="*60)
        input("Press Enter for next query...")


if __name__ == "__main__":
    main()