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
    config_file_path = files(override_package.replace("-", "_")) / "data/config.toml"
    try:
        with config_file_path.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        logger.warning(f"Unfound '{config_file_path}' file.")
    check_custom_settings(data)
    return data


def check_custom_settings(data):
    messages = []
    source = data.get("data_source")
    if source:
        name = source.get("name")
    else:
        messages = ["Missing 'data_source' in config file."]
    if name == "odoo":
        """"""
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
