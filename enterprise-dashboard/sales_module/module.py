from shiny import ui, module, Inputs, Outputs, Session
import sales_module.sales as sales
import sales_module.to_invoice as invoicing
import sales_module.reporting as reporting


@module.ui
def module_ui():
    return ui.page_navbar(
        ui.nav_panel(
            ui.h3("Ventes"),
            sales.sales_ui("sales"),
        ),
        ui.nav_panel(ui.h3("À facturer"), invoicing.to_invoice_ui("invoicing")),
        ui.nav_panel(ui.h3("Reporting"), reporting.reporting_ui("reporting")),
    )


@module.server
def module_server(input: Inputs, output: Outputs, session: Session):
    sales.sales_server("sales")
    invoicing.to_invoice_server("invoicing")
    reporting.reporting_server("reporting")
