from shiny import module, Inputs, Outputs, Session, reactive, ui, render

import matplotlib.pyplot as plt
import polars as pl

from shared import (
    OTHER_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


# TODO
## Donner un choix de graphe aux utilisateurs


@module.ui
def product_ui():
    return ui.page_fluid(
        ui.h2("Ventes de produits"),
        ui.hr(),
        ui.row(
            ui.column(
                6, ui.h3("par revenus générés"), ui.output_plot("display_product_plot")
            ),
            ui.column(
                6,
                ui.h3("par unités vendues"),
                ui.output_plot("display_best_sellers_by_qty"),
            ),
        ),
    )


@module.server
def product_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order_line_filtered():
        return OTHER_RELS.get()["sale_order_line"].filter(
            pl.col("create_date").is_between(
                SELECTED_PERIOD_LOW_BOUND.get(), SELECTED_PERIOD_HIGH_BOUND.get()
            )
        )

    @reactive.calc
    def get_best_sellers_by_qty():
        sale_order_line = get_sale_order_line_filtered()

        infos = (
            sale_order_line.select("name", "product_uom_qty")
            .group_by("name")
            .agg(pl.col("product_uom_qty").sum())
            .sort(by="product_uom_qty", descending=False)
            .cast({"product_uom_qty": pl.Int32})
        )

        x_data: list[str] = infos.select("name").to_series().to_list()
        y_data: list[int] = infos.select("product_uom_qty").to_series().to_list()

        plt.barh(x_data, y_data)

    @render.plot
    def display_best_sellers_by_qty():
        return get_best_sellers_by_qty()

    @reactive.calc
    def get_product_plot():
        try:
            sale_order_line = get_sale_order_line_filtered()

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
                sale_order_line_grouped.select("price_unit").to_series().to_list()
            )

            labels: list[str] = []

            for i in range(len(name_labels)):
                labels.append(
                    f"{name_labels[i]}\nrevenue:{int(qty_ordered_labels[i])}€"
                )

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
