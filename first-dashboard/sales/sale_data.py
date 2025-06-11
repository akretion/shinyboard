import polars as pl
from models.sales_data_model import sales_data_model
from connect import Connect

"""TODO
- Mettre 'db' dans un singleton, ou faire un Design en Factory pour empêcher lles répétition de
db = Connect("dsn")
"""

# CX Params


def getSalesData():
    # df_type = "polars"

    db = Connect("dsn1")

    sales_model = sales_data_model()

    # primary tables
    sales_model.sale_order = db.read("SELECT * FROM sale_order").rename(
        {"user_id": "sale_order_uid"}
    )

    sales_model.res_users = db.read("SELECT * FROM res_users")

    sales_model.res_partner = db.read("SELECT * FROM res_partner").rename(
        {"user_id": "res_partner_uid", "name": "res_partner_name"}
    )

    # joins
    sales_model.salesperson_amount_no_tax = (
        sales_model.sale_order.join_where(
            sales_model.res_partner,
            pl.col("sale_order_uid").eq(pl.col("res_partner_uid")),
            suffix="_res_partner",
        )
        .select("res_partner_name", "amount_untaxed")
        .group_by(pl.col("res_partner_name"))
        .sum()
        .sort(descending=True, by="amount_untaxed")
    )

    # dates and times
    sales_model.date_df = db.read(
        "SELECT CURRENT_TIMESTAMP(0) + interval '2 hours' AS current_time, DATE_TRUNC('month', CURRENT_TIMESTAMP(0)) AS truncated "
    )
    sales_model.relative_dates_df = db.read(
        "SELECT MAX(date_order) + interval '1 days' AS max_do, MIN(date_order) AS min_do FROM sale_order"
    )
    sales_model.current_date = (
        sales_model.date_df.select("current_time")
        .to_series()
        .dt.replace_time_zone(None)
        .to_list()[0]
    )

    sales_model.min_date_order = (
        sales_model.relative_dates_df.select("min_do").to_series().to_list()[0]
    )
    sales_model.max_date_order = (
        sales_model.relative_dates_df.select("max_do").to_series().to_list()[0]
    )

    return sales_model
