# Turn GitHub Copilot into Your Personal Analytics AI: An Intro for Business Analysts

*What if the GitHub Copilot subscription your company already pays for could create dashboards from plain English? This article includes a complete working application you can try in 5 minutes.*

---

## The Problem Every BA Knows Too Well

You need a new report. It's urgent. Stakeholders want to see customer lifetime value by segment, revenue trends, and a breakdown of payment methods.

So you do what you've always done:
1. Submit a ticket to the data team
2. Wait 3-5 business days (if you're lucky)
3. Receive the report
4. Realize you needed one more column
5. Go back to step 1

Sound familiar?

Meanwhile, you have GitHub Copilot sitting there, helping developers write code. But what if it could help *you* query data just by asking questions in plain English?

**It can. And I'll show you how.**

---

## The Untapped Power in Your Toolbox

Here's something most Business Analysts don't realize:

GitHub Copilot isn't just for writing code. Under the hood, it's powered by advanced AI models that understand language, logic, and structured data. The same intelligence that helps developers write Python can help you write SQL queries.

You don't need:
- A separate OpenAI API subscription ($$$)
- Data engineering expertise
- Python or Node.js installed
- Permission from IT to install new tools

You need:
- Your existing GitHub Copilot license
- Docker (that's it!)
- 5 minutes to set up

---

## What We're Building

By the end of this article, you'll have a personal analytics assistant that:

1. **Accepts natural language questions** - "Who are our top customers?"
2. **Generates SQL automatically** - Using your data documentation
3. **Creates visualizations** - Charts and tables from your data
4. **Runs entirely on your laptop** - Your data never leaves your machine

Here's what the finished product looks like:

```
You: "Show me monthly revenue trends"

AI: Here's what I found:
    [SQL Query displayed]
    [Data Table with results]
    [Line Chart visualization]
```

---

## The Secret Sauce: Your Data Documentation

Here's the critical insight that makes this work: **the AI is only as good as your data documentation.**

Most text-to-SQL tools fail because they only see raw table and column names. When you ask "show me high-value customers," the AI has no idea what "high-value" means in your business context.

### Why dbt (or Any Data Modeling Tool) is Critical

We use **dbt (data build tool)** in this project, but the principle applies to any data modeling approach - whether it's dbt, LookML, Cube.js, or even well-documented views in your data warehouse.

**The key insight: Your data documentation becomes the AI's business knowledge.**

Without documentation, the AI sees:

```
TABLE: customers
COLUMNS: cust_id, ltv, seg
```

*What does "ltv" mean? What are the "seg" values? The AI has to guess.*

With rich documentation, the AI sees:

```
TABLE: customers
DESCRIPTION: Customer profiles with calculated lifetime value and segmentation.
             Use this table for customer behavior analysis and marketing segmentation.

COLUMNS:
- customer_id: Unique identifier for each customer
- lifetime_value: Total amount spent across all orders in dollars.
                  Higher values indicate more valuable customers.
                  Calculated as SUM(order_amount) across all orders.
- customer_segment: Customer tier based on lifetime value:
                    'High Value' (>$100), 'Medium Value' ($50-100),
                    'Low Value' (<$50)
```

*Now the AI understands your business logic!*

### The Documentation Investment Pays Off

This is why organizations that have invested in data documentation (through dbt, data catalogs, or semantic layers) are perfectly positioned to leverage AI:

- **Column descriptions** teach the AI what metrics mean
- **Table descriptions** explain when to use each table
- **Business logic** embedded in documentation guides query generation
- **Example queries** provide patterns for the AI to follow

**If your organization already uses dbt, you're 80% of the way there.** Your existing schema.yml files become the AI's training data.

> **Bottom line:** The time your data team spent documenting models in dbt isn't just for human readability anymore - it's now training data for AI-powered analytics.

---

## How It Works (Technical Overview)

```
┌─────────────────────────────────────────────────────────────┐
│                 Your Question (Natural Language)             │
│              "Who are our high-value customers?"             │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Text-to-SQL Engine                         │
│  Schema + Example Queries + Your Question → Prompt           │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Copilot                           │
│  Generates SQL based on context and question                 │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       DuckDB                                 │
│  Executes query locally and returns results                  │
└─────────────────────────────────────┬───────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                    Visualization                             │
│  Automatically generates appropriate charts                  │
└─────────────────────────────────────────────────────────────┘
```

**Key Components:**

1. **Text-to-SQL Engine** - Custom engine with few-shot learning (18 example queries included)
2. **copilot-api** - Exposes GitHub Copilot as an API endpoint
3. **dbt** - Data transformation and documentation framework
4. **DuckDB** - Lightning-fast local database
5. **Docker** - One-command setup that builds everything automatically

---

## Try It Yourself (5-Minute Setup)

You have two options: **Docker** (recommended - no installation required!) or **Local Python** (for customization).

---

### Option A: Docker Setup (Easiest - No Installation Required!)

Docker handles everything - **no Python, no Node.js, no dependencies to install.**

**Step 1: Clone the repository**

```bash
git clone https://github.com/janovincze/bi_with_copilot.git
cd bi_with_copilot
```

**Step 2: Authenticate with GitHub Copilot (one-time only)**

```bash
docker compose run --rm auth
```

This starts the GitHub Device Flow authentication:

1. The terminal displays a **user code** and a URL:
   ```
   Please visit: https://github.com/login/device
   And enter code: ABCD-1234
   ```

2. Open https://github.com/login/device in your browser

3. Sign in to GitHub (if not already signed in)

4. Enter the **user code** from your terminal

5. Click **Authorize** to grant access

6. Return to terminal - you'll see "Authentication successful!"

> **Important:** Your GitHub account needs an active Copilot subscription.

**Step 3: Start everything**

```bash
docker compose up
```

That's it! Docker will:
- Start the Copilot API proxy
- Build the Python environment
- Run `dbt build` to create models and seed data
- Start Streamlit automatically

Open http://localhost:8501 and start asking questions.

**Alternative: Run Flask instead**
```bash
docker compose --profile flask up
# Open http://localhost:8084
```

---

### Option B: Local Python Setup

If you prefer running without Docker or want to customize the code:

**Step 1: Clone the Repository**

```bash
git clone https://github.com/janovincze/bi_with_copilot.git
cd bi_with_copilot
```

**Step 2: Run Setup**

**Mac/Linux:**
```bash
./setup.sh
```

**Windows:**
```cmd
setup.bat
```

This installs dependencies and builds the sample data models.

**Step 3: Start Copilot API**

```bash
# First time: authenticate with GitHub
npx copilot-api@latest auth
```

This starts the GitHub Device Flow - follow the same steps as Docker:
1. Open https://github.com/login/device
2. Enter the code shown in terminal
3. Click **Authorize**

```bash
# Start the server
npx copilot-api@latest start --rate-limit 10
```

**Step 4: Train and Launch**

In a new terminal:

```bash
source venv/bin/activate
cd ai_dashboard
python train_vanna.py
streamlit run app_streamlit.py
```

---

### Start Asking Questions!

Open http://localhost:8501 and try:

**Basic queries:**
- "Show me monthly revenue"
- "Top 10 customers by lifetime value"
- "Revenue breakdown by payment method"

**Advanced analytics (yes, it handles these too!):**
- "Show cumulative revenue over time"
- "Calculate month over month growth rate"
- "What percentage of revenue comes from top 20% of customers?"
- "Segment customers into LTV percentile bands"

---

## Real-World Application

The demo uses sample data, but the real power comes from connecting to your actual data warehouse.

**To adapt this for your organization:**

1. **Replace the dbt models** with your actual data models
2. **Add rich documentation** to your schema.yml files
3. **Train the model** on your specific queries and terminology
4. **Connect to your database** (PostgreSQL, Snowflake, BigQuery supported)

The key is documentation quality. The more context you give the AI about what your data means, the better it performs.

---

## Important Considerations

### Security & Privacy

- Queries are sent to GitHub Copilot for processing
- Don't use with sensitive/confidential data without proper authorization
- Consider local alternatives (Ollama + Llama) for sensitive workloads

### Terms of Service

Using copilot-api to access Copilot may not align with GitHub's Terms of Service. Check with your organization's policies before deploying in production.

### Accuracy

AI-generated SQL isn't always perfect. Always verify important queries, especially for:
- Financial reports
- Compliance reporting
- Executive dashboards

---

## Why Streamlit? (And What's Coming Next)

You might be wondering: *"Why Streamlit? My organization uses Power BI / Tableau / Looker."*

**Streamlit is just for demonstration.** It's the fastest way to show you the concept works without any complex setup. The real value isn't the frontend - it's the text-to-SQL engine that can integrate with *any* visualization tool.

---

## What's Coming Next - The Roadmap

This is **Part 1** of a series. Here's what's coming:

---

### Part 2: Power BI Integration 📊

**Stop waiting for the data team.** In the next article, I'll show you how to:

- Connect this text-to-SQL engine directly to Power BI
- Create a custom Power BI visual that accepts natural language
- Query your existing Power BI datasets using plain English
- Build self-service reports without learning DAX

*If you're a Power BI user, this is the article you've been waiting for.*

---

### Part 3: Your Own Fine-Tuned Local Model 🔒

**This is the big one.**

What if you could have an AI model that:
- **Knows YOUR schema** - trained specifically on your tables, columns, and business logic
- **Speaks YOUR language** - understands your company's terminology and acronyms
- **Runs 100% locally** - no data ever leaves your network
- **Costs nothing** - no API fees, no per-query charges
- **Works offline** - no internet connection required

**I'm building a complete guide to fine-tuning a local LLM on your specific data warehouse schema.**

This means:
- 🏢 **Enterprise-safe** - IT and Security teams can approve it because data never leaves your infrastructure
- 🎯 **Higher accuracy** - A model trained on YOUR schema outperforms generic models
- 💰 **Zero ongoing costs** - Run unlimited queries without API fees
- 🔐 **Complete privacy** - Sensitive column names and business logic stay internal

> **Coming soon:** A step-by-step guide to fine-tune Llama 3 (or similar) on your dbt schema, deployable on a single laptop or your organization's servers.

*Subscribe to be notified when Part 2 and Part 3 are published.*

---

## Takeaways

1. **You already have access to powerful AI** through GitHub Copilot
2. **Your dbt documentation is now AI training data** - the investment in data modeling pays dividends
3. **Self-service analytics is possible** without waiting for the data team
4. **Streamlit is just the beginning** - Power BI integration is coming in Part 2
5. **The future is local fine-tuned models** - enterprise-safe, private, and free (Part 3)

The future of analytics isn't about tools - it's about asking questions in your own language and getting answers instantly.

Your GitHub Copilot is ready to help. Are you?

---

**Resources:**

- [GitHub Repository](https://github.com/janovincze/bi_with_copilot) - Full source code
- [dbt Documentation](https://docs.getdbt.com) - Data transformation best practices
- [copilot-api](https://github.com/ericc-ch/copilot-api) - GitHub Copilot API proxy
- [DuckDB](https://duckdb.org) - Fast in-process analytics database

---

## Try It Now

The repository is ready to clone. In 5 minutes, you can be asking questions in plain English and getting SQL + visualizations.

**[Clone the Repository →](https://github.com/janovincze/bi_with_copilot)**

---

*Did you try this? Share your experience in the comments! I'd love to hear what questions you asked and how well the AI performed.*

**Follow me for the next articles in this series:**
- 📊 **Part 2: Power BI Integration** - Natural language queries in your Power BI reports
- 🔒 **Part 3: Fine-Tuned Local Model** - Enterprise-safe, private, and free

---

#DataAnalytics #BusinessIntelligence #AI #GitHubCopilot #dbt #Docker #DataScience #BusinessAnalysis #NoCode #SelfServiceAnalytics #PowerBI #TextToSQL
