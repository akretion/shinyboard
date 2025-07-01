from peewee import AutoField, CharField, Model  # type: ignore[all]
from shared import QUERY_DB


class StoredQuery(Model):
    id = AutoField()
    display_title = CharField()
    query = CharField()
    df_key_name = CharField()

    class Meta:
        database = QUERY_DB
        table_name = "storedquery"
