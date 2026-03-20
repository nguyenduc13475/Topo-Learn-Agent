# 🧠 Topo-Learn Agent

<p align="left">
  <img src="https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Neo4j-018BFF?style=for-the-badge&logo=neo4j&logoColor=white" alt="Neo4j" />
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
</p>

**Topo-Learn Agent** is an Intelligent Learning System designed to transform static academic documents and video lectures into interactive, dynamic learning experiences. By leveraging Large Language Models (Google Gemini), Knowledge Graphs (Neo4j), and Spaced Repetition algorithms (SM-2), it extracts core concepts, maps their dependencies, and creates personalized study paths.

Developed by **Nguyễn Văn Đức**.

---

## ✨ Key Features

- **📄 Smart Multimodal Ingestion:** Upload PDFs and Video lectures (MP4). The system automatically parses text using Docling and transcribes audio using Faster-Whisper.
- **🕸️ Automated Knowledge Graphs:** Uses AI to extract key concepts and determine their prerequisite dependencies, visualizing them as an interactive Directed Acyclic Graph (DAG) via React Flow.
- **🤖 Context-Aware AI Tutor:** Chat with an AI assistant powered by Gemini 1.5 Pro that understands the specific document context and concept you are currently studying.
- **📝 Dynamic Quiz Generation:** Automatically generates targeted multiple-choice questions to test your understanding of specific concepts.
- **🧠 Spaced Repetition (SM-2):** Tracks your quiz performance and calculates the optimal time to review concepts, ensuring long-term memory retention.
- **⚡ Real-Time Processing:** Built with a distributed Celery worker architecture and WebSocket connections to provide real-time status updates on document parsing and graph building.

---

## 🛠️ Technology Stack Detail

**Frontend**

- **Framework:** Next.js 15 (React 19)
- **Styling:** Tailwind CSS v4, Shadcn UI
- **State Management:** Zustand
- **Visualization:** React Flow (XYFlow), Dagre (DAG layouting)

**Backend & ML**

- **Framework:** FastAPI (Python 3.10)
- **AI/LLM:** Google Gemini API (2.5 Flash Lite for extraction, 3.1 Flash Lite Preview for tutoring)
- **ML Libraries:** Faster-Whisper, Docling, OpenCV, PyTorch
- **Task Queue:** Celery

**Databases & Infrastructure**

- **Relational DB:** PostgreSQL 15
- **Graph DB:** Neo4j 5.12
- **Message Broker / Cache:** Redis 7
- **Containerization:** Docker & Docker Compose
- **Proxy:** Nginx

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed.
- _(Optional but recommended)_ NVIDIA GPU with CUDA toolkit installed for faster ML processing (Whisper/Docling).
- A Google Gemini API Key.

### Installation

1. **Clone the repository:**

   ```bash
   git clone <your-repo-url>
   cd Topo-Learn-Agent
   ```

2. **Configure Environment Variables:**
   Navigate to the `backend` directory and copy the example environment file:

   ```bash
   cp backend/.env.example backend/.env
   ```

   Open `backend/.env` and fill in your actual credentials, most importantly your `GEMINI_API_KEY` and a secure `SECRET_KEY`.

3. **Build and start the application:**
   From the root directory, run:

   ```bash
   docker compose --profile gpu --env-file backend/.env up --build
   ```

   if you have gpu on your machine or

   ```bash
   docker compose --profile cpu --env-file backend/.env up --build
   ```

   if you only have cpu.

4. **Access the application:**
   - **Frontend (Web App):** `http://localhost:3000`
   - **Backend API Docs:** `http://localhost:8000/docs`
   - **Neo4j Browser:** `http://localhost:7474`

---

## 📂 Project Structure

```text
.
├── backend/                   # FastAPI Server & AI Workers
│   ├── app/
│   │   ├── ai_modules/        # Gemini integration and prompt engineering
│   │   ├── api/               # REST API & WebSocket endpoints
│   │   ├── core/              # Config, security, and Celery setup
│   │   ├── db/                # PostgreSQL and Neo4j connections
│   │   ├── models/            # SQLAlchemy database models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   └── services/          # Business logic, SM-2, and ML processing
│   ├── data/uploads/          # Local storage fallback for files
│   ├── worker.Dockerfile      # GPU-enabled image for Celery workers
│   └── Dockerfile             # Standard image for the FastAPI server
├── frontend/                  # Next.js Web Application
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   ├── components/        # Reusable UI components (Shadcn)
│   │   ├── features/          # Domain-specific components (Auth, Graph, Quiz)
│   │   ├── hooks/             # Custom React hooks (Auth, WebSockets, Translation)
│   │   ├── lib/               # Utility functions and API client
│   │   └── store/             # Zustand state management
│   └── Dockerfile             # Next.js production builder image
├── docker-compose.yml         # Local development orchestration
├── docker-compose.prod.yml    # Production orchestration with Nginx
└── nginx.conf                 # Reverse proxy configuration
```

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for details.

Copyright (c) 2026 Nguyễn Văn Đức
