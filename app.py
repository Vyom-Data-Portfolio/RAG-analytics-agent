"""
RAG Analytics Agent - Streamlit UI
Interactive chat interface with RAG visualization
"""

import streamlit as st
import os
from datetime import datetime
from agent_with_rag import RAGAnalyticsAgent
import pandas as pd
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="RAG Analytics Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .rag-badge {
        background-color: #e8f4f8;
        color: #1f77b4;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-badge {
        background-color: #fff3cd;
        color: #856404;
        padding: 0.2rem 0.4rem;
        border-radius: 0.2rem;
        font-size: 0.7rem;
        margin: 0.1rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'rag_enabled' not in st.session_state:
    st.session_state.rag_enabled = True

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # RAG toggle
    rag_enabled = st.toggle(
        "Enable RAG Enhancement",
        value=st.session_state.rag_enabled,
        help="Use RAG to retrieve relevant context from knowledge base"
    )
    st.session_state.rag_enabled = rag_enabled
    
    # RAG parameters
    if rag_enabled:
        st.markdown("### RAG Parameters")
        rag_k = st.slider(
            "Documents to Retrieve (k)",
            min_value=1,
            max_value=10,
            value=5,
            help="Number of relevant documents to retrieve"
        )
    else:
        rag_k = 5
    
    st.markdown("---")
    
    # Database info
    st.markdown("### 📊 Database Info")
    db_path = "saas_analytics.db"
    if os.path.exists(db_path):
        st.success("✅ Database connected")
        
        # Show database stats
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subscriptions WHERE status='active'")
            active_subs = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM transactions WHERE status='success'")
            transactions = cursor.fetchone()[0]
            
            conn.close()
            
            st.metric("Users", f"{user_count:,}")
            st.metric("Active Subscriptions", f"{active_subs:,}")
            st.metric("Transactions", f"{transactions:,}")
            
        except Exception as e:
            st.warning(f"Could not load stats: {str(e)}")
    else:
        st.error("❌ Database not found")
        st.info("Run `python generate_data.py` to create database")
    
    st.markdown("---")
    
    # Knowledge base info
    st.markdown("### 📚 Knowledge Base")
    if os.path.exists("chroma_db"):
        st.success("✅ Knowledge base ready")
        st.caption("97 chunks embedded")
    else:
        st.error("❌ Not embedded")
        st.info("Run `python embed_knowledge_base.py`")
    
    st.markdown("---")
    
    # Example queries
    st.markdown("### 💡 Example Queries")
    
    example_queries = [
        "What is our current MRR?",
        "Show me revenue by plan tier",
        "How many active customers do we have?",
        "What's our churn rate this month?",
        "Which customers are at high risk?",
        "What's our CAC by marketing channel?",
        "Show me top features by usage",
        "What's our trial conversion rate?"
    ]
    
    for query in example_queries:
        if st.button(query, key=f"example_{query}", use_container_width=True):
            st.session_state.example_query = query
    
    st.markdown("---")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main content
st.markdown('<div class="main-header">🤖 RAG Analytics Agent</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-header">Ask questions about your SaaS data in plain English '
    f"""{"<span class='rag-badge'>RAG ENABLED</span>" if rag_enabled else ""}</div>""",
    unsafe_allow_html=True
)

# Initialize agent
@st.cache_resource
def get_agent(use_rag, k):
    try:
        return RAGAnalyticsAgent(
            db_path="saas_analytics.db",
            use_rag=use_rag,
            rag_k=k
        )
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return None

agent = get_agent(rag_enabled, rag_k)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show metadata if available
        if "metadata" in message and message["metadata"]:
            meta = message["metadata"]
            
            # Show RAG sources
            if "rag_sources" in meta and meta["rag_sources"]:
                st.markdown("**📚 Retrieved from:**")
                sources_html = " ".join([
                    f'<span class="source-badge">{source}</span>'
                    for source in meta["rag_sources"]
                ])
                st.markdown(sources_html, unsafe_allow_html=True)
            
            # Show SQL query
            if "sql" in meta and meta["sql"]:
                with st.expander("📝 View SQL Query"):
                    st.code(meta["sql"], language="sql")
            
            # Show results table
            if "results" in meta and meta["results"]:
                with st.expander("📊 View Results"):
                    st.text(meta["results"])

# Handle example query from sidebar
if 'example_query' in st.session_state:
    query = st.session_state.example_query
    del st.session_state.example_query
    
    # Add to messages
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching knowledge base..." if rag_enabled else "🤔 Thinking..."):
            try:
                result = agent.query(query)
                
                if result["success"]:
                    # Format response
                    response = f"### Query Results\n\n"
                    
                    if rag_enabled and result.get("retrieved_docs", 0) > 0:
                        response += f"*Retrieved {result['retrieved_docs']} relevant documents from knowledge base*\n\n"
                    
                    response += f"**SQL Generated:**\n```sql\n{result['sql']}\n```\n\n"
                    response += f"**Results:**\n```\n{result['results']}\n```"
                    
                    st.markdown(response)
                    
                    # Store message with metadata
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response,
                        "metadata": {
                            "sql": result["sql"],
                            "results": result["results"],
                            "rag_sources": result.get("rag_sources", []),
                            "rag_enabled": result["rag_enabled"]
                        }
                    })
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {}
                    })
                    
            except Exception as e:
                error_msg = f"❌ Error processing query: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_msg,
                    "metadata": {}
                })
    
    st.rerun()

# Chat input
if prompt := st.chat_input("Ask a question about your data..."):
    # Check if agent is ready
    if not agent:
        st.error("Agent not initialized. Please check configuration.")
    elif not os.path.exists("saas_analytics.db"):
        st.error("Database not found. Please run `python generate_data.py` first.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Searching knowledge base..." if rag_enabled else "🤔 Thinking..."):
                try:
                    result = agent.query(prompt)
                    
                    if result["success"]:
                        # Format response
                        response = f"### Query Results\n\n"
                        
                        if rag_enabled and result.get("retrieved_docs", 0) > 0:
                            response += f"*Retrieved {result['retrieved_docs']} relevant documents from knowledge base*\n\n"
                        
                        response += f"**SQL Generated:**\n```sql\n{result['sql']}\n```\n\n"
                        response += f"**Results:**\n```\n{result['results']}\n```"
                        
                        st.markdown(response)
                        
                        # Store message with metadata
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "metadata": {
                                "sql": result["sql"],
                                "results": result["results"],
                                "rag_sources": result.get("rag_sources", []),
                                "rag_enabled": result["rag_enabled"]
                            }
                        })
                    else:
                        error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg,
                            "metadata": {}
                        })
                        
                except Exception as e:
                    error_msg = f"❌ Error processing query: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "metadata": {}
                    })

# Footer
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🤖 Powered by:**")
    st.caption("Claude Sonnet 4 (Anthropic)")

with col2:
    st.markdown("**📚 RAG System:**")
    st.caption("ChromaDB + Sentence Transformers")

with col3:
    st.markdown("**📊 Knowledge Base:**")
    st.caption("97 chunks | 4 files | 15+ metrics")
