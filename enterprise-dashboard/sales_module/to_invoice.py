from shiny import module, render, ui, Inputs, Outputs, Session
from great_tables import GT, md

import polars as pl

from shared import (
    EPOCH,
    AVAILABLE_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def to_invoice_ui():
    return ui.page_fluid(ui.output_ui("display_to_invoice_df"))


@module.server
def to_invoice_server(inputs: Inputs, outputs: Outputs, session: Session):
    def get_to_invoice_df():
        try:
            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:
                return GT(
                    AVAILABLE_RELS.get()["sale_order"].filter(
                        pl.col("invoice_status") != "no",
                        pl.col("date_order").is_between(
                            SELECTED_PERIOD_LOW_BOUND.get(),
                            SELECTED_PERIOD_HIGH_BOUND.get(),
                        ),
                    )
                ).tab_header(title=md("# Ventes à facturer"))

            else:
                return GT(pl.DataFrame())

        except KeyError as KE:
            ui.notification_show(
                ui.h4(
                    "vous n'avez pas accès à la table des ventes, ou elle est indisponible"
                )
            )
            print(KE)
            return GT(pl.DataFrame())

        except Exception:
            ui.notification_show(ui.h4("une erreur est survenue ':) ..."), type="error")
            return GT(pl.DataFrame())

    @render.ui
    def display_to_invoice_df():
        return get_to_invoice_df()
