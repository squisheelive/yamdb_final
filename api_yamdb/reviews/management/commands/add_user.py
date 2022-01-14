from django.core.management.base import CommandError
from reviews.models import User

from .add_model import SubCommand


class Command(SubCommand):
    help = 'add csv to User model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = User

    def insert_table_to_db(self, data):
        try:
            self.model_name.objects.create(
                id=data["id"],
                username=data["username"],
                email=data["email"],
                role=data["role"],
                bio=data["bio"],
                first_name=data["first_name"],
                last_name=data["last_name"]
            )
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name}: {str(e)}'
            )
