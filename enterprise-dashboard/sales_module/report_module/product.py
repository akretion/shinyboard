from shiny import module, Inputs, Outputs, Session, reactive, ui, render

import matplotlib.pyplot as plt
import polars as pl

from shared import (
    OTHER_RELS,
    EPOCH,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


# TODO
## Donner un choix de graphe aux utilisateurs


@module.ui
def product_ui():
    return ui.page_fluid(ui.output_plot("display_product_plot"))


@module.server
def product_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_product_plot():
        try:
            sale_order_line = OTHER_RELS.get()["sale_order_line"]

            if SELECTED_PERIOD_HIGH_BOUND.get() != EPOCH:
                sale_order_line = sale_order_line.filter(
                    pl.col("create_date") >= SELECTED_PERIOD_LOW_BOUND.get(),
                    pl.col("create_date") <= SELECTED_PERIOD_HIGH_BOUND.get(),
                )

            sale_order_line_grouped = (
                sale_order_line.select("name", "product_uom_qty", "price_unit", "id")
                .group_by("name")
                .agg(
                    pl.col("price_unit").sum(),
                    pl.col("product_uom_qty").sum(),
                    pl.col("id").count(),
                )
                .select("name", "product_uom_qty", "price_unit")
            )

            x_data = sale_order_line_grouped.select("price_unit").to_series().to_list()
            name_labels = sale_order_line_grouped.select("name").to_series().to_list()
            qty_ordered_labels = (
                sale_order_line_grouped.select("product_uom_qty").to_series().to_list()
            )

            labels: list[str] = []

            for i in range(len(name_labels)):
                labels.append(f"{name_labels[i]}\nqty:{int(qty_ordered_labels[i])}")

            plt.pie(x=x_data)
            plt.legend(labels, loc="best", bbox_to_anchor=(1, 1))
            plt.tight_layout()

        except KeyError as KE:
            print(KE)

        except Exception as EX:
            print(EX)

    @render.plot
    def display_product_plot():
        return get_product_plot()
