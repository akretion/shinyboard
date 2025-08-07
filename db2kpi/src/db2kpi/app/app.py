"""App class represent any kind of application.
It is an abstract class that defines the basic methods
"""

from dataclasses import dataclass
from abc import ABC, abstractmethod
from db2kpi import db_connect
from db2kpi.tool import _


@dataclass
class App(ABC):
    name: str = None
    # instance of the class which created App object
    instance: object = None
    data: dict = None
    conn: db_connect.DbConnect = None
    logins: dict = None

    @abstractmethod
    def get_logins(self):
        pass

    @abstractmethod
    def get_organizations(self):
        pass

    @abstractmethod
    def get_tables(self):
        pass
