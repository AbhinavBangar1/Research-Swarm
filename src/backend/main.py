from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Multi-Agent Research Swarm API")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Research Swarm Backend is running"}

# Placeholder for the WebSocket endpoint that will stream LangGraph events
@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_json({"status": "connected", "message": "Agent stream ready"})
    # Event loop will go here
    # while True:
    #     data = await websocket.receive_text()
