from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from plotly.graph_objects import Figure
from plotly.graph_objects import FigureWidget
from pages.shared import APP_CONSTANTS
from great_tables import GT
from shiny import Inputs
from shiny import module
from shiny import Outputs
from shiny import reactive
from shiny import render
from shiny import Session
from shiny import ui
from shinywidgets import output_widget
from shinywidgets import render_plotly

# TODO
# Donner un choix de graphe aux utilisateurs


@module.ui
def product_ui():
    return ui.page_fluid(
        ui.h2("Catégorie la plus populaire"),
        ui.hr(),
        ui.row(
            ui.column(
                7,
                ui.card(
                    ui.card_header(ui.h3("par revenu")),
                    ui.card_body(
                        ui.output_ui(
                            "display_trending_category_revenue",
                        ),
                    ),
                ),
            ),
            ui.column(
                5,
                ui.card(
                    ui.card_header(ui.h3("par unités vendues")),
                    ui.card_body(
                        ui.output_ui(
                            "display_trending_category_units_sold",
                        ),
                    ),
                ),
            ),
        ),
        ui.h2("Ventes de produits"),
        ui.hr(),
        ui.h3("par revenus générés"),
        ui.output_ui("display_product_plot_ui"),
        ui.output_ui("redirect_script"),
        ui.output_ui("product_plot_widget"),
        ui.h3("par unités vendues"),
        ui.output_ui("display_best_sellers_qty_ui"),
    )


