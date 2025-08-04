"""
TODO
- base style
- keep instance
"""

import gettext
from dataclasses import dataclass
from db2kpi import loader

_ = gettext.gettext


@dataclass
class Instance:
    models: list
    name: str


def main():
    data = loader.load()
    source = data["data_source"]
    inst = Instance(name=source["name"], models=source["models"])
    return inst


instance = main()
