# import seaborn as sns
# import pyarrow as PyA
from faicons import icon_svg

from shiny import App, ui

# Data
from shared import hr_employee_skill


# Pages
from general_stats import gen_stat_page, gen_stat_server
from interactive_stats import interactive_stats_page, interactive_stats_server


app_ui = ui.page_navbar(

    ui.nav_panel("Géneral", "Général", gen_stat_page("gen1")),
    ui.nav_panel("Intéractif", "Intéractif", interactive_stats_page("it1")),

    title="Stats sur les Ressources Humaines"
)


def server(input, o1utput, session):
    gen_stat_server("gen1")
    interactive_stats_server("it1")


app = App(app_ui, server)
