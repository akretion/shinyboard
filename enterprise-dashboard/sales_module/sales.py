from shiny import module, Inputs, Outputs, Session, ui, render, reactive

from great_tables import GT, md

import polars as pl

from shared import (
    EPOCH,
    AVAILABLE_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def sales_ui():
    return ui.page_fluid(ui.output_ui("display_sale_order"))


@module.server
def sales_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order():
        try:
            sale_order_df = AVAILABLE_RELS.get()["sale_order"]

            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:  # to avoid errors
                return GT(
                    sale_order_df.filter(
                        pl.col("date_order").is_between(
                            SELECTED_PERIOD_LOW_BOUND.get(),
                            SELECTED_PERIOD_HIGH_BOUND.get(),
                        )
                    )
                ).tab_header(title=md("# Les ventes"), subtitle=md("toutes confondues"))
            else:
                return GT(sale_order_df).tab_header(
                    title=md("# Les ventes"), subtitle=md("toutes confondues")
                )

        except KeyError as KE:
            ui.notification_show(
                ui.h3("vous n'avez apparemment pas accès à la table des ventes.")
            )
            print(KE)
            return GT(pl.DataFrame()).tab_header(
                title=md("# Les ventes"), subtitle=md("toutes confondues")
            )

        except Exception:
            ui.notification_show(ui.h3("une erreur est survenue ':) ..."))
            return GT(pl.DataFrame()).tab_header(
                title=md("# Les ventes"), subtitle=md("toutes confondues")
            )

    @render.ui
    def display_sale_order():
        return get_sale_order()
