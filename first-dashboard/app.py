# import seaborn as sns
# import pyarrow as PyA
from faicons import icon_svg
from pathlib import Path

from shiny import App, ui, reactive, render

## TODO
# - Réunir les deux pages HR dans un seul onglet, puis créer une sous page
# de navigation dans la page aggrégat

# Pages
from hr import hr_app
from sales import sales_app
from purchase import purchase_app
from shared import getSharedData

shared_data = getSharedData()

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h3('Critères de filtres'),
        ui.hr(),
        ui.input_select(
            'company_name',
            ui.h4('par entreprise(s)'),
            shared_data.company_names,
            multiple=True
        ),

        ui.input_slider(
            'date_slider',
            ui.h4('par dates'),
            min=1,
            max=10,
            value=[1, 10],
            drag_range=True
        )
    ),

    ui.page_navbar(
        ui.head_content(ui.include_css(Path(__file__).parent / "app.css")),
        ui.nav_panel("RH", ui.h1("Ressources Humaines"), hr_app.hr_app("hr")),
        ui.nav_panel("Ventes", ui.h1("Ventes"), sales_app.sales_app("sales")),
        ui.nav_panel("Achat", ui.h1("Achat"), purchase_app.purchase_app("purchase")),
        title="Statistiques sur une entreprise",
    )
)


def server(input, output, session):
    hr_app.hr_app_server("hr")
    sales_app.sales_app_server("sales")
    purchase_app.purchase_app_server("purchase")

    @reactive.effect
    def selectedCompanyhandler():
        print("selected company handler called")
        shared_data.setSelectedCompany(input.company_name())


    @reactive.effect
    def selectedDatesHandler():
        print("selected dates handler called")
        shared_data.setSelectedDate(*input.date_slider())

app = App(app_ui, server)
