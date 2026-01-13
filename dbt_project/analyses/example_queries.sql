-- Example queries for training the AI model
-- These queries demonstrate common business questions and their SQL solutions

-- Q: Show monthly revenue trends
-- A:
SELECT
    revenue_month,
    total_revenue,
    total_orders,
    average_order_value
FROM revenue_by_month
ORDER BY revenue_month;

-- Q: Who are the top 10 customers by lifetime value?
-- A:
SELECT
    full_name,
    lifetime_value,
    number_of_orders,
    customer_segment
FROM customers
ORDER BY lifetime_value DESC
LIMIT 10;

-- Q: What is the revenue breakdown by payment method?
-- A:
SELECT
    payment_method,
    total_amount,
    transaction_count,
    pct_of_revenue
FROM payment_analysis
ORDER BY total_amount DESC;

-- Q: How many customers are in each segment?
-- A:
SELECT
    customer_segment,
    COUNT(*) as customer_count,
    SUM(lifetime_value) as total_revenue
FROM customers
GROUP BY customer_segment
ORDER BY total_revenue DESC;

-- Q: What is the average order value by month?
-- A:
SELECT
    revenue_month,
    average_order_value,
    total_orders
FROM revenue_by_month
ORDER BY revenue_month;

-- Q: Show customer retention metrics
-- A:
SELECT
    customer_type,
    COUNT(*) as customer_count,
    AVG(number_of_orders) as avg_orders,
    AVG(lifetime_value) as avg_lifetime_value
FROM customers
GROUP BY customer_type
ORDER BY avg_lifetime_value DESC;

-- Q: What is the return rate by customer segment?
-- A:
SELECT
    customer_segment,
    customer_count,
    total_orders,
    total_returns,
    return_rate_pct
FROM revenue_by_customer
ORDER BY return_rate_pct DESC;

-- Q: Compare revenue between high value and low value customers
-- A:
SELECT
    customer_segment,
    SUM(total_revenue) as revenue,
    SUM(customer_count) as customers,
    ROUND(SUM(total_revenue) / SUM(customer_count), 2) as avg_per_customer
FROM revenue_by_customer
WHERE customer_segment IN ('High Value', 'Low Value')
GROUP BY customer_segment;
