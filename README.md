# AI Chatbot API

AI Chatbot API is a FastAPI backend for building a ChatGPT-like application with user accounts, persistent chat history, real-time WebSocket streaming, Google Gemini integration, and Retrieval-Augmented Generation (RAG).

The project is designed as the backend layer for a chat application. It receives user messages, enriches them with relevant knowledge-base content, sends the final prompt to Gemini, streams the answer back to the client, and stores both user and AI messages in PostgreSQL.

## What This Project Builds

- User authentication API with registration, login, bcrypt password hashing, and JWT access tokens.
- Real-time chat over WebSocket at `/ws/chat/{user_id}`.
- Persistent chat sessions and message history stored in PostgreSQL.
- RAG-powered responses using a local knowledge base from the `knowledge/` folder.
- Hybrid retrieval with multilingual semantic search, TF-IDF keyword search, and CrossEncoder reranking.
- Google Gemini response generation through the official `google-genai` SDK.
- REST endpoints for reading chat sessions and chat history.

## Tech Stack

- **Backend framework:** FastAPI
- **Runtime:** Python 3.10+
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Validation:** Pydantic v2
- **Authentication:** bcrypt and PyJWT
- **AI provider:** Google Gemini via `google-genai`
- **RAG and ML:** SentenceTransformers, Scikit-learn, CrossEncoder, PyTorch
- **Server:** Uvicorn

## What You Need Before Running

Prepare these items before starting the application:

- Python 3.10 or newer.
- PostgreSQL running locally, in Docker, or on a hosted database service.
- A database created for this project, for example `ai_chatbot_db`.
- A Google Gemini API key from Google AI Studio.
- A JWT secret key for signing access tokens.
- A `.env` file based on `.env.template`.
- Optional knowledge-base files in `knowledge/` if you want RAG responses.

## Setup

Clone the repository and enter the project folder:

```bash
git clone https://github.com/your-username/ai_chatbot.git
cd ai_chatbot
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirement.txt
```

## Environment Configuration

Copy the template file:

```bash
cp .env.template .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.template .env
```

Fill in these required values:

- `ENV_DATABASE_URL`: PostgreSQL connection string, for example `postgresql://user:password@localhost:5432/ai_chatbot_db`.
- `ENV_GEMINI_API_KEY`: Google Gemini API key.
- `ENV_GEMINI_MODEL`: Gemini model used for chat responses.
- `ENV_JWT_SECRET_KEY`: secret key for signing JWT tokens.
- `ENV_JWT_ALGORITHM`: JWT algorithm, usually `HS256`.
- `ENV_ACCESS_TOKEN_EXPIRE_MINUTES`: token lifetime in minutes.
- `ENV_PROMPT_FOLDER` and `ENV_PROMPT_SYSTEM`: system prompt location.
- `ENV_KNOWLEDGE_FOLDER` and `ENV_KNOWLEDGE_FILE`: RAG knowledge-base location.

Generate a strong JWT secret with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Database

The application creates SQLAlchemy tables automatically when `main.py` starts:

- `users`
- `chat_sessions`
- `messages`

Make sure the database in `ENV_DATABASE_URL` already exists and the configured user can create tables.

If you use the included `docker-compose.yml`, start PostgreSQL with:

```bash
docker compose up -d
```

Then set `ENV_DATABASE_URL` to match the database credentials in that compose file.

## Running The Application

Start the API server:

```bash
python -m uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Interactive Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## API Overview

### User API

- `POST /users/register`: create a new user account.
- `POST /users/login`: authenticate a user and return a JWT token plus profile data.

### Chat History API

- `GET /chat/sessions/{user_id}`: list chat sessions for a user.
- `GET /chat/history/{session_id}`: list all messages in a chat session.

### WebSocket Chat API

Connect a WebSocket client to:

```text
ws://127.0.0.1:8000/ws/chat/{user_id}
```

Send a JSON payload:

```json
{
  "message": "What is RAG?"
}
```

Optional fields:

```json
{
  "message": "Summarize this file",
  "session_id": "existing-session-uuid",
  "file_paths": ["path/to/file.pdf"]
}
```

The server streams response chunks:

```json
{ "type": "stream", "content": "Retrieval" }
```

When streaming is complete, the server sends:

```json
{ "type": "done", "session_id": "session-uuid" }
```

## RAG Knowledge Base

RAG uses files configured by:

- `ENV_KNOWLEDGE_FOLDER`
- `ENV_KNOWLEDGE_FILE`

The default knowledge file is loaded from the `knowledge/` directory. Keep the content focused and factual because retrieved knowledge is inserted into the Gemini prompt as additional context.

Supported knowledge file types are defined in `utils/config.py`, including JSON, PDF, Excel, CSV, TXT, and Markdown.

## Project Structure

```text
ai_chatbot/
|-- api/             # FastAPI routers and endpoints
|-- core/            # Database and security setup
|-- doc/             # Architecture notes, roadmap, and integration guides
|-- knowledge/       # RAG source files
|-- models/          # SQLAlchemy database models
|-- prompt/          # System prompt files for AI behavior
|-- repository/      # Database CRUD operations
|-- schemas/         # Pydantic request and response schemas
|-- services/        # Business logic, Gemini integration, and RAG retrieval
|-- tests/           # Test and local experiment scripts
|-- utils/           # Config loader, logger, file loaders, and WebSocket manager
|-- main.py          # FastAPI application entry point
`-- requirement.txt  # Python dependencies
```

## Development Notes

- Keep secrets in `.env`; do not commit real API keys or database passwords.
- Use `README.md` for setup and usage information.
- Use `doc/` for deeper architecture notes and implementation plans.
- Keep code comments in English so the project documentation stays consistent.
