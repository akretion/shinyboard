

import polars as pl

hr_data = pl.read_database_uri(uri="postgresql://odoo:odoodb@127.0.0.1:5432/test", query="SELECT * FROM hr_employee_skill")