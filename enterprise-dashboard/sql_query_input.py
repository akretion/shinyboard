from shiny import ui, render, reactive
from shiny import module, Inputs, Outputs, Session

import sqlglot
import sqlglot.expressions

from connect import Connect


@module.ui
def sql_query_input():
    return ui.page_fluid(
        ui.input_text("query", "Votre requête"),
        ui.input_action_button("exec", "lancer"),
        ui.output_ui("query_res_display"),
    )


@module.server
def sql_query_server(input: Inputs, output: Outputs, session: Session):
    DB = Connect("dsn1")
    differentiator: reactive.value[int] = reactive.value(0)
    ui_res_list: reactive.value[list[ui.Tag]] = reactive.value([])
    dataframe_functions: reactive.value[list] = reactive.value([])

    @reactive.effect
    @reactive.calc
    def dynamical_server_function():
        for func in dataframe_functions.get():
            func()

    @render.ui
    def query_res_display():
        return ui_res_list.get()

    def handle_plot_query():
        if parse_postgres(input.query()):
            if valid_postgres(input.query()):
                DataFrame = DB.read(input.query())
                print(DataFrame)

                expr = sqlglot.parse_one(input.query())

                for col in expr.args["expressions"]:
                    if type(col) is sqlglot.expressions.Column:
                        print(type(col))
                        # then it's an aggregate expression
                        # x_data = DataFrame.select(f'{col.this}')

    def handle_dataframe_query():
        if input.query().strip() != "":
            if parse_postgres(input.query()):
                if valid_postgres(input.query()):
                    query = f"{input.query()}"
                    DataFrame = DB.read(query=query)

                    @output(id=f"{differentiator.get()}")
                    @render.data_frame
                    def df_func():
                        df = DataFrame
                        return df

                    ui_res_list.set(
                        [
                            *ui_res_list.get(),
                            ui.div(
                                ui.h3(query),
                                ui.output_data_frame(f"{differentiator.get()}"),
                            ),
                        ]
                    )

                    differentiator.set(differentiator.get() + 1)

                else:
                    print(
                        "Your statement contains illegal operations (you can't Update, Delete or Create)"
                    )
            else:
                print("Your SQL statement is Invalid")

        else:
            print("Please input a query before executing the query")

    @reactive.effect
    @reactive.event(input.exec)
    def query_handler():
        if input.query().upper().find("GROUP BY"):
            # on considère que ça peut-être affiché en tant que graphe
            handle_plot_query()
        else:
            handle_dataframe_query()


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
    ):
        return True
    else:
        return False
