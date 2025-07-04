from shiny import module, ui, render, Inputs, Outputs, Session, reactive
from great_tables import GT

import polars as pl
import matplotlib.pyplot as plt

from shared import (
    AVAILABLE_RELS,
    OTHER_RELS,
    SELECTED_PERIOD_LOW_BOUND,
    SELECTED_PERIOD_HIGH_BOUND,
)


@module.ui
def salespersons_ui():
    return ui.page_fluid(
        ui.h3("Revenus par vendeurs"),
        ui.hr(),
        ui.output_plot("display_salespersons_plot"),
        ui.h3(ui.output_text("display_sales_plot_text")),
        ui.hr(),
        ui.output_plot("display_sales_plot"),
        ui.row(
            ui.column(
                6,
                ui.h3("Nombre de ventes par clients"),
                ui.output_ui("display_client_sales_df"),
            ),
            ui.column(
                6,
                ui.h3("Revenus par clients"),
                ui.output_ui("display_client_revenue_df"),
            ),
        ),
    )


@module.server
def salespersons_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order_filtered():
        return AVAILABLE_RELS.get()["sale_order"].filter(
            pl.col("date_order").is_between(
                SELECTED_PERIOD_LOW_BOUND.get(), SELECTED_PERIOD_HIGH_BOUND.get()
            )
        )

    def get_sale_order_line_filtered():
        return OTHER_RELS.get()["sale_order_line"].filter(
            pl.col("create_date").is_between(
                SELECTED_PERIOD_LOW_BOUND.get(), SELECTED_PERIOD_HIGH_BOUND.get()
            )
        )

    @reactive.calc
    def get_salespersons_plot():
        sale_order = get_sale_order_filtered()

        try:
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

            fig, axes = plt.subplots()

            axes.barh(x_data, y_data)

            return fig

        except KeyError as KE:
            print(KE)
        except Exception as EX:
            print(EX)

    @render.plot(
        alt="Revenus par vendeurs : Aucune donnée trouvée avec les filtres choisis... Essayez de les changer !"
    )
    def display_salespersons_plot():
        return get_salespersons_plot()

    @reactive.calc
    def get_sales_plot():
        sale_order = get_sale_order_filtered()

        first_and_last_tick: list = [
            SELECTED_PERIOD_LOW_BOUND.get(),
            SELECTED_PERIOD_HIGH_BOUND.get(),
        ]
        data = (
            sale_order.select("date_order", "sale_order")
            .group_by("date_order")
            .agg(pl.count("sale_order"))
            .sort(by="date_order", descending=False)
            .to_series()
            .to_list()
        )

        fig, axes = plt.subplots()

        axes.plot(data)
        axes.set_yticks(first_and_last_tick)

        return fig

    @render.plot(
        alt="Ventes de la période sélectionée : aucune vente trouvée avec les filtres choisis... Essayez de les changer !"
    )
    def display_sales_plot():
        return get_sales_plot()

    @render.text
    def display_sales_plot_text():
        return f"Ventes (du {SELECTED_PERIOD_LOW_BOUND.get()} au {SELECTED_PERIOD_HIGH_BOUND.get()})"

    @reactive.calc
    def get_client_df():
        sale_order_line = get_sale_order_line_filtered()

        clients_ranked = (
            sale_order_line.select("customer", "id")
            .group_by("customer")
            .agg(pl.col("id").count())
            .sort(by="id", descending=True)
            .rename({"id": "commandes"})
        )

        return GT(clients_ranked)

    @render.ui
    def display_client_sales_df():
        return get_client_df()

    @reactive.calc
    def get_client_revenue_df():
        sale_order_line = get_sale_order_line_filtered()

        clients_ranked = (
            sale_order_line.select("customer", "price_total")
            .group_by("customer")
            .agg(pl.col("price_total").sum())
            .sort(by="price_total", descending=True)
        )

        return GT(clients_ranked)

    @render.ui
    def display_client_revenue_df():
        return get_client_revenue_df()
