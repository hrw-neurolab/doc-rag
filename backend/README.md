# 🔧 Backend

This service exposes the API used by doc-rag. It indexes your documents and chats with them using various LLM components.

## 🧰 Tech stack

- **FastAPI** with Beanie ODM
- **MongoDB** for storage
- **LangChain** + **Ollama** for embeddings and chat
- **PyPDF** and other helpers for ingesting files

## 🏗️ Local installation

1. Ensure Python 3.12 is available.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy the example environment file and edit values as needed:
   ```bash
   cp .env.example .env
   ```
4. Start the server:
   ```bash
   fastapi run src/main.py --port 8000
   ```

When running with Docker Compose refer to `.env.docker` and the root README.
