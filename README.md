# Restaurant Voice Hub

This is a full-stack application with a React frontend and a FastAPI (Python) backend, designed to integrate with ElevenLabs for AI voice ordering.

## Prerequisites

1.  **Node.js**: [Download & Install](https://nodejs.org/) (for the frontend)
2.  **Python 3.8+**: [Download & Install](https://www.python.org/) (for the backend)
3.  **ngrok**: [Download & Install](https://ngrok.com/) (for external access/ElevenLabs)

## Setup & Startup Guide

To run this application on any machine (including a new PC), follow these steps:

### 1. Setup Backend (Python)

Open a terminal/command prompt in the `restaurant-voice-hub` directory:

```bash
# Install Python dependencies
pip install fastapi uvicorn requests python-multipart

# Start the Backend Server
python backend/main.py
```
*The backend will start on `http://localhost:8001`.*

### 2. Setup Frontend (React)

Open a **new** terminal in the `restaurant-voice-hub` directory:

```bash
# Install Node dependencies (first time only)
npm install

# Start the Frontend
npm run dev
```
*The frontend dashboard will be available at `http://localhost:8081` (or similar).*

### 3. Setup External Access (ngrok)

To allow ElevenLabs (or other external tools) to talk to your local backend, you need a tunnel.
Open a **third** terminal:

```bash
# Start ngrok pointing to your backend port
# Replace the domain with your specific static domain if you have one
ngrok http --domain=overbig-harrison-unfervidly.ngrok-free.dev 8001
```

### Using ngrok on a Different PC

If you move this project to another computer, you can continue using the same static domain (`overbig-harrison-unfervidly.ngrok-free.dev`), but you must follow these rules:

1.  **Authenticate**: You must log in to ngrok on the new PC using the **same ngrok account** (or Auth Token) that owns the domain.
    ```bash
    ngrok config add-authtoken <YOUR_AUTH_TOKEN>
    ```
    *(You can find your token on the [ngrok Dashboard](https://dashboard.ngrok.com/get-started/your-authtoken))*

2.  **Single Session**: You cannot run the tunnel on two computers at the same time with the same domain (on the free plan).
    *   **Stop ngrok on the old PC** (Ctrl+C in the terminal).
    *   Start it on the new PC using the command in Step 3 above.

## Configuration

### Environment Variables (.env)
The frontend connects to the backend using the configuration in `.env`.
For local development (to avoid ISP blocking issues), use:
```
VITE_API_URL=http://localhost:8001
```

### ElevenLabs Setup
When configuring your Agent in ElevenLabs:
1.  Use the **ngrok URL** (e.g., `https://overbig-harrison-unfervidly.ngrok-free.dev`) for all tool definitions.
2.  Your local dashboard will continue to work via `localhost`.

## Troubleshooting

*   **Menu Search Failed**: Ensure the backend is running and the ngrok tunnel is active with the correct domain.
*   **Availability Toggle Issue**: Ensure you are using the latest code where `api.ts` maps `availability` correctly.
*   **ISP Blocking**: If `curl` to the ngrok URL fails locally, use `localhost` for local testing.
