with payments as (
    select * from {{ ref('stg_payments') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

payment_details as (
    select
        p.payment_id,
        p.order_id,
        p.payment_method,
        p.amount,
        o.order_date,
        strftime(o.order_date, '%Y-%m') as payment_month
    from payments p
    left join orders o on p.order_id = o.order_id
)

select
    payment_method,
    count(*) as transaction_count,
    count(distinct order_id) as order_count,
    round(sum(amount), 2) as total_amount,
    round(avg(amount), 2) as average_amount,
    round(min(amount), 2) as min_amount,
    round(max(amount), 2) as max_amount,
    round(100.0 * count(*) / sum(count(*)) over (), 2) as pct_of_transactions,
    round(100.0 * sum(amount) / sum(sum(amount)) over (), 2) as pct_of_revenue
from payment_details
group by payment_method
order by total_amount desc
