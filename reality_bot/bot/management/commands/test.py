import asyncio
import time
from code.utils import country_objects

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    # async def handle(self, *args, **options):
    def handle(self, *args, **options):
        # country_object_checked = [
        #     '✅ ' + country_objects[i] for i in range(len(country_objects))
        # ] + ['Отменить внесение покупателя', 'Подтвердить выбор']
        # print(country_object_checked)

        # times = []
        # club_count = 2
        # item_count = 2
        # delay = 10
        # gypotetic_delay = (((club_count * item_count - 1) * delay) / 60)

        # if gypotetic_delay < 1:
        #     print(f'бот будет работать {gypotetic_delay * 60} сек')
        # else:
        #     print (f'бот будет работать {gypotetic_delay} мин')

        # fact_delay = 0
        # for x in range(club_count):
        #     for y in range(item_count):
        #         timestamp = time.time()
        #         print(timestamp)
        #         times.append(timestamp)
        #         if not (y == item_count - 1 and x == club_count - 1):
        #             await asyncio.sleep(delay)

        # fact_delay = times[-1] - times[0]

        # if (fact_delay / 60) < 1:
        #     print(f'бот работал {fact_delay} сек')
        # else:
        #     print (f'бот работал {fact_delay * 60} мин')

        phone_str = list('+79875821174')
        new_phone_str = ['x' if phone_str.index(x) > 5 else x for x in phone_str]
        new_phone_str = ''.join(new_phone_str)

        print(new_phone_str)


if __name__ == '__main__':
    Command().handle()
# asyncio.run(Command().handle())
