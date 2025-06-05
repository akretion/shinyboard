import polars as pl
import connectorx as cx

from models.hr_data_model import hr_data_model

connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"


def getHRData():
    
    hr_model = hr_data_model()

    # employee_id, skill_id, ...
    hr_model.hr_employee_skill = cx.read_sql(
        conn=connection, 
        query="SELECT * FROM hr_employee_skill", 
        return_type="polars"
    )

    # id -> skill_skill_id, ...
    hr_model.hr_skill = cx.read_sql(
        conn=connection, 
        query="SELECT id, name->>'en_US' AS name, create_date, write_date FROM hr_skill;",
        return_type="polars"
    ).rename({
            "id": "skill_skill_id",
            "create_date": "skill_create_date",
            "write_date": "skill_write_date",
        })

    hr_model.hr_employee_named_skill = hr_model.hr_employee_skill.join_where(
        hr_model.hr_skill, 
        pl.col("skill_skill_id") == pl.col("id")
    ).select("employee_id", "name", "skill_id")

    hr_model.skill_series = hr_model.hr_employee_named_skill.select("name")

    return hr_model





