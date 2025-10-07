# 📚 doc-rag

**doc-rag** is a Retrieval-Augmented Generation playground that lets you chat with your own documents. 📝🤖
Upload PDFs or snippets, the backend indexes them and uses LLMs to answer your questions while the frontend provides a clean chat UI.

## 🛠️ Tech stack

- 🐳 **Docker Compose** orchestrates the services
- 🐍 **FastAPI** + MongoDB for the backend
- 🖥️ **Vite** + **Vue&nbsp;3** for the frontend

## 🚀 Quick start

1. Ensure the environment files are in place:
   * `backend/.env.docker` already exists with sane defaults—tweak it if needed.
   * Query classifier model has to be manually added to `backend/src/nlp`. The model could be trained using the scripts under `text_classifier` (refer to `text_classifier/README.md`) for further information.
   * Copy the frontend example file:
   ```bash
   cp frontend/.env.example frontend/.env
   ```
2. Build and launch the stack:
   ```bash
   docker compose up --build
   ```
   This pulls up MongoDB, the backend, the frontend build container and an Nginx server on port **80**.

For more ways to run the project and development tips, see the [backend README](backend/README.md) and the [frontend README](frontend/README.md).
