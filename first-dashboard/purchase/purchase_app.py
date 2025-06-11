from shiny import ui, module
from purchase.suppliers_stats import suppliers_stats_page, suppliers_stats_server


@module.ui
def purchase_app():
    return ui.navset_pill(
        ui.nav_panel(
            "Fournisseurs", ui.h2("Fournisseurs"), suppliers_stats_page("suppliers")
        ),
        ui.nav_panel("Livraisons", ui.h2("Livraisons"), ui.h1("PLACEHOLDER")),
    )


@module.server
def purchase_app_server(input, output, session):
    suppliers_stats_server("suppliers")
