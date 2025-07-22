"""TODO
- use adhoc exception class

"""

import os
import connectorx as cx
import polars as pl
from dotenv import load_dotenv

import logging

logger = logging.getLogger(__name__)
load_dotenv()


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
        dsns = os.getenv("SHINYDSN")
        if not dsns:
            print(f"dsns : {dsns}")
            raise Exception("No DSN environment variable found.")
        print(f"DSNS : {dsns}")

        # My code : Logic for nested env var declarations
        ## list in format [ [DSN, URL], [DSN, URL], ... ]
        dsns_var_names = [
            var_name.split("=") for var_name in dsns.replace("SHINYDSN=", "").split("|")
        ]
        ## will contain pairs like ["DSN"] = URL
        dsns_var_dict = {}
        ## populate dict from [ [DSN, URL], [DSN, URL], ... ]
        for dsns_var_pair in dsns_var_names:
            dsns_var_dict[dsns_var_pair[0].strip()] = dsns_var_pair[1]
        # what tf am i supposed to do from there...
        # code that was given to me
        # for dsn_env in os.getenv("SHINYDSN").split("|"):
        #     dsn_env = dsn_env.strip()
        #     if not dsn_env or "=" not in dsn_env:
        #         continue
        #     dsn_name, dsn_url = dsn.split("=", 1)
        #     dsn[dsn_name.strip()] = dsn_url.strip()
        #     logger.info(f"DSN {dsn_name} available")

        return dsns_var_dict

    def _get_conn(self, dsn: str):
        try:
            cx.read_sql(conn=dsn, query="SELECT 1", return_type="polars")
        except Exception as e:
            logging.log(logging.ERROR, f"Failed to connect to {dsn}: {e}")
            raise (e)
        self.conn = dsn

    def read(self, query: str, return_type="polars") -> pl.DataFrame:
        return cx.read_sql(conn=self.conn, return_type=return_type, query=query)
