# 🤖 NL2SQL Agent

**An autonomous natural language to SQL agent with self-correction and transparent reasoning**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

NL2SQL Agent is an intelligent system that converts natural language questions into SQL queries, executes them against a database, and returns human-readable answers. Built with LangGraph and powered by Google Gemini, it features autonomous error correction, transparent reasoning traces, and an intuitive Streamlit interface. The agent can understand complex questions, navigate database schemas, and recover from mistakes—making database querying accessible to everyone.

---

## 🤔 Why Text-to-SQL is Harder Than It Looks

### Ambiguity and Context

Natural language is inherently ambiguous, and the same question can be interpreted in multiple ways depending on context. When a user asks "Show me sales last month," the system must resolve several ambiguities: Which month does "last month" refer to—the previous calendar month or the last 30 days? What timezone should be used for date calculations? Which "sales" table should be queried if multiple exist? Does "sales" mean revenue, units sold, or number of transactions? The agent must make intelligent assumptions about these ambiguities, validate them against the database schema, and sometimes even infer business logic that isn't explicitly stated. Unlike structured query languages where every term has a precise meaning, natural language requires the system to understand not just syntax, but the user's intent, domain knowledge, and the implicit context that humans naturally bring to conversations.

### Complex Joins and Relationships

Real-world databases rarely consist of simple, flat tables. They contain complex schemas with dozens or hundreds of tables connected through intricate foreign key relationships. When a user asks "Show me customers who ordered products from the electronics category," the system must understand that this seemingly simple question requires joining multiple tables: customers → orders → order_details → products → categories. This is multi-hop reasoning—the agent must traverse the relationship graph, identify the correct join paths, and construct queries that efficiently retrieve the data. The challenge intensifies with aggregations and grouping: "What's the average order value per customer by region?" requires not only understanding the joins but also knowing which fields to aggregate, how to group results, and in what order to apply these operations. A single misunderstood relationship or incorrect join condition can produce completely wrong results, and the agent must validate its understanding of the schema before generating SQL.

### SQL Dialect Differences

SQL is not a single, universal language—it's a family of dialects that vary significantly across database systems. Date functions are a prime example: SQLite uses `date('now')`, PostgreSQL uses `CURRENT_DATE`, and MySQL uses `CURDATE()`. String operations differ too: concatenation might be `||` in SQLite, `CONCAT()` in MySQL, or `+` in SQL Server. Even basic syntax varies: SQLite doesn't support `RIGHT JOIN` or `FULL OUTER JOIN`, while PostgreSQL has powerful array operations that don't exist in other systems. Window functions, JSON operations, and recursive queries all have dialect-specific implementations. This means the agent must not only generate correct SQL logic but also produce dialect-specific syntax for the target database. Error messages compound this challenge—a syntax error in SQLite produces different messages than the same error in PostgreSQL, making debugging and self-correction more complex. The agent must be aware of these differences and adapt its SQL generation accordingly.

---

## ✨ Features

- 🤖 **Autonomous Agent** using LangGraph for intelligent workflow orchestration
- 🔄 **Self-Correction** with retry logic (up to 3 attempts) that learns from errors
- 🔍 **Transparent Reasoning** with detailed execution trace showing every step
- ✅ **SQL Validation** before execution using EXPLAIN QUERY PLAN
- 📊 **Interactive Streamlit UI** with real-time feedback and sample questions
- 💾 **Pre-loaded Northwind Database** with realistic sample data
- 🎯 **Powered by Google Gemini** LLM for intelligent SQL generation
- 🛡️ **Error Handling** with detailed error analysis and recovery strategies

---

## 🏗️ Architecture

