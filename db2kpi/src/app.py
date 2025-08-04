from pathlib import Path
from db2kpi.main import _, instance

from shiny import App, Inputs, Outputs, Session, reactive, render, ui
from shinywidgets import output_widget, render_plotly

app_dir = Path(__file__).parent


app_css = app_dir / "db2kpi/style/app.css"


app_ui = ui.page_fillable(
    ui.card(
        ui.card_header(
            "Kpi",
        ),
        ui.layout_sidebar(
            ui.sidebar(
                "Settings",
                ui.output_ui("get_data_source"),
                bg="#f8f8f8",
            ),
            "Content",
            ui.hr(),
        ),
    ),
    ui.include_css(app_css),
)


def app_server(input: Inputs, output: Outputs, session: Session):

    @render.ui
    def get_data_source():
        return ui.input_radio_buttons(
            "df_radio_buttons",
            ui.div(ui.span(_("Sources"))),
            instance.models,
        )


app = App(app_ui, app_server)
