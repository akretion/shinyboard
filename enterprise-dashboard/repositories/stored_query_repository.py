from models.stored_query_model import StoredQuery
from repositories.simple_repository import SimpleRepository
from shared import QUERY_DB


class StoredQueryRepository(SimpleRepository):
    def __init__(self):
        QUERY_DB.create_tables([StoredQuery])

    def get_prog_instance(self):
        return StoredQuery()

    def get_all(self):
        return super().get_all(StoredQuery)

    def create(self, display_title: str, query: str, df_key_name: str):
        return super().create(
            StoredQuery,
            display_title=display_title,
            query=query,
            df_key_name=df_key_name,
        )
