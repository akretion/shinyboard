from __future__ import annotations
from pages.main import _

import tomllib
import logging
import gettext

import polars as pl
from required_package_utils import install_packages, get_installed_modules

from connect import Connect
from pages.shared import APP_CONSTANTS, Styles
from shiny import App
from shiny import Inputs
from shiny import Outputs
from shiny import reactive
from shiny import render
from shiny import Session
from shiny import ui

fr = gettext.translation(domain="base", localedir="i18n/locales", languages=["fr"])

fr.install()

_ = fr.gettext

app_css = Styles.get_instance().styles_dir_path / "app.css"

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.output_ui("credentials_input"),
        ui.hr(),
        ui.output_ui("get_avail_df_name_list"),
        ui.output_ui("user_filters"),
    ),
    ui.include_css(app_css),
    ui.output_ui("login_handler"),
)


def app_server(input: Inputs, output: Outputs, session: Session):
    # REFACTOR #1:
    #   sql_query_input.sql_query_server("sql")

    differentiator = reactive.value(0)
    package_ui_collection = reactive.value([])
    other_apps_collection = reactive.value([])

    def package_handler():
        """
        ## Summary
        - installs packages via required_package_utils.install_packages() **(blocking call)**
        - declares UI and puts it in a list of ready-to-unpack UI
        - calls servers.
        \n
        the function is called **only if the user successfully logs in** (in login_handler).
        """
        install_packages()
        module_dict = get_installed_modules()
        value = differentiator.get()
        ui_collection = []
        other_ui_collection = []
        for key in module_dict.keys():
            for mod in module_dict[f"{key}"]:
                mod.package_definitions.definitions["server"](
                    f"pckg{value}"
                )  # will be activated either way
                collection_reference = None
                match key:
                    case "highlighted":
                        collection_reference = ui_collection
                    case "hidden":
                        collection_reference = other_ui_collection
                    case _:
                        collection_reference = other_ui_collection
                collection_reference.append(
                    mod.package_definitions.definitions["ui"](f"pckg{value}")
                )
                differentiator.set(value + 1)
        package_ui_collection.set(ui_collection)
        other_apps_collection.set(other_ui_collection)

    translation = {
        _("Sales"): "sale_order",
        _("Purchases"): "purchase_order",
        _("Partners"): "res_partner",
    }
    # CONSTANTS
    DB = Connect("dsn1")
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
                ui.h3(f"{in_logins.get()['user']}"),
                ui.input_action_button("disconnect", _("Disconnect")),
            )
        else:
            return ui.div(
                ui.input_text(
                    "login",
                    ui.span(_("Login")),
                    placeholder=_("Lowercase identifier"),
                ),
                ui.input_password("password", ui.span(_("Password"))),
                ui.input_action_button("login_button", _("Log in")),
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
            ui.h1(_("Log in to an Odoo user")),
            ui.span(
                _("This will allow you to have access to appropriate indicators"),
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
        APP_CONSTANTS.CURRENT_USER_NAME.set(input.login())
        APP_CONSTANTS.CURRENT_USER_ID.set(uid)
        in_logins.set(newValue)
        
        if (
            not LOGINS.select("login")
            .filter(pl.col("login") == str(input.login()).strip())
            .is_empty()
        ):
            package_handler()

    @render.ui
    def login_handler():
        if in_logins.get()["user"] == "":
            return fallback
        elif in_logins.get()["valid"]:
            is_logged_in.set(True)
            return (
                ui.navset_bar(
                    *package_ui_collection.get(),
                    ui.nav_spacer(),
                    ui.nav_menu(
                        ui.h2(_("Apps")),
                        *other_apps_collection.get(),
                    ),
                    title="",
                ),
            )
        else:
            return ui.page_fluid(
                ui.h1(_(f"No user named {in_logins.get()['user']}")),
                ui.span(_("Please check entered informations.")),
            )

    @reactive.effect
    @reactive.event(input.disconnect)
    def log_out():
        is_logged_in.set(False)
        in_logins.set({"valid": False, "user": "", "user_id": -1})

    @reactive.effect
    def set_table_times():
        with open("config.toml", "rb") as CONFIG:
            CONFIG = tomllib.load(CONFIG)
            try:
                TABLE_TIME = CONFIG["TABLE_TIMES"]
                new_dict = {}
                for name, value in TABLE_TIME.items():
                    new_dict.update({name: value})
                APP_CONSTANTS.TABLE_TIME_COLUMNS.set(new_dict)
            except Exception as EX:
                logging.log(logging.ERROR, "ERROR : An exception occured (see below)")
                logging.log(
                    logging.ERROR,
                    f"""\n-----EXCEPTION-----\n
                            {EX}
                            \n-----END OF EXCEPTION-----""",
                )

                logging.log(
                    logging.WARN,
                    "The above exception is most likely due to config.toml "
                    "sections or variables being invalid.",
                )
                logging.log(
                    logging.WARN,
                    "Please check config.toml",
                )

    @reactive.effect
    def set_df_and_shared_values():
        # Columns [write_date] must be renamed, else it conflicts with joined tables.
        sale_order_joined = DB.read(
            """
        SELECT
            order_partner.name AS customer,
            order_user.name AS salesperson,
            sale_order.name AS sale_order,
            order_company.name AS company,
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

        JOIN res_company AS order_company
        ON sale_order.company_id = order_company.id
        """
        )
        purchase_order_joined = DB.read(
            """
        SELECT
            purchase_order.name AS purchase_order_name,
            purchase_company.name AS company,
            purchase_order.create_date AS purchase_order_create_date,
            purchase_order.company_id AS purchase_order_company_id,
            purchase_order.user_id AS purchase_order_user_id,
            purchase_order.write_uid AS purchase_order_write_uid,
            purchase_order.write_date AS purchase_order_write_date

        FROM purchase_order

        JOIN res_partner
        ON purchase_order.partner_id = res_partner.id

        JOIN res_company AS purchase_company
        ON purchase_order.company_id = purchase_company.id
        """,
        )

        res_company = DB.read("""SELECT * FROM res_company""")

        res_partner = DB.read("""SELECT * FROM res_partner""")

        APP_CONSTANTS.MIN_DB_TIME.set(
            sale_order_joined.sql(
                """SELECT MIN(date_order) AS min FROM self""",
            ).to_dict()["min"][0],
        )
        APP_CONSTANTS.MAX_DB_TIME.set(
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
                order_line_company.name AS company,
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

            JOIN res_company AS order_line_company
            ON sol.company_id = order_line_company.id
            """,
        )

        product_product = DB.read(
            """
            SELECT
                product_tmpl_id,
                default_code
            FROM product_product
            """
        )
        APP_CONSTANTS.OTHER_RELS.set(
            {
                "product_product": product_product,
                "sale_order_line": sale_order_line,
                "res_company": res_company,
            }
        )
        APP_CONSTANTS.AVAILABLE_RELS.set(
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
                ui.h4(_("Source")),
                [name for name in translation.keys()],
            )

    @render.ui
    def user_filters():
        if is_logged_in.get():
            res_companies = (
                APP_CONSTANTS.OTHER_RELS.get()["res_company"]
                .select("name")
                .to_series()
                .to_list()
            )

            if len(res_companies) < 1:
                return ui.span(
                    ui.input_slider(
                        "date_range",
                        ui.h4(_("Date")),
                        APP_CONSTANTS.MIN_DB_TIME.get(),
                        APP_CONSTANTS.MAX_DB_TIME.get(),
                        [
                            APP_CONSTANTS.MIN_DB_TIME.get(),
                            APP_CONSTANTS.MAX_DB_TIME.get(),
                        ],
                        time_format="%Y-%m-%d",
                        drag_range=True,
                    )
                )
            else:
                return ui.span(
                    ui.input_slider(
                        "date_range",
                        ui.h4(_("Date")),
                        APP_CONSTANTS.MIN_DB_TIME.get(),
                        APP_CONSTANTS.MAX_DB_TIME.get(),
                        [
                            APP_CONSTANTS.MIN_DB_TIME.get(),
                            APP_CONSTANTS.MAX_DB_TIME.get(),
                        ],
                        time_format="%Y-%m-%d",
                        drag_range=True,
                    ),
                    ui.input_selectize(
                        "company_name",
                        ui.h4(_("Company")),
                        res_companies,
                        selected=res_companies[0],
                        multiple=True,
                    ),
                )

    @reactive.effect
    @reactive.event(input.df_radio_buttons)
    def update_df_name_on_input():
        APP_CONSTANTS.SELECTED_DATAFRAME_NAME.set(translation[input.df_radio_buttons()])
        APP_CONSTANTS.FRENCH_NAME.set(input.df_radio_buttons())

    @reactive.effect
    @reactive.event(input.date_range)
    def date_range_handler():
        values = input.date_range()
        APP_CONSTANTS.SELECTED_PERIOD_LOW_BOUND.set(values[0])
        APP_CONSTANTS.SELECTED_PERIOD_HIGH_BOUND.set(values[1])

    @reactive.effect
    @reactive.event(input.company_name)
    def company_name_handler():
        APP_CONSTANTS.SELECTED_COMPANY_NAMES.set(input.company_name())


app = App(app_ui, app_server)
