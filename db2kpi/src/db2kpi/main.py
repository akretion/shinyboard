"""
TODO
- filters: dates, companies
"""

from dataclasses import dataclass
from db2kpi import config, db_connect
from db2kpi.app.odoo import Odoo
from db2kpi.tool import _


@dataclass
class Instance:
    name: str
    # Data Source Name, usually a connection string
    dsn: str
    # List of models or table to be used
    models: list
    conn: db_connect.DbConnect = False
    # Odoo metadata for the particular case where it's an Odoo database
    kind: object = False

    def connect(self):
        if not self.conn:
            conn = db_connect.DbConnect(self.dsn)
            if conn:
                self.conn = conn
        return self.conn

    def plug_app(self, data):
        if self.name == "odoo":
            self.kind = get_type(self.name)(conn=self.conn, data=data.get("odoo"))


def main():
    data = config.load()
    source = data["data_source"]
    dsn = data["dsn"]["main"]
    inst = Instance(name=source["name"], dsn=dsn, models=source["models"])
    inst.connect()
    inst.plug_app(data)
    inst.kind.get_logins()
    return inst


def get_type(type_):
    match type_:
        case "odoo":
            return Odoo
        # case "sage100":
        #     return Sage100
        # case "business_central":
        #     return BusinessCentral
        case _:
            raise ValueError(f"Unsupported type: {type_}")


instance = main()