```
                          User Question
                               ↓
    ┌─────────────────────────────────────────────────┐
    │              LangGraph Agent                    │
    │                                                 │
    │  ┌───────────────────────────────────────────┐ │
    │  │   1. Schema Loader                        │ │
    │  │   • Introspect database structure         │ │
    │  │   • Load table schemas and relationships  │ │
    │  └───────────────────────────────────────────┘ │
    │                      ↓                          │
    │  ┌───────────────────────────────────────────┐ │
    │  │   2. SQL Generator                        │ │
    │  │   • Analyze question + schema             │ │
    │  │   • Generate SQL with Gemini LLM          │ │
    │  └───────────────────────────────────────────┘ │
    │                      ↓                          │
    │  ┌───────────────────────────────────────────┐ │
    │  │   3. SQL Validator                        │ │
    │  │   • Run EXPLAIN QUERY PLAN                │ │
    │  │   • Check syntax without execution        │ │
    │  └───────────────────────────────────────────┘ │
    │                      ↓                          │
    │  ┌───────────────────────────────────────────┐ │
    │  │   4. SQL Executor                         │ │
    │  │   • Execute validated query               │ │
    │  │   • Capture results or errors             │ │
    │  └───────────────────────────────────────────┘ │
    │              ↓                 ↓                │
    │         Success            Error                │
    │              ↓                 ↓                │
    │  ┌──────────────────┐  ┌──────────────────┐   │
    │  │   5. Formatter   │  │  6. Error Handler│   │
    │  │   • Convert to   │  │  • Analyze error │   │
    │  │     natural lang │  │  • Decide retry  │   │
    │  └──────────────────┘  └──────────────────┘   │
    │                              ↓                  │
    │                       Retry (max 3x)           │
    │                              ↓                  │
    │                    Back to SQL Generator       │
    └─────────────────────────────────────────────────┘
                               ↓
                    Results + Execution Trace
```

### Component Details

- **Schema Loader**: Introspects the SQLite database to extract table structures, column names, data types, and foreign key relationships. This context is crucial for accurate SQL generation.

- **SQL Generator**: Uses Google Gemini LLM to convert natural language questions into SQL queries. It receives the user's question along with the complete database schema and generates dialect-specific SQL.

- **Validator**: Runs SQLite's `EXPLAIN QUERY PLAN` command to validate SQL syntax without actually executing the query. This catches syntax errors early and prevents potentially harmful queries.

- **Executor**: Executes the validated SQL query against the database and captures either the results or any runtime errors that occur during execution.

- **Error Handler**: Analyzes execution errors to determine if they're recoverable. It extracts error details, decides whether to retry, and provides context for the next generation attempt.

- **Formatter**: Converts raw SQL results into natural language answers that are easy for users to understand. It uses the LLM to create human-readable responses.

---

## 🛠️ Tech Stack

- **LangGraph**: Agent orchestration framework that manages the workflow state machine and enables autonomous decision-making
- **LangChain**: LLM integration library providing abstractions for prompt management, chains, and tool usage
- **Google Gemini**: Advanced large language model (gemini-1.5-flash) for SQL generation and natural language processing
- **SQLite**: Lightweight, serverless database engine with the Northwind sample dataset pre-loaded
- **Streamlit**: Modern web framework for building interactive data applications with Python
- **Python 3.8+**: Core programming language with type hints and modern async support

---

## 📦 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Google API key for Gemini (free tier available at [Google AI Studio](https://makersuite.google.com/app/apikey))
- Git (for cloning the repository)

### Step-by-Step Instructions

```bash
# 1. Clone the repository
git clone <repository-url>
cd nl2sql-agent

# 2. Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

# 5. Initialize the database
python data/setup_db.py

# 6. Run the application
streamlit run app.py
```

### Getting a Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"** or **"Get API Key"**
4. Copy the generated API key
5. Open the `.env` file in your project directory
6. Add your API key: `GOOGLE_API_KEY=your_api_key_here`
7. Save the file

**Note**: The Gemini API offers a generous free tier that's perfect for development and testing.

---

## 🚀 Usage

### Quick Start

1. **Launch the application**: After running `streamlit run app.py`, your browser will automatically open to `http://localhost:8501`

2. **Try a sample question**: Click any of the pre-loaded sample questions in the sidebar, or type your own question in the text input

3. **Watch the agent work**: The execution trace panel shows each step the agent takes, including SQL generation, validation, and error handling

4. **View results**: See the natural language answer, the generated SQL query, and the raw data results

### Sample Questions

The application comes with 5 pre-loaded questions that demonstrate different query types:

1. **"Which customers placed the most orders last year?"**  
   Tests: Aggregation, grouping, date filtering, ordering

2. **"What are the top 5 selling products by revenue?"**  
   Tests: Joins across multiple tables, revenue calculation, limiting results

