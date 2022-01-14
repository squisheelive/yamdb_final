from django.core.management.base import CommandError
from reviews.models import Category, Title

from .add_model import SubCommand


class Command(SubCommand):
    help = 'add csv to Title model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Title

    def insert_table_to_db(self, data):
        try:
            category = Category.objects.get(pk=data["category"])
            self.model_name.objects.create(
                id=data["id"],
                name=data["name"],
                year=data["year"],
                category=category
            )
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name}: {str(e)}'
            )