@module.server
def product_server(inputs: Inputs, outputs: Outputs, session: Session):
    link: reactive.value[str] = reactive.value("http://localhost:8069/odoo/products/0")
    redirecting_script: reactive.value[str] = reactive.value("")

    graph_types: dict[str, reactive.value[str]] = {
        "best_sellers_qty": reactive.value("bar"),
        "all_products": reactive.value("pie"),
    }
    selected_graph_type_product_plot: reactive.value[str] = reactive.value("bar")

    def get_product_product():
        return APP_CONSTANTS.OTHER_RELS.get()["product_product"]

    @reactive.calc
    def get_sale_order_line_filtered():
        return (
            APP_CONSTANTS.OTHER_RELS.get()["sale_order_line"]
            .join_where(
                APP_CONSTANTS.AVAILABLE_RELS.get()["sale_order"],
                pl.col("order_id") == pl.col("id_right"),
            )
            .filter(
                pl.col(
                    f"{APP_CONSTANTS.TABLE_TIME_COLUMNS.get()['sale_order']}"
                ).is_between(
                    APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.get(),
                    APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.get(),
                ),
                pl.col("company").is_in(APP_CONSTANTS.SELECTED_COMPANY_NAMES.get()),
            )
        )

    # BEST SELLERS BY UNITS SOLD
    @reactive.calc
    def get_best_sellers_qty_df():
        sale_order_line = get_sale_order_line_filtered()
        return (
            sale_order_line.select("name", "product_uom_qty")
            .group_by("name")
            .agg(pl.col("product_uom_qty").sum())
            .sort(by="product_uom_qty", descending=False)
            .cast({"product_uom_qty": pl.Int32})
        )

    # only the visual
    @render_plotly
    def get_best_sellers_qty_plotly():
        df = get_best_sellers_qty_df()

        match graph_types["best_sellers_qty"].get():
            case "bar":
                return px.bar(
                    data_frame=df, x="name", y="product_uom_qty", width=1200, height=800
                )
            case "line":
                return px.area(
                    data_frame=df, x="name", y="product_uom_qty", width=1200, height=800
                )
            case _:
                return px.bar(
                    data_frame=df, x="name", y="product_uom_qty", width=1200, height=800
                )

    # both the visual and the input - what's displayed by shiny
    @render.ui
    def display_best_sellers_qty_ui():
        return ui.row(
            ui.input_select(
                "graph_type_best_sellers_qty",
                ui.span("type de graphe"),
                ["bar", "line"],
            ),
            output_widget("get_best_sellers_qty_plotly"),
        )

    # sets the correct value in graph type according to uinput
    @reactive.effect
    @reactive.event(inputs.graph_type_best_sellers_qty)
    def handle_best_sellers_qty_input():
        new_type = inputs.graph_type_best_sellers_qty()
        graph_types["best_sellers_qty"].set(new_type)

    # PRODUCT PIE BY REVENUE
    def get_product_plot_df():
        sale_order_line = get_sale_order_line_filtered()
        return (
            sale_order_line.select(
                "name",
                "product_uom_qty",
                "price_unit",
                "id",
            )
            .group_by("name")
            .agg(
                pl.col("price_unit").sum(),
                pl.col("product_uom_qty").sum(),
                pl.col("id").count(),
            )
            .select("name", "product_uom_qty", "price_unit")
        )

    @render_plotly
    def get_product_plot_plotly():
        df = get_product_plot_df()
        match graph_types["all_products"].get():
            case "pie":
                fig: FigureWidget | Figure = px.pie(
                    df,
                    values="price_unit",
                    names="name",
                    width=1200,
                    height=800,
                )
                fig.update_layout(
                    legend=dict(
                        x=1,
                        y=0,
                        traceorder="normal",
                        title_font_family=None,
                        font=dict(
                            family=None,
                            size=15,
                            color="black",
                        ),
                        bgcolor="LightSteelBlue",
                        bordercolor="Black",
                        borderwidth=1,
                    ),
                )
                fig: FigureWidget | Figure = go.FigureWidget(fig.data, fig.layout)
                fig.data[0].on_click(handle_pie_click)  # type: ignore
                return fig

            case "bar":
                fig = px.bar(df, x="name", y="price_unit", width=1200, height=800)
                fig.data[0].on_click(handle_pie_click)  # type: ignore
                return fig

    @render.ui
    def display_product_plot_input():
        return (
            ui.input_select(
                "graph_type_product_plot",
                ui.span("type de graphe"),
                ["pie", "bar", "dataframe"],
            ),
        )

    @render.ui
    def display_product_plot_ui():
        if graph_types["all_products"].get() != "dataframe":
            return ui.row(
                ui.output_ui("display_product_plot_input"),
                output_widget("get_product_plot_plotly"),
            )
        else:
            return ui.row(
                ui.output_ui("display_product_plot_input"), GT(get_product_plot_df())
            )

    @reactive.effect
    @reactive.event(inputs.graph_type_product_plot)
    def handle_product_plot_input():
        new_type = inputs.graph_type_product_plot()
        graph_types["all_products"].set(new_type)

    def handle_pie_click(trace, points, state):
        product_template = get_product_product()
        labels = trace.labels
        selected = f"{labels[points.point_inds[0]]}"
        split = selected.split("]")
        if split:
            selected = split[0].strip().replace("[", "")
            my_id = (
                product_template.filter(pl.col("default_code").eq(f"{selected}"))
                .select("product_tmpl_id")
                .to_series()
                .to_list()
            )
            link.set(f"http://localhost:8069/odoo/products/{my_id[0]}")
            redirecting_script.set(
                f"""
            window.open('{link.get()}', '_blank')
            """
            )
        else:
            print("this looks like a service, not a product...")

    @render.ui
    def redirect_script():
        return ui.tags.script(
            f"""
        {redirecting_script.get()}
        """
        )

    @reactive.calc
    def get_trending_category_units_sold():
        sale_order_line = get_sale_order_line_filtered()
        info = (
            sale_order_line.select("category", "id")
            .group_by("category")
            .agg(pl.col("id").count())
            .sort(by="id", descending=True)
            .limit(1)
            .to_dict()
        )
        if info["category"].is_empty() or info["id"].is_empty():
            return {
                "category": "aucune catégorie pour la période sélectionnée",
                "count": "0",
            }
        else:
            return {"category": info["category"][0], "count": info["id"][0]}

    @render.ui
    def display_trending_category_units_sold():
        result = get_trending_category_units_sold()
        return ui.span(
            ui.h2(f"{result['category']}"),
            ui.h4(f"avec {result['count']} unités vendues."),
        )

    @reactive.calc
    def get_trending_category_revenue():
        sale_order_line = get_sale_order_line_filtered()
        info = (
            sale_order_line.select("category", "price_total")
            .group_by("category")
            .agg(pl.col("price_total").sum())
            .sort(by="price_total", descending=True)
            .limit(1)
            .to_dict()
        )
        if info["category"].is_empty() or info["price_total"].is_empty():
            return {
                "category": "pas de revenu pour la période sélectionnée",
                "price": "0",
            }
        else:
            return {"category": info["category"][0], "price": info["price_total"][0]}

    @render.ui
    def display_trending_category_revenue():
        result = get_trending_category_revenue()
        return ui.span(
            ui.h2(f"{result['category']}"),
            ui.h4(f"avec {result['price']}$ de revenu généré."),
        )
