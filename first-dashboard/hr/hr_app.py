from hr.general_stats import gen_stat_page, gen_stat_server
from hr.interactive_stats import interactive_stats_page, interactive_stats_server

from shiny import ui, module


@module.ui
def hr_app():
    return ui.navset_pill(
        ui.nav_panel(
            "RH - Compétences", ui.h1("Compétences"), gen_stat_page("general")
        ),
        ui.nav_panel(
            "RH - Stats Intéractives",
            ui.h1("Stats Intéractives"),
            interactive_stats_page("interactive"),
        ),
    )


@module.server
def hr_app_server(input, output, server):
    gen_stat_server("general")
    interactive_stats_server("interactive")
