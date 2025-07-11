"""
File that contains states and informations that
should be shared across files.
"""

from __future__ import annotations

from datetime import datetime

import polars as pl
import sqlglot.expressions
from pages.connect import Connect
from peewee import SqliteDatabase
from shiny import reactive


# CONSTANTS
EPOCH = datetime(1970, 1, 1, 0, 0, 0)

# ORM DATABASE
DB_CONF = SqliteDatabase("odoo_shiny.db")

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
        """,
    )

    # assignation des schémas dans shared
    available_tables_df.select("table_name").to_series().to_list()
    table_name_schema_dict = {}

    print(table_name_schema_dict)


# DATAFRAME DATA

AVAILABLE_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
# tables available to the user.

SELECTED_DATAFRAME_NAME: reactive.value[str] = reactive.value("")
# Holds the canonical, in DB name of the currently selected table.

FRENCH_NAME: reactive.value[str] = reactive.value("")
# Holds the french name of the currently selected table.

MIN_DB_TIME: reactive.value[datetime] = reactive.value(EPOCH)
# Minimum time found in database.

MAX_DB_TIME: reactive.value[datetime] = reactive.value(EPOCH)
# Maximum time found in database.

OTHER_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
# tables available for internal use.

TABLE_TIME_COLUMNS: reactive.value[dict[str, str]] = reactive.value()
# Associates table names to their respective columns that should be used for time calculations.


# GLOBAL USER FILTERS

SELECTED_PERIOD_HIGH_BOUND: reactive.value[datetime] = reactive.value(EPOCH)
# The rightmost value of the date_range.

SELECTED_PERIOD_LOW_BOUND: reactive.value[datetime] = reactive.value(EPOCH)
# The leftmost value of the data_range.

SELECTED_COMPANY_NAMES: reactive.value[list[str]] = reactive.value([""])
# The selected value of the company selection dropdown


# UTILS
def parse_postgres(q: str):
    """checks if the query is valid postgres."""
    try:
        expr = sqlglot.parse_one(q, read="postgres")

        # cases not detected by sqlglot
        if isinstance(expr, sqlglot.expressions.Select) and not expr.expressions:
            raise sqlglot.ParseError(
                "Incomplete SELECT statement, no column specified",
            )

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
