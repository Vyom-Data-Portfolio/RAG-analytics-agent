# 🚀 QUICK START GUIDE

## For Windows Users

### 1. Extract the ZIP
Extract to: `C:\Users\nnint\OneDrive\Desktop\Appli\projects\rag-analytics-agent`

### 2. Run Setup Script
```cmd
# Double-click setup.bat
# OR run in Command Prompt:
cd C:\Users\nnint\OneDrive\Desktop\Appli\projects\rag-analytics-agent
setup.bat
```

### 3. Configure API Key
```cmd
# Copy the template
copy .env.example .env

# Edit .env with Notepad
notepad .env

# Add your key:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 4. Embed Knowledge Base (One-Time, ~2-3 min)
```cmd
# Activate venv first
venv\Scripts\activate

# Run embedding
python embed_knowledge_base.py
```

### 5. Test It!
```cmd
python agent_with_rag.py
```

---

## For Mac/Linux Users

### 1. Extract the ZIP
```bash
cd ~/projects
unzip rag-analytics-agent.zip
cd rag-analytics-agent
```

### 2. Run Setup Script
```bash
bash setup.sh
```

### 3. Configure API Key
```bash
cp .env.example .env
nano .env  # or use any text editor

# Add your key:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
```

### 4. Embed Knowledge Base
```bash
source venv/bin/activate
python embed_knowledge_base.py
```

### 5. Test It!
```bash
python agent_with_rag.py
```

---

## ✅ What Should Happen

### After setup.bat/sh:
```
✅ venv/ folder created
✅ Dependencies installed
✅ Ready to configure
```

### After embed_knowledge_base.py:
```
==============================================================
EMBEDDING KNOWLEDGE BASE
==============================================================

  Loading metrics.md...
    Created 15 chunks
  Loading schema_docs.md...
    Created 18 chunks
  ...

✅ EMBEDDING COMPLETE
Collection: saas_analytics_kb
Total chunks: 97
Database path: chroma_db
==============================================================
```

### After agent_with_rag.py:
```
==============================================================
RAG ANALYTICS AGENT - TEST
==============================================================

✅ RAG enhancement enabled

QUERY: What is our current MRR?
------------------------------------------------------------
✅ Success
📚 Retrieved 5 documents
   Sources: metrics.md, examples.json, business_logic.md

[SQL query and results shown here]
```

---

## ⏱️ Time Estimate

- Setup: 5-10 minutes
- Embedding: 2-3 minutes
- Testing: 1 minute

**Total: ~10-15 minutes to get running**

---

## 🐛 Troubleshooting

### "Python is not installed"
Install Python 3.8+ from python.org

### "ANTHROPIC_API_KEY not found"
1. Make sure you copied .env.example to .env
2. Make sure you added your actual API key (starts with sk-ant-)
3. Make sure there are no spaces around the =

### "Collection not found"
Run: `python embed_knowledge_base.py`

### "Module not found"
```bash
# Activate venv first!
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Then run the script
```

---

## 📚 Next Steps

After successful test:
1. Read SETUP_GUIDE.md for detailed docs
2. Explore knowledge_base/ files
3. Try more queries in agent_with_rag.py
4. Run comparison test: `python test_rag_improvement.py`

---

## 🎯 Project Structure

```
rag-analytics-agent/          ← You are here
├── venv/                      ← Created by setup
├── chroma_db/                 ← Created by embedding
├── knowledge_base/            ← Pre-configured
├── *.py files                 ← Ready to run
├── .env                       ← You create this
└── README.md                  ← Start here
```

---

**Got everything working?** You're ready to query! 🎉

**Need help?** Check SETUP_GUIDE.md or the troubleshooting section above.
