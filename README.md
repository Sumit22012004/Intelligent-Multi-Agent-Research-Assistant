# Intelligent Multi-Agent Research Assistant

An AI-powered research assistant using multiple specialized agents to help with academic research and information gathering.

## 🚀 Quick Start (Phase 1)

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Gemini API key
- Perplexity API key

### Setup

1. **Clone the repository**
```bash
cd Intelligent-Multi-Agent-Research-Assistant
```

2. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

3. **Download HuggingFace models** (first time only)
```bash
python scripts/download_models.py
```

4. **Start services with Docker**
```bash
docker-compose up -d
```

5. **Initialize database** (first time only)
```bash
python scripts/init_db.py
```

6. **Access the application**
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Without Docker (Local Development)

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Start MongoDB**
```bash
# Install MongoDB locally or use Docker:
docker run -d -p 27017:27017 --name mongodb mongo:7.0
```

3. **Start Qdrant**
```bash
# Install Qdrant locally or use Docker:
docker run -d -p 6333:6333 --name qdrant qdrant/qdrant:v1.7.4
```

4. **Download models and initialize database**
```bash
python scripts/download_models.py
python scripts/init_db.py
```

5. **Start backend**
```bash
uvicorn backend.main:app --reload --port 8000
```

6. **Start frontend** (in another terminal)
```bash
streamlit run frontend/app.py --server.port 8501
```

## 📊 Phase 1 Status

✅ Project structure created  
✅ Docker configuration ready  
✅ MongoDB connection  
✅ Qdrant vector database  
✅ HuggingFace embeddings  
✅ Gemini AI integration  
✅ FastAPI backend  
✅ Streamlit frontend  

## 🔄 Next Phases

- **Phase 2:** Document processing, arXiv, Perplexity integration
- **Phase 3:** Multi-agent system (Researcher, Summarizer, Analyst)
- **Phase 4:** User memory and session management
- **Phase 5:** Complete frontend with visualizations
- **Phase 6:** Testing, optimization, documentation

## 📖 Documentation

See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for complete system architecture and implementation details.

## 🤝 Contributing

This is a personal project. Contributions are welcome!

## 📝 License

MIT License
