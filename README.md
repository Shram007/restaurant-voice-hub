# Restaurant Voice Hub

This is a full-stack application with a React frontend and a FastAPI (Python) backend, designed to integrate with ElevenLabs for AI voice ordering.

## Cloud Deployment Guide (Vercel + Render + Supabase)

This project is set up to be deployed on the cloud.

### 1. Database (Supabase)

1. Create a new project on [Supabase](https://supabase.com/).
2. Go to the **SQL Editor** in the Supabase dashboard.
3. Copy the contents of `supabase_schema.sql` (in the project root) and run it to create the tables.
4. Get your **Project URL** and **API Key** (anon public) from Project Settings > API.

### 2. Backend (Render)

1. Create a new Web Service on [Render](https://render.com/).
2. Connect your GitHub repository.
3. **Build Command**: `pip install -r backend/requirements.txt`
4. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**:
    * `SUPABASE_URL`: Your Supabase Project URL
    * `SUPABASE_KEY`: Your Supabase Anon Key
    * `PYTHON_VERSION`: `3.9.0` (optional, but recommended)
6. Deploy. Once finished, copy your **Render Backend URL** (e.g., `https://my-app.onrender.com`).

### 3. Frontend (Vercel)

1. Import your project into [Vercel](https://vercel.com/).
2. **Project Settings**:
    * `ROOT_DIRECTORY`: Set to `frontend`.
    * `FRAMEWORK_PRESET`: Vite
3. **Environment Variables**:
    * `VITE_API_URL`: Paste your **Render Backend URL** (e.g., `https://restaurant-voice-hub.onrender.com`).
    * *Important: Do NOT use the ngrok URL or localhost.*
4. Deploy.

### 4. ElevenLabs Configuration

1. Update your Agent's tool definitions in ElevenLabs.
2. Replace the `ngrok` URL with your new **Render Backend URL**.

---

## Local Development Guide

### Prerequisites

1. **Node.js**: [Download & Install](https://nodejs.org/) (for the frontend)
2. **Python 3.8+**: [Download & Install](https://www.python.org/) (for the backend)
3. **ngrok**: [Download & Install](https://ngrok.com/) (for external access/ElevenLabs)

### Setup Steps

1. **Setup Backend**:

    ```bash
    # Install dependencies
    pip install -r backend/requirements.txt
    
    # Set Supabase Env Vars (Windows PowerShell)
    $env:SUPABASE_URL="your_url"
    $env:SUPABASE_KEY="your_key"
    
    # Start Server (from root directory)
    python backend/main.py
    ```

2. **Setup Frontend**:

    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3. **Setup Tunnel**:

    ```bash
    ngrok http --domain=overbig-harrison-unfervidly.ngrok-free.dev 8001
    ```

## Configuration

The frontend connects to the backend using the configuration in `.env`.
For local development, create a `.env` file in the `frontend/` directory:

```env
VITE_API_URL=http://localhost:8001
```

---

## MCP Server

`backend/mcp_server.py` exposes all five tool endpoints as [Model Context Protocol](https://modelcontextprotocol.io/) callable tools over stdio JSON-RPC 2.0.

### Tools exposed

| Tool | Description |
|------|-------------|
| `menu_search` | Search the live menu by keyword |
| `order_create_or_update` | Create or update a pending order |
| `get_eta` | Get order preparation ETA |
| `order_confirm` | Confirm a pending order |
| `handoff_to_human` | Escalate to a human agent |

### Run the MCP server

```bash
python backend/mcp_server.py
```

The server reads JSON-RPC requests from `stdin` and writes responses to `stdout` — compatible with any MCP host (Claude Desktop, Cursor, etc.).

### Smoke test

```bash
python backend/mcp_server_test.py
```
