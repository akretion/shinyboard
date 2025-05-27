
import matplotlib.pyplot as plt
import polars as pl

from shiny import App, ui, reactive, render, module

from shared import hr_data
columns = hr_data.get_column("skill_id").to_list()


@module.ui
def interactive_stats_page(): 
    return ui.page_sidebar(
        ui.sidebar(
            ui.h2("Informations"),
            ui.input_select("skill_id", "choisissez une compétence", columns)
        ),
        ui.page_fluid( # partie centrale
            ui.row(
                ui.column(6,
                    ui.card(
                        ui.card_header(ui.output_text("displayCPWS")),
                        ui.card_footer("possèdent la compétence")
                    ),
                ),
            ),

            ui.card(
                ui.card_header( "Personnes par niveaux de maîtrise" ),
                ui.output_plot("displayPeoplePerSkills")
            ),
        )
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

# PLACEHOLDERS

    placeholder_text = "Pas encore implémenté !"
    placeholder_plot = plt.bar(5, 10, width=0.8, bottom=None, align='center', data=None)

# TOTAL EMPLOYEE COUNT
    def getTotalEmployeeCount():
        return f"{hr_data.select("employee_id").count().get_column("employee_id")[0]}"
        
    
# AVG OF PEOPLE WITH A SKILL
    @reactive.calc
    def getCountPeopleWithSkill():

        ppl_with_skill = hr_data.select("employee_id", "skill_id").filter(
            pl.col("skill_id").eq(int(input.skill_id()))
            ).count().get_column("employee_id")[0]
        
        return f"{ppl_with_skill} sur {getTotalEmployeeCount()} employés"
    
    @render.text
    def displayCPWS():
        return getCountPeopleWithSkill()

# People per skills
    @reactive.calc
    def getPeoplePerSkills() -> plt.plot:
        return placeholder_plot
    
    @render.plot
    def displayPeoplePerSkills():
        return getPeoplePerSkills()