from shiny import ui, render, reactive
from shiny import module, Inputs, Outputs, Session

import sqlglot
from models.GeneratedDataModel import GeneratedDataModel

from connect import Connect


@module.ui
def sql_query_input():
    return ui.page_fluid(
        ui.input_text("query", "Votre requête"), ui.output_ui("query_res_display")
    )


@module.server
def sql_query_server(input: Inputs, output: Outputs, session: Session):
    DB = Connect("dsn1")
    query_res_list: reactive.value[list[GeneratedDataModel]] = reactive.value([])
    ui_res_list: reactive.value[list[ui.Tag]] = reactive.value([])

    @reactive.calc
    def query_res_process():
        return ui_res_list.get()

    @render.ui
    def query_res_display():
        return query_res_process()

    @reactive.effect
    def query_handler():
        if parse_postgres(input.query()):
            if valid_postgres(input.query()):
                query = f"{input.query()}"
                DataFrame = DB.read(input.query())

                query_res_list.set(
                    [
                        *query_res_list.get(),
                        GeneratedDataModel(query, DataFrame, "dataframe"),
                    ]
                )

            else:
                print(
                    "Your statement contains illegal operations (you can't Update, Delete or Create)"
                )
        else:
            print("Your SQL statement is Invalid")


# UTILS
def parse_postgres(q: str):
    """checks if the query is valid postgres"""
    try:
        sqlglot.parse(q)
        return True

    except sqlglot.ParseError as parseError:
        print(f"POSTGRES PARSE ERROR : {parseError}")
        return False

    except Exception as exception:
        print(f"UNEXCPECTED EXCEPTION  : {exception}")
        return False


def valid_postgres(q: str):
    """checks if the query only contains projections (no Create, Update or Delete allowed)"""
    if (
        q.upper().find("UPDATE") < 0
        or q.upper().find("DELETE") < 0
        or q.upper().find("CREATE") < 0
    ):
        return True
    else:
        return False
