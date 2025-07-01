from shiny import ui, module, Inputs, Outputs, Session


@module.ui
def module_ui():
    return ui.page_navbar(
        ui.nav_panel(ui.h3("Produits")),
        ui.nav_panel(
            ui.h3("Vendeurs"),
        ),
        ui.nav_panel(
            ui.h3("À facturer"),
        ),
        ui.nav_panel(ui.h3("Statistiques")),
    )


def module_server(input: Inputs, output: Outputs, session: Session):
    pass