3. **"Show me all orders that were shipped late"**  
   Tests: Date comparison, filtering, understanding business logic

4. **"Which sales rep has the highest average order value?"**  
   Tests: Complex aggregation, employee data, average calculations

5. **"What's the month-over-month revenue trend?"**  
   Tests: Time-series analysis, date grouping, trend calculation

### Understanding the Trace

The execution trace panel provides transparency into the agent's decision-making process:

- **Schema Loading**: Shows which tables and columns were loaded into context
- **SQL Generation**: Displays the SQL query generated by Gemini, including the reasoning
- **Validation**: Shows the EXPLAIN QUERY PLAN output confirming syntax correctness
- **Execution**: Displays query results or error messages
- **Error Handling**: If errors occur, shows the error analysis and retry decision
- **Retry Attempts**: Each retry is logged with the improved prompt and new SQL
- **Final Answer**: The natural language response generated from the results

This transparency helps you understand how the agent works and debug any issues.

---

## 📁 Project Structure

```
nl2sql-agent/
├── README.md                 # This file - comprehensive documentation
├── requirements.txt          # Python dependencies and versions
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules for Python projects
├── app.py                   # Main Streamlit application entry point
│
├── data/
│   ├── setup_db.py          # Database initialization script
│   ├── .gitkeep             # Keeps directory in git
│   └── northwind.db         # SQLite database (created by setup_db.py)
│
├── agent/
│   ├── __init__.py          # Agent package initialization
│   ├── state.py             # Agent state definition (AgentState class)
│   ├── graph.py             # LangGraph workflow definition
│   │
│   └── nodes/               # Agent node implementations
│       ├── __init__.py
│       ├── schema_loader.py # Database schema introspection
│       ├── sql_generator.py # SQL generation with Gemini
│       ├── validator.py     # SQL validation using EXPLAIN
│       ├── executor.py      # SQL execution and result capture
│       ├── error_handler.py # Error handling and retry logic
│       └── formatter.py     # Natural language answer formatting
│
└── ui/
    ├── __init__.py
    ├── .gitkeep             # Keeps directory in git
    └── components.py        # Reusable Streamlit UI components
```

---

## ⚙️ How It Works

### The Agent Loop

The NL2SQL Agent follows a sophisticated workflow to convert questions into answers:

1. **Question Input**: User submits a natural language question through the Streamlit interface

2. **Schema Loading**: The agent introspects the database to load table structures, column names, data types, and relationships into context

3. **SQL Generation**: Gemini LLM receives the question and schema, then generates an appropriate SQL query with reasoning

4. **Validation**: The generated SQL is validated using SQLite's `EXPLAIN QUERY PLAN` to catch syntax errors before execution

5. **Execution**: If validation passes, the query is executed against the database

6. **Success Path**: If execution succeeds, results are formatted into a natural language answer using the LLM

7. **Error Path**: If execution fails, the error is analyzed and the agent decides whether to retry

8. **Retry Logic**: On retry, the error message and context are added to the prompt, allowing Gemini to learn from its mistake

9. **Final Output**: After success or max retries (3), the agent returns the final answer with a complete execution trace

### Self-Correction Mechanism

The agent's self-correction capability is key to its reliability:

- **Error Capture**: All errors are captured with full context including the SQL query, error message, and database state

- **Error Analysis**: The error handler examines the error type and determines if it's recoverable (syntax errors, wrong table names) or fatal (database corruption)

- **Contextual Retry**: When retrying, the agent provides Gemini with:
  - The original question
  - The database schema
  - The previous SQL attempt
  - The error message received
  - Guidance on what went wrong

- **Learning from Mistakes**: Gemini uses this context to generate improved SQL that addresses the specific error

- **Attempt Limiting**: Maximum 3 retry attempts prevent infinite loops while giving the agent enough chances to succeed

- **Trace Logging**: Every attempt is logged in the execution trace, providing full transparency into the correction process

This mechanism allows the agent to handle common errors like typos, wrong table names, incorrect join conditions, and syntax mistakes autonomously.

---

## 🎨 Customization

### Using Your Own Database

To use a different SQLite database:

1. **Replace the database file**:
   ```bash
   # Backup the original
   mv data/northwind.db data/northwind.db.backup
   
   # Copy your database
   cp /path/to/your/database.db data/northwind.db
   ```

