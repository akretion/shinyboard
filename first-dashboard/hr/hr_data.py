
import polars as pl
import connectorx as cx

connection = "postgresql://odoo:odoodb@127.0.0.1:5432/test"


# employee_id, skill_id, ...
hr_employee_skill = cx.read_sql(conn=connection, query="SELECT * FROM hr_employee_skill", return_type="polars")

# id -> skill_skill_id, ...

hr_skill = cx.read_sql(conn=connection, query="SELECT id, name->>'en_US' AS name, create_date, write_date FROM hr_skill;", return_type="polars")


# to avoid naming conflicts in the join_where clause
hr_skill_renamed = hr_skill.rename({
    "id": "skill_skill_id",
    "create_date": "skill_create_date",
    "write_date" : "skill_write_date" 
})


# employee_id, skill_skill_id, name
hr_employee_named_skill = hr_employee_skill.join_where(
    hr_skill_renamed,
    pl.col("skill_skill_id") == pl.col("id")
).select("employee_id", "name", "skill_id")


# for the option list
skill_series = hr_employee_named_skill.select("name")