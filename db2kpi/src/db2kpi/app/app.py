"""App class represent any kind of application.
It is an abstract class that defines the basic methods
"""

from abc import ABC, abstractmethod
from db2kpi.db_connect import DbConnect
from db2kpi.tool import _


class App(ABC):

    name: str = None
    data: dict = None
    conn: DbConnect = None
    logins: dict = None
    dsn: str = None
    # List of models or table to be used
    domain: list

    def __init__(self, data):
        self.name = data["data_source"]["name"]
        self.dsn = data["dsn"]["main"]
        self.data = data
        self.domain = data["domain"].keys()

    def connect(self):
        if not self.conn:
            conn = DbConnect(self.dsn)
            if conn:
                self.conn = conn
        return self.conn

    @abstractmethod
    def get_organizations(self):
        pass

    @abstractmethod
    def get_tables(self):
        pass
