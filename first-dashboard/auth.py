from shiny import App, ui

auth_ui = ui.page_fluid(
    ui.h1("Shinyboard"),
    ui.h2("Veuillez vous authentifier pour accéder à vôtre application."),
    ui.input_text("res_users_login", ui.span("Login"), placeholder="login"),
)


def auth_server(input, output, session):
    pass


auth_app = App(auth_ui, auth_server)
