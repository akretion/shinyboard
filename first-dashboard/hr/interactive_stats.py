import matplotlib.pyplot as plt
import polars as pl

from shiny import App, ui, reactive, render, module

from hr.hr_data import getHRData
from models.hr_data_model import Hr_data_model
from shared import placeholder_plot, placeholder_text
import json


hr_data = getHRData()

@module.ui
def interactive_stats_page():
    return ui.page_sidebar(
        ui.sidebar(
            ui.h2("Critères de tri"),
            ui.input_select(
                "skill_name",
                "choisissez une compétence",
                hr_data.skill_series.to_series().to_list(),
            ),
        ),
        ui.page_fluid(  # partie centrale
            ui.row(
                ui.column(
                    6,
                    ui.card(
                        ui.card_header(ui.output_text("displayCPWS")),
                        ui.card_footer("possèdent la compétence"),
                    ),
                ),
            ),
            ui.card(
                ui.card_header("Personnes par niveaux de maîtrise"),
                ui.output_plot("displayPeoplePerSkills"),
            ),
        ),
    )


@module.server
def interactive_stats_server(input, output, session):
    """
    NAME
        server

    DESCRIPTION
        Callback of the UI. When the UI loads, this function will be called.
        Its purpose is to make data available for the front to take (via inputs)
    """

    # TOTAL EMPLOYEE COUNT
    def getTotalEmployeeCount():
        return f"{hr_data.hr_employee_named_skill.select('employee_id').count().get_column('employee_id')[0]}"

    # AVG OF PEOPLE WITH A SKILL
    @reactive.calc
    def getCountPeopleWithSkill():
        ppl_with_skill = (
            hr_data.hr_employee_named_skill.filter(pl.col("name") == input.skill_name())
            .count()
            .get_column("employee_id")[0]
        )

        print(hr_data.hr_employee_named_skill.group_by("name").all())

        return f"{ppl_with_skill} employé(s) sur {getTotalEmployeeCount()}"

    @render.text
    def displayCPWS():
        return getCountPeopleWithSkill()

    # People per skills
    @reactive.calc
    def getPeoplePerSkills():
        return placeholder_plot

    @render.plot
    def displayPeoplePerSkills():
        return getPeoplePerSkills()
