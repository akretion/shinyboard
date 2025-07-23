from __future__ import annotations

import plotly.express as px
import polars as pl
from great_tables import GT
from pages.shared import APP_CONSTANTS
from shiny import Inputs
from shiny import module
from shiny import Outputs
from shiny import reactive
from shiny import render
from shiny import Session
from shiny import ui
from shinywidgets import output_widget
from shinywidgets import render_widget


@module.ui
def salespersons_ui():
    return ui.page_fluid(
        ui.h3("Revenus par vendeurs"),
        ui.hr(),
        output_widget("display_salespersons_plot"),
        ui.h3(ui.output_text("display_sales_plot_text")),
        ui.hr(),
        output_widget("display_sales_plot"),
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
        return APP_CONSTANTS.AVAILABLE_RELS.get()["sale_order"].filter(
            pl.col(APP_CONSTANTS.TABLE_TIME_COLUMNS.get()["sale_order"]).is_between(
                APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.get(),
                APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.get(),
            ),
            pl.col("company").is_in(APP_CONSTANTS.SELECTED_COMPANY_NAMES.get()),
        )

    def get_sale_order_line_filtered():
        return APP_CONSTANTS.OTHER_RELS.get()["sale_order_line"].filter(
            pl.col("create_date").is_between(
                APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.get(),
                APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.get(),
            ),
            pl.col("company").is_in(APP_CONSTANTS.SELECTED_COMPANY_NAMES.get()),
        )

    def get_salespersons_plot():
        sale_order = get_sale_order_filtered()

        try:
            sale_order_grouped_by_amount_tt = (
                sale_order.select("salesperson", "amount_total")
                .group_by("salesperson")
                .agg(pl.col("amount_total").sum())
            )
            fig = px.bar(
                title="Revenus par vendeurs",
                data_frame=sale_order_grouped_by_amount_tt,
                x="salesperson",
                y="amount_total",
            )
            return fig

        except KeyError as KE:
            print(KE)
        except Exception as EX:
            print(EX)

    @render_widget  # type: ignore
    def display_salespersons_plot():
        return get_salespersons_plot()

    @reactive.calc
    def get_sales_plot():
        sale_order = get_sale_order_filtered()
        data = (
            sale_order.select("date_order", "sale_order")
            .group_by("date_order")
            .agg(pl.count("sale_order"))
            .sort(by="date_order", descending=False)
        )

        fig = px.area(
            data_frame=data.cast(
                {
                    "date_order": pl.String,
                },
            ).rename(
                {
                    "sale_order": "nombre de ventes",
                    "date_order": "date de vente",
                }
            ),
            x="date de vente",
            y="nombre de ventes",
        )

        return fig

    @render_widget  # type: ignore
    def display_sales_plot():
        return get_sales_plot()

    @render.text
    def display_sales_plot_text():
        return f"Ventes (du {APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.get()} au {APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.get()})"

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
