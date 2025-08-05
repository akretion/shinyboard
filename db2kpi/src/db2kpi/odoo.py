from dataclasses import dataclass
from db2kpi import db_connect
from db2kpi.tool import _


@dataclass
class Odoo:
    name: str = "odoo"
    data: dict = False
    conn: db_connect.DbConnect = False
    logins: dict = False

    def get_logins(self):
        ignored = tuple(self.data.get("misc").get("ignored_logins"))
        query = f"SELECT id, login FROM res_users WHERE login NOT IN {ignored}"
        self.logins = self.conn.read_sql(query)
        print(self.logins)
