from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = 'Export to yaml'



    def handle(self, *args, **options):
        print("yaml export started")