from shiny import ui, render, reactive
from shiny import module, Inputs, Outputs, Session

import matplotlib.pyplot as plt
import polars as pl
import sqlglot
import sqlglot.expressions
import inspect  # to get sqlglot's class hierarchy
from shared import AVAILABLE_RELS, SELECTED_DATAFRAME_NAME

from connect import Connect

DB = Connect("dsn1")


@module.ui
def sql_query_input():
    return ui.page_fluid(
        ui.br(),
        ui.h4(f"aperçu de {SELECTED_DATAFRAME_NAME.get()}"),
        ui.output_data_frame("selected_df"),
        ui.hr(),
        ui.input_text_area("query", ui.h3("Entre vôtre requête SQL")),
        ui.markdown(
            f"""
            ### À savoir
            - sélectionnez une table **dans la barre latérale**.
            - Vos requêtes seront exécutées sur la **table sélectionnée**.
            - Remplacez le nom de la table par **'my_table'** dans vos requêtes.
            - Utilisez les noms de colonnes dans l'aperçu de **{SELECTED_DATAFRAME_NAME.get()}**
            """
        ),
        ui.input_action_button("exec", "lancer"),
        ui.output_ui("query_res_display"),
    )


@module.server
def sql_query_server(input: Inputs, output: Outputs, session: Session):
    # in deprecation...
    differentiator: reactive.value[int] = reactive.value(0)
    ui_res_list: reactive.value[list[ui.Tag]] = reactive.value([])
    output_functions: reactive.value[list] = reactive.value([])

    @render.data_frame
    def selected_df():
        base_df = AVAILABLE_RELS.get()[SELECTED_DATAFRAME_NAME.get()]

        dotted_row = pl.DataFrame(
            [[None for _ in base_df.columns]], schema=base_df.schema
        )

        peek = pl.concat([base_df.head(3), dotted_row, base_df.tail(3)], how="vertical")

        return peek

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
                CURRENT_DATAFRAME = AVAILABLE_RELS.get()[
                    f"{SELECTED_DATAFRAME_NAME.get()}"
                ]

                if (
                    input.query().replace("my_table", "test") == input.query()
                    and input.query().replace("self", "test") == input.query()
                ):
                    # my_table or self wasn't typed by user, aborting function
                    print("Invalid table name, use 'my_table' (or 'self') instead")
                    return

                else:
                    query_with_self = input.query().replace("my_table", "self")
                    query_with_df_name = input.query().replace(
                        "my_table", f"{SELECTED_DATAFRAME_NAME.get()}"
                    )

                    expr = sqlglot.parse_one(query_with_self)
                    x_data = []
                    y_data = []

                    for col in expr.args["expressions"]:
                        if type(col) is sqlglot.expressions.Column:
                            print(f"is column : {col}")
                            # if it's a regular column
                            print(
                                CURRENT_DATAFRAME.select(f"{col}").to_series().to_list()
                            )
                            x_data = (
                                CURRENT_DATAFRAME.select(f"{col}").to_series().to_list()
                            )

                        elif (
                            isinstance(col, sqlglot.expressions.Alias)
                            and len(y_data) == 0
                            or isinstance(col, sqlglot.expressions.AggFunc)
                        ):
                            agg_col_name = col.args["this"].this

                            y_data = (
                                CURRENT_DATAFRAME.select(f"{agg_col_name}")
                                .to_series()
                                .to_list()
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
                                ui.h3(query_with_df_name),
                                ui.output_plot(f"{differentiator.get()}"),
                            ),
                        ]
                    )

                    differentiator.set(differentiator.get() + 1)

    def handle_dataframe_query():
        if input.query().strip() != "":
            if parse_postgres(input.query()):
                if valid_postgres(input.query()):
                    if (
                        input.query().replace("my_table", "test") == input.query()
                        and input.query().replace("self", "test") == input.query()
                    ):
                        # my_table or self wasn't typed by user, aborting function
                        print("Invalid table name, use 'my_table' (or 'self') instead")
                        return

                    query_with_self = f"{input.query().replace('my_table', 'self')}"
                    f"{input.query().replace('my_table', f'{SELECTED_DATAFRAME_NAME.get()}')}"

                    CURRENT_DATAFRAME = AVAILABLE_RELS.get()[
                        f"{SELECTED_DATAFRAME_NAME.get()}"
                    ]

                    @output(id=f"{differentiator.get()}")
                    @render.data_frame
                    def df_func():
                        df = CURRENT_DATAFRAME.sql(query_with_self)
                        return df

                    output_functions.set([*output_functions.get(), df_func])

                    ui_res_list.set(
                        [
                            *ui_res_list.get(),
                            ui.div(
                                ui.h3(query_with_self),
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
            handle_dataframe_query()

    def return_placeholders(pl_title: str, pl_text: str):
        @output(id=f"{differentiator.get()}")
        @render.ui
        def func():
            return ui.card(ui.card_header(pl_title), ui.card_body(pl_text))

        ui_res_list.set([*ui_res_list.get(), ui.output_ui(f"{differentiator.get()}")])

        differentiator.set(differentiator.get() + 1)


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
