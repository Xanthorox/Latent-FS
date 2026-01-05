# 🌌 Latent-FS: The Vector File System

<div align="center">

**Making AI Memory Visible, Tangible, and Trainable**

*What if you could see inside your AI's mind? What if you could organize its thoughts with a simple drag-and-drop?*

[![GPU Accelerated](https://img.shields.io/badge/GPU-Accelerated-green?logo=nvidia)](https://github.com/xanthorox/latent-fs)
[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://github.com/xanthorox/latent-fs)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-blue?logo=typescript)](https://github.com/xanthorox/latent-fs)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**[Demo](#-demo) • [Features](#-revolutionary-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Performance](#-performance)**

</div>

---

## 🎯 The Problem

Vector databases are the backbone of modern AI systems—storing embeddings for RAG, semantic search, and AI memory. But there's a fundamental problem:

**Vector databases are invisible black boxes.**

- 🔮 You can't *see* how your AI organizes information
- 🎲 You can't *understand* why documents cluster together
- 🚫 You can't *correct* the AI when it miscategorizes content
- 🤷 You have no intuitive way to *interact* with high-dimensional vector spaces

Developers are building AI systems on top of invisible, uncontrollable foundations. It's like coding blindfolded.

## 💡 The Solution

**Latent-FS transforms your vector database into a visual, interactive file system.**

Imagine opening a folder explorer, but instead of files organized by name or date, you see **semantic clusters**—folders that represent *concepts* discovered by AI. Documents naturally group by meaning, not metadata.

But here's the revolutionary part: **You can drag-and-drop files between folders to teach the AI.**

When you move a document to a different semantic folder, Latent-FS doesn't just update a label—it **modifies the embedding itself**, nudging the vector representation toward the target concept. The AI learns from your spatial intuition.

**This is drag-to-train. This is the future of human-AI collaboration.**

---

## 🚀 Revolutionary Features

### 🎨 **Visual Vector Space**
- See your embeddings as a familiar file system interface
- Semantic folders auto-generated with AI-powered names
- Dark mode glassmorphism UI that feels like magic

### 🧲 **Drag-to-Train Technology**
- Drag documents between semantic folders
- Real-time embedding modification using weighted vector averaging
- Instant re-clustering with smooth animations

### ⚡ **GPU-Accelerated Performance**
- CUDA-optimized embedding generation (125+ docs/sec)
- Sub-100ms clustering for 500 documents
- 15,000+ re-embedding operations per second

### 🧠 **Intelligent Clustering**
- Unsupervised K-Means clustering in vector space
- Dynamic cluster count adjustment
- LLM-generated semantic folder names

### 🎬 **Smooth Animations**
- Framer Motion layout animations
- Documents "fly" to new positions when clusters change
- Visual feedback that makes the invisible visible

### 🔒 **100% Local & Private**
- No external API calls
- Local transformer models
- Your data never leaves your machine

---

## 🎥 Demo

> *Coming soon: Watch embeddings reorganize in real-time as you drag documents between semantic clusters*

### What You'll See:
1. **Initial Clustering**: 20 diverse documents automatically organized into 5 semantic folders
2. **Drag-to-Train**: Move a "Python tutorial" from "Programming" to "Data Science"
3. **Magic Happens**: Watch the embedding shift, clusters reorganize, and the document settle into its new semantic home
4. **Instant Feedback**: Smooth animations show the AI learning from your action

---

## ✨ Why This Matters

### For AI Developers
- **Debug your RAG systems** by visualizing how documents cluster
- **Improve retrieval quality** by correcting miscategorized embeddings
- **Understand your AI** through spatial representation of vector spaces

### For Researchers
- **Explore embedding spaces** with an intuitive interface
- **Test clustering algorithms** with real-time visual feedback
- **Demonstrate AI concepts** to non-technical audiences

### For the Future
- **Human-in-the-loop learning** through spatial interaction
- **Intuitive AI training** without writing code
- **Democratizing AI** by making it visible and controllable

---

## 🏃 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- NVIDIA GPU with CUDA support (optional, falls back to CPU)

### Installation

```bash
# Clone the repository
git clone https://github.com/xanthorox/latent-fs.git
cd latent-fs

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Running the System

```bash
# Terminal 1: Start the backend
cd backend
python main.py
# Backend runs on http://localhost:8000

# Terminal 2: Start the frontend
cd frontend
npm run dev
# Frontend runs on http://localhost:3000
```

### First Steps

1. Open http://localhost:3000 in your browser
2. The system auto-populates with 20 diverse sample documents
3. See semantic folders appear in the sidebar (e.g., "Space Exploration", "Cooking Recipes")
4. Drag a document card to a different folder
5. Watch the magic happen! ✨

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + TypeScript)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Sidebar    │  │  Grid View   │  │  Drag Layer  │      │
│  │  (Folders)   │  │  (Files)     │  │  (DnD)       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                            │                                 │
│                    ┌───────▼────────┐                        │
│                    │  API Client    │                        │
│                    └───────┬────────┘                        │
└────────────────────────────┼──────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼──────────────────────────────────┐
│                   Backend (FastAPI + Python)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Embedding   │  │   Cluster    │  │  Re-Embed    │       │
│  │   Service    │  │   Engine     │  │   Engine     │       │
│  │  (GPU/CUDA)  │  │  (K-Means)   │  │  (Vector Δ)  │       │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘       │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                            │                                  │
│                    ┌───────▼────────┐                         │
│                    │   ChromaDB     │                         │
│                    │  (Persistent)  │                         │
│                    └────────────────┘                         │
└───────────────────────────────────────────────────────────────┘
```

### Core Technologies

**Backend:**
- **FastAPI**: High-performance REST API
- **sentence-transformers**: State-of-the-art embeddings
- **ChromaDB**: Vector database with persistence
- **scikit-learn**: K-Means clustering
- **PyTorch + CUDA**: GPU acceleration

**Frontend:**
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Framer Motion**: Smooth animations
- **React DnD**: Drag-and-drop interactions
- **Tailwind CSS**: Modern styling

---

## ⚡ Performance

Benchmarked on NVIDIA GeForce RTX 3060:

| Operation | Performance | Details |
|-----------|-------------|---------|
| **Embedding Generation** | 125 docs/sec | GPU-accelerated, batch processing |
| **Single Embedding** | ~3-5ms | Sub-millisecond on GPU |
| **Clustering (500 docs)** | 92ms | K-Means with 5 clusters |
| **Re-embedding** | 14,979 ops/sec | Vector math optimization |
| **Database Write** | 189 docs/sec | ChromaDB persistence |
| **Database Read** | 0.62ms | Single document retrieval |
| **Similarity Calc** | 50,371 ops/sec | Cosine similarity |

**All tests pass: 63/63 ✅**

---

## 🧪 The Science Behind It

### Embedding Modification

When you drag a document to a new folder, Latent-FS performs a **weighted vector average**:

```
new_embedding = (1 - α) × current_embedding + α × target_centroid
```

Where:
- `α` (alpha) = 0.3 (nudge strength)
- `current_embedding` = document's current vector
- `target_centroid` = mean vector of target cluster

This gently "nudges" the document's representation toward the target concept while preserving its core semantic meaning.

### Why This Works

1. **Embeddings are continuous**: Small changes in vector space = small changes in meaning
2. **Centroids represent concepts**: The cluster center embodies the semantic theme
3. **Weighted averaging preserves information**: We don't overwrite, we blend
4. **Re-clustering validates**: If the nudge was meaningful, the document stays in the new cluster

---

## 🎓 Use Cases

### 1. **RAG System Debugging**
```
Problem: Your chatbot retrieves irrelevant documents
Solution: Visualize why documents cluster incorrectly, drag to fix
Result: Improved retrieval accuracy
```

### 2. **Content Organization**
```
Problem: Thousands of documents, no clear structure
Solution: Let AI discover semantic categories automatically
Result: Intuitive, meaning-based organization
```

### 3. **AI Education**
```
Problem: Explaining embeddings and vector spaces is abstract
Solution: Show students a visual, interactive representation
Result: Concrete understanding of abstract concepts
```

### 4. **Research & Experimentation**
```
Problem: Testing different clustering approaches is tedious
Solution: Real-time visual feedback on clustering quality
Result: Faster iteration and better insights
```

---

## 🛠️ Development

### Project Structure

```
latent-fs/
├── backend/
│   ├── services/          # Core business logic
│   │   ├── embedding.py   # GPU-accelerated embeddings
│   │   ├── clustering.py  # K-Means clustering
│   │   ├── reembedding.py # Vector modification
│   │   ├── naming.py      # LLM folder naming
│   │   └── database.py    # ChromaDB manager
│   ├── api/
│   │   └── routes.py      # REST endpoints
│   ├── models/
│   │   └── schemas.py     # Pydantic models
│   └── tests/             # 63 comprehensive tests
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   │   ├── FileSystemView.tsx
│   │   ├── Sidebar.tsx
│   │   ├── GridView.tsx
│   │   └── DocumentCard.tsx
│   ├── lib/
│   │   ├── api-client.ts  # Backend communication
│   │   └── types.ts       # TypeScript types
│   └── hooks/             # Custom React hooks
└── data/                  # ChromaDB persistence
```

### Running Tests

```bash
# Backend tests (63 tests)
cd backend
pytest -v

# Performance benchmarks
python test_performance.py

# Frontend build
cd frontend
npm run build
```

### API Endpoints

```
POST   /ingest          # Ingest documents
GET    /cluster         # Get semantic folders
POST   /re-embed        # Modify embedding (drag-to-train)
GET    /documents       # List all documents
GET    /health          # Health check
```

---

## 🌟 What Makes This Special

### 1. **First of Its Kind**
No other tool lets you visually interact with vector embeddings through drag-and-drop. This is genuinely novel.

### 2. **Production-Ready Performance**
Not a toy demo—this is GPU-accelerated, thoroughly tested, and handles hundreds of documents smoothly.

### 3. **Beautiful UX**
Dark mode glassmorphism, smooth Framer Motion animations, and intuitive interactions make complex AI feel magical.

### 4. **Fully Local**
Your data stays on your machine. No API keys, no cloud dependencies, no privacy concerns.

### 5. **Educational Value**
Makes abstract AI concepts (embeddings, vector spaces, clustering) tangible and understandable.

---

## 🚧 Roadmap

- [ ] **Hierarchical Clustering**: Multi-level folder structures
- [ ] **Custom Embedding Models**: Support for domain-specific models
- [ ] **Collaborative Features**: Multi-user editing
- [ ] **Export/Import**: Save and share semantic organizations
- [ ] **Advanced Visualizations**: 3D vector space exploration
- [ ] **Plugin System**: Extend with custom clustering algorithms
- [ ] **Mobile Support**: Touch-based drag-and-drop

---

## 🤝 Contributing

Contributions are welcome! This project is at the intersection of AI, UX, and systems engineering—there's room for all kinds of expertise.

### Areas for Contribution
- 🎨 UI/UX improvements
- 🧠 Alternative clustering algorithms
- ⚡ Performance optimizations
- 📚 Documentation and tutorials
- 🧪 Additional test coverage
- 🌐 Internationalization

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Gary Dev** @ [Xanthorox](https://github.com/xanthorox)

*Building the future of human-AI interaction, one vector at a time.*

---

## 🙏 Acknowledgments

- **sentence-transformers** for state-of-the-art embeddings
- **ChromaDB** for elegant vector storage
- **Next.js** and **FastAPI** for excellent developer experience
- The open-source AI community for inspiration

---

## 📬 Contact & Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/xanthorox/latent-fs/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/xanthorox/latent-fs/discussions)
- 🐦 **Twitter**: [@xanthorox](https://twitter.com/xanthorox)
- 📧 **Email**: gary@xanthorox.dev

---

<div align="center">

**If this project excites you, give it a ⭐ on GitHub!**

*Making AI visible, one embedding at a time.*

</div>
