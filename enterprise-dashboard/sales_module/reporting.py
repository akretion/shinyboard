from shiny import module, ui, Inputs, Outputs, Session


@module.ui
def reporting_ui():
    return ui.page_fluid(
        ui.navset_pill(
            ui.nav_panel(ui.h4("Produits"), "produits"),
            ui.nav_panel(ui.h4("Vendeurs"), "vendeurs"),
        )
    )


@module.server
def reporting_server(inputs: Inputs, outputs: Outputs, session: Session):
    pass
