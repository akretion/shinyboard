from pages.shared import DB_CONF
from peewee import AutoField, CharField, Model  # type: ignore[all]


class StoredQuery(Model):
    id = AutoField()
    display_title = CharField()
    query = CharField()
    df_key_name = CharField()

    class Meta:
        database = DB_CONF
        table_name = "query"
