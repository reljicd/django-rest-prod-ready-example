import csv
from datetime import datetime

from django.core.management import BaseCommand
from django.utils.timezone import make_aware

from clicks.models import Click


class Command(BaseCommand):
    help = 'Load the clicks from csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        path = kwargs['path']
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['id']:
                    Click.objects.get_or_create(
                        campaign=row['campaign'],
                        timestamp=make_aware(datetime.utcfromtimestamp(
                            int(row['timestamp']))),
                    )
