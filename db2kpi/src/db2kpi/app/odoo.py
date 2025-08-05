from dataclasses import dataclass
from db2kpi import db_connect
from db2kpi.tool import _
from db2kpi.app.app import App


@dataclass
class Odoo(App):
    name: str = "odoo"
    data: dict = False
    conn: db_connect.DbConnect = False
    logins: dict = False

    def get_logins(self):
        ignored = tuple(self.data.get("misc").get("ignored_logins"))
        query = f"SELECT id, login FROM res_users WHERE login NOT IN {ignored}"
        self.logins = self.conn.read(query)

    def get_organizations(self):
        query = """
        SELECT c.id, p.name FROM res_company c 
            LEFT JOIN res_partner p ON p.id = c.partner_id
        ORDER BY c.id DESC
        """
        return self.conn.read(query, out="list")
