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


def main():
    data = loader.load()
    inst = Instance(models=data["data_source"]["models"])
    return inst


instance = main()
