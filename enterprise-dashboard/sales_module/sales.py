from shiny import module, Inputs, Outputs, Session, ui, render, reactive

import polars as pl

from shared import (
    EPOCH,
    AVAILABLE_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def sales_ui():
    return ui.page_fluid(ui.output_data_frame("display_sale_order"))


@module.server
def sales_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order():
        try:
            sale_order_df = AVAILABLE_RELS.get()["sale_order"]

            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:  # to avoid errors
                return sale_order_df.filter(
                    pl.col("sale_order_create_date") >= SELECTED_PERIOD_LOW_BOUND.get(),
                    pl.col("sale_order_create_date")
                    <= SELECTED_PERIOD_HIGH_BOUND.get(),
                )
            else:
                return sale_order_df

        except KeyError as KE:
            ui.notification_show(
                ui.h3("vous n'avez apparemment pas accès à la table des ventes.")
            )
            print(KE)
            return pl.DataFrame()

        except Exception:
            ui.notification_show(ui.h3("une erreur est survenue ':) ..."))
            return pl.DataFrame()

    @render.data_frame
    def display_sale_order():
        return get_sale_order()
