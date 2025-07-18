from shiny import Inputs
from shiny import Outputs
from shiny import Session
from shiny import ui
from shiny import module

from .sql_query_input import sql_query_input, sql_query_server
from .stored_queries_page import stored_queries_ui, stored_queries_server


@module.ui
def package_ui():
    return ui.nav_panel(
        ui.tooltip(
            ui.h2("Generate Charts"),
            "Generate new charts from SQL queries, and save them for later.",
            placement="bottom",
        ),
        ui.navset_pill(
            ui.nav_panel("Chart Generation", sql_query_input("qi")),
            ui.nav_panel("Stored Queries", stored_queries_ui("sq")),
        ),
    )


@module.server
def package_server(inputs: Inputs, outputs: Outputs, session: Session):
    sql_query_server("qi")
    stored_queries_server("sq")


definitions = {"ui": package_ui, "server": package_server}
