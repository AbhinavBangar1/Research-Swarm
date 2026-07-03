## Multi Agent Research Assitant

## Architecture & Agents

This project uses **LangGraph** to coordinate specialized AI agents:

- **Planner Node**: Decomposes complex user queries into a strict list of atomic, searchable sub-questions using Pydantic structured output.
- **Web Searcher Node** : Executes queries via DuckDuckGo to retrieve real-time context.
- **Verifier Node** : Evaluates retrieved context. If inadequate, loops back to search. Applies Confidence Scoring to claims.
- **Report Generator** : Aggregates verified claims into a final markdown report.

## Setup Instructions

1. Clone the Repository

```bash
```

2. Install Dependencies

```bash
pip install -r requirements.txt
```
