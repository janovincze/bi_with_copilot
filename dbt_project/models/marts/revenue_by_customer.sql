with customers as (
    select * from {{ ref('customers') }}
)

select
    customer_segment,
    customer_type,
    count(*) as customer_count,
    sum(lifetime_value) as total_revenue,
    round(avg(lifetime_value), 2) as average_lifetime_value,
    sum(number_of_orders) as total_orders,
    round(avg(number_of_orders), 2) as average_orders_per_customer,
    sum(return_count) as total_returns,
    round(100.0 * sum(return_count) / nullif(sum(number_of_orders), 0), 2) as return_rate_pct
from customers
group by customer_segment, customer_type
order by total_revenue desc
