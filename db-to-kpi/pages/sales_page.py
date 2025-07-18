from shiny import ui, module, Inputs, Outputs, Session
from .module import sales as sales
from .module import to_invoice as invoicing

# REFACTOR #1 : from pages import reporting


@module.ui
def module_ui():
    return ui.page_navbar(
        ui.nav_panel(
            ui.h3("Ventes"),
            sales.sales_ui("sales"),
        ),
        ui.nav_panel(ui.h3("À facturer"), invoicing.to_invoice_ui("invoicing")),
        # REFACTOR #1 :
        #       ui.nav_panel(ui.h3("Reporting"), reporting.reporting_ui("reporting")),
    )


@module.server
def module_server(input: Inputs, output: Outputs, session: Session):
    sales.sales_server("sales")
    invoicing.to_invoice_server("invoicing")


# REFACTOR #1 :
#   reporting.reporting_server("reporting")
