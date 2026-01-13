"""
Utility to parse dbt schema.yml files and extract documentation for AI training.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any


def parse_schema_file(schema_path: Path) -> List[Dict[str, Any]]:
    """
    Parse a dbt schema.yml file and extract model documentation.

    Args:
        schema_path: Path to a dbt schema.yml file

    Returns:
        List of model documentation dictionaries
    """
    with open(schema_path, "r") as f:
        schema = yaml.safe_load(f)

    if not schema or "models" not in schema:
        return []

    return schema.get("models", [])


def model_to_documentation(model: Dict[str, Any]) -> str:
    """
    Convert a dbt model definition to a documentation string for AI training.

    Args:
        model: Model definition from schema.yml

    Returns:
        Formatted documentation string
    """
    lines = []

    # Model name and description
    name = model.get("name", "unknown")
    description = model.get("description", "").strip()

    lines.append(f"Table: {name}")
    if description:
        lines.append(f"Description: {description}")

    # Column documentation
    columns = model.get("columns", [])
    if columns:
        lines.append("Columns:")
        for col in columns:
            col_name = col.get("name", "unknown")
            col_desc = col.get("description", "").strip()
            if col_desc:
                lines.append(f"  - {col_name}: {col_desc}")
            else:
                lines.append(f"  - {col_name}")

    return "\n".join(lines)


def get_all_documentation(dbt_project_path: Path) -> List[str]:
    """
    Extract all model documentation from a dbt project.

    Args:
        dbt_project_path: Path to dbt project root

    Returns:
        List of documentation strings, one per model
    """
    models_path = dbt_project_path / "models"
    documentation = []

    # Find all schema.yml files
    for schema_file in models_path.glob("**/*.yml"):
        models = parse_schema_file(schema_file)
        for model in models:
            doc = model_to_documentation(model)
            if doc:
                documentation.append(doc)

    return documentation


if __name__ == "__main__":
    # Test the parser
    from config import DBT_PROJECT_DIR

    docs = get_all_documentation(DBT_PROJECT_DIR)
    print(f"Found {len(docs)} model documentation entries:\n")
    for doc in docs:
        print(doc)
        print("-" * 50)
