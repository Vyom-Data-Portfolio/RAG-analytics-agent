# Docker Setup Guide

## 🐳 Quick Start with Docker

### Prerequisites
- Docker Desktop installed ([Download here](https://www.docker.com/products/docker-desktop))
- 4GB RAM minimum
- 10GB disk space

---

## ⚡ Option 1: Docker Compose (Easiest)

### Step 1: Clone Repository
```bash
git clone https://github.com/Vyom-Data-Portfolio/RAG-analytics-agent.git
cd RAG-analytics-agent
```

### Step 2: Configure API Key
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your ANTHROPIC_API_KEY
# Windows: notepad .env
# Mac/Linux: nano .env
```

### Step 3: Setup Database & Embeddings (One-Time)
```bash
# Generate synthetic database
docker-compose run --rm rag-analytics-agent python generate_data.py

# Embed knowledge base
docker-compose run --rm rag-analytics-agent python embed_knowledge_base.py
```

### Step 4: Launch Application
```bash
docker-compose up
```

**Access at:** http://localhost:8501

### Stop Application
```bash
# Press Ctrl+C, then:
docker-compose down
```

---

## 🔧 Option 2: Docker (Manual)

### Step 1: Build Image
```bash
docker build -t rag-analytics-agent .
```

### Step 2: Generate Data & Embeddings
```bash
# Generate database
docker run --rm \
  -v $(pwd)/saas_analytics.db:/app/saas_analytics.db \
  rag-analytics-agent python generate_data.py

# Embed knowledge base
docker run --rm \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-analytics-agent python embed_knowledge_base.py
```

### Step 3: Run Container
```bash
docker run -d \
  --name rag-analytics-agent \
  -p 8501:8501 \
  -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/saas_analytics.db:/app/saas_analytics.db \
  -v $(pwd)/chroma_db:/app/chroma_db \
  rag-analytics-agent
```

**Access at:** http://localhost:8501

### Stop Container
```bash
docker stop rag-analytics-agent
docker rm rag-analytics-agent
```

---

## 📊 What Happens Inside the Container

### On Build:
1. Installs Python 3.11
2. Installs all dependencies (chromadb, streamlit, etc.)
3. Copies application code
4. Exposes port 8501

### On Run:
1. Loads .env file with API key
2. Mounts database and embeddings (persistent)
3. Starts Streamlit UI
4. Available at http://localhost:8501

---

## 🔍 Verify Setup

### Check if container is running:
```bash
docker ps
```

You should see:
```
CONTAINER ID   IMAGE                  STATUS         PORTS
abc123def456   rag-analytics-agent   Up 2 minutes   0.0.0.0:8501->8501/tcp
```

### View logs:
```bash
docker-compose logs -f
```

Or:
```bash
docker logs -f rag-analytics-agent
```

### Check health:
```bash
docker-compose ps
```

Should show: `State: Up (healthy)`

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Use different port
docker-compose down
# Edit docker-compose.yml: change "8501:8501" to "8502:8501"
docker-compose up
# Access at http://localhost:8502
```

### API Key Not Working
```bash
# Verify .env file exists
cat .env

# Should show: ANTHROPIC_API_KEY=sk-ant-...

# Recreate container
docker-compose down
docker-compose up
```

### Database Not Found
```bash
# Regenerate database
docker-compose run --rm rag-analytics-agent python generate_data.py

# Restart
docker-compose restart
```

### Knowledge Base Not Embedded
```bash
# Re-embed
docker-compose run --rm rag-analytics-agent python embed_knowledge_base.py

# Restart
docker-compose restart
```

### Out of Memory
```bash
# Increase Docker memory limit in Docker Desktop settings
# Settings → Resources → Memory → Set to 4GB+
```

---

## 📦 Docker Image Details

### Image Size
- Base image (python:3.11-slim): ~150MB
- With dependencies: ~1.5GB
- Total: ~1.6GB

### What's Included
- Python 3.11
- All Python dependencies
- Application code
- Knowledge base files

### What's NOT Included (Mounted)
- Database (saas_analytics.db)
- Embeddings (chroma_db/)
- Environment variables (.env)

**Why?** These are generated/configured by the user and should persist across container restarts.

---

## 🚀 Production Deployment

### Docker Hub (Optional)
```bash
# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 -t yourusername/rag-analytics-agent:v2.0.0 .

# Push to Docker Hub
docker push yourusername/rag-analytics-agent:v2.0.0
```

### Cloud Deployment

#### AWS ECS
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URI
docker tag rag-analytics-agent:latest YOUR_ECR_URI/rag-analytics-agent:latest
docker push YOUR_ECR_URI/rag-analytics-agent:latest
```

#### Google Cloud Run
```bash
# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT/rag-analytics-agent
gcloud run deploy rag-analytics-agent --image gcr.io/YOUR_PROJECT/rag-analytics-agent --platform managed
```

#### Heroku
```bash
heroku container:push web -a your-app-name
heroku container:release web -a your-app-name
```

---

## 🔐 Security Notes

### API Keys
- Never commit .env file to git
- Use environment variables in production
- Rotate keys regularly

### Network Security
- Container exposes port 8501 only
- No database ports exposed
- All data stays local

### Data Persistence
- Database and embeddings mounted as volumes
- Survives container restarts
- Backup by copying files

---

## 💡 Tips

### Faster Rebuilds
```bash
# Use Docker layer caching
docker-compose build --no-cache  # Only when dependencies change
```

### Development Mode
```bash
# Mount code directory for live reload
docker run -d \
  -p 8501:8501 \
  -v $(pwd):/app \
  -e ANTHROPIC_API_KEY=your_key \
  rag-analytics-agent
```

### Check Resource Usage
```bash
docker stats rag-analytics-agent
```

### Clean Up
```bash
# Remove container and image
docker-compose down
docker rmi rag-analytics-agent

# Remove volumes (deletes data!)
docker-compose down -v
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Container running: `docker ps`
- [ ] Health check passing: `docker-compose ps`
- [ ] UI accessible at http://localhost:8501
- [ ] Database connected (check sidebar)
- [ ] Knowledge base embedded (check sidebar)
- [ ] Can query and get results
- [ ] RAG sources displayed

---

## 📞 Need Help?

**Container won't start:**
```bash
docker-compose logs
```

**Database issues:**
```bash
docker-compose run --rm rag-analytics-agent ls -la
# Check if saas_analytics.db exists
```

**Permission issues (Linux/Mac):**
```bash
sudo chown -R $USER:$USER .
```

---

## 🎉 You're Done!

Your RAG Analytics Agent is now running in Docker!

- ✅ Isolated environment
- ✅ Reproducible setup
- ✅ Easy deployment
- ✅ Works on any OS

Share the Docker image or just the docker-compose.yml for others to run! 🚀
