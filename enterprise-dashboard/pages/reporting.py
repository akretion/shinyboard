from pages.module import product, salespersons
from shiny import Inputs, Outputs, Session, module, ui


@module.ui
def reporting_ui():
    return ui.page_fluid(
        ui.navset_pill(
            ui.nav_panel(
                ui.h4("Vendeurs"), salespersons.salespersons_ui("salespersons")
            ),
            ui.nav_panel(ui.h4("Produits"), product.product_ui("products")),
        )
    )


@module.server
def reporting_server(inputs: Inputs, outputs: Outputs, session: Session):
    salespersons.salespersons_server("salespersons")
    product.product_server("products")
