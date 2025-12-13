# Portfolio Project - AI Coding Agent Instructions

## Project Overview
This is an AI-powered portfolio and blogging platform. It features an automated blog generation system and an interactive chatbot.
- **Backend:** Python (FastAPI) with MongoDB and ChromaDB.
- **Frontend:** React (Create React App).
- **AI:** Google Gemini (primary) and OpenAI (fallback).
- **Search:** Serper.dev (primary) and DuckDuckGo (fallback).

## Architecture & Core Components

### Backend (`backend/`)
- **Entry Point:** `backend/server.py` is the main FastAPI application. It handles API endpoints and runs the `APScheduler` for scheduled tasks.
- **AI Service:** `backend/gemini_service.py` wraps the Google Gemini API. `backend/agent_service.py` orchestrates the AI agent logic.
- **Data Storage:**
  - **MongoDB:** Primary database for blog posts and user data.
  - **ChromaDB:** Vector database for semantic search and RAG (Retrieval-Augmented Generation), managed by `backend/chromadb_monitor.py`.
- **Search:** `backend/search_engine.py` and `backend/serper_admin.py` handle web searches.

### Frontend (`frontend/`)
- Standard React application structure.
- Interacts with the backend via REST API.

## Critical Workflows

### Running the Backend
- **Production:** Uses `backend/render_start.sh` which runs `uvicorn server:app`.
- **Development:**
  ```bash
  cd backend
  uvicorn server:app --reload --port 8000
  ```

### Blog Generation
- **Scheduled:** Runs automatically via `APScheduler` in `server.py` (default: 1 AM UTC).
- **Manual Trigger:** POST to `/trigger-blog-generation`.
- **Logic:** `scheduled_blog_generation` in `server.py` calls `gemini_service.generate_blog_post`.

### Testing
- **Unit/Integration Tests:** Located in `backend/` with prefix `test_`.
- **Key Test Scripts:**
  - `test_blog_generator.py`: Validates blog creation.
  - `test_serper.py`: Checks search API connectivity.
  - `test_api.py`: Tests API endpoints.
  - `test_gemini_service.py`: Verifies AI model integration.

## Conventions & Patterns

### Environment Configuration
- All secrets must be in `.env`.
- Key variables: `GEMINI_API_KEY`, `SERPER_API_KEY`, `MONGO_URL`, `CLOUDINARY_*`.
- See `backend/render_start.sh` for default values and fallback logic.

### Logging
- Application logs are written to `agent.log` and stdout.
- Use the `BlogScheduler` or `AlluAgent` loggers defined in `server.py` and `agent_service.py`.

### Vector Database
- Uses `chromadb.CloudClient`.
- `backend/chromadb_monitor.py` handles tracking and storage limits.

### AI Integration
- Prefer `gemini_service` over direct API calls.
- Always implement fallbacks (e.g., if Gemini fails, log and try OpenAI if configured).

## Integration Points
- **Cloudinary:** Used for image hosting (configured in `server.py`).
- **SendGrid:** Used for email notifications (`backend/notification_service.py`).
- **Render:** Deployment platform; respects `Procfile` and `render_start.sh`.
