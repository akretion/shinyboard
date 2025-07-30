"""
File that contains states and informations that
should be shared across files.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from dataclasses import dataclass
import polars as pl
import sqlglot.expressions
from connect import Connect
from peewee import SqliteDatabase
from shiny import reactive


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


# APP DATA
@dataclass
class Styles:
    instance = None

    @staticmethod
    def get_instance():
        if not Styles.instance:
            Styles.instance = Styles()
        return Styles.instance

    def __init__(self):
        self.styles_dir_path = Path("styles/")


# DATAFRAME DATA


@dataclass
class Config:
    instance = None

    @staticmethod
    def get_instance():
        if not Config.instance:
            Config.instance = Config()
        return Config.instance

    def __init__(self):
        self.DB_CONF = SqliteDatabase("odoo_shiny.db")


@dataclass
class Constants:

    instance = None

    @staticmethod
    def get_instance():
        if not Constants.instance:
            Constants.instance = Constants()
        return Constants.instance

    def __init__(self):

        # CONSTANTS
        self.EPOCH = datetime(1970, 1, 1, 0, 0, 0)

        # CREDENTIALS
        self.CURRENT_USER_ID = reactive.value(-1)
        self.CURRENT_USER_NAME = reactive.value("")

        self.AVAILABLE_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
        # tables available to the user.

        self.SELECTED_DATAFRAME_NAME: reactive.value[str] = reactive.value("")
        # Holds the canonical, in DB name of the currently selected table.

        self.FRENCH_NAME: reactive.value[str] = reactive.value("")
        # Holds the french name of the currently selected table.

        self.MIN_DB_TIME: reactive.value[datetime] = reactive.value(self.EPOCH)
        # Minimum time found in database.

        self.MAX_DB_TIME: reactive.value[datetime] = reactive.value(self.EPOCH)
        # Maximum time found in database.

        self.OTHER_RELS: reactive.value[dict[str, pl.DataFrame]] = reactive.value()
        # tables available for internal use.

        self.TABLE_TIME_COLUMNS: reactive.value[dict[str, str]] = reactive.value()
        # Associates table names to their respective columns that should be used for time calculations.

        # GLOBAL USER FILTERS

        self.SELECTED_PERIOD_HIGH_BOUND: reactive.value[datetime] = reactive.value(
            self.EPOCH
        )
        # The rightmost value of the date_range.

        self.SELECTED_PERIOD_LOW_BOUND: reactive.value[datetime] = reactive.value(
            self.EPOCH
        )
        # The leftmost value of the data_range.

        self.SELECTED_COMPANY_NAMES: reactive.value[list[str]] = reactive.value([""])
        # The selected value of the company selection dropdown


APP_CONSTANTS = Constants.get_instance()
APP_CONFIG = Config.get_instance()


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
