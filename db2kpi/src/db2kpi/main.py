"""
TODO
- sources:
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
    domain: list
    conn: db_connect.DbConnect = False
    # App metadata are stored here according to the kind of app
    kind: object = False

    def connect(self):
        if not self.conn:
            conn = db_connect.DbConnect(self.dsn)
            if conn:
                self.conn = conn
        return self.conn

    def plug_application(self, data):
        if self.name == "odoo":
            self.kind = get_kind_object(self.name)(
                conn=self.conn, data=data.get("odoo"), instance=self
            )


def main():
    data = config.load()
    source = data["data_source"]
    dsn = data["dsn"]["main"]
    inst = Instance(name=source["name"], dsn=dsn, domain=data["domain"].keys())
    inst.connect()
    inst.plug_application(data)
    inst.kind.get_logins()
    # inst.kind.get_tables()
    return inst


def get_kind_object(kind):
    match kind:
        case "odoo":
            return Odoo
        # case "sage100":
        #     return Sage100
        # case "business_central":
        #     return BusinessCentral
        case _:
            raise ValueError(f"Unsupported type: {kind}")


instance = main()
