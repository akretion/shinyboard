import polars as pl

from shiny import App, ui, render, module, reactive

# Primary tables
from sales.sale_data import getSalesData
from shared import datetime

sales_data = getSalesData()
company_names: list = []
company_dict: dict = {}

for i in range(len(sales_data.company_id_dict)+1):
    company_names.append(sales_data.company_id_dict['name'][i])
    company_dict[f"{sales_data.company_id_dict['name'][i]}".replace(" ", "").strip()] = sales_data.company_id_dict['id'][i]

print(list(company_dict))

@module.ui
def sales_persons_page():

    return ui.page_sidebar(
        ui.sidebar(
            ui.h2("Indicateurs"),
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
                'company_name',
                ui.h3("sélectionnez une entreprise"),
                company_names
            )
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

    # SALESPERSONS RANKED
    @reactive.calc  # works without, but crucial for optimization
    def getSalesPersons():
        print(
            f"(sales_persons.py l62): INPUT SLIDER : {input.dateslider()}\n TYPE : {type(input.dateslider())}"
        )
        return (
            sales_data.sale_order.filter(
                input.dateslider()[0] <= pl.col("date_order"),
                input.dateslider()[1] >= pl.col("date_order"),
                company_dict[f"{input.company_name()}".replace(" ", "").strip()] == pl.col("company_id")
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
        print(f"BSP DICT (sales_persons.py l87): \n{bsp_dict}")
        return f"{expr_name} avec {expr_amount}$ de ventes hors taxes au total"

    # ORDERS
    @reactive.calc
    def getOrders():
        pass

    def displayOrders():
        pass
