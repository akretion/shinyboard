import os
import connectorx as cx
import logging

logger = logging.getLogger(__name__)

""" TODO
- use adhoc exception class

"""



class Connect:
    """my = Connect("mydsn")
    my.read("SELECT name FROM mytable")

    """

    conn = False

    def __init__(self, dsn):
        dsns = self._get_data_sources()
        if dsn not in dsns:
            raise Exception("DSN not found in available data sources.")
        self._get_conn(dsns[dsn])

    def _get_data_sources(self):
        dsn = {}
        dsns = os.getenv("DSN")
        if not dsns:
            raise Exception("No DSN environment variable found.")
        for dsn_env in os.getenv("DSN").split("|"):
            dsn_env = dsn_env.strip()
            if not dsn_env or "=" not in dsn_env:
                continue
            dsn_name, dsn_url = dsn.split("=", 1)
            dsn[dsn_name.strip()] = dsn_url.strip()
            logger.info(f"DSN {dsn_name} available")
        return dsn

    def _get_conn(self, dsn):
        try:
            connection = cx.read_sql(conn=dsn, query="SELECT 1", return_type="polars")
        except Exception as e:
            print(f"Failed to connect to {dsn}: {e}")
            raise (e)
        self.conn = connection

    def read(self, query, return_type="polars"):
        return cx.read_sql(self.conn, query, return_type=return_type)
