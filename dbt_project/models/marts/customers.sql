with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('orders') }}
),

customer_orders as (
    select
        customer_id,
        min(order_date) as first_order_date,
        max(order_date) as most_recent_order_date,
        count(order_id) as number_of_orders,
        sum(order_amount) as lifetime_value,
        sum(case when is_completed then order_amount else 0 end) as completed_order_value,
        sum(case when is_returned then 1 else 0 end) as return_count
    from orders
    group by customer_id
)

select
    c.customer_id,
    c.first_name,
    c.last_name,
    c.full_name,
    co.first_order_date,
    co.most_recent_order_date,
    coalesce(co.number_of_orders, 0) as number_of_orders,
    coalesce(co.lifetime_value, 0) as lifetime_value,
    coalesce(co.completed_order_value, 0) as completed_order_value,
    coalesce(co.return_count, 0) as return_count,
    case
        when co.lifetime_value > 100 then 'High Value'
        when co.lifetime_value > 50 then 'Medium Value'
        when co.lifetime_value > 0 then 'Low Value'
        else 'No Orders'
    end as customer_segment,
    case
        when co.number_of_orders > 3 then 'Frequent'
        when co.number_of_orders > 1 then 'Repeat'
        when co.number_of_orders = 1 then 'New'
        else 'Prospect'
    end as customer_type
from customers c
left join customer_orders co on c.customer_id = co.customer_id
