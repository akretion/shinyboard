from __future__ import annotations

import polars as pl
from great_tables import GT, md
from shiny import Inputs, Outputs, Session, module, reactive, render, ui

from ..shared import EPOCH, pstates as ps


@module.ui
def sales_ui():
    return ui.page_fluid(ui.output_ui("display_sale_order"))


@module.server
def sales_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order():
        try:
            sale_order_df = ps.available_rels.get()["sale_order"]

            if ps.selected_period_high_bound.get() != EPOCH:  # to avoid errors
                return GT(
                    sale_order_df.filter(
                        pl.col(
                            f"{ps.table_time_columns.get()['sale_order']}"
                        ).is_between(
                            ps.selected_period_low_bound.get(),
                            ps.selected_period_high_bound.get(),
                        ),
                        pl.col("company").is_in(ps.selected_company_names.get()),
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
