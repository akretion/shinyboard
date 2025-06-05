import polars as pl
import matplotlib.pyplot as plt
import datetime
import json

from hr.hr_data import getHRData

"""
TODO
REFACTOR:
- Faire un fichier local avec les credentials de la DB et l'URL
"""


def save_parquets():
    hr_data = getHRData()
    """
    NAME
        save_parquets
    DESCRIPTION
        creates highly compressed files that are saved of dataframes
    """
    hr_data.hr_employee_skill.write_parquet("./parquets/hr_employee_skill")
    hr_data.hr_skill.write_parquet("./parquets/hr_skill")
    hr_data.hr_employee_named_skill.write_parquet("./parquets/hr_employee_named_skill")


save_parquets()

placeholder_text = "Pas encore implémenté !"
placeholder_plot = plt.bar([2, 4, 6, 8, 10, 12, 14], [10, 11, 12, 13, 14, 16, 18])
