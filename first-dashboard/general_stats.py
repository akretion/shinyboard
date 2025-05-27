
from shiny import App, ui, reactive, render, module
import polars as pl

# Data import
from shared import hr_data


@module.ui
def page():
    return ui.page_fluid(
        ui.column(12,
            ui.h2("Statistiques Générales")
        ),

        ui.column(6,
            ui.card(
                ui.card_header( ui.output_text("getMostKnownSkill") ),
                ui.card_footer(" est la compétence la plus maîtrisée")
            )
        ),

        ui.column(6,
            ui.card(
                ui.card_header( ui.output_text("getLeastKnownSkill") ),
                ui.card_footer(" est la compétence la moins maîtrisée")
            )
        )
    )


@module.server
def server(input, output, session):
# MOST KNOWN SKILL
    @render.text
    def getMostKnownSkill():

        group_by_skills = hr_data.select(pl.count("employee_id"), "skill_id").group_by("skill_id")

        group_to_amount = group_by_skills.len(name="amountOfPeople").sort(by="amountOfPeople", descending=True)

        most_known_skill = group_to_amount.limit(1).get_column("skill_id")[0]


        return most_known_skill
    
# LEAST KNOWN SKILL
    @render.text
    def getLeastKnownSkill():
        group_by_skills = hr_data.select(pl.count("employee_id"), "skill_id").group_by("skill_id")

        group_to_amount = group_by_skills.len(name="amountOfPeople").sort(by="amountOfPeople", descending=False)

        least_known_skill = group_to_amount.limit(1).get_column("skill_id")[0]


        return least_known_skill