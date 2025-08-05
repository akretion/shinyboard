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

    def read(self, query: str, out: str = None) -> pl.DataFrame:
        output = cx.read_sql(conn=self.conn, query=query, return_type="polars")
        if output.is_empty():
            logger.info("No data returned for query: %s", query)
        if out == "list":
            return output.to_dicts()
        return output
