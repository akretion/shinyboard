from shiny import ui, module, Inputs, Outputs, Session
from .module import sales as sales
from .module import to_invoice as invoicing


@module.ui
def module_ui():
    return ui.page_navbar(
        ui.nav_panel(
            ui.h3("Ventes"),
            sales.sales_ui("sales"),
        ),
        ui.nav_panel(ui.h3("À facturer"), invoicing.to_invoice_ui("invoicing")),
    )


@module.server
def module_server(input: Inputs, output: Outputs, session: Session):
    sales.sales_server("sales")
    invoicing.to_invoice_server("invoicing")
