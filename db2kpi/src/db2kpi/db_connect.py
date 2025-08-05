import os
import connectorx as cx
import polars as pl
import logging

logger = logging.getLogger(__name__)


class DbConnect:

    conn = False

    def __init__(self, dsn):
        self._get_conn(dsn)

    def _get_conn(self, dsn: str):
        try:
            cx.read_sql(conn=dsn, query="SELECT 1", return_type="polars")
        except Exception as e:
            logging.log(logging.ERROR, f"Failed to connect to {dsn}: {e}")
            raise (e)
        self.conn = dsn

    def read_pl(self, query: str) -> pl.DataFrame:
        return cx.read_sql(conn=self.conn, return_type="polars", query=query)

    def read_sql(self, query: str):
        return cx.read_sql(conn=self.conn, query=query)
