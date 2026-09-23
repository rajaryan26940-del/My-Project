"""
FastAPI Server for AdaptiveAI Autonomous Agent System
"""
import os
import sys
from typing import Optional, Dict, Any

# Ensure root directory is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.agent import AdaptiveAgent

app = FastAPI(
    title="AdaptiveAI — Self-Learning Autonomous AI Agent API",
    description="Production-grade API for self-learning autonomous agent with episodic memory, ML strategy prediction, and continuous learning feedback loop.",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent Instance
agent = AdaptiveAgent(db_path="data/episodic_memory.db", auto_retrain_interval=5)

# Pydantic Schemas
class ExecuteTaskRequest(BaseModel):
    user_goal: str
    force_strategy: Optional[str] = None

class FeedbackRequest(BaseModel):
    task_id: str
    rating: int # 1 to 5 stars

@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "AdaptiveAI",
        "episodes_count": agent.episodic_memory.get_episode_count(),
        "ml_model_loaded": agent.strategy_selector.ml_model is not None
    }

@app.post("/api/execute")
def execute_task(req: ExecuteTaskRequest):
    if not req.user_goal or not req.user_goal.strip():
        raise HTTPException(status_code=400, detail="user_goal string cannot be empty.")
    try:
        result = agent.execute_task(
            user_goal=req.user_goal.strip(),
            force_strategy=req.force_strategy
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Task Execution Error: {str(e)}")

@app.get("/api/episodes")
def get_episodes(limit: int = 50):
    return agent.episodic_memory.fetch_recent_episodes(limit=limit)

@app.get("/api/metrics")
def get_metrics():
    return agent.get_system_metrics()

@app.post("/api/retrain")
def trigger_retrain():
    res = agent.trigger_retrain()
    return res

@app.post("/api/feedback")
def submit_feedback(req: FeedbackRequest):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5 stars.")
    agent.episodic_memory.update_user_feedback(req.task_id, req.rating)
    return {
        "status": "success",
        "message": f"Feedback rating {req.rating} recorded for task {req.task_id}",
        "task_id": req.task_id
    }

@app.get("/api/semantic-memory")
def get_semantic_memory(query: Optional[str] = None):
    if query:
        return agent.semantic_memory.search_similar_tasks(query)
    return agent.semantic_memory.kb_items

# Mount Frontend Static Directory if available
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/")
    def read_root():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "AdaptiveAI API Running. Access /docs for Swagger API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
