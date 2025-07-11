from abc import ABC

from peewee import Model


class SimpleRepository(ABC):
    def get_prog_instance(self):
        return Model()

    def create(self, model: type[Model], **args):
        model.create(**args)

    def get_one(self, model: type[Model], id: int):
        return model.get_by_id(id)

    def get_all(self, model: type[Model]):
        return model.select()

    def save(self, instance: Model):
        instance.save()

    def delete(self, instance: Model):
        instance.delete_instance()

    def delete_by_id(self, model: type[Model], id: int):
        model.delete().where(model.id == id).execute()  # type: ignore[attr-defined]
