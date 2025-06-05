import polars as pl
import matplotlib.pyplot as plt
import connectorx as cx
from models.shared_data_model import Shared_data_model

from hr.hr_data import getHRData

"""
TODO
REFACTOR:
- Faire un fichier local avec les credentials de la DB et l'URL
"""

def getSharedData():
    connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"

    shared_data = Shared_data_model()

    # tables
    shared_data.res_company = cx.read_sql(conn=connection, query="SELECT * FROM res_company", return_type='polars')
    shared_data.res_partner = cx.read_sql(conn=connection, query="SELECT * FROM res_partner", return_type='polars')

    # read-to-use structures
    shared_data.company_id_dict = shared_data.res_company.select("name", "id").to_dict()

    for i in range(len(shared_data.company_id_dict)+1):
        shared_data.company_names.append(shared_data.company_id_dict['name'][i])
        shared_data.company_dict[f"{shared_data.company_id_dict['name'][i]}".replace(" ", "").strip()] = shared_data.company_id_dict['id'][i]

    return shared_data


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
