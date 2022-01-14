from django.core.management.base import CommandError
from reviews.models import Review, Title, User

from .add_model import SubCommand


class Command(SubCommand):
    help = 'add csv to Review model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Review

    def insert_table_to_db(self, data):
        try:
            title = Title.objects.get(pk=data["title_id"])
            print(title)
            author = User.objects.get(pk=data["author"])
            self.model_name.objects.create(
                id=data["id"],
                title=title,
                author=author,
                pub_date=data["pub_date"],
                text=data["text"],
                score=data["score"]

            )
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name}: {str(e)}'
            )
