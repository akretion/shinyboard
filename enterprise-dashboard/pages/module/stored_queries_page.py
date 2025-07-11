from shiny import module, ui, Inputs, Outputs, Session, render


from pages.shared import AVAILABLE_RELS, valid_postgres, parse_postgres

import sqlglot.expressions
import inspect

from appdata.stored_query_repository import StoredQueryRepository
from appdata.stored_query_model import StoredQuery  # only for type hints


@module.ui
def stored_queries_ui():
    return ui.page_fluid(ui.h3("stored queries"), ui.output_ui("display_query_cards"))


@module.server
def stored_queries_server(input: Inputs, outputs: Outputs, session: Session):
    STORED_QUERY_REPO = StoredQueryRepository()
    all_queries: list[StoredQuery] = STORED_QUERY_REPO.get_all()

    def get_query_cards() -> list[ui.Tag]:
        card_list = []

        for query in all_queries:
            card_list.append(
                ui.card(
                    ui.card_header(ui.h3(f"{query.display_title}")),
                    ui.card_body(f"the actual indicator will be here : {query.query}"),
                    ui.card_footer(ui.h4(f"effectuée sur {query.df_key_name}")),
                )
            )

        return card_list

    @render.ui
    def display_query_cards():
        return get_query_cards()

    def build_visual(query: StoredQuery):
        query_string = str(query.query)

        if parse_postgres(query_string) and valid_postgres(query_string):
            df_to_use = AVAILABLE_RELS.get()[f"{query.df_key_name}"]
            query_string = query_string.replace(f"{query.df_key_name}", "self")

            # Graph case
            if query_string.upper().find("GROUP BY") > 0:
                expr = sqlglot.parse_one(query_string)
                y_data = []

                for col in expr.args["expressions"]:
                    if type(col) is sqlglot.expressions.Column:
                        (df_to_use.select(f"{col}").to_series().to_list())

                    elif (
                        isinstance(col, sqlglot.expressions.Alias)
                        and len(y_data) == 0
                        or isinstance(col, sqlglot.expressions.AggFunc)
                    ):
                        agg_col_name = col.args["this"].this

                        y_data = (
                            df_to_use.select(f"{agg_col_name}").to_series().to_list()
                        )

                        # should never happen
                    else:
                        print(inspect.getmro(type(col)))
                        raise Exception(
                            "Oops, that's not supposed to happen ! The type of column you queried isn't recognized"
                        )
