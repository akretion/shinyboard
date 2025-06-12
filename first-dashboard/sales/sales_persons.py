import polars as pl

from shiny import ui, render, module, reactive


## TODO
# - Affichage conditionnel pour les tables
# - Meilleur affichage conditionnel pour les autres champs

# Primary tables
from sales.sale_data import getSalesData
from shared import getSharedData

sales_data = getSalesData()
shared_data = getSharedData()


@module.ui
def sales_persons_page():
    return ui.page_sidebar(
        ui.sidebar(
            ui.h2("Critères de tri"),
            ui.input_slider(
                "dateslider",
                ui.div(
                    ui.h3("Sélectionnez une période"),
                    ui.span(
                        "la période affichée correspond à la totalité des commandes effectuées"
                    ),
                ),
                min=sales_data.min_date_order,
                max=sales_data.max_date_order,
                value=[sales_data.min_date_order, sales_data.max_date_order],
                time_format="%Y-%m-%d",
                timezone="UTC",
                drag_range=True,
            ),
            ui.input_select(
                "company_name",
                ui.h3("sélectionnez une entreprise"),
                shared_data.company_names,
            ),
        ),
        ui.row(
            ui.column(
                6,
                ui.card(
                    ui.card_header("Meilleur Vendeur"),
                    ui.card_body(ui.output_text("displayBestSalesPerson")),
                ),
            ),
            ui.column(
                6,
                ui.card(
                    ui.card_header("Classement des Vendeurs"),
                    ui.card_body(ui.output_data_frame("displaySalesPersons")),
                ),
            ),
        ),
    )


@module.server
def sales_persons_server(input, output, session):
    @reactive.calc
    def getCompanyDict():
        return shared_data.company_dict

    # SALESPERSONS RANKED
    @reactive.calc  # works without, but crucial for optimization
    def getSalesPersons():
        if shared_data.getSelectedCompany()[0] == "":
            return (
                sales_data.sale_order.filter(
                    input.dateslider()[0] <= pl.col("date_order"),
                    input.dateslider()[1] >= pl.col("date_order"),
                    # shared_data.company_dict[f"{input.company_name()}".replace(" ", "").strip()] == pl.col("company_id"),
                )
                .join_where(
                    sales_data.res_partner,
                    pl.col("sale_order_uid").eq(pl.col("res_partner_uid")),
                    suffix="_res_partner",
                )
                .select("res_partner_name", "amount_untaxed")
                .group_by(pl.col("res_partner_name"))
                .sum()
                .sort(descending=True, by="amount_untaxed")
            )

        print(
            [
                getCompanyDict()[company_name.replace(" ", "").strip()]
                for company_name in shared_data.getSelectedCompany()
            ]
        )
        return (
            sales_data.sale_order.filter(
                input.dateslider()[0] <= pl.col("date_order"),
                input.dateslider()[1] >= pl.col("date_order"),
                # shared_data.company_dict[f"{input.company_name()}".replace(" ", "").strip()] == pl.col("company_id"),
                pl.col("company_id").is_in(
                    [
                        getCompanyDict()[company_name.replace(" ", "").strip()]
                        for company_name in shared_data.getSelectedCompany()
                    ]
                ),
            )
            .join_where(
                sales_data.res_partner,
                pl.col("sale_order_uid").eq(pl.col("res_partner_uid")),
                suffix="_res_partner",
            )
            .select("res_partner_name", "amount_untaxed")
            .group_by(pl.col("res_partner_name"))
            .sum()
            .sort(descending=True, by="amount_untaxed")
        )

    @render.data_frame
    def displaySalesPersons() -> pl.DataFrame:
        return getSalesPersons().rename(
            {"res_partner_name": "nom", "amount_untaxed": "montant des ventes ($)"}
        )

    # BEST SALESPERSON
    @render.text
    def displayBestSalesPerson():
        bsp_dict = getSalesPersons().to_dict()
        expr_name = (
            bsp_dict["res_partner_name"][0]
            if not bsp_dict["res_partner_name"].is_empty()
            else "Aucun vendeur dans la période sélectionnée."
        )
        expr_amount = (
            bsp_dict["amount_untaxed"][0]
            if not bsp_dict["amount_untaxed"].is_empty()
            else "Aucun montant à afficher dans la période sélectionnée"
        )
        return f"{expr_name} avec {expr_amount}$ de ventes hors taxes au total"

    @render.data_frame
    def displaySaleOrderWithInfo():
        pass
