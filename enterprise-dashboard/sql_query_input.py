from shiny import ui, render, reactive
from shiny import module, Inputs, Outputs, Session

import matplotlib.pyplot as plt
import sqlglot
import sqlglot.expressions
import inspect  # to get sqlglot's class hierarchy
from shared import CURRENT_USER_ID, available_tables

from connect import Connect

DB = Connect("dsn1")


@module.ui
def sql_query_input():
    return ui.page_fluid(
        ui.br(),
        ui.hr(),
        ui.input_text("query", ui.h3("Entre vôtre requête SQL")),
        ui.markdown(
            """
            ### À savoir
            - mettez des **alias** pour vos **fonctions d'aggrégation** pour une sortie plus stable et lisible.
            - les requêtes avec des clauses **GROUP BY** seront affichées sous forme de **graphe**.
            - les requêtes sans seront sous forme de **tableau**
            """
        ),
        ui.span(
            "mettez des alias pour vos fonction d'aggrégation pour une sortie plus stable et lisible."
        ),
        ui.input_action_button("exec", "lancer"),
        ui.output_ui("query_res_display"),
    )


@module.server
def sql_query_server(input: Inputs, output: Outputs, session: Session):
    differentiator: reactive.value[int] = reactive.value(0)
    ui_res_list: reactive.value[list[ui.Tag]] = reactive.value([])
    output_functions: reactive.value[list] = reactive.value([])

    def getAvailableRelDF():
        print(available_tables(CURRENT_USER_ID.get(), DB))

    @reactive.calc
    def dynamical_server_function():
        for func in output_functions.get():
            func()

    @render.ui
    def query_res_display():
        return ui_res_list.get()

    def handle_plot_query():
        if parse_postgres(input.query()):
            if valid_postgres(input.query()):
                DataFrame = DB.read(input.query())

                expr = sqlglot.parse_one(input.query())
                x_data = []
                y_data = []

                for col in expr.args["expressions"]:
                    if type(col) is sqlglot.expressions.Column:
                        print(f"is column : {col}")
                        # if it's a regular column
                        print(DataFrame.select(f"{col}").to_series().to_list())
                        x_data = DataFrame.select(f"{col}").to_series().to_list()

                    elif (
                        isinstance(col, sqlglot.expressions.Alias) and len(y_data) == 0
                    ):
                        agg_col_name = col.args["this"].this

                        y_data = (
                            DataFrame.select(f"{agg_col_name}").to_series().to_list()
                        )

                    # testing for something wrong
                    else:
                        print(inspect.getmro(type(col)))

                print(f"X_DATA : {x_data}")
                print(f"Y_DATA : {y_data}")

                @output(id=f"{differentiator.get()}")
                @render.plot
                def plot_output():
                    plt.bar(x_data, y_data)

                output_functions.set([*output_functions.get(), plot_output])

                ui_res_list.set(
                    [
                        *ui_res_list.get(),
                        ui.span(
                            ui.h3(input.query()),
                            ui.output_plot(f"{differentiator.get()}"),
                        ),
                    ]
                )

                differentiator.set(differentiator.get() + 1)

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

                    output_functions.set([*output_functions.get(), df_func])

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
        if input.query().upper().find("GROUP BY") > 0:
            # on considère que ça peut-être affiché en tant que graphe
            handle_plot_query()
        else:
            getAvailableRelDF()
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
        or q.upper().find("DROP") < 0
    ):
        return True
    else:
        return False
