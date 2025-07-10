

# ShinyBoard

## FR
## Prérequis
- une base de données Postgresql suivant le schéma Odoo 18 et les modules sales et purchase (sinon, installez [odoo]('https://github.com/odoo/odoo'))

## Lancer l'application 🚀
```bash
# après avoir cloné le projet sur votre machine
python -m venv your-env
cp -r shinyboard your-env
cd your-env && source bin/activate
cd shinyboard/enterprise-dashboard && shiny run app.py --launch-browser
```

## Utiliser l'application

### Base de données utilisée ou personnalisée
> **ATTENTION**
> Cette application est actuellement en phase de développement et ne marche pas sans les modules sales_management, stock, purchase (achat). Cependant si vous avez une base
> de données Odoo fonctionnelle :
- modifiez le fichier enterprise_dashboard/.env pour que
    - l'URL derrière 'dsn1=' corresponde au DSN de votre base de données Odoo
    - l'URL derrière 'dsn2=' corresponde au DSN de la seconde base 'query_db'
 il sera ensuite possible de se connecter à l'application en utilisant un login présent
> dans votre base de données sans spécifier le mot de passe et en cliquand sur "Se connecter"

## Base de données par défaut
> Cela marche pareil que pour une base de données personnalisée ou utilisée, à l'exception du fait que vous devez utiliser
> des identifiants par défaut ('demo' ou 'admin')


## EN
## Requirements
- a Postgresql Database that has an Odoo 18 Schema with sales and purchase modules (if you don't have it, install [odoo]('https://github.com/odoo/odoo'))

## Launching the app 🚀
```bash
# after you cloned this project on your device
python -m venv your-env
cp -r shinyboard your-env
cd your-env && source bin/activate
cd shinyboard/enterprise-dashboard && shiny run app.py --launch-browser
```

## Using the app

### Used, customized database
> **WARNING**
> this app is still currently in its development phase, and isn't working without the sales and purchase modules. However, if you have that, you can log into the app typing a login in your database while omitting the password and clicking "Se connecter" to have access to the full app.

### Default database
> Will work in the same way as for a customized DB, except you need use default logins ('demo' or 'admin').
