from __future__ import annotations

import configparser

import polars as pl
import sales_module.module
import sales_module.sales
import sql_query_input
import stored_queries_page
from connect import Connect
from shared import AVAILABLE_RELS
from shared import CURRENT_USER_ID
from shared import CURRENT_USER_NAME
from shared import FRENCH_NAME
from shared import MAX_DB_TIME
from shared import MIN_DB_TIME
from shared import OTHER_RELS
from shared import SELECTED_DATAFRAME_NAME
from shared import SELECTED_PERIOD_HIGH_BOUND
from shared import SELECTED_PERIOD_LOW_BOUND
from shared import TABLE_TIME_COLUMNS
from shiny import App
from shiny import Inputs
from shiny import Outputs
from shiny import reactive
from shiny import render
from shiny import Session
from shiny import ui


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("credentials_input"),
        ui.hr(),
        ui.output_ui("get_avail_df_name_list"),
        ui.output_ui("user_filters"),
    ),
    ui.output_ui("login_handler"),
)


def app_server(input: Inputs, output: Outputs, session: Session):
    sql_query_input.sql_query_server("sql")

    translation = {
        "Ventes": "sale_order",
        "Achat": "purchase_order",
        "Partenaires": "res_partner",
    }

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
                    "login",
                    ui.span("Login"),
                    placeholder="identifiant en minuscule",
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
            """,
        )

        # assignation des schémas dans shared
        available_tables_df.select("table_name").to_series().to_list()
        table_name_schema_dict = {}
        """
        for rel in table_list:
            if(rel == "ir.actions.report"):
                continue
            print(rel.replace(".", "_"))
            table_name_schema_dict[rel.replace(".", "_")] =
            DB.read(f"SELECT * FROM {rel.replace(".", "_")}").schema
        """

        print(table_name_schema_dict)

        # retour de l'UI

    # CENTER
    @render.ui
    def fallback():
        return ui.page_fluid(
            ui.h1("Connectez-vous à un utilisateur"),
            ui.span(
                "Cela vous permettra d'avoir accès à des indicateurs appropriés.",
            ),
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
                    sales_module.module.module_ui("sales_mod"),
                    sales_module.module.module_server("sales_mod"),
                ),
                ui.nav_panel(
                    ui.h2("génération d'indicateurs"),
                    ui.h1(f"Vous êtes connecté à {in_logins.get()['user']} !"),
                    ui.span(
                        "Entrez des requêtes SQL pour générer des indicateurs visuels",
                    ),
                    sql_query_input.sql_query_input("sql"),
                ),
                ui.nav_panel(
                    ui.h2("requêtes stockées"),
                    stored_queries_page.stored_queries_ui("stored"),
                    stored_queries_page.stored_queries_server("stored"),
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
    def set_table_times():
        conf_parser = configparser.ConfigParser()
        conf_parser.read("dbconfig.ini")

        try:
            TABLE_TIME = conf_parser["TABLE_TIMES"]
            new_dict = {}

            for name, value in TABLE_TIME.items():
                new_dict.update({name: value})

            TABLE_TIME_COLUMNS.set(new_dict)

        except Exception as EX:
            print(
                f"""an exception occured (see below)
                \n-----EXCEPTION-----\n
                {EX}\n-----END OF EXCEPTION-----""",
            )
            print(
                "The above exception is most likely due to dbconfig.ini "
                "sections or variables being invalid.",
            )
            print(
                "Please check dbconfig.ini",
            )

    @reactive.effect
    def set_df_and_shared_values():
        #    print(available_tables(CURRENT_USER_ID.get(), DB))

        # Columns [write_date] must be renamed, else it conflicts with joined tables.
        sale_order_joined = DB.read("""
        SELECT
            order_partner.name AS customer,
            order_user.name AS salesperson,
            sale_order.name AS sale_order,
            sale_order.company_id AS sale_order_company_id,
            sale_order.user_id AS sale_order_user_id,
            sale_order.write_uid AS write_uid,
            sale_order.invoice_status,
            sale_order.state,
            sale_order.amount_total,
            sale_order.amount_tax,
            sale_order.date_order::date,
            sale_order.create_date::date AS sale_order_create_date,
            sale_order.write_date::date AS sale_order_write_date,
            sale_order.require_payment,
            sale_order.require_signature,
            sale_order.id AS id

        FROM sale_order

        JOIN res_partner AS order_partner
        ON sale_order.partner_id = order_partner.id

        JOIN res_partner AS order_user
        ON sale_order.user_id = order_user.user_id
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

        """,
        )

        res_company = DB.read("""SELECT * FROM res_company""")

        res_partner = DB.read("""SELECT * FROM res_partner""")

        MIN_DB_TIME.set(
            sale_order_joined.sql(
                """SELECT MIN(date_order) AS min FROM self""",
            ).to_dict()["min"][0],
        )
        MAX_DB_TIME.set(
            sale_order_joined.sql(
                """SELECT MAX(date_order) + interval '1 day' AS max FROM self""",
            ).to_dict()["max"][0],
        )

        sale_order_line = DB.read(
            """
            SELECT
                sol.id,
                order_id,
                sol.name AS name,
                product_category.complete_name AS category,
                res_partner.name AS customer,
                product_uom_qty,
                price_unit,
                price_total,
                sol.create_date::date

            FROM sale_order_line sol

            JOIN res_partner
            ON res_partner.id = sol.order_partner_id

            JOIN product_product
            ON sol.product_id = product_product.id

            JOIN product_template
            ON product_product.product_tmpl_id = product_template.id

            JOIN product_category
            ON product_template.categ_id = product_category.id
            """,
        )

        product_product = DB.read(
            """
            SELECT
                id,
                default_code
            FROM product_product
            """
        )

        OTHER_RELS.set(
            {
                "product_product": product_product,
                "sale_order_line": sale_order_line,
                "res_company": res_company,
            }
        )

        AVAILABLE_RELS.set(
            {
                "sale_order": sale_order_joined,
                "purchase_order": purchase_order_joined,
                "res_partner": res_partner,
            },
        )

    @render.ui
    def get_avail_df_name_list():
        if is_logged_in.get():
            return ui.input_radio_buttons(
                "df_radio_buttons",
                ui.h3("sélectionnez une table"),
                [name for name in translation.keys()],
            )

    @render.ui
    def user_filters():
        if is_logged_in.get():
            return ui.span(
                ui.input_slider(
                    "date_range",
                    ui.span("sélection de date"),
                    MIN_DB_TIME.get(),
                    MAX_DB_TIME.get(),
                    [MIN_DB_TIME.get(), MAX_DB_TIME.get()],
                    time_format="%Y-%m-%d",
                    drag_range=True,
                ),
            )

    @reactive.effect
    @reactive.event(input.df_radio_buttons)
    def update_df_name_on_input():
        SELECTED_DATAFRAME_NAME.set(translation[input.df_radio_buttons()])
        FRENCH_NAME.set(input.df_radio_buttons())

    @reactive.effect
    @reactive.event(input.date_range)
    def date_range_handler():
        values = input.date_range()

        SELECTED_PERIOD_LOW_BOUND.set(values[0])
        SELECTED_PERIOD_HIGH_BOUND.set(values[1])


app = App(app_ui, app_server)
