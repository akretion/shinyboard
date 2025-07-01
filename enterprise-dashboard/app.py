from shiny import App, reactive, render, ui
from shiny import Inputs, Outputs, Session

from connect import Connect

import polars as pl


from shared import (
    CURRENT_USER_ID,
    CURRENT_USER_NAME,
    AVAILABLE_RELS,
    SELECTED_DATAFRAME_NAME,
)
import sql_query_input


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("credentials_input"),
        ui.hr(),
        ui.output_ui("get_avail_df_name_list"),
    ),
    ui.output_ui("login_handler"),
)


def app_server(input: Inputs, output: Outputs, session: Session):
    sql_query_input.sql_query_server("sql")

    # CONSTANTS
    DB = Connect("dsn2")
    LOGINS = DB.read("SELECT id, login FROM res_users")

    # REACTIVE VARS - UI depends on them
    in_logins = reactive.value({"valid": False, "user": "", "user_id": -1})
    is_logged_in = reactive.value(False)

    reactive.value(pl.DataFrame())

    # SIDEBAR
    @render.ui
    def credentials_input():
        if is_logged_in.get():
            return ui.div(
                ui.h3(f"Connecté à {in_logins.get()['user']}"),
                ui.input_action_button("disconnect", "Se déconnecter"),
            )

        else:
            return ui.div(
                ui.input_text(
                    "login", ui.span("Login"), placeholder="identifiant en minuscule"
                ),
                ui.input_password("password", ui.span("Mot de passe")),
                ui.input_action_button("login_button", "Se connecter"),
            )

    @render.ui
    def available_tables():
        available_tables_df = DB.read(
            f"""
 SELECT ir_model.model AS table_name
FROM ir_model
JOIN ir_model_access
ON ir_model.id = ir_model_access.model_id
JOIN res_groups_users_rel
ON ir_model_access.group_id = res_groups_users_rel.gid
JOIN res_users
ON res_users.id = res_groups_users_rel.uid
WHERE ir_model.transient = FALSE 
AND res_users.id = {in_logins.get()["user_id"]}
AND ir_model.model !~ '.show$'
            """
        )

        # assignation des schémas dans shared
        available_tables_df.select("table_name").to_series().to_list()
        table_name_schema_dict = {}
        """
        for rel in table_list:
            if(rel == "ir.actions.report"):
                continue
            print(rel.replace(".", "_"))
            table_name_schema_dict[rel.replace(".", "_")] = DB.read(f"SELECT * FROM {rel.replace(".", "_")}").schema
        """

        print(table_name_schema_dict)

        # retour de l'UI

    # CENTER
    @render.ui
    def fallback():
        return ui.page_fluid(
            ui.h1("Connectez-vous à un utilisateur"),
            ui.span("Cela vous permettra d'avoir accès à des indicateurs appropriés."),
        )

    @reactive.effect
    @reactive.event(input.login_button)
    def login():
        uid = (
            LOGINS.filter(pl.col("login") == input.login())
            .select("id")
            .to_series()
            .to_list()[0]
        )
        newValue = {
            "valid": (
                not LOGINS.select("login")
                .filter(pl.col("login") == str(input.login()).strip())
                .is_empty()
            ),
            "user": input.login(),
            "user_id": uid,
        }

        CURRENT_USER_NAME.set(input.login())
        CURRENT_USER_ID.set(uid)
        in_logins.set(newValue)

    @render.ui
    def login_handler():
        if in_logins.get()["user"] == "":
            return fallback

        elif in_logins.get()["valid"]:
            is_logged_in.set(True)
            return ui.page_navbar(
                ui.nav_panel(
                    ui.h2("ventes"),
                ),
                ui.nav_panel(
                    ui.h2("génération d'indicateurs"),
                    ui.h1(f"Vous êtes connecté à {in_logins.get()['user']} !"),
                    ui.span(
                        "Entrez des requêtes SQL pour générer des indicateurs visuels"
                    ),
                    sql_query_input.sql_query_input("sql"),
                ),
                ui.nav_panel(
                    ui.h2("requêtes stockées"),
                    # page that displays database stored queries
                ),
                # set shared data to the currently connected user
            )

        else:
            return ui.page_fluid(
                ui.h1(f"Aucun utilisateur nommé {in_logins.get()['user']}"),
                ui.span("Veuillez vérifier l'ortographe de vos informations"),
            )

    @reactive.effect
    @reactive.event(input.disconnect)
    def log_out():
        is_logged_in.set(False)
        in_logins.set({"valid": False, "user": "", "user_id": -1})

    @reactive.effect
    def set_available_rel_df():
        #    print(available_tables(CURRENT_USER_ID.get(), DB))
        sale_order_joined = DB.read("""
        SELECT
            res_partner.name AS partner,
            sale_order.name AS sale_order,
            sale_order.create_date AS sale_order_create_date,
            sale_order.company_id AS sale_order_company_id,
            sale_order.user_id AS sale_order_user_id,
            sale_order.write_uid AS sale_order_write_uid,
            sale_order.write_date AS sale_order_write_date,
            sale_order.state,
            sale_order.amount_total,
            sale_order.amount_tax,
            sale_order.date_order,
            sale_order.require_payment,
            sale_order.require_signature

        FROM sale_order
        JOIN res_partner ON res_partner.id = sale_order.partner_id
        """)

        purchase_order_joined = DB.read(
            """
        SELECT
            purchase_order.name AS purchase_order_name,
            purchase_order.create_date AS purchase_order_create_date,
            purchase_order.company_id AS purchase_order_company_id,
            purchase_order.user_id AS purchase_order_user_id,
            purchase_order.write_uid AS purchase_order_write_uid,
            purchase_order.write_date AS purchase_order_write_date

        FROM purchase_order 
        JOIN res_partner 
        ON purchase_order.partner_id = res_partner.id
                                        
        
        """
        )

        res_company = DB.read("""SELECT * FROM res_company""")

        DB.read("""SELECT * FROM res_partner""")

        AVAILABLE_RELS.set(
            {
                "sale_order": sale_order_joined,
                "purchase_order": purchase_order_joined,
                "res_company": res_company,
            }
        )

    @render.ui
    def get_avail_df_name_list():
        if is_logged_in.get():
            return ui.input_radio_buttons(
                "df_radio_buttons",
                ui.h3("sélectionnez une table"),
                [name for name in AVAILABLE_RELS.get().keys()],
            )

    @reactive.effect
    @reactive.event(input.df_radio_buttons)
    def update_df_name_on_input():
        SELECTED_DATAFRAME_NAME.set(input.df_radio_buttons())


app = App(app_ui, app_server)
