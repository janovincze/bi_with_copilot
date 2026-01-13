# Copilot Analytics - Docker Image
# Builds and runs the AI-powered dashboard with dbt + DuckDB

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy dbt project
COPY dbt_project/ ./dbt_project/

# Copy AI dashboard application
COPY ai_dashboard/ ./ai_dashboard/

# Build dbt project (seeds + models)
WORKDIR /app/dbt_project
RUN dbt deps && dbt seed && dbt build

# Back to app root
WORKDIR /app

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV COPILOT_API_URL=http://host.docker.internal:4141/v1

# Expose ports for both Flask and Streamlit
EXPOSE 8084 8501

# Default command runs Streamlit
# Override with: docker run ... python ai_dashboard/app_flask.py
CMD ["streamlit", "run", "ai_dashboard/app_streamlit.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
