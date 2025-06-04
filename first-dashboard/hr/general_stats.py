
from shiny import App, ui, reactive, render, module
import polars as pl
import matplotlib.pyplot as plt
import json

# Data import
from hr.hr_data import hr_skill, hr_employee_skill, hr_employee_named_skill
from shared import placeholder_plot, placeholder_text

@module.ui
def gen_stat_page():
    return ui.page_fluid(
        ui.row(
            ui.column(5,
                ui.card(
                    ui.card_header( ui.output_text("getMostKnownSkill") ),
                    ui.card_footer(" est la compétence la plus maîtrisée")
                )
            ),

            ui.column(5,
                ui.card(
                    ui.card_header( ui.output_text("getLeastKnownSkill") ),
                    ui.card_footer(" est la compétence la moins maîtrisée")
                )
            ),

            ui.output_data_frame("getSkills"),

            ui.h3("Répartition des personnes par compétences"),
            ui.output_plot("displayPeoplePerSkills")
        )
    )


@module.server
def gen_stat_server(input, output, session):
# MOST KNOWN SKILL
    @render.text
    def getMostKnownSkill():

        group_by_skills = hr_employee_skill.select(pl.count("employee_id"), "skill_id").group_by("skill_id")

        group_to_amount = group_by_skills.len(name="amountOfPeople").sort(by="amountOfPeople", descending=True)

        most_known_skill = group_to_amount.limit(1).get_column("skill_id")[0]

        return most_known_skill
    
# LEAST KNOWN SKILL
    @render.text
    def getLeastKnownSkill():
        group_by_skills = hr_employee_skill.select(pl.count("employee_id"), "skill_id").group_by("skill_id")

        group_to_amount = group_by_skills.len(name="amountOfPeople").sort(by="amountOfPeople", descending=False)

        least_known_skill = group_to_amount.limit(1).get_column("skill_id")[0]


        return least_known_skill

        
    @render.data_frame
    def getSkills():

        return hr_employee_named_skill
    
    

