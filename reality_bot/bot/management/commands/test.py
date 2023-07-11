from code.utils import country_objects
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        country_object_checked = [
            '✅ ' + country_objects[i] for i in range(len(country_objects))
        ] + ['Отменить внесение покупателя', 'Подтвердить выбор']
        print(country_object_checked)

if __name__ == '__main__':
    Command.handle()
