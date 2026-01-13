"""
Training script for the Copilot Analytics engine.
Adds example question-SQL pairs for better few-shot learning.

This script should be run after dbt build to populate the database.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from copilot_vanna import CopilotAnalytics
from config import DBT_PROJECT_DIR, DATABASE_PATH


# Example question-SQL pairs for few-shot learning
# These help the LLM understand the schema and generate better queries
TRAINING_EXAMPLES = [
    # ===========================================
    # Basic queries
    # ===========================================
    (
        "Show monthly revenue",
        "SELECT revenue_month, total_revenue, total_orders FROM revenue_by_month ORDER BY revenue_month"
    ),
    (
        "What is the total revenue by month?",
        "SELECT revenue_month, ROUND(total_revenue, 2) as revenue FROM revenue_by_month ORDER BY revenue_month"
    ),
    (
        "Who are the top 10 customers by lifetime value?",
        "SELECT full_name, ROUND(lifetime_value, 2) as lifetime_value, number_of_orders, customer_segment FROM customers ORDER BY lifetime_value DESC LIMIT 10"
    ),
    (
        "How many customers do we have?",
        "SELECT COUNT(*) as customer_count FROM customers"
    ),
    (
        "Show customers by segment",
        "SELECT customer_segment, COUNT(*) as count, ROUND(SUM(lifetime_value), 2) as total_value FROM customers GROUP BY customer_segment ORDER BY total_value DESC"
    ),
    (
        "What is the revenue breakdown by payment method?",
        "SELECT payment_method, ROUND(total_amount, 2) as total, ROUND(pct_of_revenue, 1) as percent FROM payment_analysis ORDER BY total DESC"
    ),
    (
        "How many orders do we have?",
        "SELECT COUNT(*) as order_count FROM orders"
    ),
    (
        "What is the average order value?",
        "SELECT ROUND(AVG(order_amount), 2) as avg_order_value FROM orders"
    ),

    # ===========================================
    # Advanced queries with Window Functions
    # ===========================================

    # Running total / Cumulative sum
    (
        "Show cumulative revenue over time",
        """WITH monthly AS (
    SELECT revenue_month, total_revenue
    FROM revenue_by_month
)
SELECT
    revenue_month,
    ROUND(total_revenue, 2) as monthly_revenue,
    ROUND(SUM(total_revenue) OVER (ORDER BY revenue_month), 2) as cumulative_revenue
FROM monthly
ORDER BY revenue_month"""
    ),

    # Month-over-month growth rate
    (
        "Calculate month over month revenue growth rate",
        """WITH monthly AS (
    SELECT
        revenue_month,
        total_revenue,
        LAG(total_revenue) OVER (ORDER BY revenue_month) as prev_month_revenue
    FROM revenue_by_month
)
SELECT
    revenue_month,
    ROUND(total_revenue, 2) as revenue,
    ROUND(prev_month_revenue, 2) as prev_month,
    CASE
        WHEN prev_month_revenue > 0
        THEN ROUND(100.0 * (total_revenue - prev_month_revenue) / prev_month_revenue, 1)
        ELSE NULL
    END as growth_rate_pct
FROM monthly
ORDER BY revenue_month"""
    ),

    # Customer ranking with percentiles
    (
        "Rank customers by lifetime value with percentile",
        """SELECT
    full_name,
    ROUND(lifetime_value, 2) as lifetime_value,
    customer_segment,
    ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) as rank,
    ROUND(PERCENT_RANK() OVER (ORDER BY lifetime_value) * 100, 1) as percentile
FROM customers
WHERE lifetime_value > 0
ORDER BY lifetime_value DESC
LIMIT 20"""
    ),

    # Moving average
    (
        "Show 3-month moving average of revenue",
        """SELECT
    revenue_month,
    ROUND(total_revenue, 2) as monthly_revenue,
    ROUND(AVG(total_revenue) OVER (
        ORDER BY revenue_month
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) as moving_avg_3m
FROM revenue_by_month
ORDER BY revenue_month"""
    ),

    # Customer cohort analysis by first order month
    (
        "Show customer cohort analysis by first order month",
        """WITH customer_cohorts AS (
    SELECT
        strftime(first_order_date, '%Y-%m') as cohort_month,
        customer_id,
        lifetime_value,
        number_of_orders
    FROM customers
    WHERE first_order_date IS NOT NULL
)
SELECT
    cohort_month,
    COUNT(*) as customers_acquired,
    ROUND(AVG(lifetime_value), 2) as avg_lifetime_value,
    ROUND(AVG(number_of_orders), 1) as avg_orders,
    ROUND(SUM(lifetime_value), 2) as total_cohort_revenue
FROM customer_cohorts
GROUP BY cohort_month
ORDER BY cohort_month"""
    ),

    # Revenue contribution by top customers (Pareto analysis)
    (
        "What percentage of revenue comes from top 20% of customers",
        """WITH ranked_customers AS (
    SELECT
        customer_id,
        full_name,
        lifetime_value,
        SUM(lifetime_value) OVER () as total_revenue,
        ROW_NUMBER() OVER (ORDER BY lifetime_value DESC) as rank,
        COUNT(*) OVER () as total_customers
    FROM customers
    WHERE lifetime_value > 0
),
top_20_pct AS (
    SELECT *
    FROM ranked_customers
    WHERE rank <= total_customers * 0.2
)
SELECT
    COUNT(*) as top_20_pct_customers,
    (SELECT COUNT(*) FROM ranked_customers) as total_customers,
    ROUND(SUM(lifetime_value), 2) as top_20_revenue,
    ROUND((SELECT SUM(lifetime_value) FROM ranked_customers), 2) as total_revenue,
    ROUND(100.0 * SUM(lifetime_value) / (SELECT SUM(lifetime_value) FROM ranked_customers), 1) as revenue_pct
FROM top_20_pct"""
    ),

    # Order frequency distribution
    (
        "Show distribution of customers by number of orders",
        """WITH order_buckets AS (
    SELECT
        customer_id,
        number_of_orders,
        CASE
            WHEN number_of_orders = 0 THEN '0 orders'
            WHEN number_of_orders = 1 THEN '1 order'
            WHEN number_of_orders BETWEEN 2 AND 3 THEN '2-3 orders'
            WHEN number_of_orders BETWEEN 4 AND 5 THEN '4-5 orders'
            ELSE '6+ orders'
        END as order_bucket
    FROM customers
)
SELECT
    order_bucket,
    COUNT(*) as customer_count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) as percentage
