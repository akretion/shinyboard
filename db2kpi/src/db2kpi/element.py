from dataclasses import dataclass
from shiny import reactive


@dataclass
class Elements:

    organizations: reactive.value[list[str]] = reactive.value([""])


elements = Elements()
