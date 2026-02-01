from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import tools, dashboard, pos

app = FastAPI(title="Restaurant Voice Hub API")

# Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(tools.router)
app.include_router(dashboard.router)
app.include_router(pos.router, prefix="/pos")

@app.get("/health")
def health_check():
    return {"ok": True, "time": datetime.now().isoformat()}

@app.get("/")
def root():
    return {"message": "Restaurant Voice Hub API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
