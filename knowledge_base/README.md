# RAG Analytics Agent - Knowledge Base

## Overview
This knowledge base powers the RAG (Retrieval-Augmented Generation) system for our text-to-SQL analytics agent. It contains business context, metric definitions, query examples, and best practices that help Claude generate more accurate SQL queries.

## Directory Structure

```
knowledge_base/
├── README.md (this file)
├── metrics.md              # Business metric definitions & calculations
├── schema_docs.md          # Table relationships & semantic descriptions
├── examples.json           # 30 example (question, SQL) pairs
└── business_logic.md       # Query rules, patterns, & best practices
```

## File Descriptions

### 1. metrics.md
**Purpose**: Define SaaS business metrics with exact calculation formulas

**Contains**:
- Revenue metrics (MRR, ARR, ARPU, LTV, NRR)
- Customer metrics (Churn Rate, Customer Count, Health Score)
- Engagement metrics (DAU, MAU, Feature Adoption)
- Support metrics (Resolution Time, Ticket Volume)
- Campaign metrics (CAC, Marketing ROI)

**Use when**: User asks about specific metric definitions or calculations

**Example queries answered**:
- "How is MRR calculated?"
- "What's a good churn rate?"
- "Define net revenue retention"

---

### 2. schema_docs.md
**Purpose**: Explain database schema with business context

**Contains**:
- Table relationships and ER diagram
- Semantic column descriptions
- Common join patterns
- Data types and formats
- Index strategy
- Query performance tips

**Use when**: Need to understand table structure, relationships, or join logic

**Example queries answered**:
- "How do I join users and transactions?"
- "What tables contain revenue data?"
- "What does the status column mean?"

---

### 3. examples.json
**Purpose**: Provide few-shot learning examples of (question, SQL) pairs

**Contains**:
- 30 real-world query examples
- Categorized by type (Revenue, Customer, Engagement, etc.)
- SQL with explanations
- Business context for each query

**Use when**: Similar question to previous queries, need query template

**Example queries matched**:
- "Show me MRR by plan tier" → finds ID #2
- "What's our churn rate?" → finds ID #5
- "Top customers by revenue" → finds ID #26

---

### 4. business_logic.md
**Purpose**: Define query construction rules and best practices

**Contains**:
- Critical query rules (revenue normalization, date handling)
- Edge cases and gotchas
- Performance optimization patterns
- Natural language → SQL interpretation guide
- Query validation checklist

**Use when**: Building complex queries, handling edge cases, optimizing performance

**Example queries answered**:
- "How do I calculate MRR correctly?"
- "What's the best way to filter by date?"
- "How do I avoid double-counting customers?"

---

## How RAG Works in This System

### 1. Query Vector Embedding
When user asks: **"What's our MRR by industry?"**
- User question is embedded into vector space
- Stored in ChromaDB vector database

### 2. Semantic Search
System retrieves top-k most relevant documents:
- **From metrics.md**: MRR definition and calculation
- **From examples.json**: Similar query (ID #7: "Show me customer distribution by industry")
- **From business_logic.md**: Rules about revenue normalization and GROUP BY

### 3. Context Injection
Retrieved context is injected into Claude's prompt:
```
Based on this context:
[MRR definition...]
[Example query...]
[Business rules...]

Generate SQL for: "What's our MRR by industry?"
```

### 4. SQL Generation
Claude generates accurate SQL using retrieved knowledge:
```sql
SELECT 
    u.industry, 
    SUM(CASE WHEN s.billing_cycle = 'monthly' THEN s.amount
        WHEN s.billing_cycle = 'annual' THEN s.amount / 12.0
        WHEN s.billing_cycle = 'quarterly' THEN s.amount / 3.0
    END) as mrr
FROM users u
JOIN subscriptions s ON u.user_id = s.user_id
WHERE s.status = 'active'
GROUP BY u.industry
ORDER BY mrr DESC
```

## RAG Retrieval Strategy

### What to Retrieve

| User Question Contains | Retrieve From |
|------------------------|---------------|
| Metric name (MRR, CAC, LTV) | metrics.md |
| Table/column name | schema_docs.md |
| Similar past question | examples.json |
| "How do I..." or "Best way to..." | business_logic.md |
| Complex multi-table query | schema_docs.md + examples.json |
| Edge case ("exclude trials", "active only") | business_logic.md |

### Retrieval Parameters
- **k=3** for simple questions (1 metric definition)
- **k=5** for moderate complexity (joins, segmentation)
- **k=8** for complex questions (multi-table, calculations)

### Similarity Threshold
- **>0.7**: High confidence, use directly
- **0.5-0.7**: Moderate confidence, verify relevance
- **<0.5**: Low confidence, may not be helpful

---

## Updating the Knowledge Base

### Adding New Metrics
1. Add definition to `metrics.md`
2. Add example query to `examples.json`
3. Add any special rules to `business_logic.md`
4. Re-embed documents in ChromaDB

### Adding New Tables
1. Update `schema_docs.md` with table description
2. Add common join patterns
3. Create example queries in `examples.json`
4. Update business logic if needed

### Improving Retrieval
- Add more diverse examples
- Include edge cases and error corrections
- Document common user mistakes
- Add synonyms and alternative phrasings

---

## Testing the Knowledge Base

### Test Queries
Run these to verify RAG is working:

**Simple (should retrieve from metrics.md)**
- "What is MRR?"
- "How do you calculate churn rate?"

**Schema-based (should retrieve from schema_docs.md)**
- "How are users and subscriptions related?"
- "What's in the transactions table?"

**Example-matching (should retrieve from examples.json)**
- "Show me revenue by plan tier"
- "How many active customers do we have?"

**Complex (should retrieve from multiple sources)**
- "What's our highest-value customer segment?"
- "Show me customers at risk of churning"

### Validation
For each test:
1. Check which documents were retrieved
2. Verify relevance scores
3. Confirm SQL accuracy
4. Test query execution

---

## Vector Embedding Details

### Embedding Model
- **Model**: OpenAI text-embedding-3-small or Claude embeddings
- **Dimensions**: 1536 (or 768 for Claude)
- **Chunk Size**: Documents split at ~500 tokens
- **Overlap**: 50 tokens between chunks

### ChromaDB Collection
- **Collection Name**: `saas_analytics_kb`
- **Distance Metric**: Cosine similarity
- **Metadata**: filename, category, last_updated

---

## Maintenance Schedule

**Weekly**
- Review failed/incorrect queries
- Add new examples to examples.json

**Monthly**
- Update metrics with new business definitions
- Add new table documentation
- Refine business logic rules

**Quarterly**
- Re-embed all documents
- Optimize retrieval parameters
- Clean up outdated examples

---

## Knowledge Base Statistics

**Total Documents**: 4 main files
**Total Examples**: 30 query pairs
**Metrics Defined**: 15+
**Tables Documented**: 10
**Business Rules**: 50+
**Estimated Tokens**: ~50,000 tokens total
**Vector Chunks**: ~120 (after chunking)

---

## Next Steps

1. ✅ Enhanced database schema (10 tables)
2. ✅ Comprehensive metrics documentation
3. ✅ 30 example query pairs
4. ✅ Business logic rules
5. ⏳ Vector embedding script
6. ⏳ RAG retrieval integration
7. ⏳ Enhanced data generator
8. ⏳ Testing & validation

---

## Contact & Feedback

This knowledge base is designed to improve over time. As you encounter:
- Missing metrics
- Unclear documentation
- Incorrect examples
- Edge cases not covered

...add them to the appropriate file and re-embed the knowledge base.

The better the knowledge base, the better the RAG system performs! 🚀
