# Multi-Agent Research Swarm

A powerful, entirely local multi-agent research swarm built with Python, LangGraph, FastAPI, and React. This system autonomously decomposes complex queries, queries the web, verifies facts to prevent hallucinations, and synthesizes its findings into a cohesive Markdown report—all while providing sub-second visibility into the agent's reasoning loop.

## Features

*   **Multi-Agent Orchestration (LangGraph):** A stateful graph architecture with a Supervisor agent routing tasks between specialized worker agents (Planner, Searcher, Verifier, Generator).
*   **Fully Local LLM Pipeline:** Powered entirely offline using Ollama and the Qwen 2.5 (7B) model. No third-party API keys required.
*   **Real-Time WebSocket Streaming:** A FastAPI backend streams live agent state updates, node transitions, and raw JSON outputs directly to the frontend.
*   **Fact-Verification & Memory:** A deterministic pipeline where a Verifier agent grades search contexts and extracts claims. Integrated **ChromaDB** serves as a persistent semantic memory to prevent redundant failed search paths.
*   **Automated LLM-as-a-Judge Evaluation:** A custom benchmarking script leveraging the local LLM to automatically evaluate generated reports on Relevance, Depth, and Formatting.
*   **Resilient React UI:** A Vite-powered React frontend featuring auto-reconnection logic and a dynamic terminal-style live trace panel for the ReAct loop.

## Tech Stack

*   **Backend:** Python, FastAPI, WebSockets, LangChain, LangGraph, Ollama (Qwen 2.5:7b), ChromaDB, DuckDuckGo Search API, Pydantic
*   **Frontend:** React, Vite, JavaScript, CSS (Glassmorphism design)
*   **Architecture:** Multi-Agent Systems, ReAct (Reasoning and Acting), Event-Driven Streaming

## Installation & Setup

### Prerequisites
*   Python 3.10+
*   Node.js & npm
*   [Ollama](https://ollama.ai/) installed with the Qwen 2.5 7B model (`ollama run qwen2.5:7b`)

### Backend Setup
1. Clone the repository and navigate to the root directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI backend:
   ```bash
   python -m uvicorn src.backend.main:app --port 8000
   ```

### Frontend Setup
*(Note: If the frontend is stored in a separate repository or directory, navigate there first.)*
1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```

## System Architecture

1.  **Supervisor:** Reads the global state and routes to the next best agent.
2.  **Planner:** Decomposes the complex user query into a series of smaller, atomic sub-questions.
3.  **Searcher:** Queries DuckDuckGo for the current sub-question to grab web context.
4.  **Verifier:** Evaluates the search context against the sub-question. Extracts factual claims with confidence scores and verifies against ChromaDB memory.
5.  **Generator:** Synthesizes the verified claims into the final structured markdown report.

## Evaluation

To evaluate a generated report (e.g., `report_output.md`) using the local LLM-as-a-judge:
```bash
python -m src.backend.eval.benchmarker
```
