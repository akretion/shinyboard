import inspect  # to get sqlglot's class hierarchy
from typing import Union

import matplotlib.pyplot as plt
import polars as pl
import sqlglot.expressions
from appdata.stored_query_repository import StoredQueryRepository
from connect import Connect
from pages.shared import pstates as ps
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

# TODO
## A repository Resolver : no need to import individual repositories,
## just feed an instance to the resolver and it makes
## the operation for you

DB = Connect("dsn2")
STORED_QUERY_REPO = StoredQueryRepository()


@module.ui
def sql_query_input():
    return ui.page_fluid(
        ui.br(),
        ui.output_ui("df_preview_title"),
        ui.output_data_frame("selected_df"),
        ui.hr(),
        ui.input_text_area("query", ui.h3("Entrez vôtre requête SQL")),
        ui.output_ui("get_tips"),
        ui.input_action_button("exec", "lancer"),
        ui.output_ui("query_res_display"),
    )


@module.server
def sql_query_server(input: Inputs, output: Outputs, session: Session):
    differentiator: reactive.value[int] = reactive.value(0)
    title_diff = "title_"
    state_diff = "state_"
    input_diff = "input_"
    button_diff = "button_"

    input_states: Union[
        reactive.value[dict[str, reactive.value[bool]]], reactive.value[dict]
    ] = reactive.value({})  # True: closed, False: in edition
    ui_res_list: reactive.value[list[ui.Tag]] = reactive.value([])

    @render.data_frame
    def selected_df():
        base_df = ps.available_rels.get()[ps.selected_dataframe_name.get()]

        dotted_row = pl.DataFrame(
            [[None for _ in base_df.columns]], schema=base_df.schema
        )

        peek = pl.concat([base_df.head(3), dotted_row, base_df.tail(3)], how="vertical")

        return peek

    @render.ui
    def query_res_display():
        return ui_res_list.get()

    @reactive.effect
    @reactive.event(input.exec)
    def query_handler():
        if parse_postgres(input.query()) and valid_postgres(input.query()):
            CURRENT_DATAFRAME = ps.available_rels.get()[
                f"{ps.selected_dataframe_name.get()}"
            ]

        if (
            input.query().replace("my_table", "test") == input.query()
            and input.query().replace("self", "test") == input.query()
        ):
            # my_table or self wasn't typed by user, aborting function
            ui.notification_show(
                ui.h3(
                    "table non reconnue, utilisez 'my_table' ou 'self'.", type="warning"
                )
            )
            return

        else:
            query_with_self: str = input.query().replace("my_table", "self")

            query_with_df_name: str = (
                input.query().replace("my_table", f"{ps.selected_dataframe_name.get()}")
                if input.query().replace(
                    "my_table", f"{ps.selected_dataframe_name.get()}"
                )
                is not input.query().replace(
                    "my_table", f"{ps.selected_dataframe_name.get()}"
                )
                else input.query().replace(
                    "self", f"{ps.selected_dataframe_name.get()}"
                )
            )

            title_to_store: reactive.value[str] = reactive.value(query_with_df_name)

            current_diff = differentiator.get()

            # Graph case
            if input.query().upper().find("GROUP BY") > 0:
                expr = sqlglot.parse_one(query_with_self)
                x_data = []
                y_data = []

                for col in expr.args["expressions"]:
                    if type(col) is sqlglot.expressions.Column:
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

                    # should never happen
                    else:
                        print(inspect.getmro(type(col)))
                        raise Exception(
                            "Oops, that's not supposed to happen ! The type of column "
                            "you queried isn't recognized"
                        )

                @output(id=f"{differentiator.get()}")
                @render.plot
                def plot_output():
                    plt.bar(x_data, y_data)

                ui_res_list.set(
                    [
                        *ui_res_list.get(),
                        ui.span(
                            ui.card(
                                ui.output_ui(f"{title_diff}{current_diff}"),
                                ui.card_body(ui.output_plot(f"{current_diff}")),
                                ui.row(ui.output_ui(f"{button_diff}{current_diff}")),
                            )
                        ),
                    ]
                )

            # Dataframe case
            else:

                @output(id=f"{current_diff}")
                @render.data_frame
                def df_func():
                    df = CURRENT_DATAFRAME.sql(query_with_self)
                    return df

                ui_res_list.set(
                    [
                        *ui_res_list.get(),
                        ui.card(
                            ui.output_ui(f"{title_diff}{current_diff}"),
                            ui.card_body(ui.output_data_frame(f"{current_diff}")),
                            ui.card_footer(
                                ui.row(ui.output_ui(f"{button_diff}{current_diff}"))
                            ),
                        ),
                    ]
                )
            # IN ANY CASE
            input_states.get().update(
                {f"{state_diff}{current_diff}": reactive.value(True)}
            )

            @output(id=f"{title_diff}{current_diff}")
            @render.ui
            def titlefunc():
                # print(f'differentiator in titlefunc: {differentiator.get()}')
                try:
                    if input_states.get()[f"{state_diff}{current_diff}"].get():
                        return ui.h3(title_to_store.get())
                    else:
                        return ui.row(
                            ui.column(
                                8,
                                ui.input_text(
                                    f"{input_diff}{current_diff}",
                                    "entrez le nouveau titre",
                                ),
                            ),
                            ui.column(
                                4,
                                ui.input_action_button(
                                    f"confirm_{current_diff}", "confirmer"
                                ),
                            ),
                        )
                except KeyError:
                    # print(f"key {state_diff}{current_diff} doesn't exist
                    # in input_states")
                    # print(f"input_states' keys : {input_states.get().keys()}")
                    return ui.notification_show("**sonic 2 game overr**")

            @reactive.effect
            @reactive.event(input[f"edit_{current_diff}"])
            def editing_switch():
                print(f"editing switch of {state_diff}{current_diff} activated")
                input_states.get()[f"{state_diff}{current_diff}"].set(False)
                input_states.set(input_states.get())  # forces invalidation

            @reactive.effect
            @reactive.event(input[f"confirm_{current_diff}"])
            def confirm_new_title():
                nonlocal title_to_store
                title_to_store.set(input[f"{input_diff}{current_diff}"]())
                input_states.get()[f"{state_diff}{current_diff}"].set(True)

                ui.notification_show(ui.h3("Titre modifié."), type="message")

            ## SAVING TO DB - data independant ##
            @reactive.effect
            @reactive.event(input[f"save_{current_diff}"])
            def save_query_to_db():
                STORED_QUERY_REPO.create(
                    display_title=title_to_store.get(),
                    query=query_with_df_name,
                    df_key_name=ps.selected_dataframe_name.get(),
                )

                ui.notification_show(ui.h3("Requête sauvegardée."), type="message")

            ###

            @output(id=f"{button_diff}{current_diff}")
            @render.ui
            def buttonfunc():
                # print(f'differentiator in button func: {differentiator.get()}')
                return ui.card_footer(
                    ui.row(
                        ui.column(
                            6,
                            ui.input_action_button(
                                f"edit_{current_diff}", "modifier le titre"
                            ),
                        ),
                        ui.column(
                            6,
                            ui.input_action_button(
                                f"save_{current_diff}", "sauvegarder la requête"
                            ),
                        ),
                    )
                )

                # CALLED FIRST
                # adds a new state set to 'closed' (True)

                # print("ui res list updated")

            differentiator.set(differentiator.get() + 1)

    @render.text
    def df_name():
        return f"{ps.french_name.get()}"

    @render.ui
    def df_preview_title():
        return ui.h4(f"Aperçu de {ps.french_name.get()}")

    @render.ui
    def get_tips():
        return ui.markdown(
            f"""
            ### À savoir
            - sélectionnez une table **dans la barre latérale**.
            - Vos requêtes seront exécutées sur la **table sélectionnée**.
            - Remplacez le nom de la table par **'my_table'** dans vos requêtes.
            - Utilisez les noms de colonnes dans l'aperçu de **{ps.french_name.get()}**
            """
        )

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
    """checks if the query only contains projections
    (no Create, Update or Delete allowed)
    """
    if (
        q.upper().find("UPDATE") < 0
        or q.upper().find("DELETE") < 0
        or q.upper().find("CREATE") < 0
        or q.upper().find("DROP") < 0
    ):
        return True
    else:
        return False
