[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/framework-LangGraph-blue.svg)](https://github.com/langchain-ai/langgraph)
[![Last Commit](https://img.shields.io/github/last-commit/mdSHash/Text-to-SQL-Agent)](https://github.com/mdSHash/Text-to-SQL-Agent/commits/main)

# Text-to-SQL Agent

**An autonomous natural-language-to-SQL agent with self-correction, transparent reasoning traces, and an interactive Streamlit UI — built for developers and analysts who want to query databases without writing SQL.**

<!-- TODO: Add actual screenshot -->
![Demo](./assets/demo.png)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Author / Contact](#author--contact)

---

## Overview

Text-to-SQL Agent converts plain-English questions into executable SQL, runs them against a SQLite database, and returns human-readable answers. It is designed for analysts, developers, and non-technical users who need fast, reliable access to relational data without memorizing schema details or SQL syntax.

The agent is orchestrated as a stateful LangGraph workflow: it loads the database schema, generates SQL via Google Gemini, validates the query plan, executes it, and — if something fails — retries with error context up to three times before gracefully reporting the issue.

---

## Features

- **Autonomous multi-step workflow** — LangGraph orchestrates schema loading, SQL generation, validation, execution, and answer formatting as a directed graph
- **Self-correcting retries** — on execution failure the agent feeds the error back to the LLM and regenerates SQL (up to 3 attempts)
- **SQL validation before execution** — uses SQLite `EXPLAIN QUERY PLAN` to catch syntax errors without touching data
- **Full execution trace** — every node records timestamped details so users can inspect the agent's reasoning
- **Natural-language answers** — raw query results are summarized into clear prose by a second LLM call
- **Interactive Streamlit UI** — dark glassmorphism theme with sample questions, query history, and real-time trace visualization
- **Pre-loaded Northwind database** — ships with a realistic multi-table dataset (Customers, Products, Orders, Employees, OrderDetails)
- **Typed state management** — `TypedDict`-based state ensures type safety across all graph nodes
- **Extensible node architecture** — each processing step is an isolated module, easy to swap or extend

---

## Tech Stack

| Layer          | Technology                          |
| -------------- | ----------------------------------- |
| Language       | Python 3.8+                         |
| Agent Framework| LangGraph 0.2.x                     |
| LLM            | Google Gemini 2.5 Flash (via `google-genai`) |
| Orchestration  | LangChain 0.3.x                     |
| UI             | Streamlit 1.39+                     |
| Database       | SQLite 3 (standard library)         |
| Data Handling  | Pandas 2.2+                         |
| Environment    | python-dotenv                       |
| Testing        | pytest, unittest                    |

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))
- pip (or any PEP-517 compatible installer)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/mdSHash/Text-to-SQL-Agent.git
cd Text-to-SQL-Agent
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your API key.

5. Initialize the database (optional — the database ships pre-built):

```bash
python data/setup_db.py
```

### Environment Variables

| Variable          | Description                        | Required | Example                          |
| ----------------- | ---------------------------------- | -------- | -------------------------------- |
| `GOOGLE_API_KEY`  | Google Gemini API key for LLM calls | Yes      | `AIzaSy...`                      |

### Running Locally

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`.

---

## Usage

### Ask a question through the UI

Launch the app, type a natural-language question in the text area, and click **Submit Query**. The agent processes the question and displays the SQL, raw results, a natural-language answer, and the full execution trace.

### Sample queries you can try

```text
Which customers placed the most orders?
What are the top 5 most expensive products?
Show total revenue by country.
```

### Programmatic usage

You can invoke the agent directly from Python without the UI:

```python
from agent.graph import run_agent

result = run_agent("How many orders were shipped to Germany?")

print(result["sql_query"])       # Generated SQL
print(result["final_answer"])    # Natural-language answer
print(result["trace"])           # Step-by-step execution trace
```

---

## Project Structure

```text
Text-to-SQL-Agent/
├── app.py                        # Streamlit application entry point
├── requirements.txt              # Python dependencies
├── pytest.ini                    # pytest configuration and markers
├── .env.example                  # Template for environment variables
├── agent/
│   ├── __init__.py               # Package marker
│   ├── graph.py                  # LangGraph workflow definition and compilation
│   ├── state.py                  # TypedDict state shared across nodes
│   └── nodes/
│       ├── __init__.py           # Nodes sub-package marker
│       ├── schema_loader.py      # Loads SQLite schema into agent state
│       ├── sql_generator.py      # Generates SQL via Google Gemini LLM
│       ├── validator.py          # Validates SQL with EXPLAIN QUERY PLAN
│       ├── executor.py           # Executes SQL and captures results/errors
│       ├── error_handler.py      # Manages retries and error context
│       └── formatter.py          # Formats results into natural-language answers
├── ui/
│   └── components.py             # Streamlit UI components and custom CSS
├── data/
│   ├── setup_db.py               # Script to create and populate Northwind DB
│   └── northwind.db              # Pre-built SQLite database
└── tests/
    ├── __init__.py               # Tests package marker
    ├── test_agent_nodes.py       # Unit tests for individual nodes
    ├── test_database.py          # Database setup and query tests
    ├── test_graph.py             # Graph compilation and routing tests
    ├── test_integration.py       # End-to-end integration tests
    └── test_ui_components.py     # UI component tests
```

---

## Configuration

### pytest.ini

Test configuration lives in [`pytest.ini`](pytest.ini). Key settings:

- **Test discovery**: files matching `test_*.py` in the `tests/` directory
- **Markers**: `unit`, `integration`, `ui`, `database`, `slow`, `requires_api_key`
- **Output**: verbose with short tracebacks and suppressed deprecation warnings

### Database path

All nodes resolve the database path relative to the project root:

```python
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "northwind.db"
```

To use a different database, update `DB_PATH` in `schema_loader.py`, `validator.py`, and `executor.py`.

### LLM model

The agent uses `gemini-2.5-flash` by default. To change the model, edit the `model` parameter in [`agent/nodes/sql_generator.py`](agent/nodes/sql_generator.py:57) and [`agent/nodes/formatter.py`](agent/nodes/formatter.py:54).

### Retry limit

Maximum retries are set to 3 in [`agent/graph.py`](agent/graph.py:28). Adjust the threshold in `_route_after_error` to change this behavior.

---

## Testing

Run the full test suite:

```bash
pytest
```

Run tests by marker:

```bash
pytest -m unit
pytest -m integration
pytest -m database
```

Run a specific test file:

```bash
pytest tests/test_agent_nodes.py -v
```

The test suite covers:

- Individual node behavior (schema loading, SQL generation, validation, execution, error handling, formatting)
- Graph compilation and conditional routing logic
- Database setup and integrity
- UI component rendering
- End-to-end integration with mocked LLM responses

---

## Deployment

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. Set `GOOGLE_API_KEY` in the Streamlit secrets manager.
4. Deploy.

### Docker (manual)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t nl2sql-agent .
docker run -e GOOGLE_API_KEY=your_key -p 8501:8501 nl2sql-agent
```

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature`.
3. Write code following the existing style (type hints, docstrings, snake_case).
4. Add or update tests for any new functionality.
5. Run `pytest` and ensure all tests pass.
6. Commit with clear, imperative messages: `Add retry backoff to error handler`.
7. Open a Pull Request against `main` with a description of what changed and why.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Author / Contact

Built by [mdSHash](https://github.com/mdSHash).

Repository: [https://github.com/mdSHash/Text-to-SQL-Agent](https://github.com/mdSHash/Text-to-SQL-Agent)
