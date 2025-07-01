from shiny import module, render, ui, Inputs, Outputs, Session

import polars as pl

from shared import (
    EPOCH,
    AVAILABLE_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def to_invoice_ui():
    return ui.page_fluid(ui.output_data_frame("display_to_invoice_df"))


@module.server
def to_invoice_server(inputs: Inputs, outputs: Outputs, session: Session):
    def get_to_invoice_df():
        try:
            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:
                return AVAILABLE_RELS.get()["sale_order"].filter(
                    pl.col("invoice_status") != "no",
                    pl.col("sale_order_create_date") >= SELECTED_PERIOD_LOW_BOUND.get(),
                    pl.col("sale_order_create_date")
                    <= SELECTED_PERIOD_HIGH_BOUND.get(),
                )

            else:
                return pl.DataFrame()

        except KeyError as KE:
            ui.notification_show(
                ui.h4(
                    "vous n'avez pas accès à la table des ventes, ou elle est indisponible"
                )
            )
            print(KE)
            return pl.DataFrame()

        except Exception:
            ui.notification_show(ui.h4("une erreur est survenue ':) ..."), type="error")
            return pl.DataFrame()

    @render.data_frame
    def display_to_invoice_df():
        return get_to_invoice_df()
