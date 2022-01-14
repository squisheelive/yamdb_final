import csv
import os

from django.core.management.base import BaseCommand, CommandError


class SubCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='filename for csv file')

    def get_csv_file(self, filename):
        return os.path.join('data', filename)

    def clear_model(self):
        try:
            self.model_name.objects.all().delete()
        except Exception as e:
            raise CommandError(
                f'Error in clearing {self.model_name}: {str(e)}'
            )

    def insert_table_to_db(self, data):
        try:
            self.model_name.objects.create(
                id=data["id"],
                name=data["name"],
                slug=data["slug"],
            )
        except Exception as e:
            raise CommandError(
                f'Error in inserting {self.model_name}: {str(e)}'
            )

    def handle(self, *args, **kwargs):
        filename = kwargs['filename']
        self.stdout.write(self.style.SUCCESS(f'filename:{filename}'))
        file_path = self.get_csv_file(filename)
        line_count = 0
        try:
            with open(file_path, encoding="utf8") as csv_file:
                csv_reader = csv.DictReader(csv_file, delimiter=',')
                self.clear_model()
                for data in csv_reader:
                    self.insert_table_to_db(data)
                    line_count += 1
                    print(f'{line_count} added to {self.model_name}')
            self.stdout.write(
                self.style.SUCCESS(
                    f'{line_count} entries added to {self.model_name}'
                )
            )
        except FileNotFoundError:
            raise CommandError(f'File {file_path} does not exist')
