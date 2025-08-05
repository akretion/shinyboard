from pathlib import Path
from db2kpi.tool import _
from db2kpi.main import instance
from db2kpi.element import elements as elm

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_plotly

app_dir = Path(__file__).parent
app_css = app_dir / "db2kpi/style/app.css"


app_ui = ui.page_fillable(
    ui.card(
        ui.card_header("Kpi"),
        ui.layout_sidebar(
            ui.sidebar(
                "Settings",
                ui.output_ui("data_source"),
                ui.output_ui("organizations"),
                # ui.output_ui("debug"),
                bg="#f8f8f8",
            ),
            "Content",
        ),
    ),
    ui.include_css(app_css),
)


def app_server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def data_source():
        return ui.input_radio_buttons(
            "df_radio_buttons",
            ui.div(ui.span(_("Sources"))),
            instance.models,
        )

    @render.ui
    def organizations():
        orgas = [x["name"] for x in instance.kind.get_organizations()]
        return (
            ui.input_selectize(
                "organization",
                ui.span(_("Organizations")),
                orgas,
                selected=orgas[0],
                multiple=True,
            ),
        )

    @reactive.effect
    @reactive.event(input.organization)
    def organization_handler():
        elm.organizations.set(input.organization())

    @render.ui
    def debug():
        dbg = [
            instance.kind.get_organizations().__str__(),
            instance.kind.__str__(),
        ]
        return ui.span("debug:"), ui.pre("\n- ".join(dbg))


app = App(app_ui, app_server)
