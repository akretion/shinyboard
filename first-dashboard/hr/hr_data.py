import polars as pl
import connectorx as cx

from models.hr_data_model import Hr_data_model
from connect import Connect

"""TODO
- Mettre 'db' dans un singleton, ou faire un Design en Factory pour empêcher lles répétition de
db = Connect("dsn")
"""

def getHRData():

    db = Connect("dsn1")

    print("MY.READ: \n")
    print(db.read("SELECT name FROM hr_skill"))
    
    hr_model = Hr_data_model()

    # employee_id, skill_id, ...
    hr_model.hr_employee_skill = db.read("SELECT * FROM hr_employee_skill")

    # id -> skill_skill_id, ...
    hr_model.hr_skill = (
        db
        .read("SELECT id, name->>'en_US' AS name, create_date, write_date FROM hr_skill;")
        .rename({
            "id": "skill_skill_id",
            "create_date": "skill_create_date",
            "write_date": "skill_write_date",
        })
        )

    hr_model.hr_employee_named_skill = hr_model.hr_employee_skill.join_where(
        hr_model.hr_skill, 
        pl.col("skill_skill_id") == pl.col("id")
    ).select("employee_id", "name", "skill_id")

    hr_model.skill_series = hr_model.hr_employee_named_skill.select("name")

    return hr_model





