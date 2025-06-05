# import seaborn as sns
# import pyarrow as PyA
from faicons import icon_svg
from pathlib import Path

from shiny import App, ui

## TODO ##
# - Réunir les deux pages HR dans un seul onglet, puis créer une sous page
# de navigation dans la page aggrégat

# Pages
from hr import hr_app
from sales.sales_app import sales_stats_page, sales_stats_server

app_ui = ui.page_navbar(
    ui.head_content(ui.include_css(Path(__file__).parent / "app.css")),
    ui.nav_panel("RH", ui.h1("Ressources Humaines"), hr_app.hr_app("hr")),
    ui.nav_panel("Ventes", ui.h1("Ventes"), sales_stats_page("sales")),
    title="Statistiques sur une entreprise",
)


def server(input, o1utput, session):
    hr_app.hr_app_server("hr")
    sales_stats_server("sales")


app = App(app_ui, server)
