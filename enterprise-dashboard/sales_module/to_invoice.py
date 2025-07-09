from __future__ import annotations

import polars as pl
from great_tables import GT
from great_tables import md
from shared import AVAILABLE_RELS
from shared import EPOCH
from shared import SELECTED_PERIOD_HIGH_BOUND
from shared import SELECTED_PERIOD_LOW_BOUND
from shared import TABLE_TIME_COLUMNS
from shared import SELECTED_COMPANY_NAMES
from shiny import Inputs
from shiny import module
from shiny import Outputs
from shiny import render
from shiny import Session
from shiny import ui


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
                        pl.col(f"{TABLE_TIME_COLUMNS.get()['sale_order']}").is_between(
                            SELECTED_PERIOD_LOW_BOUND.get(),
                            SELECTED_PERIOD_HIGH_BOUND.get(),
                        ),
                        pl.col("company").is_in(SELECTED_COMPANY_NAMES.get()),
                    ),
                ).tab_header(title=md("# Ventes à facturer"))

            else:
                return GT(pl.DataFrame())

        except KeyError as KE:
            ui.notification_show(
                ui.h4(
                    "vous n'avez pas accès à la table des ventes, ou elle est indisponible",
                ),
            )
            print(KE)
            return GT(pl.DataFrame())

        except Exception:
            ui.notification_show(
                ui.h4("une erreur est survenue ':) ..."),
                type="error",
            )
            return GT(pl.DataFrame())

    @render.ui
    def display_to_invoice_df():
        return get_to_invoice_df()
