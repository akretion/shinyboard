import polars as pl
import connectorx as cx
from models.sales_data_model import sales_data_model

# CX Params


def getSalesData():
    connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"
    #df_type = "polars"

    sales_model = sales_data_model()
    
    # tables
    sales_model.sale_order = cx.read_sql(conn=connection, query="SELECT * FROM sale_order", return_type='polars').rename({"id": "sale_order_id", "user_id": "sale_order_uid"})
    sales_model.res_users = cx.read_sql(conn=connection, query="SELECT * FROM res_users", return_type='polars').rename({"id": "res_users_id", "login": "res_users_login"})
    sales_model.res_partner = cx.read_sql(conn=connection, query="SELECT * FROM res_partner", return_type='polars').rename({"id": "res_partner_id", "user_id": "res_partner_uid", "name": "res_partner_name"})
    sales_model.res_company = cx.read_sql(conn=connection, query="SELECT * FROM res_company", return_type='polars')
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

    # ready-to-use structures (based on dataframes)
    sales_model.company_id_dict = sales_model.res_company.select("name", "id").to_dict()
    print(sales_model.company_id_dict)

    # dates and times
    sales_model.date_df = cx.read_sql(conn=connection, query="SELECT CURRENT_TIMESTAMP(0) + interval '2 hours' AS current_time, DATE_TRUNC('month', CURRENT_TIMESTAMP(0)) AS truncated ", return_type='polars')
    sales_model.relative_dates_df = cx.read_sql(conn=connection, query="SELECT MAX(date_order) + interval '1 days' AS max_do, MIN(date_order) AS min_do FROM sale_order",return_type='polars')
    sales_model.current_date = (sales_model.date_df.select("current_time").to_series().dt.replace_time_zone(None).to_list()[0])

    sales_model.min_date_order = sales_model.relative_dates_df.select("min_do").to_series().to_list()[0]
    sales_model.max_date_order = sales_model.relative_dates_df.select("max_do").to_series().to_list()[0]

    return sales_model
