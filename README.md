# Copilot Analytics

**Turn GitHub Copilot into Your Personal Analytics AI**

Ask questions about your data in plain English. Get SQL queries and visualizations automatically.

```
You: "Show me monthly revenue trends"
AI:  [Generates SQL] → [Runs Query] → [Creates Chart]
```

## Why This Exists

Business Analysts often have GitHub Copilot through their organization but don't realize they can use it for data analytics. This project shows how to:

- Convert natural language questions to SQL queries
- Auto-generate charts and visualizations
- Use your existing Copilot subscription (no extra API costs)
- Leverage your dbt documentation as AI training data

## The Key Insight: Documentation = AI Intelligence

**The AI is only as good as your data documentation.**

This project uses dbt schema descriptions to teach the AI your business logic. When you document that `lifetime_value` means "total revenue from customer" and `customer_segment` has values like "High Value" and "Low Value" - the AI understands your business context.

**If your organization uses dbt, you're already 80% ready.** Your existing schema.yml files become AI training data.

## Quick Start with Docker (Recommended)

**No Python or Node.js installation required!** Just Docker.

### Prerequisites

- Docker and Docker Compose
- GitHub Copilot subscription

### Setup

**Step 1: Clone the repository**

```bash
git clone https://github.com/janovincze/bi_with_copilot.git
cd bi_with_copilot
```

**Step 2: Authenticate with GitHub Copilot (first time only)**

```bash
docker compose run --rm auth
```

This starts the GitHub Device Flow authentication:

1. The terminal will display a **user code** (e.g., `ABCD-1234`) and a URL
2. Open https://github.com/login/device in your browser
3. Sign in to GitHub if prompted
4. Enter the **user code** shown in your terminal
5. Click **Authorize** to grant access to GitHub Copilot
6. Return to your terminal - you should see "Authentication successful!"

```
Example terminal output:
───────────────────────────────────────────────
  Please visit: https://github.com/login/device
  And enter code: ABCD-1234
───────────────────────────────────────────────
```

> **Note:** Your GitHub account must have an active GitHub Copilot subscription (individual, business, or enterprise).

**Step 3: Start everything**

```bash
docker compose up
```

**That's it!** Open http://localhost:8501 in your browser.

Docker automatically:
- Starts the Copilot API proxy
- Builds the dbt project and creates the database
- Launches the Streamlit dashboard

### Docker Services

| Service | Command | URL | Description |
|---------|---------|-----|-------------|
| `auth` | `docker compose run --rm auth` | - | One-time GitHub authentication |
| Default | `docker compose up` | http://localhost:8501 | Copilot API + Streamlit |
| Flask | `docker compose --profile flask up` | http://localhost:8084 | Copilot API + Flask |
| Dev | `docker compose --profile dev up` | http://localhost:8501 | Dev mode with live reload |

### How Docker Works

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Compose                        │
│  ┌─────────────┐      ┌─────────────────────────────┐   │
│  │ copilot-api │◄────►│ streamlit (dbt built-in)    │   │
│  │  (port 4141)│      │    (port 8501)              │   │
│  └──────┬──────┘      └─────────────────────────────┘   │
│         │                                                │
│         │ Docker volume: copilot-credentials             │
└─────────┼───────────────────────────────────────────────┘
          │
          ▼
   GitHub Copilot API
```

Credentials are stored in a Docker volume - you only authenticate once.

---

## Alternative: Local Python Setup

If you prefer running without Docker or want to customize the code:

### Prerequisites

- Python 3.9 - 3.13 (Python 3.14+ not supported by dbt)
- Node.js 18+ (for copilot-api)
- GitHub Copilot subscription

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/janovincze/bi_with_copilot.git
cd bi_with_copilot

# 2. Run setup script
./setup.sh          # macOS/Linux
# or
setup.bat           # Windows
```

### Running

**Terminal 1 - Start Copilot API:**
```bash
# First time only: authenticate with GitHub
npx copilot-api@latest auth
```

This starts the GitHub Device Flow:
1. Terminal shows a **user code** and URL
2. Open https://github.com/login/device
3. Enter the code and click **Authorize**
4. Return to terminal - authentication complete!

```bash
# Start the API server
npx copilot-api@latest start --rate-limit 10
```

**Terminal 2 - Start Dashboard:**
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate

cd ai_dashboard
python train_vanna.py     # First time only
streamlit run app_streamlit.py
```

Open http://localhost:8501 in your browser.

---

## Example Questions

Once running, try asking:

- "Show me monthly revenue trends"
- "Who are the top 10 customers by lifetime value?"
- "What is the revenue breakdown by payment method?"
- "How many customers are in each segment?"
- "What's the average order value?"
- "Show cumulative revenue over time"
- "Calculate month over month growth rate"

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Your Question (Natural Language)             │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     Text-to-SQL Engine                       │
│    Schema + Examples + Question → LLM → SQL Query            │
└─────────────────────────────────────┬───────────────────────┘
                                      │
            ┌─────────────────────────┼─────────────────────────┐
            ▼                         ▼                         ▼
    ┌───────────────┐       ┌───────────────┐       ┌───────────────┐
    │  copilot-api  │       │    DuckDB     │       │  dbt Models   │
    │  (LLM proxy)  │       │ (query engine)│       │  (metadata)   │
    └───────┬───────┘       └───────────────┘       └───────────────┘
            │
            ▼
    ┌───────────────┐
    │ GitHub Copilot│
    └───────────────┘
```

