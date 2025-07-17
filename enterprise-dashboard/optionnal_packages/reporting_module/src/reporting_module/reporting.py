from shiny import module, ui, Inputs, Outputs, Session

import salespersons
import product


@module.ui
def reporting_ui():
    return ui.nav_panel(
        ui.h2("Reporting"),
        ui.navset_pill(
            ui.nav_panel(
                ui.h4("Vendeurs"), salespersons.salespersons_ui("salespersons")
            ),
            ui.nav_panel(ui.h4("Produits"), product.product_ui("products")),
        ),
    )


@module.server
def reporting_server(inputs: Inputs, outputs: Outputs, session: Session):
    salespersons.salespersons_server("salespersons")
    product.product_server("products")
