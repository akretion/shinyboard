from dataclasses import dataclass
import polars as pl
from db2kpi.tool import _
from db2kpi.app.app import App


@dataclass
class Odoo(App):
    name: str = "odoo"

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

    def get_tables(self):
        """Return list of tables according to:
        - config data source set manually
        - user grants
        """
        sql = f"""
        SELECT model, name FROM ir_model WHERE model IN {tuple(self.instance.models)}"""
        df = self.instance.conn.read(sql)
        # TODO manage exceptions
        df = df.with_columns(
            table=pl.col("model").str.replace(".", "_", literal=True, n=10)
        )
        print(df)
        return df.select("table").to_series().to_list()
