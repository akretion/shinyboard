from __future__ import annotations

import polars as pl
from great_tables import GT
from great_tables import md
from pages.shared import AVAILABLE_RELS
from pages.shared import EPOCH
from pages.shared import SELECTED_PERIOD_HIGH_BOUND
from pages.shared import SELECTED_PERIOD_LOW_BOUND
from pages.shared import SELECTED_COMPANY_NAMES
from pages.shared import TABLE_TIME_COLUMNS
from shiny import Inputs
from shiny import module
from shiny import Outputs
from shiny import reactive
from shiny import render
from shiny import Session
from shiny import ui


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
                        pl.col(f"{TABLE_TIME_COLUMNS.get()['sale_order']}").is_between(
                            SELECTED_PERIOD_LOW_BOUND.get(),
                            SELECTED_PERIOD_HIGH_BOUND.get(),
                        ),
                        pl.col("company").is_in(SELECTED_COMPANY_NAMES.get()),
                    ),
                ).tab_header(title=md("# Les ventes"), subtitle=md("toutes confondues"))
            else:
                return GT(sale_order_df).tab_header(
                    title=md("# Les ventes"),
                    subtitle=md("toutes confondues"),
                )

        except KeyError as KE:
            ui.notification_show(
                ui.h3("vous n'avez apparemment pas accès à la table des ventes."),
            )
            print(KE)
            return GT(pl.DataFrame()).tab_header(
                title=md("# Les ventes"),
                subtitle=md("toutes confondues"),
            )

        except Exception:
            ui.notification_show(ui.h3("une erreur est survenue ':) ..."))
            return GT(pl.DataFrame()).tab_header(
                title=md("# Les ventes"),
                subtitle=md("toutes confondues"),
            )

    @render.ui
    def display_sale_order():
        return get_sale_order()
