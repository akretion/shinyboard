from peewee import AutoField, CharField, Model  # type: ignore[all]
from pages.shared import APP_CONFIG


class StoredQuery(Model):
    id = AutoField()
    display_title = CharField()
    query = CharField()
    df_key_name = CharField()

    class Meta:
        database = APP_CONFIG.DB_CONF
        table_name = "query"
