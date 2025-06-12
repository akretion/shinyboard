

# ShinyBoard

## Prérequis
> ollama 3.2(+) installé localement

## Lancer l'application (stats, sans login)
```bash
# après avoir créé un venv, et avoir installé avec requirements.txt
cd first-dashboard
shiny run app.py
```

## Avec login
```bash
cd first-dashboard
uvicorn app:auth_app
```
> uvicorn permet de lancer une application Starlette
> Starlette offre une mécanique de routage entre plusieurs applications (Starlette ou Shiny Python, qui utilise Starlette)