FROM order_buckets
GROUP BY order_bucket
ORDER BY
    CASE order_bucket
        WHEN '0 orders' THEN 1
        WHEN '1 order' THEN 2
        WHEN '2-3 orders' THEN 3
        WHEN '4-5 orders' THEN 4
        ELSE 5
    END"""
    ),

    # Payment method trends over time
    (
        "Show payment method usage trend by month",
        """WITH monthly_payments AS (
    SELECT
        strftime(o.order_date, '%Y-%m') as order_month,
        p.payment_method,
        SUM(p.amount) as total_amount
    FROM stg_payments p
    JOIN stg_orders o ON p.order_id = o.order_id
    GROUP BY 1, 2
)
SELECT
    order_month,
    payment_method,
    ROUND(total_amount, 2) as amount,
    ROUND(100.0 * total_amount / SUM(total_amount) OVER (PARTITION BY order_month), 1) as pct_of_month
FROM monthly_payments
ORDER BY order_month, total_amount DESC"""
    ),

    # Customer lifetime value percentile bands
    (
        "Segment customers into LTV percentile bands",
        """WITH customer_percentiles AS (
    SELECT
        customer_id,
        full_name,
        lifetime_value,
        NTILE(4) OVER (ORDER BY lifetime_value) as quartile
    FROM customers
    WHERE lifetime_value > 0
)
SELECT
    CASE quartile
        WHEN 1 THEN 'Bottom 25%'
        WHEN 2 THEN '25-50%'
        WHEN 3 THEN '50-75%'
        WHEN 4 THEN 'Top 25%'
    END as ltv_band,
    COUNT(*) as customers,
    ROUND(MIN(lifetime_value), 2) as min_ltv,
    ROUND(MAX(lifetime_value), 2) as max_ltv,
    ROUND(AVG(lifetime_value), 2) as avg_ltv,
    ROUND(SUM(lifetime_value), 2) as total_ltv
FROM customer_percentiles
GROUP BY quartile
ORDER BY quartile DESC"""
    ),

    # Revenue velocity - days between orders
    (
        "Analyze average days between customer orders",
        """WITH order_gaps AS (
    SELECT
        customer_id,
        order_date,
        LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as prev_order_date,
        order_date - LAG(order_date) OVER (PARTITION BY customer_id ORDER BY order_date) as days_between
    FROM orders
),
customer_velocity AS (
    SELECT
        customer_id,
        AVG(days_between) as avg_days_between_orders,
        COUNT(*) as repeat_purchases
    FROM order_gaps
    WHERE days_between IS NOT NULL
    GROUP BY customer_id
)
SELECT
    CASE
        WHEN avg_days_between_orders <= 30 THEN 'High frequency (<=30 days)'
        WHEN avg_days_between_orders <= 60 THEN 'Medium frequency (31-60 days)'
        ELSE 'Low frequency (>60 days)'
    END as purchase_frequency,
    COUNT(*) as customer_count,
    ROUND(AVG(avg_days_between_orders), 1) as avg_days_between,
    SUM(repeat_purchases) as total_repeat_purchases
FROM customer_velocity
GROUP BY 1
ORDER BY avg_days_between"""
    ),
]


def train_analytics(analytics: CopilotAnalytics) -> None:
    """
    Add training examples to the analytics engine.

    Args:
        analytics: CopilotAnalytics instance to train
    """
    print("Adding training examples...")

    for question, sql in TRAINING_EXAMPLES:
        analytics.add_training_example(question, sql)
        print(f"  Added: {question[:50]}...")

    print(f"\nAdded {len(TRAINING_EXAMPLES)} training examples")


def test_analytics(analytics: CopilotAnalytics) -> None:
    """
    Test the analytics engine with a few queries (requires LLM connection).

    Args:
        analytics: CopilotAnalytics instance to test
    """
    print("\nTesting database connection...")

    # Test direct SQL execution
    df = analytics.run_sql("SELECT COUNT(*) as count FROM customers")
    print(f"  Customer count: {df['count'].iloc[0]}")

    df = analytics.run_sql("SELECT COUNT(*) as count FROM orders")
    print(f"  Order count: {df['count'].iloc[0]}")

    print("\nDatabase connection OK!")


def main():
    """Main entry point for training script."""
    print("=" * 60)
    print("Copilot Analytics - Setup Script")
    print("=" * 60)

    # Check if database exists
    if not DATABASE_PATH.exists():
        print(f"\nError: Database not found at {DATABASE_PATH}")
        print("Please run 'dbt build' first to create the database.")
        sys.exit(1)

    print(f"\nDatabase: {DATABASE_PATH}")
    print(f"dbt Project: {DBT_PROJECT_DIR}")

    # Create analytics instance
    analytics = CopilotAnalytics()
    analytics.connect()

    # Add training examples
    train_analytics(analytics)

    # Test the connection
    test_analytics(analytics)

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start copilot-api: npx copilot-api@latest start --rate-limit 10")
    print("2. Run the app: streamlit run app_streamlit.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
