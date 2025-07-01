from shiny import reactive

import polars as pl

from connect import Connect
from peewee import PostgresqlDatabase


# ORM DATABASE
QUERY_DB = PostgresqlDatabase("query_db", user="cosmos")

# CREDENTIALS
CURRENT_USER_ID = reactive.value(-1)
CURRENT_USER_NAME = reactive.value("")


# USER UTILS
def available_tables(uid: int, connection: Connect):
    available_tables_df = connection.read(
        f"""
        SELECT ir_model.model AS table_name
        FROM ir_model
        JOIN ir_model_access
        ON ir_model.id = ir_model_access.model_id
        JOIN res_groups_users_rel
        ON ir_model_access.group_id = res_groups_users_rel.gid
        JOIN res_users
        ON res_users.id = res_groups_users_rel.uid
        WHERE ir_model.transient = FALSE 
        AND res_users.id = {uid}
        AND ir_model.model !~ '.show$'
        """
    )

    # assignation des schémas dans shared
    available_tables_df.select("table_name").to_series().to_list()
    table_name_schema_dict = {}

    print(table_name_schema_dict)


# DATAFRAME DATA

SELECTED_DATAFRAME_NAME: reactive.value[str] = reactive.value("")

AVAILABLE_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()

# DATAFRAME BASED DATA

COMPANY_TO_ID_DICT: reactive.value[dict]
