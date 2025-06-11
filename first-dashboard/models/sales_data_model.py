import polars as pl
from datetime import datetime

"""
TODO
- Bouger res_partner et res_users vers shared : pas spécifique à sale_data
"""

# CX Params
connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"

epoch = datetime(1970, 1, 1, 0, 0, 0, 0)


class sales_data_model:
    def __init__(self) -> None:
        # primary tables
        self.sale_order: pl.DataFrame = pl.DataFrame()
        self.res_users: pl.DataFrame = pl.DataFrame()
        self.res_partner: pl.DataFrame = pl.DataFrame()
        self.res_company: pl.DataFrame = pl.DataFrame()

        # joins
        self.sales_persons: pl.DataFrame = pl.DataFrame()
        self.salesperson_amount_no_tax: pl.DataFrame = pl.DataFrame()

        # structured data from dataframes
        self.company_id_dict: dict = dict()

        # dates
        self.date_df: pl.DataFrame = pl.DataFrame()
        self.relative_dates_df: pl.DataFrame = pl.DataFrame()

        # dates and times
        self.current_date: datetime = epoch
        self.min_date_order: datetime = epoch
        self.max_date_order: datetime = epoch
