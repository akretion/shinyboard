import os
import connectorx as cx
import logging

logger = logging.getLogger(__name__)

dsns = os.getenv("DSN")


def get_data_sources():
    dsn = {}
    for envdsn in dsns.split("|"):
        envdsn = envdsn.strip()
        if not envdsn or ":" not in envdsn:
            continue
        dsn_name, dsn_url = dsn.split(":", 1)
        dsn[dsn_name.strip()] = dsn_url.strip()
        logger.info(f"DSN {dsn_name} available")
    return dsn


def get_data_source(mydsn):
    dsn_url = get_data_sources.get(mydsn)
    try:
        connection = cx.read_sql(conn=dsn_url, query="SELECT 1", return_type="polars")
        # connection.close()
    except Exception as e:
        print(f"Failed to connect to {dsn_url}: {e}")
    return connection


def _read_sql(self, query, return_type="polars"):
    return self.db_conf_id._read_sql(query, return_type=return_type)
