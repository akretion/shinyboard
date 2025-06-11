from shiny import App, reactive, render, ui
from shiny import Inputs, Outputs, Session

from connect import Connect

import polars as pl

import chat


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(
            "login", ui.span("Login"), placeholder="identifiant en minuscule"
        ),
        ui.input_password("password", ui.span("Mot de passe")),
    ),
    ui.output_ui("appropriate_ui"),
    ui.input_action_button("login_button", "Se connecter"),
)


def app_server(input: Inputs, output: Outputs, session: Session):
    chat.chat_module_server("chat_module")

    db = Connect("dsn1")
    logins = db.read("SELECT login FROM res_users")

    in_logins = reactive.value(False)

    @render.ui
    def fallback():
        return ui.page_fluid(
            ui.h1("Connectez-vous à un utilisateur"),
            ui.span("Cela vous permettra d'avoir accès à des indicateurs appropriés."),
        )

    @reactive.effect
    @reactive.event(input.login_button)
    def login():
        print(f"BEFORE : {in_logins.get()}")
        newValue = (
            not logins.select("login")
            .filter(pl.col("login") == str(input.login()).strip())
            .is_empty()
        )
        print(f"newValue : {newValue}")
        in_logins.set(newValue)
        print(f"AFTER : {in_logins.get()}")

    @render.ui
    def appropriate_ui():
        if input.login() == "":
            print("FALLBACK RETURNED")
            return fallback

        elif in_logins.get():
            return ui.page_fluid(
                ui.h1(f"vous êtes connecté à {input.login()}"),
                # set shared data to the currently connected user
                chat.chat_module_ui("chat_module"),
            )

        else:
            return ui.page_fluid(
                ui.h1(f"Aucun utilisateur nommé {input.login()}"),
                ui.span("Veuillez vérifier l'ortograhpe de vos informations"),
            )


app = App(app_ui, app_server)
