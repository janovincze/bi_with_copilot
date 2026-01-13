with orders as (
    select * from {{ ref('stg_orders') }}
),

payments as (
    select * from {{ ref('stg_payments') }}
),

order_payments as (
    select
        order_id,
        sum(amount) as total_amount,
        count(*) as payment_count
    from payments
    group by order_id
)

select
    o.order_id,
    o.customer_id,
    o.order_date,
    o.order_status,
    coalesce(op.total_amount, 0) as order_amount,
    coalesce(op.payment_count, 0) as payment_count,
    case
        when o.order_status = 'completed' then true
        else false
    end as is_completed,
    case
        when o.order_status in ('return_pending', 'returned') then true
        else false
    end as is_returned
from orders o
left join order_payments op on o.order_id = op.order_id
