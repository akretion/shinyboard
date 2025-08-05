import subprocess
import logging
import tomllib
from importlib.resources import files

logger = logging.getLogger(__name__)


def load():
    package = get_override_package()
    return get_custom_settings(package)


def get_override_package():
    with open("db2kpi/data/config.toml", "rb") as config:
        parsed = tomllib.load(config)
        return recursive_dict_get(parsed, ["override_package", "package"])


def get_custom_settings(override_package):
    def get_config_data(file, package=override_package):
        file_path = files(package.replace("-", "_")) / f"data/{file}.toml"
        data = False
        try:
            with file_path.open("rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            logger.critical(f"Unfound '{file_path}.toml' file.")
        return data

    main_settings = get_config_data("config")
    dsn = get_config_data("dsn")
    main_settings.update(dsn)
    check_custom_settings(main_settings)
    name = main_settings["data_source"]["name"]
    if name == "odoo":
        odoo_like = get_config_data("odoo-like-db", "db2kpi")
        main_settings.update({"odoo": odoo_like})
    return main_settings


def check_custom_settings(data):
    messages = []
    source = data.get("data_source")
    if not source:
        messages = ["Missing 'data_source' in config.toml file."]
    name = source.get("name")
    if not name:
        messages.append("Missing 'name' in 'data_source' section in config.toml file")
        if name == "odoo":
            """"""
            # TODO manage case where this is not Odoo
    dsn = data.get("dsn")
    if not dsn or not dsn.get("main"):
        messages.append("Missing 'dsn.main' section in dsn.toml file")
    if messages:
        logger.error(f"Custom settings check failed: {', '.join(messages)}")


def recursive_dict_get(my_dict, keys):
    tree = my_dict.copy()
    for key in keys:
        value = tree.get(key)
        if value:
            tree = tree[key]
        else:
            return False
    return tree
