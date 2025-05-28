
from shiny import App, ui, reactive, render, module
import polars as pl
import matplotlib.pyplot as plt
import json

# Data import
from shared import hr_employee_skill, hr_skill
from shared import placeholder_plot, placeholder_text

@module.ui
def gen_stat_page():
    return ui.page_fluid(
        ui.column(12,
            ui.h2("Statistiques Générales")
        ),
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
    ()

# PEOPLE PER SKILLS
    @reactive.calc
    def getPeoplePerSkills() -> plt.plot:

        dictOfSkills = dictSkillById()

        ppl_per_skills = hr_employee_skill.select(pl.count("employee_id"), "skill_id").group_by("skill_id").len("amount").sort(by="amount",descending=True)

        x_skills = ppl_per_skills.get_column("skill_id")
        x_named_skills = {}

        for skill_id in x_skills:
            x_named_skills[skill_id] = dictOfSkills[skill_id]

        y_ppl = ppl_per_skills.get_column("amount")

        plot = plt.bar(x_named_skills, y_ppl)

        return plot
    
    @render.plot
    def displayPeoplePerSkills():
        return getPeoplePerSkills()
    
    @render.data_frame
    def getSkills():

        return hr_skill 
    
# INTERNAL UTILS
    def dictSkillById():

        dict_id_to_name = {}

        id_to_name = hr_skill.select("id", "name")

        skill_ids = id_to_name.get_column("id")
        skill_names = id_to_name.get_column("name")

        if(not dict_id_to_name):
            for idx in range(skill_ids.len()):
                dict_id_to_name[skill_ids[idx]] = skill_names[idx]

        return dict_id_to_name

    

