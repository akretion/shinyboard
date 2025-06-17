from pathlib import Path

from shiny import reactive

import polars as pl

app_dir = Path(__file__).parent

sch_list: list[pl.Schema] = []

df_schemas = reactive.value(sch_list)
