from dataclasses import dataclass
from shiny import reactive
from datetime import datetime


EPOCH = datetime(1970, 1, 1, 0, 0, 0)


@dataclass
class Elements:

    organizations: reactive.value[list[str]] = reactive.value([""])
    # organizations such as companies or any associations
    min_date: reactive.value[datetime] = reactive.value(EPOCH)
    # Minimum time found in database.
    max_date: reactive.value[datetime] = reactive.value(EPOCH)
    # Maximum time found in database.
    selected_max_date: reactive.value[datetime] = reactive.value(EPOCH)
    # The rightmost value of the date_range.
    selected_min_date: reactive.value[datetime] = reactive.value(EPOCH)
    # The leftmost value of the data_range.


elements = Elements()
