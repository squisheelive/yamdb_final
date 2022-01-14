from reviews.models import Genre

from .add_model import SubCommand


class Command(SubCommand):
    help = 'add csv to Genre model'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_name = Genre
