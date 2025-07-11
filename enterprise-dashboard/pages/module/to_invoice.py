from __future__ import annotations

import polars as pl
from great_tables import GT, md
from pages.shared import EPOCH
from pages.shared import pstates as ps
from shiny import Inputs, Outputs, Session, module, render, ui


@module.ui
def to_invoice_ui():
    return ui.page_fluid(ui.output_ui("display_to_invoice_df"))


@module.server
def to_invoice_server(inputs: Inputs, outputs: Outputs, session: Session):
    def get_to_invoice_df():
        try:
            if ps.selected_period_high_bound.get() != EPOCH:
                return GT(
                    ps.available_rels.get()["sale_order"].filter(
                        pl.col("invoice_status") != "no",
                        pl.col(
                            f"{ps.table_time_columns.get()['sale_order']}"
                        ).is_between(
                            ps.selected_period_low_bound.get(),
                            ps.selected_period_high_bound.get(),
                        ),
                        pl.col("company").is_in(ps.selected_company_names.get()),
                    ),
                ).tab_header(title=md("# Ventes à facturer"))

            else:
                return GT(pl.DataFrame())

        except KeyError as KE:
            ui.notification_show(
                ui.h4(
                    "vous n'avez pas accès à la table des ventes, "
                    "ou elle est indisponible",
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
