from shiny import module, ui, render, Inputs, Outputs, Session, reactive

import polars as pl
import matplotlib.pyplot as plt

from shared import (
    AVAILABLE_RELS,
    EPOCH,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def salespersons_ui():
    return ui.page_fluid(ui.output_plot("display_salespersons_plot"))


@module.server
def salespersons_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_salespersons_plot():
        try:
            sale_order = AVAILABLE_RELS.get()["sale_order"]

            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:
                sale_order = sale_order.filter(
                    pl.col("sale_order_create_date") >= SELECTED_PERIOD_LOW_BOUND.get(),
                    pl.col("sale_order_create_date")
                    <= SELECTED_PERIOD_HIGH_BOUND.get(),
                )

            sale_order_grouped_by_amount_tt = (
                sale_order.select("salesperson", "amount_total")
                .group_by("salesperson")
                .agg(pl.col("amount_total").sum())
            )

            x_data: list[str] = (
                sale_order_grouped_by_amount_tt.select("salesperson")
                .to_series()
                .to_list()
            )
            y_data: list[int] = (
                sale_order_grouped_by_amount_tt.select("amount_total")
                .to_series()
                .to_list()
            )

            plt.barh(x_data, y_data)

        except KeyError as KE:
            print(KE)
        except Exception as EX:
            print(EX)

    @render.plot
    def display_salespersons_plot():
        return get_salespersons_plot()
