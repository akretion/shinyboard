

import polars as pl
import matplotlib.pyplot as plt


hr_employee_skill = pl.read_database_uri(uri="postgresql://odoo:odoodb@127.0.0.1:5432/test", query="SELECT * FROM hr_employee_skill")
hr_skill = pl.read_database_uri(uri="postgresql://odoo:odoodb@127.0.0.1:5432/test", query="SELECT * FROM hr_skill")

print(hr_skill)

placeholder_text = "Pas encore implémenté !"
placeholder_plot = plt.bar([2, 4, 6, 8, 10, 12, 14], [10, 11, 12, 13, 14, 16, 18])