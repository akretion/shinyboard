from abc import ABC, abstractmethod
from db2kpi.tool import _


class App(ABC):
    @abstractmethod
    def get_logins(self):
        pass

    @abstractmethod
    def get_organizations(self):
        pass
