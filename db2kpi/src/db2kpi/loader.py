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
    def get_config_data(file):
        file_path = files(override_package.replace("-", "_")) / f"data/{file}.toml"
        try:
            with file_path.open("rb") as f:
                data = tomllib.load(f)
        except FileNotFoundError:
            logger.warning(f"Unfound '{file_path}.toml' file.")
        return data

    main_settings = get_config_data("config")
    check_custom_settings(main_settings)
    dsn = get_config_data("dsn")
    return main_settings


def check_custom_settings(data):
    messages = []
    source = data.get("data_source")
    if source:
        name = source.get("name")
    else:
        messages = ["Missing 'data_source' in config file."]
    if name == "odoo":
        """"""
        # TODO manage case where this is not Odoo
    else:
        messages.append("Missing 'name' in 'data_source' section in config file")
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
