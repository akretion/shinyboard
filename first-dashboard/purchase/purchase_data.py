
import connectorx as cx
import polars as pl
from datetime import datetime as dt
from models.purchase_data_model import Purchase_data_model

def getPurchaseData():
    connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"

    purchase_data = Purchase_data_model()

    purchase_data.purchase_order = cx.read_sql(conn=connection, query = "SELECT * FROM purchase_order", return_type='polars')
    purchase_data.suppliers = cx.read_sql(conn=connection, query = "SELECT res_partner.name, res_partner.email, res_partner.website, purchase_order.write_date, purchase_order.company_id FROM res_partner JOIN purchase_order ON purchase_order.partner_id = res_partner.id", return_type='polars')

    return purchase_data