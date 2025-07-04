from shiny import reactive

import polars as pl
import sqlglot.expressions
from datetime import datetime

from connect import Connect
from peewee import PostgresqlDatabase


# CONSTANTS
EPOCH = datetime(1970, 1, 1, 0, 0, 0)

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

AVAILABLE_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
"""Available to the user"""

SELECTED_DATAFRAME_NAME: reactive.value[str] = reactive.value("")
FRENCH_NAME: reactive.value[str] = reactive.value("")

MIN_DB_TIME: reactive.value[datetime] = reactive.value(EPOCH)
MAX_DB_TIME: reactive.value[datetime] = reactive.value(EPOCH)

OTHER_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
"""Available for internal use"""

# DATAFRAME RELATED DATA

COMPANY_TO_ID_DICT: reactive.value[dict]


# GLOBAL USER FILTERS

SELECTED_PERIOD_HIGH_BOUND: reactive.value[datetime] = reactive.value(EPOCH)
SELECTED_PERIOD_LOW_BOUND: reactive.value[datetime] = reactive.value(EPOCH)


# UTILS
def parse_postgres(q: str):
    """checks if the query is valid postgres"""
    try:
        expr = sqlglot.parse_one(q, read="postgres")

        # cases not detected by sqlglot
        if isinstance(expr, sqlglot.expressions.Select) and not expr.expressions:
            raise sqlglot.ParseError("Incomplete SELECT statement, no column specified")

        return True

    except sqlglot.ParseError as parse_error:
        print(parse_error)
        return False

    except Exception as error:
        print(error)
        return False


def valid_postgres(q: str):
    """checks if the query only contains projections (no Create, Update or Delete allowed)"""
    if (
        q.upper().find("UPDATE") < 0
        or q.upper().find("DELETE") < 0
        or q.upper().find("CREATE") < 0
        or q.upper().find("DROP") < 0
    ):
        return True
    else:
        return False
