"""
Flask-based web application for Copilot Analytics.
Simple API endpoint for text-to-SQL queries.

Prerequisites:
1. Run 'dbt build' to create the database
2. Start copilot-api: npx copilot-api@latest start --rate-limit 10
3. Run this script: python app_flask.py

Access the app at: http://localhost:8084
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, request, jsonify, render_template_string
from copilot_vanna import CopilotAnalytics
from train_vanna import TRAINING_EXAMPLES
from config import DATABASE_PATH

app = Flask(__name__)

# Global analytics instance
analytics = None


def get_analytics():
    """Get or create the analytics instance."""
    global analytics
    if analytics is None:
        analytics = CopilotAnalytics()
        analytics.connect()
        for question, sql in TRAINING_EXAMPLES:
            analytics.add_training_example(question, sql)
    return analytics


# Simple HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Copilot Analytics</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 900px; margin: 0 auto; padding: 20px; }
        h1 { color: #333; }
        .input-group { margin: 20px 0; }
        input[type="text"] { width: 70%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; }
        button { padding: 10px 20px; font-size: 16px; background: #0066cc; color: white; border: none; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0052a3; }
        .result { margin-top: 20px; padding: 15px; background: #f5f5f5; border-radius: 4px; }
        .sql { background: #2d2d2d; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }
        .error { background: #fee; color: #c00; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background: #f0f0f0; }
        .examples { margin-top: 30px; }
        .examples button { margin: 5px; background: #666; font-size: 14px; }
        .examples button:hover { background: #444; }
    </style>
</head>
<body>
    <h1>📊 Copilot Analytics</h1>
    <p>Ask questions about your data in plain English</p>

    <div class="input-group">
        <input type="text" id="question" placeholder="e.g., Show me monthly revenue trends" onkeypress="if(event.key==='Enter')askQuestion()">
        <button onclick="askQuestion()">Ask</button>
    </div>

    <div class="examples">
        <strong>Try these:</strong><br>
        <button onclick="setQuestion('Show monthly revenue trends')">Monthly revenue</button>
        <button onclick="setQuestion('Top 10 customers by lifetime value')">Top customers</button>
        <button onclick="setQuestion('Revenue by payment method')">Payment methods</button>
        <button onclick="setQuestion('How many customers in each segment?')">Customer segments</button>
    </div>

    <div id="result"></div>

    <script>
        function setQuestion(q) {
            document.getElementById('question').value = q;
            askQuestion();
        }

        async function askQuestion() {
            const question = document.getElementById('question').value;
            if (!question) return;

            document.getElementById('result').innerHTML = '<div class="result">Thinking...</div>';

            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question})
                });
                const data = await response.json();

                if (data.error) {
                    document.getElementById('result').innerHTML =
                        '<div class="result error"><strong>Error:</strong> ' + data.error + '</div>';
                } else {
                    let html = '<div class="result">';
                    html += '<h3>SQL Query:</h3><pre class="sql">' + data.sql + '</pre>';

                    if (data.data && data.data.length > 0) {
                        html += '<h3>Results:</h3><table><tr>';
                        const cols = Object.keys(data.data[0]);
                        cols.forEach(col => html += '<th>' + col + '</th>');
                        html += '</tr>';
                        data.data.forEach(row => {
                            html += '<tr>';
                            cols.forEach(col => html += '<td>' + row[col] + '</td>');
                            html += '</tr>';
                        });
                        html += '</table>';
                    }
                    html += '</div>';
                    document.getElementById('result').innerHTML = html;
                }
            } catch (e) {
                document.getElementById('result').innerHTML =
                    '<div class="result error"><strong>Error:</strong> ' + e.message + '</div>';
            }
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Serve the main page."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/ask', methods=['POST'])
def ask():
    """Handle question and return SQL + results."""
    try:
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({'error': 'No question provided'})

        analytics = get_analytics()

        # Generate SQL
        sql = analytics.generate_sql(question)

        # Execute query
        df = analytics.run_sql(sql)

        # Convert to JSON-friendly format
        result = df.to_dict(orient='records')

        return jsonify({
            'question': question,
            'sql': sql,
            'data': result
        })

    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/schema')
def schema():
    """Return the database schema."""
    try:
        analytics = get_analytics()
        return jsonify({'schema': analytics.get_schema()})
    except Exception as e:
        return jsonify({'error': str(e)})


def main():
    """Start the Flask application."""
    print("=" * 60)
    print("Copilot Analytics - Flask Dashboard")
    print("=" * 60)

    # Check prerequisites
    if not DATABASE_PATH.exists():
        print(f"\nError: Database not found at {DATABASE_PATH}")
        print("Please run 'dbt build' first.")
        sys.exit(1)

    print("\nMake sure copilot-api is running:")
    print("  npx copilot-api@latest start --rate-limit 10")
    print()
    print("=" * 60)
    print("Starting Flask server...")
    print("Open http://localhost:8084 in your browser")
    print("=" * 60 + "\n")

    # Initialize analytics on startup
    get_analytics()

    # Run the app
    app.run(host="0.0.0.0", port=8084, debug=False)


if __name__ == "__main__":
    main()