2. **Update setup script** (optional):
   - Edit `data/setup_db.py` if you need custom initialization
   - The agent will automatically introspect any SQLite database

3. **Test the schema loading**:
   - Run the app and check if tables are loaded correctly
   - The schema loader works with any SQLite database structure

**Note**: For PostgreSQL, MySQL, or other databases, you'll need to modify the schema loader and executor nodes to use appropriate database drivers.

### Changing the LLM

To use a different language model:

1. **Install the appropriate LangChain integration**:
   ```bash
   pip install langchain-openai  # For OpenAI
   pip install langchain-anthropic  # For Claude
   ```

2. **Update SQL Generator** (`agent/nodes/sql_generator.py`):
   ```python
   from langchain_openai import ChatOpenAI
   
   # Replace ChatGoogleGenerativeAI with:
   llm = ChatOpenAI(model="gpt-4", temperature=0)
   ```

3. **Update Formatter** (`agent/nodes/formatter.py`):
   - Make the same LLM replacement

4. **Update environment variables**:
   - Add the new API key to `.env` (e.g., `OPENAI_API_KEY`)

5. **Adjust prompts if needed**:
   - Different models may respond better to different prompt styles

### Customizing the UI

**Component Changes** (`ui/components.py`):
- Modify `render_trace()` to change trace display format
- Update `render_results()` to customize result presentation
- Add new components for additional features

**Layout Changes** (`app.py`):
- Adjust `st.columns()` ratios for different layouts
- Modify sidebar content and organization
- Add new sections or remove existing ones

**Styling** (`app.py` - `apply_custom_css()` function):
- Edit CSS to change colors, fonts, spacing
- Add custom classes for new components
- Modify the trace panel styling

Example CSS customization:
```python
def apply_custom_css():
    st.markdown("""
        <style>
        .main { background-color: #f0f2f6; }
        .trace-step { 
            background-color: #ffffff;
            border-left: 4px solid #4CAF50;
        }
        </style>
    """, unsafe_allow_html=True)
```

---

## 🔧 Troubleshooting

### Common Issues and Solutions

**"No API key found" or "Invalid API key"**
- **Cause**: Missing or incorrect `GOOGLE_API_KEY` in `.env` file
- **Solution**: 
  1. Ensure `.env` file exists in project root
  2. Verify the API key is correct (no extra spaces)
  3. Check that the key hasn't expired
  4. Try generating a new key from Google AI Studio

**"Database not found" or "Unable to open database file"**
- **Cause**: Database hasn't been initialized
- **Solution**: 
  ```bash
  python data/setup_db.py
  ```
- **Verify**: Check that `data/northwind.db` exists and is not empty

**"Import errors" or "Module not found"**
- **Cause**: Dependencies not installed or virtual environment not activated
- **Solution**:
  ```bash
  # Activate virtual environment first
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  
  # Reinstall dependencies
  pip install -r requirements.txt
  ```

**"Agent fails repeatedly" or "All retry attempts exhausted"**
- **Cause**: API key issues, network problems, or genuinely difficult questions
- **Solution**:
  1. Check API key validity and quota
  2. Verify internet connection
  3. Try simpler questions first
  4. Check the trace to see what errors occurred
  5. Ensure database schema is loaded correctly

**"Streamlit won't start" or "Address already in use"**
- **Cause**: Port 8501 is already in use by another application
- **Solution**:
  ```bash
  # Use a different port
  streamlit run app.py --server.port 8502
  
  # Or kill the process using port 8501
  # Windows:
  netstat -ano | findstr :8501
  taskkill /PID <process_id> /F
  
  # macOS/Linux:
  lsof -ti:8501 | xargs kill -9
  ```

**"SQL syntax errors persist" or "Invalid SQL generated"**
- **Cause**: Complex question, ambiguous schema, or LLM limitations
- **Solution**:
  1. Rephrase the question more clearly
  2. Check if the required tables/columns exist
  3. Try breaking complex questions into simpler parts
  4. Review the trace to understand what SQL was generated

**"Results are empty" or "No data returned"**
- **Cause**: Query is correct but no matching data exists
- **Solution**:
  1. Verify data exists in the database
  2. Check date ranges and filters in your question
  3. Try broader questions first
  4. Inspect the generated SQL to ensure it matches your intent