## Project Structure

```
copilot-analytics/
├── dbt_project/              # dbt data models
│   ├── models/
│   │   ├── staging/          # Staging models
│   │   └── marts/            # Business-ready models
│   └── seeds/                # Sample data (50 customers, 100 orders)
│
├── ai_dashboard/             # AI application
│   ├── copilot_vanna.py      # Text-to-SQL engine
│   ├── train_vanna.py        # Training examples (18 queries)
│   ├── app_flask.py          # Flask web app
│   └── app_streamlit.py      # Streamlit web app
│
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker orchestration
├── setup.sh / setup.bat      # Local setup scripts
├── Makefile                  # Common commands
└── requirements.txt          # Python dependencies
```

## Data Model

The sample data represents a fictional Jaffle Shop restaurant:

| Table | Description |
|-------|-------------|
| `customers` | Customer profiles with lifetime value and segmentation |
| `orders` | Order transactions with payment totals |
| `revenue_by_month` | Monthly revenue aggregations |
| `revenue_by_customer` | Revenue by customer segment |
| `payment_analysis` | Payment method breakdown |

## Make Commands

### Docker Commands (Recommended)
```bash
make docker-auth      # Authenticate with GitHub Copilot
make docker-up        # Start everything (copilot-api + streamlit)
make docker-down      # Stop all services
make docker-flask     # Run Flask instead of Streamlit
make docker-dev       # Dev mode with live reload
make docker-build     # Rebuild Docker images
make docker-clean     # Remove images and credentials
```

### Local Commands
```bash
make setup            # Full local setup
make copilot-auth     # Authenticate Copilot (requires Node.js)
make copilot-start    # Start Copilot API (requires Node.js)
make train            # Train the model
make run-flask        # Start Flask app
make run-streamlit    # Start Streamlit app
make dbt-build        # Rebuild dbt models
make dbt-docs         # View dbt documentation
make clean            # Clean all generated files
```

## Connecting Your Own Data

1. **Replace dbt models** in `dbt_project/models/` with your own
2. **Add rich descriptions** to schema.yml files (the AI uses these!)
3. **Re-run training**: Add your example queries to `train_vanna.py`
4. **Rebuild**: `docker compose build --no-cache && docker compose up`

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
# Default: GitHub Copilot
COPILOT_API_URL=http://localhost:4141/v1
LLM_MODEL=gpt-4.1

# Alternative: Direct OpenAI
# OPENAI_API_KEY=sk-...
```

## Alternative LLM Backends

**OpenAI (Direct):**
```bash
export OPENAI_API_KEY=sk-your-key
```

**Ollama (Local, Free):**
```bash
ollama pull llama3
export OLLAMA_HOST=http://localhost:11434
```

## Troubleshooting

### Docker Issues

**"Credentials not found" or authentication errors:**
```bash
docker compose run --rm auth
```

**"Service unhealthy" errors:**
```bash
docker compose logs copilot-api
docker compose down && docker compose up
```

**Reset everything:**
```bash
docker compose down --volumes
docker compose run --rm auth
docker compose up
```

### Local Setup Issues

**"Python 3.14 compatibility error":**
```bash
# Install Python 3.13 (macOS)
brew install python@3.13
# Re-run setup - it will find Python 3.13 automatically
```

**"Database not found":**
```bash
cd dbt_project && dbt build
```

**"Connection refused":**
Make sure copilot-api is running in a separate terminal.

## Limitations & Disclaimers

- **Rate Limits**: GitHub Copilot has usage limits. Rate limiting is built-in.
- **Terms of Service**: Using copilot-api may not align with GitHub's ToS. Check your organization's policies.
- **Data Privacy**: Queries are sent to Copilot. Don't use with sensitive data without authorization.
- **Accuracy**: AI-generated SQL may not always be correct. Always verify important queries.

## Why Streamlit?

**Streamlit is just for demonstration.** It's the fastest way to prove the concept works. The real value is the text-to-SQL engine, which can integrate with any visualization tool.

## What's Next - Series Roadmap

This is **Part 1** of a series:

### Part 2: Power BI Integration 📊
- Connect the text-to-SQL engine to Power BI
- Natural language queries in your existing Power BI reports
- Self-service analytics without learning DAX

### Part 3: Fine-Tuned Local Model 🔒
**The enterprise-safe solution:**
- Train a model on YOUR specific schema and business terminology
- Runs 100% locally - no data leaves your network
- Zero API costs - unlimited queries
- IT/Security approved - complete data privacy

> A fine-tuned local model trained on your dbt schema will outperform generic models and can be deployed on a single laptop or your organization's servers.

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT

---

**This is Part 1 of a series.** Star this repo to be notified when Part 2 (Power BI) and Part 3 (Fine-Tuned Local Model) are released.

*Built with [dbt](https://getdbt.com), [DuckDB](https://duckdb.org), [Streamlit](https://streamlit.io), and [copilot-api](https://github.com/ericc-ch/copilot-api)*
