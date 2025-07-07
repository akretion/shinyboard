from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
from plotly.graph_objects import Figure
from plotly.graph_objects import FigureWidget
from shared import AVAILABLE_RELS
from shared import OTHER_RELS
from shared import SELECTED_PERIOD_HIGH_BOUND
from shared import SELECTED_PERIOD_LOW_BOUND
from shared import TABLE_TIME_COLUMNS
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
        output_widget("display_product_plot"),
        ui.h3("par unités vendues"),
        output_widget("display_best_sellers_by_qty"),
    )


@module.server
def product_server(inputs: Inputs, outputs: Outputs, session: Session):
    @reactive.calc
    def get_sale_order_line_filtered():
        return (
            OTHER_RELS.get()["sale_order_line"]
            .join_where(
                AVAILABLE_RELS.get()["sale_order"],
                pl.col("order_id") == pl.col("id_right"),
            )
            .filter(
                pl.col(f"{TABLE_TIME_COLUMNS.get()['sale_order']}").is_between(
                    SELECTED_PERIOD_LOW_BOUND.get(),
                    SELECTED_PERIOD_HIGH_BOUND.get(),
                ),
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
        y_data: list[int] = (
            infos.select(
                "product_uom_qty",
            )
            .to_series()
            .to_list()
        )

        return px.bar(x=x_data, y=y_data)

    @render_plotly  # type: ignore
    def display_best_sellers_by_qty():
        return get_best_sellers_by_qty()

    def get_product_plot():
        try:
            sale_order_line = get_sale_order_line_filtered()

            sale_order_line_grouped = (
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

            name_labels = (
                sale_order_line_grouped.select(
                    "name",
                )
                .to_series()
                .to_list()
            )
            qty_ordered_labels = (
                sale_order_line_grouped.select(
                    "price_unit",
                )
                .to_series()
                .to_list()
            )

            labels: list[str] = []

            for i in range(len(name_labels)):
                labels.append(
                    f"{name_labels[i]}\nrevenue:{int(qty_ordered_labels[i])}€",
                )

            """
            plt.pie(x=x_data)
            plt.legend(labels, loc="best", bbox_to_anchor=(1, 1))
            plt.tight_layout()
            """
            print(sale_order_line_grouped)

            fig: FigureWidget | Figure = px.pie(
                sale_order_line_grouped,
                values="price_unit",
                names="name",
                width=1200,
                height=800,
            )
            fig.update_layout(
                legend=dict(
                    x=1,
                    y=0,
                    traceorder="reversed",
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

            fig.data[0].on_click(handle_click)  # type: ignore

            return fig

        except KeyError as KE:
            print(
                f"as KeyError has occured, it most likely means the table you're trying to access isn't available.\n------EXCEPTIONc\n{KE}\n------ENF OF EXCEPTION------",
            )

        except Exception as EX:
            print(EX)

    @render_plotly  # type: ignore
    def display_product_plot():
        return get_product_plot()

    def handle_click(trace, points, state):
        print("TEST")

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
