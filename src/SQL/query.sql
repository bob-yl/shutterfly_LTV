
with visits as (
	select
		customer_id,
		date(DATE_ADD(visit_time, INTERVAL(1-DAYOFWEEK(visit_time)) DAY)) week_id,
        count(*) as visit_count
	from site_visits
    group by
		customer_id,
        date(DATE_ADD(visit_time, INTERVAL(1-DAYOFWEEK(visit_time)) DAY))),
week_count as (
	select 
		datediff(max(week_id), min(week_id))/7 week_count
	from visits),
orders as (
	select
		o1.customer_id,
		date(DATE_ADD(o1.order_time, INTERVAL(1-DAYOFWEEK(o1.order_time)) DAY)) week_id,
        sum(coalesce(o1.amount - o2.amount, o1.amount)) amount
	from orders o1
    left join orders o2
    on o1.order_id = o2.order_id and o1.version-1 = o2.version
    group by
    customer_id,
    date(DATE_ADD(order_time, INTERVAL(1-DAYOFWEEK(order_time)) DAY)))

select
	v.customer_id,
    (sum(amount/visit_count)/max(week_count))*(sum(visit_count)/max(week_count))*52*10 ltv
from visits v
left join orders o
on v.customer_id = o.customer_id and v.week_id = o.week_id
left join week_count w
on 1 = 1
group by v.customer_id
order by ltv desc
limit 1

