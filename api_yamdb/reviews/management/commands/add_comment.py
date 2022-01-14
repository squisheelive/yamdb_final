from django.core.management.base import CommandError

from reviews.models import Comment, Review, User
from .add_model import SubCommand


class Command(SubCommand):
    help = 'add csv to Comment model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Comment

    def insert_table_to_db(self, data):
        try:
            review = Review.objects.get(pk=data["review_id"])
            author = User.objects.get(pk=data["author"])
            self.model_name.objects.create(
                id=data["id"],
                review=review,
                author=author,
                pub_date=data["pub_date"],
                text=data["text"]
            )
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name}: {str(e)}'
            )
