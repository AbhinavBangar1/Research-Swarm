import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.backend.graph.workflow import swarm_app
import os

app = FastAPI(title="Multi-Agent Research Swarm API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text(json.dumps({"type": "info", "data": "Connected to Agent Swarm"}))
    
    try:
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            query = payload.get("query", "")
            
            if not query:
                continue
                
            await websocket.send_text(json.dumps({"type": "info", "data": f"Starting research on: {query}"}))
            
            initial_state = {
                "original_query": query,
                "sub_questions": [],
                "current_question_idx": 0,
                "next_agent": "Planner",
                "retrieved_contexts": [],
                "verified_claims": [],
                "final_report": ""
            }
            
            try:
                for output in swarm_app.stream(initial_state, {"recursion_limit": 50}):
                    for node_name, state_update in output.items():
                        print("\n" + "="*80)
                        print(f"[AGENT LOOP] Finished node: {node_name.upper()}")
                        print("="*80)
                        
                        import pprint
                        pprint.pprint(state_update, indent=2, width=100)
                        print("-" * 80 + "\n")
                            
                        await websocket.send_text(json.dumps({
                            "type": "agent_update",
                            "node": node_name.upper(),
                            "data": f"Node executed successfully."
                        }))
                        
                        if "final_report" in state_update and state_update["final_report"]:
                            print("\n*** FINAL REPORT GENERATED AND SENT TO FRONTEND ***\n")
                            await websocket.send_text(json.dumps({
                                "type": "final_report",
                                "data": state_update["final_report"]
                            }))
                            
            except Exception as e:
                error_msg = str(e)
                import traceback
                print("\n[CRITICAL ERROR IN LANGGRAPH EXECUTION]")
                traceback.print_exc()
                
                if "with_structured_output" in error_msg:
                    error_msg = "LLM Factory Error: Local Qwen model failed to output valid JSON. Try updating langchain-ollama or tweaking prompt constraints."
                await websocket.send_text(json.dumps({"type": "error", "data": error_msg}))
                
    except WebSocketDisconnect:
        print("Frontend Client disconnected")
