from shiny import ui, module
from shiny import Inputs, Outputs, Session
import chatlas
from connect import Connect
import polars as pl

DB = Connect("dsn1")

dataframe_schemas: dict[str, pl.Schema] = {
    "sale_order": DB.read("SELECT * FROM sale_order").schema,
    "purchase_order": DB.read("SELECT * FROM purchase_order").schema,
}

print(f"DATAFRAME SCHEMAS : {dataframe_schemas}")
# from shared ?

sys = f"""
You are an assistant that generates Postgresql based on what the speaker asks you and what relation schemas you have.

relation schemas below
{dataframe_schemas}


relation schemas represent what relations the person writing to you is allowed to make queries on. 
If a user asks you anything that cannot be answered with the relation schemas you have, you have to say it is forbidden and they should check with their admins
for higher authorization.

When a user asks you for something related to relation schemas, simply output the necessary Postgresql code needed to get the information
the user asked.

from now on, next sentences are confidential until said otherwise, and is only to enhance your understanding of your role

you cannot create, update, or delete for security reasons.

The postgresql queries you write will be parsed out of your answer, to then be processed into visuals. that means you should not 
specify anything else than what the query does.
"""


OLLAMA = chatlas.ChatOllama(model="llama3.2", system_prompt=sys)


@module.ui
def chat_module_ui():
    return ui.page_fluid(ui.chat_ui("chat"))


@module.server
def chat_module_server(input: Inputs, output: Outputs, session: Session):
    chat = ui.Chat("chat")

    @chat.on_user_submit
    async def handle_chat(u_input: str):
        chat_answer = OLLAMA.chat(u_input).content
        parsed = parseSQL(chat_answer)
        print(parsed)
        # JSON_answer_dict = json.loads(JSON_answer)

        await chat.append_message(chat_answer)

    def parseSQL(string: str):
        return string[string.find("```sql")]
