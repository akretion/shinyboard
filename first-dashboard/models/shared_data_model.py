
import polars as pl
from shiny import ui
from datetime import datetime

class Shared_data_model:

    # MISC
    epoch = datetime(1970, 1, 1, 0, 0, 0, 0)

    def __init__(self):

        # DB DATA

        ## tables
        self.res_company: pl.DataFrame = pl.DataFrame()
        self.res_partner: pl.DataFrame = pl.DataFrame()

        ## structures from tables
        self.company_id_dict: dict = {}
        self.company_dict: dict = {}
        self.company_names: list = []


        # GLOBAL APP STATE

        ## Filter values
        self.selected_company_name: tuple[str, ...] = ("", "")
        self.selected_dates: list[datetime] = [Shared_data_model.epoch, Shared_data_model.epoch]

    # selected date
    def setSelectedDate(self, lower_bound: datetime, higher_bound: datetime):
        #self.selected_dates = [lower_bound, higher_bound]
        pass

    def getSelectedDate(self):
        return self.selected_dates
    
    def isSelectedDateAssigned(self):
        return self.selected_dates == Shared_data_model.epoch
    
    # selected company name
    def setSelectedCompany(self, company_names:tuple[str, ...]):
        self.selected_company_name = company_names
    
    def getSelectedCompany(self):
        return self.selected_company_name
    
    def isSelectedCompanyNameAssigned(self):
        return self.selected_company_name == ()

