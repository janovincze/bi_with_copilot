"""
Simple Text-to-SQL engine using GitHub Copilot.
This is a lightweight alternative to complex agent frameworks,
designed to be easy to understand and modify.
"""

import os
import duckdb
import pandas as pd
from openai import OpenAI
from pathlib import Path
from typing import Optional, List, Tuple

from config import get_llm_config, DATABASE_PATH


class CopilotAnalytics:
    """
    A simple text-to-SQL engine that uses GitHub Copilot (via copilot-api)
    to convert natural language questions into SQL queries.

    This class is intentionally simple and educational - it shows how
    text-to-SQL works without hiding complexity in a framework.
    """

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize the analytics engine.

        Args:
            database_path: Path to DuckDB database. Defaults to config value.
        """
        # Set up database connection
        self.db_path = database_path or str(DATABASE_PATH)
        self.connection = None

        # Set up LLM client (OpenAI-compatible, works with copilot-api)
        llm_config = get_llm_config()
        self.client = OpenAI(
            api_key=llm_config["api_key"],
            base_url=llm_config["base_url"],
        )
        self.model = llm_config["model"]

        # Schema cache for prompts
        self._schema_cache: Optional[str] = None

        # Training data (question -> SQL pairs for few-shot learning)
        self.training_examples: List[Tuple[str, str]] = []

        print(f"CopilotAnalytics initialized")
        print(f"  LLM: {llm_config['base_url']} ({self.model})")
        print(f"  Database: {self.db_path}")

    def connect(self) -> None:
        """Connect to the DuckDB database."""
        if self.connection is None:
            self.connection = duckdb.connect(self.db_path, read_only=True)
            print(f"Connected to database: {self.db_path}")

    def disconnect(self) -> None:
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def run_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a DataFrame.

        Args:
            sql: SQL query to execute

        Returns:
            DataFrame with query results
        """
        self.connect()
        try:
            return self.connection.execute(sql).fetchdf()
        except Exception as e:
            raise Exception(f"SQL Error: {e}\nQuery: {sql}")

    def get_schema(self) -> str:
        """
        Get the database schema as a formatted string for the LLM prompt.
        Includes table names, column names, and types.
        """
        if self._schema_cache:
            return self._schema_cache

        self.connect()

        # Get all tables
        tables = self.run_sql("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
        """)

        schema_parts = []
        for table_name in tables['table_name']:
            # Get columns for each table
            columns = self.run_sql(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
            """)

            col_str = ", ".join([
                f"{row['column_name']} ({row['data_type']})"
                for _, row in columns.iterrows()
            ])
            schema_parts.append(f"  {table_name}: {col_str}")

        self._schema_cache = "\n".join(schema_parts)
        return self._schema_cache

    def add_training_example(self, question: str, sql: str) -> None:
        """
        Add a question-SQL pair for few-shot learning.

        Args:
            question: Natural language question
            sql: Corresponding SQL query
        """
        self.training_examples.append((question, sql))

    def _build_prompt(self, question: str) -> str:
        """
        Build the prompt for the LLM including schema and examples.

        Args:
            question: User's natural language question

        Returns:
            Complete prompt string
        """
        schema = self.get_schema()

        # Build few-shot examples section
        examples_section = ""
        if self.training_examples:
            examples = []
            for q, sql in self.training_examples[:5]:  # Use up to 5 examples
                examples.append(f"Question: {q}\nSQL: {sql}")
            examples_section = "\n\nExamples:\n" + "\n\n".join(examples)

        prompt = f"""You are a SQL expert. Generate a DuckDB SQL query for the following question.

Database Schema:
{schema}
{examples_section}

Rules:
- Return ONLY the SQL query, no explanations
- Use DuckDB SQL syntax
- For date formatting use strftime()
- Always include ORDER BY for consistent results
- Use ROUND() for decimal values

Question: {question}

SQL:"""
        return prompt

    def generate_sql(self, question: str) -> str:
        """
        Generate SQL from a natural language question using the LLM.

        Args:
            question: Natural language question about the data

        Returns:
            Generated SQL query
        """
        prompt = self._build_prompt(question)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a SQL expert that generates DuckDB SQL queries. Return only the SQL query, nothing else."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent SQL
                max_tokens=500,
            )

            sql = response.choices[0].message.content.strip()

            # Clean up the SQL (remove markdown code blocks if present)
            if sql.startswith("```"):
                sql = sql.split("```")[1]
                if sql.startswith("sql"):
                    sql = sql[3:]
            sql = sql.strip()

            return sql

        except Exception as e:
            raise Exception(f"LLM Error: {e}")

    def ask(self, question: str) -> Tuple[str, pd.DataFrame]:
        """
        Ask a question and get both the SQL and results.

        Args:
            question: Natural language question

        Returns:
            Tuple of (SQL query, DataFrame results)
        """
        sql = self.generate_sql(question)
        df = self.run_sql(sql)
        return sql, df


def create_analytics_instance(connect_db: bool = True) -> CopilotAnalytics:
    """
    Factory function to create a configured analytics instance.

    Args:
        connect_db: If True, automatically connects to the database.

    Returns:
        CopilotAnalytics instance ready to use.
    """
    analytics = CopilotAnalytics()

    if connect_db:
        analytics.connect()

    return analytics


# For backwards compatibility with existing code
CopilotVanna = CopilotAnalytics
create_vanna_instance = create_analytics_instance


if __name__ == "__main__":
    # Test the connection
    print("Testing CopilotAnalytics...")
    analytics = create_analytics_instance()

    print("\nDatabase Schema:")
    print(analytics.get_schema())

    print("\nTest query - counting customers:")
    df = analytics.run_sql("SELECT COUNT(*) as count FROM customers")
    print(df)
