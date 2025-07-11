from shiny import ui, module, render, reactive
from shiny import Inputs, Outputs, Session
from connect import Connect
import polars as pl
from vanna.remote import VannaDefault

# TODO
# enlever les credentials en clair...

api_key = "68d6be146a8946f4b10b0699722a632e"
model = "cosmos-model1"

vn = VannaDefault(model=model, api_key=api_key)

DB = Connect("dsn2")

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
