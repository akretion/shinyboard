from shiny import ui, module, render, reactive
from shiny import Inputs, Outputs, Session
from connect import Connect
import polars as pl
from vanna.remote import VannaDefault
import os

# For local dev, put credentials in a .env file
api_key = os.getenv("API_KEY_ENV", "API_KEY_SHOULDNT_BE_HERE")
model = os.getenv("MODEL_STR", "MODEL_STR_SHOULDNY+T_BE_HERE")

vn = VannaDefault(model=model, api_key=api_key)

DB = Connect("dsn1")

dataframes: dict[str, pl.DataFrame] = {
    "sale_order": DB.read("SELECT * FROM sale_order"),
    "purchase_order": DB.read("SELECT * FROM purchase_order"),
    "res_partner": DB.read("SELECT * FROM res_partner"),
}


def train_vanna():
    for key in dataframes.keys():
        vn.train(
            documentation=f"the table {key} has the following schema : {dataframes[key].schema}"
        )
        print(f"training for {key} done")

    vn.train(
        documentation="sale_order.state can take these values : 'draft', 'sent', 'sale', 'done', 'cancel'"
    )


# train_vanna()


@module.ui
def chat_module_ui():
    return ui.page_fluid(
        ui.chat_ui("chat"),
        ui.input_slider("slider_thing", "caca", 1, 10, 1),
        ui.input_slider("slider_thing_2", "caca", 1, 10, 1),
        ui.output_text("slider_text"),
    )


@module.server
def chat_module_server(input: Inputs, output: Outputs, session: Session):
    chat = ui.Chat("chat")
    print("server called")

    differentiator = 0
    runtime_server_funcs = reactive.value({})

    @render.data_frame
    def outputDF():
        return pl.DataFrame()

    @reactive.calc
    def slider_thing():
        return input.slider_thing()

    @render.text
    def slider_text():
        return slider_thing()

    @chat.on_user_submit
    async def handle_chat(u_input: str):
        sql = vn.generate_sql(u_input)

        if sql.find("JOIN") == -1:
            # corrects the query for dataframe manipulation
            df_name = getTableNameFromQuery(sql)

            df_tailored_sql = sql.replace(df_name, "self")
            fromDF = dataframes[df_name].sql(df_tailored_sql)

            @render.data_frame
            def outputDF():
                print(f"output {differentiator} appelé")
                return fromDF

            runtime_server_funcs.get()[f"{differentiator}"] = outputDF
            ui_res = ui.output_data_frame(f"{differentiator}")

        else:

            @render.ui
            def outputUI():
                print(f"output {differentiator} appelé")
                return ui.span("ELSE : pas encore défini mais présent")

            ui_res = ui.output_ui(f"{differentiator}")
            DB.read(sql)

        px = vn.generate_plotly_code(u_input)
        vn._sanitize_plotly_code(px)

        if vn.is_sql_valid(sql):
            print(ui_res)
            await chat.append_message(ui_res)


# UTILS
def getTableNameFromQuery(query: str):
    """
    NAME
        getTableNameFromQuery
    DESCRIPTION
        returns the name of the FROM-clause table the query is executed on.
        ommits JOINs because there only is a need to know on which dataframe the query
        should be executed against.
    """
    exploded = query.split("FROM")

    if len(exploded) >= 2:
        print(exploded)
        return exploded[1].strip(";").strip().replace("\n", " ").split(" ")[0]

    else:
        return query
