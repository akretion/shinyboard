from __future__ import annotations

import plotly.express as px
import polars as pl
from pages.main import _
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
from shinywidgets import render_plotly

import logging


@module.ui
def salespersons_ui():
    return ui.page_fluid(
        ui.h5("Revenus par vendeurs"),
        ui.hr(),
        output_widget("display_salespersons_plot"),
        ui.h5(ui.output_text("display_sales_plot_text")),
        ui.hr(),
        ui.output_ui("display_sales_inputs"),
        ui.output_ui("display_sales_plot_ui"),
        ui.row(
            ui.column(
                6,
                ui.h5("Nombre de ventes par clients"),
                ui.output_ui("display_client_sales_df"),
            ),
            ui.column(
                6,
                ui.h5("Revenus par clients"),
                ui.output_ui("display_client_revenue_df"),
            ),
        ),
    )


@module.server
def salespersons_server(inputs: Inputs, outputs: Outputs, session: Session):

    graph_types: dict[str, reactive.value[str]] = {
        "salespersons_plot": reactive.value("bar"),
        "sales_plot": reactive.value("area"),
    }

    #### DATA
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

    #### SALESPERSONS
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
            logging.log(logging.ERROR, KE)
        except Exception as EX:
            logging.log(logging.ERROR, EX)

    @render_plotly
    def display_salespersons_plot():
        return get_salespersons_plot()

    #### SALES
    @reactive.calc
    def get_sales_data() -> pl.DataFrame:
        """
        ## Summary:
            summary_ Gets generic data needed to build the sales per date graph

        ## Returns:
            type_ polars.DataFrame: DataFrame that describes the data
        """
        sale_order = get_sale_order_filtered()
        data = (
            sale_order.select("date_order", "sale_order", "company")
            .group_by("date_order")
            .agg(pl.count("sale_order"))
            .sort(by="date_order", descending=False)
        )

        return data

    @reactive.calc
    def get_sales_pivot():
        """
        ## Summary
            Returns a Pivot that describes a summarized version of get_sales_data()

        ## Returns:
            type_ polars.DataFrame: DataFrame that describes the data
        """
        sale_order = get_sale_order_filtered()
        return (
            sale_order.select("date_order", "sale_order", "company")
            .group_by("date_order")
            .agg(pl.count("sale_order"), pl.col("company").agg_groups())
            .sort(by="date_order", descending=False)
            .pivot(on="date_order", values="sale_order", index="company")
        )

    ######## RENDITIONS AND RENDERING
    def get_gt_sales_pivot():
        """
        ## Summary
            Great Tables Rendition of get_sales_pivot()

        ## Returns:
            type_ great_tables.GT: GreatTable object
        """
        return GT(get_sales_pivot())

    @render_plotly
    def display_sales_plotly():
        """
        ## Summary
            Plotly Rendition of get_sales_data()
        Returns:
            plotly.go.Figure: Figure object
        """
        data = get_sales_data()
        renaming = {
            "sale_order": "nombre de ventes",
            "date_order": "date de vente",
        }
        col_names = {"x": "date de vente", "y": "nombre de ventes"}

        match graph_types["sales_plot"].get():
            case "area":
                fig = px.area(
                    data_frame=data.cast(
                        {
                            "date_order": pl.String,
                        }
                    ).rename(renaming),
                    x=col_names["x"],
                    y=col_names["y"],
                )

                return fig

            case "pie":
                fig = px.pie(
                    data_frame=data.cast(
                        {
                            "date_order": pl.String,
                        }
                    ).rename(renaming),
                    names=col_names["y"],
                    values=col_names["y"],
                )

                return fig

            case "bar":
                fig = px.bar(
                    data_frame=data.cast(
                        {
                            "date_order": pl.String,
                        }
                    ).rename(renaming),
                    x=col_names["y"],
                    y=col_names["y"],
                )

                return fig

            case _:
                fig = px.line(
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

    @render.ui
    def display_sales_plot_ui():
        match graph_types["sales_plot"].get():
            case "dataframe":
                return get_gt_sales_pivot()

            case _:
                return output_widget("display_sales_plotly")

    ######## INPUTS
    @render.ui
    def display_sales_inputs():
        """
        ## Summary
            To be displayed. Returns the UI to select the graph type that displays
            **data from get_sales_plot()**

        ## Returns:
            type_ shiny.ui.Tag: UI that allows selection
        """
        return ui.input_select(
            "graph_types_sales_inputs",
            _("Type de graphe"),
            ["bar", "line", "pie", "dataframe"],
        )

    @reactive.effect
    @reactive.event(inputs.graph_types_sales_inputs)
    def sales_inputs_handler():
        new_value = inputs.graph_types_sales_inputs()
        graph_types["sales_plot"].set(new_value)

    @render.text
    def display_sales_plot_text():
        return f"Ventes (du {APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.get()} au {APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.get()})"

    #### 2 DATAFRAMES
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