---

## 🤝 Contributing

We welcome contributions to improve NL2SQL Agent! Here's how you can help:

### How to Contribute

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/nl2sql-agent.git
   cd nl2sql-agent
   ```

3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make your changes**:
   - Write clean, documented code
   - Follow existing code style
   - Add tests if applicable
   - Update documentation

5. **Test your changes**:
   ```bash
   # Run the application
   streamlit run app.py
   
   # Test with various questions
   # Verify the trace shows correct behavior
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Submit a pull request** on GitHub with:
   - Clear description of changes
   - Why the changes are needed
   - Any testing you've done

### Areas for Contribution

- 🐛 Bug fixes and error handling improvements
- ✨ New features (see Future Enhancements below)
- 📚 Documentation improvements
- 🧪 Test coverage
- 🎨 UI/UX enhancements
- 🌐 Support for additional databases
- 🔧 Performance optimizations

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 NL2SQL Agent Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

This project builds upon excellent open-source tools and resources:

- **[Northwind Database](https://github.com/jpwhite3/northwind-SQLite3)**: Classic sample database with realistic business data, perfect for demonstrating SQL capabilities

- **[LangGraph](https://github.com/langchain-ai/langgraph)**: Powerful framework for building stateful, multi-actor applications with LLMs

- **[LangChain](https://github.com/langchain-ai/langchain)**: Comprehensive library for developing applications powered by language models

- **[Google Gemini](https://deepmind.google/technologies/gemini/)**: Advanced AI model providing intelligent SQL generation and natural language understanding

- **[Streamlit](https://streamlit.io/)**: Beautiful framework for creating data applications with minimal code

- **Open Source Community**: All the developers who contribute to the tools and libraries that make this project possible

---

## 🚀 Future Enhancements

Ideas and features planned for future development:

### Database Support
- 🐘 **PostgreSQL Support**: Extend to support PostgreSQL with its advanced features
- 🐬 **MySQL Compatibility**: Add MySQL dialect support and connection handling
- 🔗 **Multi-Database**: Support querying across multiple databases simultaneously
- ☁️ **Cloud Databases**: Integration with cloud database services (AWS RDS, Azure SQL, etc.)

### Query Capabilities
- 🔍 **Query Optimization**: Suggest optimizations for generated SQL queries
- 📖 **SQL Explanations**: Natural language explanations of what the SQL query does
- 📊 **Visualization**: Automatic chart generation for appropriate query results
- 🔄 **Query History**: Persist and search through previous queries and results

### User Experience
- 💬 **Multi-Turn Conversations**: Maintain context across multiple questions
- 🎯 **Query Suggestions**: Suggest follow-up questions based on results
- 📤 **Export Options**: Export results to CSV, Excel, JSON, or PDF
- 🌙 **Dark Mode**: Theme support for better user experience
- 🔔 **Notifications**: Alert users when long-running queries complete

### Advanced Features
- 🧠 **Schema Learning**: Learn from user corrections to improve future queries
- 🔐 **Access Control**: Role-based access to different tables and queries
- 📈 **Analytics Dashboard**: Track query patterns and agent performance
- 🌍 **Multi-Language**: Support for questions in multiple languages
- 🤖 **Custom Agents**: Allow users to create specialized agents for specific domains

### Developer Tools
- 🧪 **Testing Suite**: Comprehensive test coverage with example questions
- 📊 **Benchmarking**: Performance metrics and comparison tools
- 🔌 **API Mode**: REST API for programmatic access
- 📚 **Plugin System**: Allow custom nodes and extensions
- 🐳 **Docker Support**: Containerized deployment options

---

## 📞 Support

If you encounter issues or have questions:

1. **Check the Troubleshooting section** above
2. **Review the execution trace** for detailed error information
3. **Search existing issues** on GitHub
4. **Open a new issue** with:
   - Clear description of the problem
   - Steps to reproduce
   - Execution trace output
   - Your environment details (OS, Python version, etc.)

---

## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub! It helps others discover the project and motivates continued development.

---

**Built with ❤️ using LangGraph, LangChain, and Google Gemini**

*Making database querying accessible to everyone through the power of AI*