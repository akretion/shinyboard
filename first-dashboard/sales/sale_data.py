
import polars as pl
import connectorx as cx

# CX Params
connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"
df_type = "polars"

# primary tables
sale_order = cx.read_sql(conn=connection, query="SELECT * FROM sale_order", return_type=df_type)
res_users = cx.read_sql(conn=connection, query="SELECT * FROM res_users", return_type=df_type)
res_partner = cx.read_sql(conn=connection, query="SELECT * FROM res_partner", return_type=df_type)

# time related data
date_df = cx.read_sql(conn=connection, query="SELECT CURRENT_TIMESTAMP(0) + interval '2 hours' AS current_time, DATE_TRUNC('month', CURRENT_TIMESTAMP(0)) AS truncated ", return_type=df_type)
relative_dates_df = cx.read_sql(conn=connection, query="SELECT MAX(date_order) + interval '1 days' AS max_do, MIN(date_order) AS min_do FROM sale_order", return_type=df_type)

# conversions to datetimes instead of Series
current_date = date_df.select('current_time').to_series().dt.replace_time_zone(None).to_list()[0]
truncated = date_df.select('truncated').to_series().dt.replace_time_zone(None).to_list()[0]

max_date_order = relative_dates_df.select("max_do").to_series().to_list()[0]
min_date_order = relative_dates_df.select("min_do").to_series().to_list()[0]


# the odoo db has no tz by default

sale_order = sale_order.rename({
    "id" : "sale_order_id",
    "user_id" : "sale_order_uid"
})

res_users = res_users.rename({
    "id" : "res_users_id",
    "login" : "res_users_login"
})

res_partner = res_partner.rename({
    "id" : "res_partner_id",
    "user_id" : "res_partner_uid",
    "name" : "res_partner_name"
})


sales_persons = sale_order.filter(

).join_where(
    res_users,
    pl.col('sale_order_uid').eq(pl.col('res_users_id')),

    suffix="_sale_order"
).join_where(
    res_partner,
    pl.col('res_users_id').eq(pl.col('res_partner_uid')),

    suffix="_res_partner"
).select('sale_order_id', 'sale_order_uid', 'res_users_login', 'res_partner_name')


salesperson_amount_no_tax = sale_order.join_where(
    res_partner,
    pl.col('sale_order_uid').eq(pl.col('res_partner_uid')),

    suffix="_res_partner"
).select("res_partner_name", "amount_untaxed").group_by(pl.col('res_partner_name')).sum().sort(descending=True, by="amount_untaxed")

