from sales.sales_persons import sales_persons_page, sales_persons_server
from shiny import module, ui


@module.ui
def sales_app():
    return ui.navset_pill(
        ui.nav_panel("Vendeurs", ui.h2("Vendeurs"), sales_persons_page("salesperson")),
        ui.nav_panel("Ventes de produits", ui.h2("Ventes")),
        ui.nav_panel("Produits", ui.h2("Produits")),
    )


@module.server
def sales_app_server(input, output, session):
    sales_persons_server("salesperson")
