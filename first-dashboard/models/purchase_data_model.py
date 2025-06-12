import polars as pl


class Purchase_data_model:
    def __init__(self):
        self.purchase_order: pl.DataFrame = pl.DataFrame()
        self.suppliers: pl.DataFrame = pl.DataFrame()
