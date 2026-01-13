with orders as (
    select * from {{ ref('orders') }}
),

monthly_revenue as (
    select
        strftime(order_date, '%Y-%m') as revenue_month,
        strftime(order_date, '%Y') as revenue_year,
        strftime(order_date, '%m') as month_number,
        count(distinct order_id) as total_orders,
        count(distinct customer_id) as unique_customers,
        sum(order_amount) as total_revenue,
        sum(case when is_completed then order_amount else 0 end) as completed_revenue,
        sum(case when is_returned then order_amount else 0 end) as returned_revenue,
        avg(order_amount) as average_order_value
    from orders
    group by 1, 2, 3
)

select
    revenue_month,
    revenue_year,
    month_number,
    total_orders,
    unique_customers,
    round(total_revenue, 2) as total_revenue,
    round(completed_revenue, 2) as completed_revenue,
    round(returned_revenue, 2) as returned_revenue,
    round(average_order_value, 2) as average_order_value,
    round(total_revenue / nullif(unique_customers, 0), 2) as revenue_per_customer
from monthly_revenue
order by revenue_month
