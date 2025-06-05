import polars as pl

class Hr_data_model:
    def __init__(self) -> None:
        self.hr_employee_skill: pl.DataFrame = pl.DataFrame()
        self.hr_skill: pl.DataFrame = pl.DataFrame()
        self.hr_employee_named_skill: pl.DataFrame = pl.DataFrame()
        self.skill_series: pl.DataFrame = pl.DataFrame()
        self.hr_skill_renamed: pl.DataFrame = pl.DataFrame()