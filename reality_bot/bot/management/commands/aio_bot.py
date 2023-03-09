import asyncio
import logging
import operator
import os
import re
from code.answer_messages import message_texts
from code.db_worker import DB_Worker
from code.states import (ApartmentSearch, ArchiveObjects, Buyer,
                         CallbackOnStart, CeoRegistration, DeleteBuyer,
                         DeleteCallbackStates, HouseCallbackStates,
                         HouseSearch, LandCallbackStates, LandSearch,
                         ObjForBuyer, PriceEditCallbackStates, Registration,
                         RoomCallbackStates, RoomSearch,
                         TownHouseCallbackStates, TownHouseSearch,
                         WorkersBuyers, WorkersObjects)
from code.utils import (Output, checked_apartment_category, keyboards,
                        object_city_microregions_for_checking,
                        object_country_microregions_for_checking,
                        object_microregions)
from functools import reduce

import django
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import (CallbackQuery, ContentType, InputFile, MediaGroup,
                           Message)
from bot.models import Apartment, Archive
from bot.models import Buyer as BuyerDB
from bot.models import (Ceo, CodeWord, House, Individuals, Land, Rieltors,
                        Room, Subscriptors, TownHouse)
from decouple import config
from django.core.management.base import BaseCommand
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rest.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
django.setup()

DB_NAME = config('DB_NAME')
POSTGRES_USER = config('POSTGRES_USER')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD')
DB_HOST = config('DB_HOST')
DB_PORT = config('DB_PORT')
TELEGRAM_CHANNEL_ID = config('TELEGRAM_CHANNEL_ID')

bot = Bot(token=config('TELEGRAM_TOKEN'))

dp = Dispatcher(bot, storage=MemoryStorage())


class Command(BaseCommand):
    def handle(self, *args, **options):
        executor.start_polling(dp, skip_updates=True)
# -----------------------------------------------------------------------------
# --------------------старт----------------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer(message_texts.on.get('start'), parse_mode='Markdown')
# -----------------------------------------------------------------------------
# --------------------РЕГИСТРАЦИЯ----------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['registration'])
async def entering_name(message: Message, state: FSMContext):
    if message.from_user.username is None:
        await message.answer(
            'У вас в настройках профиля не указан username (имя пользователя).'
            + ' Откройте настройки telegram и заполните это поле.'
            + ' После этого заново нажмите на команду 👉 /registration'
        )
        await state.finish()
    else:
        if Rieltors.objects.filter(user_id=message.from_user.id).exists():
            await message.answer(
                '❗ Вы уже зарегистрированы в системе'
            )
            await state.finish()
        else:
            await message.answer(
                '✏ Давай знакомиться! *Как тебя зовут?*\n'
                + '*Напиши.* Подойдёт любой формат: Имя, Имя Отчество, Имя Фамилия\n\n'
                + '🙅‍♂️ Для отмены напиши "Стоп"',
                parse_mode='Markdown'
            )
            await Registration.step1.set()


@dp.message_handler(state=Registration.step1)
async def agency_choice(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(
            user_id=message.from_user.id,
            rieltor_name=message.text,
            username=message.from_user.username
        )
        await message.answer(
            'В каком агентстве ты работаешь?',
            reply_markup=keyboards.agency_choice_kb()
        )
        await Registration.step2.set()


@dp.callback_query_handler(state=Registration.step2)
async def phone_number_entering(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(agency_name=callback.data)

        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text_for_editing'),
            parse_mode='Markdown'
        )
        await Registration.step3.set()


@dp.message_handler(state=Registration.step3)
async def registration_finish(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:

        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(phone_number='+7' + message.text[1:])
            data = await state.get_data()
            if not DB_Worker.rieltor_to_db(data):
                await message.answer(
                    message_texts.on.get('sorry_about_error')
                )
            else:
                rieltor = Rieltors.objects.get(user_id=message.from_user.id)
                await bot.send_sticker(
                    chat_id=message.from_user.id,
                    sticker="CAACAgIAAxkBAAEHTKhjxjrcni0OCgaOirMYTAeiEYMy1AACPR4AAg5kyEnoLgEu8rg2Oy0E"
                )
                await message.answer(
                    f'OK, {rieltor.name}, всё готово! Можешь начинать '
                    + 'работу с нажатия на кнопку "Меню"'
                )

                ceo = Ceo.objects.filter(agency_name=rieltor.agency_name)
                if ceo.exists():
                    for item in ceo:
                        await bot.send_message(
                            chat_id=item.user_id,
                            text='🌱 *К вам добавился пользователь:*\n'
                            + f'username в телеграм: *@{message.from_user.username}*,\n'
                            + f'имя в телеграм: *{message.from_user.first_name}*,\n'
                            + f'имя в системе: *{rieltor.name}*,\n'
                            + f'номер телефона в системе: *{rieltor.phone_number}*',
                            parse_mode='Markdown'
                        )
            await state.finish()
        else:
            await message.answer(
                message_texts.phone_number_entering_error(
                    phone_number=message.text
                ),
                parse_mode='Markdown'
            )
            logging.error(
                f'Ошибка при вводе номера телефона {message.text}.'
            )
            await Registration.step3.set()
# -----------------------------------------------------------------------------
# --------------------About----------------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['about'])
async def about(message: Message):
    await message.answer(
        '\n'.join(message_texts.on.get('about')),
        parse_mode='markdown'
    )
# -----------------------------------------------------------------------------
# --------------------------СТАТИСТИКА-----------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['getstatistics'])
async def get_statistics(message: Message):
    await message.answer(message_texts.on.get('statistics'))
# -----------------------------------------------------------------------------
# -----------------------ПОИСК ОБЪЕКТА-----------------------------------------
# -----------------------------------------------------------------------------


"""
Раскоментить для платной подписки и нижнюю удалить
Реагирует на частных риелторов
"""
# @dp.message_handler(commands=['searchobjects'])
# async def search_objects(message: Message):
#     """Ответ на кнопку просмотра базы"""

#     individuals = [int(', '.join(
#         user
#     )) for user in Individuals.objects.all().values_list('user_id')]
#     print(individuals)
#     if message.from_id in individuals:
#         await message.answer('Просмотр объектов доступно только по '
#               + 'платной подписке на бот. Свяжитесь с @davletelvir')
#     else:
#         await message.answer(
#             '✏ Выбери один из двух форматов просмотра объектов:\n'
#             + '*Каскадная* - все объекты вываливаются в чат, *с фото*.\n'
#             + '*Карусель* - лаконичное перелистывание, но *без фото*.',
#             reply_markup=keyboards.carousel_or_cascade_keyboard(),
#             parse_mode='Markdown'
#         )

# !!!Закоменьтить перед внедрением платной подписки
# 👇👇👇👇👇


@dp.message_handler(commands=['searchobjects'])
async def search_objects(message: Message):
    DB_Worker.command_counting()
    # await code.send_photo(
    #     chat_id=message.chat.id,
    #     photo=photo,
    #     caption='✏ Выбери один из двух форматов просмотра объектов:\n'
    #             + '*Каскадная* - все объекты "вываливаются" в чат, *с фото*.\n'
    #             + '*Карусель* - лаконичное перелистывание, но *без фото*.',
    #             reply_markup=keyboards.carousel_or_cascade_keyboard(),
    #             parse_mode='Markdown'
    #     )
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        await message.answer(
            '✏ Выбери один из двух форматов просмотра объектов:\n'
            + '*Каскадная* - все объекты "вываливаются" в чат, *с фото*.\n'
            + '*Карусель* - лаконичное перелистывание, но *без фото*.',
            reply_markup=keyboards.carousel_or_cascade_keyboard(),
            parse_mode='Markdown'
        )


@dp.callback_query_handler(text=['cascade', 'carousel'])
async def cascade(callback: CallbackQuery, state: FSMContext):
    """Ответ на кнопку просмотра базы в каскадной форме"""
    await state.reset_data()
    await state.update_data(view_form=callback.data)
    await callback.message.answer(
        '✏ Выбери категорию объектов для поиска',
        reply_markup=keyboards.get_category_keyboard()
    )


"""
Раскоментить для платной подписки и нижнюю удалить
реагирует на подписчиков
"""
# @dp.message_handler(commands=['addobject'])
# async def add_object(message: Message):
#     """Ответ на кнопку обавления объекта"""

#     subscriptors = [int(', '.join(
#         user
#     )) for user in Subscriptors.objects.all().values_list('user_id')]

#     if message.from_id not in subscriptors:
#         await message.answer('Добавление объектов доступно только'
#       + ' по платной подписке на бот. Свяжитесь с @davletelvir')
#     else:
#         await message.answer(
#                 '✏ Что желаешь добавить?',
#                 reply_markup=keyboards.add_category_keyboard()
#             )

# !!!Закоменьтить перед внедрением платной подписки
# 👇👇👇👇👇
# -----------------------------------------------------------------------------
# --------------------ДОБАВЛЕНИЕ ОБЪЕКТА----------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['addobject'])
async def add_object(message: Message):
    DB_Worker.command_counting()

    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            'Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        await message.answer(
                '✏ Что желаешь добавить?',
                reply_markup=keyboards.add_category_keyboard()
            )
# -----------------------------------------------------------------------------
# --------------------ПОИСК ОБЪЕКТА--------------------------------------------
# -----------------------------------------------------------------------------


@dp.callback_query_handler(text='Комнаты')
async def rooms_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✏ До какой цены вывести объекты?')
    await RoomSearch.step2.set()


@dp.message_handler(state=RoomSearch.step2)
async def rooms(message: Message, state: FSMContext):
    """
    Ответ на кнопку поиска по комнатам
    ПАГИНАЦИЮ комментами разжевал в участках ниже если чо
    """
    try:
        query_set = Room.objects.filter(
            price__lte=int(message.text)
        ).order_by('-pub_date')
        pages_count = query_set.count()
        data = await state.get_data()

        if query_set.exists():
            await state.finish()
            await message.answer(
                f'✳ Вот, что я нашёл по *комнатам* ({pages_count}):',
                parse_mode='Markdown'
            )

            """Вид отображения каскадом"""
            if data.get('view_form') == 'cascade':

                for item in query_set:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.room_search_result_text(item=item),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await message.answer_media_group(media=album)

            """Вид отображения каруселью"""
            if data.get('view_form') == 'carousel':
                if query_set:
                    page = 1
                    await message.answer(
                        message_texts.room_search_result_text(
                            item=query_set[page - 1]
                        ),
                        reply_markup=keyboards.pagination_keyboard(
                            page=page,
                            pages=pages_count,
                            category='room'
                        ),
                        parse_mode='Markdown'
                    )
                    await state.update_data(
                        page=page,
                        pages_count=pages_count,
                        query_set=query_set
                    )
        else:
            await message.answer('Ничего не найдено')
            await state.finish()

    except (ValueError) as e:
        await bot.send_sticker(
            chat_id=message.from_user.id,
            sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
        )
        await message.answer(
            message_texts.on.get('limit_entering_error'),
            parse_mode='Markdown'
        )
        logging.error(f'{e}')
        await RoomSearch.step2.set()


@dp.callback_query_handler(text=['room_prev', 'room_next'])
async def rooms_next(callback: CallbackQuery, state: FSMContext):
    """ПАГИНАЦИЯ"""
    try:
        data = await state.get_data()
        if callback.data == 'room_prev':
            page = data.get('page') - 1
        elif callback.data == 'room_next':
            page = data.get('page') + 1

        if (page > 0) and (page <= data.get('pages_count')):
            await state.update_data(page=page)
            await callback.message.edit_text(
                message_texts.room_search_result_text(
                    item=data.get('query_set')[page - 1]
                ),
                reply_markup=keyboards.pagination_keyboard(
                    page=page,
                    pages=data.get('pages_count'),
                    category='room'
                ),
                parse_mode='Markdown'
            )
    except IndexError:
        pass
    except ValueError:
        pass


@dp.callback_query_handler(text='Дома')
async def houses_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✏ До какой цены вывести объекты?')
    await HouseSearch.step2.set()


@dp.message_handler(state=HouseSearch.step2)
async def houses(message: Message, state: FSMContext):
    """Ответ на кнопку поиска по домам"""
    try:
        query_set = House.objects.filter(
            price__lte=int(message.text)
        ).order_by('-pub_date')
        pages_count = query_set.count()
        data = await state.get_data()

        if query_set.exists():
            await state.finish()
            await message.answer(
                f'✳ Вот, что я нашёл по *домам* ({pages_count}):',
                parse_mode='Markdown'
            )

            """Вид отображения каскадом"""
            if data.get('view_form') == 'cascade':
                for item in query_set:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.house_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await message.answer_media_group(media=album)

            """Вид отображения карусель"""
            if data.get('view_form') == 'carousel':
                if query_set:
                    page = 1
                    await message.answer(
                        message_texts.house_search_result_text(
                            item=query_set[page - 1]
                        ),
                        reply_markup=keyboards.pagination_keyboard(
                            page=page,
                            pages=pages_count,
                            category='house'
                        ),
                        parse_mode='Markdown'
                    )
                    await state.update_data(
                        page=page,
                        pages_count=pages_count,
                        query_set=query_set
                    )
        else:
            await message.answer('Ничего не найдено')
            await state.finish()

    except (ValueError) as e:
        await bot.send_sticker(
            chat_id=message.from_user.id,
            sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
        )
        await message.answer(
            message_texts.on.get('limit_entering_error'),
            parse_mode='Markdown'
        )
        logging.error(f'{e}')
        await HouseSearch.step2.set()


@dp.callback_query_handler(text=['house_prev', 'house_next'])
async def houses_next(callback: CallbackQuery, state: FSMContext):
    """ПАГИНАЦИЯ"""
    # МАГИЯ!
    try:
        data = await state.get_data()
        if callback.data == 'house_prev':
            page = data.get('page') - 1
        elif callback.data == 'house_next':
            page = data.get('page') + 1

        if (page > 0) and (page <= data.get('pages_count')):
            await state.update_data(page=page)
            await callback.message.edit_text(
                message_texts.house_search_result_text(
                    item=data.get('query_set')[page - 1]
                ),
                reply_markup=keyboards.pagination_keyboard(
                    page=page,
                    pages=data.get('pages_count'),
                    category='house'
                ),
                parse_mode='Markdown'
            )
    except IndexError:
        pass
    except ValueError:
        pass


@dp.callback_query_handler(text='Таунхаусы')
async def townhouses_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✏ До какой цены вывести объекты?')
    await TownHouseSearch.step2.set()


@dp.message_handler(state=TownHouseSearch.step2)
async def townhouses(message: Message, state: FSMContext):
    """Ответ на кнопку поиска по таунхаусам ПАГИНАЦИЯ"""
    try:
        query_set = TownHouse.objects.filter(
            price__lte=int(message.text)
        ).order_by('-pub_date')
        pages_count = query_set.count()
        data = await state.get_data()

        if query_set.exists():
            await state.finish()
            await message.answer(
                f'✳ Вот, что я нашёл по *таунхаусам* ({pages_count}):',
                parse_mode='Markdown'
            )

            """Вид отображения каскадом"""
            if data.get('view_form') == 'cascade':
                for item in query_set:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.townhouse_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await message.answer_media_group(media=album)

            """Вид отображения каруселью"""
            if data.get('view_form') == 'carousel':
                if query_set:
                    page = 1
                    await message.answer(
                        message_texts.townhouse_search_result_text(
                            item=query_set[page - 1]
                        ),
                        reply_markup=keyboards.pagination_keyboard(
                            page=page,
                            pages=pages_count,
                            category='townhouse'
                        ),
                        parse_mode='Markdown'
                    )
                    await state.update_data(
                        page=page,
                        pages_count=pages_count,
                        query_set=query_set
                    )
        else:
            await message.answer('Ничего не найдено')
            await state.finish()

    except (ValueError) as e:
        await bot.send_sticker(
            chat_id=message.from_user.id,
            sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
        )
        await message.answer(
            message_texts.on.get('limit_entering_error'),
            parse_mode='Markdown'
        )
        logging.error(f'{e}')
        await TownHouseSearch.step2.set()


@dp.callback_query_handler(text=['townhouse_prev', 'townhouse_next'])
async def townhouses_next(callback: CallbackQuery, state: FSMContext):
    """ПАГИНАЦИЯ"""
    try:
        data = await state.get_data()
        if callback.data == 'townhouse_prev':
            page = data.get('page') - 1
        elif callback.data == 'townhouse_next':
            page = data.get('page') + 1

        if (page > 0) and (page <= data.get('pages_count')):
            await state.update_data(page=page)
            await callback.message.edit_text(
                message_texts.townhouse_search_result_text(
                    data.get('query_set')[page - 1]
                ),
                reply_markup=keyboards.pagination_keyboard(
                    page, data.get('pages_count'), 'townhouse'
                ),
                parse_mode='Markdown'
            )
    except IndexError:
        pass
    except ValueError:
        pass


@dp.callback_query_handler(text='Участки')
async def lands_search(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('✏ До какой цены вывести объекты?')
    await LandSearch.step2.set()


@dp.message_handler(state=LandSearch.step2)
async def lands(message: Message, state: FSMContext):
    """Ответ на кнопку поиска по участкам ПАГИНАЦИЯ"""
    try:
        # подготовка инфы (кверисет) на вывод
        query_set = Land.objects.filter(
            price__lte=int(message.text)
        ).order_by('-pub_date')
        pages_count = query_set.count()
        data = await state.get_data()

        # дежурная фраза
        if query_set.exists():
            await state.finish()
            await message.answer(
                f'✳ Вот, что я нашёл по *участкам* ({pages_count}):',
                parse_mode='Markdown'
            )

            """Вид отображения каскадом"""
            if data.get('view_form') == 'cascade':
                for item in query_set:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.lands_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await message.answer_media_group(media=album)

            """вид отображения каруселью"""
            if data.get('view_form') == 'carousel':
                if query_set:
                    # установка значения номера страницы на первую
                    page = 1
                    await message.answer(
                        # вывод на экран первого элемента (инфы об объекте) кверисета
                        message_texts.lands_search_result_text(
                            item=query_set[page - 1]
                        ),
                        reply_markup=keyboards.pagination_keyboard(
                            page=page,
                            pages=pages_count,
                            category='land'
                        ),
                        parse_mode='Markdown'
                    )
                    await state.update_data(
                        # запоминание состояний в FSM для передачи
                        # во вторую часть магии
                        page=page,
                        pages_count=pages_count,
                        query_set=query_set
                    )
        else:
            await message.answer('Ничего не найдено')
            await state.finish()

    except (ValueError) as e:
        await bot.send_sticker(
            chat_id=message.from_user.id,
            sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
        )
        await message.answer(
            message_texts.on.get('limit_entering_error'),
            parse_mode='Markdown'
        )
        logging.error(f'{e}')
        await LandSearch.step2.set()


@dp.callback_query_handler(text=['land_prev', 'land_next'])
async def lands_next(callback: CallbackQuery, state: FSMContext):
    """ПАГИНАЦИЯ"""
    # вторая часть МАГИИ!
    try:
        # увеличение/уменьшение переменной номера страницы
        data = await state.get_data()
        if callback.data == 'land_prev':
            page = data.get('page') - 1
        elif callback.data == 'land_next':
            page = data.get('page') + 1

        # чтобы не было отрицательных индексов и перебора
        if (page > 0) and (page <= data.get('pages_count')):

            # запоминание текущего номера страницы
            await state.update_data(page=page)

            await callback.message.edit_text(

                # вывод на экран через кастомный метод
                message_texts.lands_search_result_text(
                    item=data.get('query_set')[page - 1]
                ),
                # кейборд из кастомного метода
                reply_markup=keyboards.pagination_keyboard(
                    page=page,
                    pages=data.get('pages_count'),
                    category='land'
                ),
                parse_mode='Markdown'
            )
    # от греха подальше, хотя не должно быть
    except IndexError:
        pass
    except ValueError:
        pass


@dp.callback_query_handler(text="Квартиры")
async def apartments(callback: CallbackQuery):
    await callback.message.edit_text(
        '✏ Выбери по количеству комнат',
        reply_markup=keyboards.get_rooms_count_keyboard()
    )


@dp.callback_query_handler(text='⏪ Назад')
async def back_button_action(callback: CallbackQuery):
    await callback.message.edit_text(
        '✏ Выбери категорию объектов для поиска',
        reply_markup=keyboards.get_category_keyboard()
    )

checked_category = {}


@dp.callback_query_handler(
    text=[
        '1-комнатные', '2-комнатные',
        '3-комнатные', '4-комнатные',
        '5-комнатные'
    ]
)
async def apartment_plan_category_choice(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.update_data(room_count=callback.data.removesuffix('-комнатные'))
    global checked_category
    key = str(callback.from_user.id)
    checked_category.setdefault(key, [])

    await callback.message.edit_text(
        '✏ Выберите категорию по планировке',
        reply_markup=keyboards.apartment_plan_category_choice(checked_buttons=[])
    )
    checked_category[key] = []

    await ApartmentSearch.step3.set()


@dp.callback_query_handler(
    state=ApartmentSearch.step3,
    text=checked_apartment_category
)
async def apartment_plan_category_checking(
    callback: CallbackQuery,
    state: FSMContext
):
    answer = callback.data
    key = str(callback.from_user.id)
    if answer == 'Подтвердить выбор':
        if not checked_category[key]:
            await callback.message.edit_text(
                '❗ Необходимо выбрать категорию',
                reply_markup=keyboards.apartment_plan_category_choice(checked_buttons=[])
            )
        else:
            await state.update_data(category=checked_category[key])
            await callback.message.edit_text('✏ До какой цены вывести объекты?')
            await ApartmentSearch.step4.set()
    else:
        if '✅' in answer:
            checked_category[key].remove(answer.removeprefix('✅ '))
        else:
            checked_category[key].append(answer)
        await callback.message.edit_text(
            '✏ Выберите категорию по планировке',
            reply_markup=keyboards.apartment_plan_category_choice(
                checked_buttons=checked_category[key]
            )
        )
        await ApartmentSearch.step3.set()


@dp.message_handler(state=ApartmentSearch.step4)
async def apartment_search_result(
    message: Message,
    state: FSMContext
):
    try:
        data = await state.get_data()
        room_count = data.get('room_count')
        category = data.get('category')
        query = reduce(
            operator.or_, [
                Q(**{'category__contains': field}) for field in category
            ]
        )
        query_set = Apartment.objects.filter(query)
        query_set = query_set.filter(
            room_quantity=int(room_count),
            price__lte=int(message.text)
        ).order_by('-pub_date')

        if query_set:
            await message.answer(
                f'✳ Вот, что я нашёл по *{room_count}-комнатным*:',
                parse_mode='Markdown',
            )
            await state.finish()

            """Вид отображения каскадом"""
            if data.get('view_form') == 'cascade':
                for item in query_set:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.apartments_search_result_text(
                                        room_count=room_count,
                                        item=item
                                    ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await message.answer_media_group(media=album)

            if data.get('view_form') == 'carousel':
                """Отображение каруселью"""
                pages_count = query_set.count()

                if query_set:
                    page = 1
                    await message.answer(
                        message_texts.apartments_search_result_text(
                            int(room_count),
                            query_set[page - 1]
                        ),
                        reply_markup=keyboards.pagination_keyboard(
                            page=page,
                            pages=pages_count,
                            category='apartment'
                        ),
                        parse_mode='Markdown'
                    )
                    await state.update_data(
                        page=page,
                        pages_count=pages_count,
                        query_set=query_set,
                        room_count=room_count
                    )
        else:
            await message.answer('Ничего не найдено')
            await state.finish()
    except (ValueError) as e:
        await bot.send_sticker(
            chat_id=message.from_user.id,
            sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
        )
        await message.answer(
            message_texts.on.get('limit_entering_error'),
            parse_mode='Markdown'
        )
        logging.error(f'{e}')
        await ApartmentSearch.step4.set()


@dp.callback_query_handler(
    text=['apartment_prev', 'apartment_next']
)
async def apartment_next(callback: CallbackQuery, state: FSMContext):
    """ПАГИНАЦИЯ"""
    try:
        data = await state.get_data()
        if callback.data == 'apartment_prev':
            page = data.get('page') - 1
        elif callback.data == 'apartment_next':
            page = data.get('page') + 1

        if (page > 0) and (page <= data.get('pages_count')):

            await state.update_data(page=page)
            await callback.message.edit_text(
                message_texts.apartments_search_result_text(
                    int(data.get('room_count')),
                    data.get('query_set')[page - 1]
                ),
                reply_markup=keyboards.pagination_keyboard(
                    page=page,
                    pages=data.get('pages_count'),
                    category='apartment'
                ),
                parse_mode='Markdown'
            )
    except IndexError:
        pass
    except ValueError:
        pass

# --------------------------------------------------------------------------
# ------------------- ОПРОС ПО КВАРТИРЕ ------------------------------------
# --------------------------------------------------------------------------


@dp.callback_query_handler(text='Квартиру')
async def add_apartment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(reality_category=callback.data)
    await callback.message.edit_text(
        'Приготовься ответить на несколько вопросов про ваш объект '
        + 'недвижимости. 😏 Это займёт не более 2-3х минут.'
        + '\n'
        + '\n✏ *Введи количество комнат*',
        reply_markup=keyboards.add_rooms_count_keyboard(),
        parse_mode='Markdown'
    )


@dp.callback_query_handler(text=[
    'add_1_room', 'add_2_room',
    'add_3_room', 'add_4_room',
    'add_5_room'
])
async def entering_room_count(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.update_data(room_count=callback.data[4])
    await callback.message.edit_text(
        '✏ *Напиши название улицы*\n\n'
        + 'без указания наименования дорог и проездов (ул., пр., пер. и т.п.)\n\n'
        + '❗ Пиши правильно: Комсомольский, Победы, Юбилейный, Берёзовское шоссе\n\n'
        + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
        parse_mode='Markdown'
    )
    await CallbackOnStart.Q1.set()


@dp.message_handler(state=CallbackOnStart.Q1)
async def entering_street_name(
    message: Message,
    state: FSMContext
):
    answer = message.text.title()
    if answer == 'Стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(street_name=answer)

        await message.answer(
            '✏ *Напиши номер дома* в формате 5, 5А или 91 корп.1\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await CallbackOnStart.next()


@dp.message_handler(state=CallbackOnStart.Q2)
async def entering_house_number(message: Message, state: FSMContext):
    answer = message.text
    if answer == 'Стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if '"' in answer:
            formatting_answer = answer.replace('"', '')
            answer = formatting_answer

        if ' ' in answer:
            formatting_answer = answer.replace(' ', '')
            answer = formatting_answer

        await state.update_data(house_number=answer.upper())
        await message.answer(
            '✏ Введите этаж квартиры',
            reply_markup=keyboards.floor_number_or_count_keyboard(
                object='apartment_floor'
            )
        )
        await CallbackOnStart.next()


@dp.callback_query_handler(state=CallbackOnStart.Q3, text=[
    '1_afloor', '2_afloor', '3_afloor', '4_afloor',
    '5_afloor', '6_afloor', '7_afloor', '8_afloor',
    '9_afloor', '10_afloor', '11_afloor', '12_afloor',
    '13_afloor', '14_afloor', '15_afloor', '16_afloor',
    '17_afloor', '18_afloor', 'Отменить внесение объекта'
])
async def entering_floor(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(floor=callback.data.removesuffix('_afloor'))
        await callback.message.edit_text(
            '✏ Введи количество этажей',
            reply_markup=keyboards.floor_number_or_count_keyboard(
                object='apartment_house_floors'
            )
        )
        await CallbackOnStart.next()


@dp.callback_query_handler(state=CallbackOnStart.Q4, text=[
    '1_afloors', '2_afloors', '3_afloors', '4_afloors',
    '5_afloors', '6_afloors', '7_afloors', '8_afloors',
    '9_afloors', '10_afloors', '11_afloors', '12_afloors',
    '13_afloors', '14_afloors', '15_afloors', '16_afloors',
    '17_afloors', '18_afloors', 'Отменить внесение объекта'
])
async def entering_floors(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(floors=callback.data.removesuffix('_afloors'))

        await callback.message.edit_text(
            '✏ *Напиши площадь квартиры*, как'
            + ' указано в свидетельстве или выписке\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await CallbackOnStart.plan_category.set()


@dp.message_handler(state=CallbackOnStart.plan_category)
async def plan_category(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(area=answer)
            await message.answer(
                '✏ К какой категории по планировке относится квартира?',
                reply_markup=keyboards.apartment_plan_category()
            )
            await CallbackOnStart.Q5.set()

        except (ValueError) as e:
            await CallbackOnStart.Q4.set()
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.callback_query_handler(state=CallbackOnStart.Q5, text=[
    'МЖК',
    'Старой планировки',
    'Улучшенной планировки',
    'Новые дома',
    'Новые дома с инд.отоплением',
    'Отменить внесение объекта'
])
async def entering_area(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(category=callback.data)
        await callback.message.edit_text(
            message_texts.on.get('enter_price'),
            parse_mode='Markdown'
        )
        await CallbackOnStart.Q6.set()


@dp.message_handler(state=CallbackOnStart.Q6)
async def entering_price(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = int(message.text)
            await state.update_data(price=answer)
            await message.answer(
                message_texts.entering_description_text(category='квартиры'),
                parse_mode='Markdown'
            )
            await CallbackOnStart.next()

        except (ValueError) as e:
            await CallbackOnStart.Q6.set()
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=CallbackOnStart.Q7)
async def entering_description(message: Message, state: FSMContext):
    answer = message.text
    if answer == 'Стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if len(message.text) <= 200:
            await state.update_data(description=answer)
            await message.answer(
                '✏ На недвижимости есть обременение?',
                reply_markup=keyboards.yes_no_keyboard('encumbrance')
            )
            await CallbackOnStart.next()
        else:
            await message.answer(
                message_texts.character_limit(len(message.text))
            )
            logging.error('Превышение лимита знаков')
            await CallbackOnStart.Q7.set()


@dp.callback_query_handler(
    state=CallbackOnStart.Q8,
    text=['yes_encumbrance', 'no_encumbrance', 'Отменить внесение объекта']
)
async def entering_encumbrance(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_encumbrance':
            await state.update_data(encumbrance=True)
        if callback.data == 'no_encumbrance':
            await state.update_data(encumbrance=False)
        await callback.message.edit_text(
            '✏ В собственности есть дети?',
            reply_markup=keyboards.yes_no_keyboard('children')
        )
        await CallbackOnStart.next()


@dp.callback_query_handler(
    state=CallbackOnStart.Q9,
    text=['yes_children', 'no_children', 'Отменить внесение объекта']
)
async def entering_children(callback: CallbackQuery, state: FSMContext):
    """Запись наличия детей"""
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_children':
            await state.update_data(children=True)
        if callback.data == 'no_children':
            await state.update_data(children=False)
        await callback.message.edit_text(
            '✏ Недвижимость возможно купить по иптоеке?',
            reply_markup=keyboards.yes_no_keyboard('mortage')
        )
        await CallbackOnStart.next()


@dp.callback_query_handler(
    state=CallbackOnStart.Q10,
    text=['yes_mortage', 'no_mortage', 'Отменить внесение объекта']
)
async def entering_mortage(callback: CallbackQuery, state: FSMContext):
    """Запись возможности покупки в ипотеку"""
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_mortage':
            await state.update_data(mortage=True)
        if callback.data == 'no_mortage':
            await state.update_data(mortage=False)
        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await CallbackOnStart.next()


@dp.message_handler(state=CallbackOnStart.Q11)
async def entering_phone_number(message: Message, state: FSMContext):
    """Запись номера телефона"""
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(owner_phone_number='+7' + message.text[1:])
            await message.answer(
                '✏ *Как зовут продавца квартиры?*\n\n'
                + 'Его имя будет видно только тебе\n\n'
                + 'Для отмены внесения объекта напиши "Стоп"',
                parse_mode='Markdown'
            )
            await CallbackOnStart.Q12.set()
        else:
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.phone_number_entering_error(message.text),
                parse_mode='Markdown'
            )
            logging.error(f'Ошибка при вводе номера телефона {message.text}')
            await CallbackOnStart.Q11.set()


@dp.message_handler(state=CallbackOnStart.Q12)
async def entering_agency_name(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(owner_name=answer)
        await message.answer(
            '✏ Загрузите до 6 фото квартиры\n\n'
        )
        await CallbackOnStart.Q14.set()


images = {}


@dp.message_handler(state=CallbackOnStart.Q14, content_types=ContentType.PHOTO)
async def report_photo(message: Message, state: FSMContext):

    global images
    key = str(message.from_user.id)
    images.setdefault(key, [])

    if len(images[key]) == 0:
        images[key].append(message.photo[-1].file_id)
        await message.answer(message_texts.on.get('code_word_text'))
        await CallbackOnStart.Q15.set()
    else:
        images[key].append(message.photo[-1].file_id)


@dp.message_handler(state=CallbackOnStart.Q15)
async def base_updating(message: Message, state: FSMContext):

    await state.update_data(code_word=message.text)
    user_id = message.from_user.id

    rieltor = Rieltors.objects.get(user_id=user_id)
    photo = images.get(str(user_id))
    images.pop(str(user_id))
    await state.update_data(photo=photo)
    await state.update_data(
        user_id=user_id,
        rieltor_name=rieltor.name,
        agency_name=rieltor.agency_name,
        rieltor_phone_number=rieltor.phone_number
    )
    data = await state.get_data()

    # ЗАПИСЬ В БАЗУ И выдача
    await asyncio.sleep(2)
    if not DB_Worker.apartment_to_db(data):
        await message.answer(
            message_texts.on.get('sorry_about_error')
        )
    else:
        album = MediaGroup()
        channel_album = MediaGroup()
        photo_list = data.get('photo')
        for photo_id in photo_list:
            if photo_id == photo_list[-1]:
                # альбом с подписью для отправки пользователям
                album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.apartment_adding_result_text(data)
                    ),
                    parse_mode='Markdown'
                )
                # альбом с подписью для отправки в канал
                channel_album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.apartment_message_for_channel(data)
                    ),
                    parse_mode='Markdown'
                )
            else:
                album.attach_photo(photo_id)
                channel_album.attach_photo(photo_id)
        await message.answer_media_group(media=album)
        await bot.send_media_group(TELEGRAM_CHANNEL_ID, channel_album)
    await state.finish()


# --------------------------------------------------------------------------
# ------------------- ОПРОС ПО КОМНАТЕ ------------------------------------
# --------------------------------------------------------------------------
@dp.callback_query_handler(text='Комнату')
async def add_room(callback: CallbackQuery, state: FSMContext):

    await state.update_data(room_reality_category=callback.data)
    await callback.message.edit_text(
        'Приготовься ответить на несколько вопросов про ваш объект '
        + 'недвижимости. 😏 Это займёт не более 2-3х минут.\n\n'
        + '✏ *Напиши название улицы*\n\n'
        + 'без указания наименования дорог и проездов (ул., пр., пер. и т.п.)\n\n'
        + '❗ Пиши правильно: Комсомольский, Победы, Юбилейный, Берёзовское шоссе\n\n',
        parse_mode='Markdown'

    )
    await RoomCallbackStates.R1.set()


@dp.message_handler(state=RoomCallbackStates.R1)
async def enetering_rooms_street_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(room_street_name=message.text.title())
        await message.answer(
            '✏ *Напиши номер дома* в формате 5, 5А или 91 корп.1\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await RoomCallbackStates.next()


@dp.message_handler(state=RoomCallbackStates.R2)
async def enetering_rooms_house_number(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if '"' in answer:
            formatting_answer = answer.replace('"', '')
            answer = formatting_answer

        if ' ' in answer:
            formatting_answer = answer.replace(' ', '')
            answer = formatting_answer

        await state.update_data(room_house_number=answer.upper())
        await message.answer(
            '✏ Введи этаж комнаты',
            reply_markup=keyboards.floor_number_or_count_keyboard('room_floor')
        )
        await RoomCallbackStates.next()


@dp.callback_query_handler(state=RoomCallbackStates.R3, text=[
    '1_rfloor', '2_rfloor', '3_rfloor', '4_rfloor',
    '5_rfloor', '6_rfloor', '7_rfloor', '8_rfloor',
    '9_rfloor', '10_rfloor', '11_rfloor', '12_rfloor',
    '13_rfloor', '14_rfloor', '15_rfloor', '16_rfloor',
    '17_rfloor', '18_rfloor', 'Отменить внесение объекта',
])
async def entering_room_floor(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(room_floor=callback.data.removesuffix('_rfloor'))
        await callback.message.edit_text(
            '✏ Введи количество этажей',
            reply_markup=keyboards.floor_number_or_count_keyboard(
                object='room_house_floors'
            )
        )
        await RoomCallbackStates.next()


@dp.callback_query_handler(state=RoomCallbackStates.R4, text=[
    '1_rfloors', '2_rfloors', '3_rfloors', '4_rfloors',
    '5_rfloors', '6_rfloors', '7_rfloors', '8_rfloors',
    '9_rfloors', '10_rfloors', '11_rfloors', '12_rfloors',
    '13_rfloors', '14_rfloors', '15_rfloors', '16_rfloors',
    '17_rfloors', '18_rfloors', 'Отменить внесение объекта',
])
async def entering_room_floors(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(room_floors=callback.data.removesuffix('_rfloors'))
        await callback.message.edit_text(
            '✏ *Введи площадь комнаты*, как в указано в свидетельстве или выписке\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await RoomCallbackStates.next()


@dp.message_handler(state=RoomCallbackStates.R5)
async def enetering_rooms_area(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text

            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(room_area=answer)
            await message.answer(
                message_texts.on.get('enter_price'),
                parse_mode='Markdown'
            )
            await RoomCallbackStates.next()

        except (ValueError) as e:
            await RoomCallbackStates.R5.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=RoomCallbackStates.R6)
async def entering_room_price(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = int(message.text)
            await state.update_data(room_price=answer)
            await message.answer(
                message_texts.entering_description_text(category='комнаты'),
                parse_mode='Markdown'
            )
            await RoomCallbackStates.next()

        except (ValueError) as e:
            await RoomCallbackStates.R6.set()
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=RoomCallbackStates.R7)
async def entering_room_description(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if len(message.text) <= 200:
            await state.update_data(room_description=answer)
            await message.answer(
                '✏ На недвижимости есть обременение?',
                reply_markup=keyboards.yes_no_keyboard(item='room_encumbrance')
                )
            await RoomCallbackStates.next()
        else:
            await message.answer(
                message_texts.character_limit(len(message.text))
            )
            logging.error('Превышение лимита знаков')
            await RoomCallbackStates.R7.set()


@dp.callback_query_handler(
    state=RoomCallbackStates.R8,
    text=['yes_room_encumbrance', 'no_room_encumbrance', 'Отменить внесение объекта']
)
async def entering_room_encumbrance(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_room_encumbrance':
            await state.update_data(room_encumbrance=True)
        if callback.data == 'no_room_encumbrance':
            await state.update_data(room_encumbrance=False)
        await callback.message.edit_text(
            '✏ В собственности есть дети?',
            reply_markup=keyboards.yes_no_keyboard(item='room_children')
        )
        await RoomCallbackStates.next()


@dp.callback_query_handler(
    state=RoomCallbackStates.R9,
    text=['yes_room_children', 'no_room_children', 'Отменить внесение объекта']
)
async def entering_room_children(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_room_children':
            await state.update_data(room_children=True)
        if callback.data == 'no_room_children':
            await state.update_data(room_children=False)
        await callback.message.edit_text(
            '✏ Недвижимость возможно купить по иптоеке?',
            reply_markup=keyboards.yes_no_keyboard(item='room_mortage')
        )
        await RoomCallbackStates.next()


@dp.callback_query_handler(
    state=RoomCallbackStates.R10,
    text=['yes_room_mortage', 'no_room_mortage', 'Отменить внесение объекта']
)
async def entering_room_mortage(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_room_mortage':
            await state.update_data(room_mortage=True)
        if callback.data == 'no_room_mortage':
            await state.update_data(room_mortage=False)
        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await RoomCallbackStates.next()


@dp.message_handler(state=RoomCallbackStates.R11)
async def entering_room_phone_number(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(room_owner_phone_number='+7' + message.text[1:])
            await message.answer(
                '✏ *Как зовут продавца комнаты?*\n\n'
                + 'Для отмены внесения объекта напиши "Стоп"',
                parse_mode='Markdown'
            )
            await RoomCallbackStates.R12.set()
        else:
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.phone_number_entering_error(
                    phone_number=message.text
                ),
                parse_mode='Markdown'
            )
            logging.error(f'Ошибка при вводе номера телефона {message.text}')
            await RoomCallbackStates.R11.set()


@dp.message_handler(state=RoomCallbackStates.R12)
async def entering_room_agency_name(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(room_owner_name=answer)
        await message.answer(
            '✏ Загрузите до 6 фото квартиры\n\n'
        )
        await RoomCallbackStates.R14.set()


@dp.message_handler(state=RoomCallbackStates.R14, content_types=ContentType.PHOTO)
async def report_room_photo(message: Message):
    global images
    key = str(message.from_user.id)
    images.setdefault(key, [])

    if len(images[key]) == 0:
        images[key].append(message.photo[-1].file_id)
        await message.answer(message_texts.on.get('code_word_text'))
        await RoomCallbackStates.R15.set()
    else:
        images[key].append(message.photo[-1].file_id)


@dp.message_handler(state=RoomCallbackStates.R15)
async def room_base_updating(message: Message, state: FSMContext):

    await state.update_data(room_code_word=message.text)
    user_id = message.from_user.id

    rieltor = Rieltors.objects.get(user_id=user_id)
    photo = images.get(str(user_id))
    images.pop(str(user_id))
    await state.update_data(room_photo=photo)
    await state.update_data(
            room_user_id=user_id,
            room_rieltor_name=rieltor.name,
            room_agency_name=rieltor.agency_name,
            room_rieltor_phone_number=rieltor.phone_number
        )

    data = await state.get_data()

    # ЗАПИСЬ В БАЗУ И выдача
    await asyncio.sleep(2)
    if not DB_Worker.room_to_db(data):
        await message.answer(
            message_texts.on.get('sorry_about_error')
        )
    else:
        album = MediaGroup()
        channel_album = MediaGroup()
        photo_list = data.get('room_photo')
        for photo_id in photo_list:
            if photo_id == photo_list[-1]:
                album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.room_adding_result_text(data)
                    ),
                    parse_mode='Markdown'
                )
                channel_album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.room_message_for_channel(data)
                    ),
                    parse_mode='Markdown'
                )
            else:
                album.attach_photo(photo_id)
                channel_album.attach_photo(photo_id)
        await message.answer_media_group(media=album)
        await bot.send_media_group(TELEGRAM_CHANNEL_ID, channel_album)
    await state.finish()


# --------------------------------------------------------------------------
# ------------------- ОПРОС ПО ДОМУ ------------------------------------
# --------------------------------------------------------------------------
@dp.callback_query_handler(text='Дом')
async def add_house(callback: CallbackQuery, state: FSMContext):

    await state.update_data(house_reality_category=callback.data)
    await callback.message.edit_text(
        'Приготовься ответить на несколько вопросов про ваш объект '
        + 'недвижимости. 😏 Это займёт не более 2-3х минут.\n\n'
        + '✏ *Укажи микрорайон расположения дома:*\n\n'
        + '✏ Если нужного микрорайона/села/деревни нет, напиши @davletelvir, добавлю.',
        reply_markup=keyboards.microregion_keyboard('object'),
        parse_mode='Markdown'
    )
    await HouseCallbackStates.H1.set()


@dp.callback_query_handler(
    state=HouseCallbackStates.H1,
    text=object_microregions.append('Отменить внесение объекта')
)
async def entering_house_street_name(
    callback: CallbackQuery, state: FSMContext
):
    """Ответ на кнопку выбора мирорайона"""
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_microregion=callback.data)
        await callback.message.edit_text(
            '✏ *Напиши название улицы* (и номер дома - по желанию)\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await HouseCallbackStates.next()


@dp.message_handler(state=HouseCallbackStates.H2)
async def entering_house_purpose(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(house_street_name=answer)
        await message.answer(
            '✏ Укажи назначение участка',
            reply_markup=keyboards.purpose_choise_keyboard()
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H3, text=[
        'ИЖС',
        'СНТ, ДНТ',
        'ЛПХ',
        'Отменить внесение объекта'
    ]
)
async def entering_house_finish(
    callback: CallbackQuery, state: FSMContext
):
    """Ответ на ввод назначения"""
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_purpose=callback.data)
        await callback.message.edit_text(
            '✏ Это завершённое строительство',
            reply_markup=keyboards.yes_no_keyboard(item='house_finish')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H4, text=[
        'yes_house_finish',
        'no_house_finish',
        'Отменить внесение объекта'
    ]
)
async def entering_house_material(
    callback: CallbackQuery, state: FSMContext
):
    """Ответ на ввод завершённости строительства"""
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_finish':
            await state.update_data(house_finish='Да')
        if callback.data == 'no_house_finish':
            await state.update_data(house_finish='Нет')

        await callback.message.edit_text(
            '✏ Укажи материал стен дома',
            reply_markup=keyboards.material_choice_keyboard()
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H5, text=[
        'Кирпич',
        'Заливной',
        'Блок, облицованный кирпичом',
        'Дерево',
        'Дерево, облицованное кирпичом',
        'Другое',
        'Отменить внесение объекта',
    ]
)
async def entering_house_gas(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_material=callback.data)
        await callback.message.edit_text(
            '✏ Укажи степень газификации дома',
            reply_markup=keyboards.gaz_choise_keyboard()
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H6, text=[
        'Газифицирован, дом отапливается',
        'Улица газифицировна, дом - нет',
        'Улица не газифицирована',
        'Отменить внесение объекта',
    ]
)
async def entering_house_waters(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_gaz=callback.data)
        await callback.message.edit_text(
            '✏ В доме есть вода?',
            reply_markup=keyboards.water_choice_keyboard()
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H7, text=[
        'Водоснабжение центральное',
        'Колодец',
        'Вода по улице',
        'Воды нет',
        'Отменить внесение объекта',
    ]
)
async def entering_house_sauna(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_water=callback.data)
        await callback.message.edit_text(
            '✏ На териитории участка/в доме есть баня или сауна',
            reply_markup=keyboards.yes_no_keyboard(item='house_sauna')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H8, text=[
        'yes_house_sauna',
        'no_house_sauna',
        'Отменить внесение объекта',
    ]
)
async def entering_house_garage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_sauna':
            await state.update_data(house_sauna='Есть')
        if callback.data == 'no_house_sauna':
            await state.update_data(house_sauna='Нет')

        await callback.message.edit_text(
            '✏ На териитории участка есть гараж?',
            reply_markup=keyboards.yes_no_keyboard(item='house_garage')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H9, text=[
        'yes_house_garage',
        'no_house_garage',
        'Отменить внесение объекта',
    ]
)
async def entering_house_fence(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_garage':
            await state.update_data(house_garage='Есть')
        if callback.data == 'no_house_garage':
            await state.update_data(house_garage='Нет')
        await callback.message.edit_text(
            '✏ Участок огорожен?',
            reply_markup=keyboards.yes_no_keyboard(item='house_fence')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H10, text=[
        'yes_house_fence',
        'no_house_fence',
        'Отменить внесение объекта',
    ]
)
async def entering_house_road(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_fence':
            await state.update_data(house_fence='Есть')
        if callback.data == 'no_house_fence':
            await state.update_data(house_fence='Нет')
        await callback.message.edit_text(
            '✏ К участку есть проезд?',
            reply_markup=keyboards.road_choice_keyboard()
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H11, text=[
        'Асфальт',
        'Неплохая насыпная дорога',
        'Неплохая грунтовая дорога',
        'Бездорожье, затрудняющее проезд',
        'Отменить внесение объекта',
    ]
)
async def entering_house_area(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(house_road=callback.data)
        await callback.message.edit_text(
            '✏ *Введи площадь дома,* как в указано в свидетельстве или выписке. '
            + 'Используйте разделитель "." для дробной и целой частей.\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await HouseCallbackStates.next()


@dp.message_handler(state=HouseCallbackStates.H12)
async def entering_house_land_area(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(house_area=answer)
            await message.answer(
                '✏ *Введи площадь участка в сотках.* '
                + '(Значение площади из документации раздели на 100) '
                + 'Используйте разделитель "." для дробной и целой частей.\n\n'
                + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
                parse_mode='Markdown'
            )
            await HouseCallbackStates.next()

        except (ValueError) as e:
            await HouseCallbackStates.H12.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=HouseCallbackStates.H13)
async def entering_house_price(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(house_land_area=answer)
            await message.answer(
                message_texts.on.get('enter_price'),
                parse_mode='Markdown'
            )
            await HouseCallbackStates.next()

        except (ValueError) as e:
            await HouseCallbackStates.H13.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=HouseCallbackStates.H14)
async def entering_house_description(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = int(message.text)
            await state.update_data(house_price=answer)
            await message.answer(
                message_texts.entering_description_text('дома'),
                parse_mode='Markdown'
            )
            await HouseCallbackStates.next()

        except (ValueError) as e:
            await HouseCallbackStates.H14.set()
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=HouseCallbackStates.H15)
async def entering_house_encumbrance(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if len(message.text) <= 200:
            await state.update_data(house_description=answer)
            await message.answer(
                '✏ На доме есть обременение?',
                reply_markup=keyboards.yes_no_keyboard('house_encumbrance')
            )
            await HouseCallbackStates.next()
        else:
            await message.answer(
                message_texts.character_limit(len(message.text))
            )
            logging.error('Превышение лимита знаков')
            await HouseCallbackStates.H15.set()


@dp.callback_query_handler(
    state=HouseCallbackStates.H16,
    text=[
        'yes_house_encumbrance',
        'no_house_encumbrance',
        'Отменить внесение объекта',
    ]
)
async def entering_house_children(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_encumbrance':
            await state.update_data(house_encumbrance=True)
        if callback.data == 'no_house_encumbrance':
            await state.update_data(house_encumbrance=False)
        await callback.message.edit_text(
            '✏ В собственности есть дети?',
            reply_markup=keyboards.yes_no_keyboard('house_children')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H17,
    text=[
        'yes_house_children',
        'no_house_children',
        'Отменить внесение объекта',
    ]
)
async def entering_house_mortage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_children':
            await state.update_data(house_children=True)
        if callback.data == 'no_house_children':
            await state.update_data(house_children=False)
        await callback.message.edit_text(
            '✏ Дом возможно купить по иптоеке?',
            reply_markup=keyboards.yes_no_keyboard('house_mortage')
        )
        await HouseCallbackStates.next()


@dp.callback_query_handler(
    state=HouseCallbackStates.H18,
    text=[
        'yes_house_mortage',
        'no_house_mortage',
        'Отменить внесение объекта',
    ]
)
async def entering_house_phone_number(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_house_mortage':
            await state.update_data(house_mortage=True)
        if callback.data == 'no_house_mortage':
            await state.update_data(house_mortage=False)
        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await HouseCallbackStates.next()


@dp.message_handler(state=HouseCallbackStates.H19)
async def entering_house_agency_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(house_owner_phone_number='+7' + message.text[1:])
            await message.answer(
                '✏ *Как зовут продавца дома?*\n\n'
                'Его имя будет видно только тебе\n\n'
                + 'Для отмены внесения объекта напиши "Стоп"',
                parse_mode='Markdown'
            )
            await HouseCallbackStates.H20.set()
        else:
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.phone_number_entering_error(message.text),
                parse_mode='Markdown'
            )
            logging.error(f'Ошибка при вводе номера телефона {message.text}')
            await HouseCallbackStates.H19.set()


@dp.message_handler(state=HouseCallbackStates.H20)
async def entering_house_rieltor_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(house_owner_name=answer)
        await message.answer(
            '✏ Загрузите до 6 фото дома\n\n'
        )
        await HouseCallbackStates.H22.set()


@dp.message_handler(state=HouseCallbackStates.H22, content_types=ContentType.PHOTO)
async def house_report_photo(message: Message):
    global images
    key = str(message.from_user.id)
    images.setdefault(key, [])

    if len(images[key]) == 0:
        images[key].append(message.photo[-1].file_id)
        await message.answer(message_texts.on.get('code_word_text'))
        await HouseCallbackStates.H23.set()
    else:
        images[key].append(message.photo[-1].file_id)


@dp.message_handler(state=HouseCallbackStates.H23)
async def house_base_updating(message: Message, state: FSMContext):

    await state.update_data(house_code_word=message.text)
    user_id = message.from_user.id

    rieltor = Rieltors.objects.get(user_id=user_id)
    photo = images.get(str(user_id))
    images.pop(str(user_id))
    await state.update_data(house_photo=photo)
    await state.update_data(
            house_user_id=user_id,
            house_rieltor_name=rieltor.name,
            house_agency_name=rieltor.agency_name,
            house_rieltor_phone_number=rieltor.phone_number
            )

    data = await state.get_data()

    # ЗАПИСЬ В БАЗУ И выдача
    await asyncio.sleep(2)
    if not DB_Worker.house_to_db(data):
        await message.answer(
            message_texts.on.get('sorry_about_error')
        )
    else:
        album = MediaGroup()
        channel_album = MediaGroup()
        photo_list = data.get('house_photo')
        for photo_id in photo_list:
            if photo_id == photo_list[-1]:
                album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.house_adding_result_text(data)
                    ),
                    parse_mode='Markdown'
                )
                channel_album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.house_message_for_channel(data)
                    ),
                    parse_mode='Markdown'
                )
            else:
                album.attach_photo(photo_id)
                channel_album.attach_photo(photo_id)
        await message.answer_media_group(media=album)
        await bot.send_media_group(TELEGRAM_CHANNEL_ID, channel_album)
    await state.finish()


# --------------------------------------------------------------------------
# ------------------- ОПРОС ПО ТАУНХАУСУ ------------------------------------
# --------------------------------------------------------------------------
@dp.callback_query_handler(text='Таунхаус')
async def add_townhouse(callback: CallbackQuery, state: FSMContext):
    """Ответ на кнопку добавления таунхауса"""

    await state.update_data(townhouse_reality_category=callback.data)
    await callback.message.edit_text(
        'Приготовься ответить на несколько вопросов про ваш объект '
        + 'недвижимости. 😏 Это займёт не более 2-3х минут.\n\n'
        + '✏ *Укажи микрорайон расположения таунхауса.*\n\n'
        + 'Если нужного микрорайона/села/деревни нет, напиши @davletelvir, добавлю.\n\n'
        + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
        reply_markup=keyboards.microregion_keyboard('object'),
        parse_mode='Markdown'
    )
    await TownHouseCallbackStates.T1.set()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T1,
    text=object_microregions.append('Отменить внесение объекта')
)
async def entering_townhouse_street_name(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_microregion=callback.data)
        await callback.message.edit_text(
            '✏ *Напиши название улицы* (и номер дома - по желанию)\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await TownHouseCallbackStates.next()


@dp.message_handler(state=TownHouseCallbackStates.T2)
async def entering_townhouse_purpose(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(townhouse_street_name=answer)
        await message.answer(
            '✏ Укажи назначение участка',
            reply_markup=keyboards.purpose_choise_keyboard()
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T3, text=[
        'ИЖС',
        'СНТ, ДНТ',
        'ЛПХ',
        'Отменить внесение объекта'
    ]
)
async def entering_townhouse_finish(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_purpose=callback.data)
        await callback.message.edit_text(
            '✏ Это завершённое строительство',
            reply_markup=keyboards.yes_no_keyboard(item='townhouse_finish')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T4, text=[
        'yes_townhouse_finish', 'no_townhouse_finish', 'Отменить внесение объекта',
    ]
)
async def entering_townhouse_material(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_finish':
            await state.update_data(townhouse_finish='Да')
        if callback.data == 'no_townhouse_finish':
            await state.update_data(townhouse_finish='Нет')

        await callback.message.edit_text(
            '✏ Укажите материал стен',
            reply_markup=keyboards.material_choice_keyboard()
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T5, text=[
        'Кирпич',
        'Заливной',
        'Блок, облицованный кирпичом',
        'Дерево',
        'Дерево, облицованное кирпичом',
        'Другое',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_gas(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_material=callback.data)
        await callback.message.edit_text(
            '✏ Укажите степень газификации',
            reply_markup=keyboards.gaz_choise_keyboard()
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T6, text=[
        'Газифицирован, дом отапливается',
        'Улица газифицировна, дом - нет',
        'Улица не газифицирована',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_waters(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_gaz=callback.data)
        await callback.message.edit_text(
            '✏ В таунхаус проведена вода?',
            reply_markup=keyboards.water_choice_keyboard()
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T7, text=[
        'Водоснабжение центральное',
        'Колодец',
        'Вода по улице',
        'Воды нет',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_sauna(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_water=callback.data)
        await callback.message.edit_text(
            '✏ На териитории участка или внутри есть баня или сауна',
            reply_markup=keyboards.yes_no_keyboard(item='townhouse_sauna')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T8, text=[
        'yes_townhouse_sauna',
        'no_townhouse_sauna',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_garage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_sauna':
            await state.update_data(townhouse_sauna='Есть')
        if callback.data == 'no_townhouse_sauna':
            await state.update_data(townhouse_sauna='Нет')

        await callback.message.edit_text(
            '✏ На териитории участка есть гараж?',
            reply_markup=keyboards.yes_no_keyboard(item='townhouse_garage')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T9, text=[
        'yes_townhouse_garage',
        'no_townhouse_garage',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_fence(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_garage':
            await state.update_data(townhouse_garage='Есть')
        if callback.data == 'no_townhouse_garage':
            await state.update_data(townhouse_garage='Нет')
        await callback.message.edit_text(
            '✏ Участок огорожен?',
            reply_markup=keyboards.yes_no_keyboard(item='townhouse_fence')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T10, text=[
        'yes_townhouse_fence',
        'no_townhouse_fence',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_road(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_fence':
            await state.update_data(townhouse_fence='Есть')
        if callback.data == 'no_townhouse_fence':
            await state.update_data(townhouse_fence='Нет')
        await callback.message.edit_text(
            '✏ К участку есть проезд?',
            reply_markup=keyboards.road_choice_keyboard()
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T11, text=[
        'Асфальт',
        'Неплохая насыпная дорога',
        'Неплохая грунтовая дорога',
        'Бездорожье, затрудняющее проезд',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_area(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(townhouse_road=callback.data)
        await callback.message.edit_text(
            message_texts.on.get('area_entering_text'),
            parse_mode='Markdown'
        )
        await TownHouseCallbackStates.next()


@dp.message_handler(state=TownHouseCallbackStates.T12)
async def entering_townhouse_land_area(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(townhouse_area=answer)
            await message.answer(
                '✏ *Введи площадь участка в сотках.* '
                + '(Значение площади из документации раздели на 100) '
                + 'Используй разделитель "." для дробной и целой частей.\n\n'
                + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
                parse_mode='Markdown'
            )
            await TownHouseCallbackStates.next()

        except (ValueError) as e:
            await TownHouseCallbackStates.T12.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=TownHouseCallbackStates.T13)
async def entering_townhouse_price(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(townhouse_land_area=answer)
            await message.answer(
                message_texts.on.get('enter_price'),
                parse_mode='Markdown'
            )
            await TownHouseCallbackStates.next()

        except (ValueError) as e:
            await TownHouseCallbackStates.T13.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=TownHouseCallbackStates.T14)
async def entering_townhouse_description(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = int(message.text)
            await state.update_data(townhouse_price=answer)
            await message.answer(
                message_texts.entering_description_text('таунхауса'),
                parse_mode='Markdown'
            )
            await TownHouseCallbackStates.next()

        except (ValueError) as e:
            await TownHouseCallbackStates.T14.set()
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=TownHouseCallbackStates.T15)
async def entering_townhouse_encumbrance(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if len(message.text) <= 200:
            await state.update_data(townhouse_description=answer)
            await message.answer(
                '✏ На таунхаусе есть обременение?',
                reply_markup=keyboards.yes_no_keyboard('townhouse_encumbrance')
            )
            await TownHouseCallbackStates.next()
        else:
            await message.answer(
                message_texts.character_limit(len(message.text))
            )
            logging.error('Превышение лимита знаков')
            await TownHouseCallbackStates.T15.set()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T16,
    text=[
        'yes_townhouse_encumbrance',
        'no_townhouse_encumbrance',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_children(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_encumbrance':
            await state.update_data(townhouse_encumbrance=True)
        if callback.data == 'no_townhouse_encumbrance':
            await state.update_data(townhouse_encumbrance=False)
        await callback.message.edit_text(
            '✏ В собственности есть дети?',
            reply_markup=keyboards.yes_no_keyboard('townhouse_children')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T17,
    text=[
        'yes_townhouse_children',
        'no_townhouse_children',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_mortage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_children':
            await state.update_data(townhouse_children=True)
        if callback.data == 'no_townhouse_children':
            await state.update_data(townhouse_children=False)
        await callback.message.edit_text(
            '✏ Таунхаусы возможно купить по иптоеке?',
            reply_markup=keyboards.yes_no_keyboard('townhouse_mortage')
        )
        await TownHouseCallbackStates.next()


@dp.callback_query_handler(
    state=TownHouseCallbackStates.T18,
    text=[
        'yes_townhouse_mortage',
        'no_townhouse_mortage',
        'Отменить внесение объекта',
    ]
)
async def entering_townhouse_phone_number(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_townhouse_mortage':
            await state.update_data(townhouse_mortage=True)
        if callback.data == 'no_townhouse_mortage':
            await state.update_data(townhouse_mortage=False)
        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await TownHouseCallbackStates.next()


@dp.message_handler(state=TownHouseCallbackStates.T19)
async def entering_townhouse_agency_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(townhouse_owner_phone_number='+7' + message.text[1:])
            await message.answer(
                '✏ *Как зовут продавца таунхауса?*\n\n'
                'Его имя будет видно только тебе\n\n'
                + 'Для отмены внесения объекта напиши "Стоп"',
                parse_mode='Markdown'
            )
            await TownHouseCallbackStates.T20.set()
        else:
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.phone_number_entering_error(message.text),
                parse_mode='Markdown'
            )
            logging.error(f'🧐 Ошибка при вводе номера телефона {message.text}')
            await TownHouseCallbackStates.T19.set()


@dp.message_handler(state=TownHouseCallbackStates.T20)
async def entering_townhouse_rieltor_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(townhouse_owner_name=answer)
        await message.answer(
            '✏ Загрузи до 6 фото таунхауса\n\n'
        )
        await TownHouseCallbackStates.T22.set()


@dp.message_handler(state=TownHouseCallbackStates.T22, content_types=ContentType.PHOTO)
async def townhouse_report_photo(message: Message):
    global images
    key = str(message.from_user.id)
    images.setdefault(key, [])

    if len(images[key]) == 0:
        images[key].append(message.photo[-1].file_id)
        await message.answer(message_texts.on.get('code_word_text'))
        await TownHouseCallbackStates.T23.set()
    else:
        images[key].append(message.photo[-1].file_id)


@dp.message_handler(state=TownHouseCallbackStates.T23)
async def townhouse_base_updating(message: Message, state: FSMContext):

    await state.update_data(townhouse_code_word=message.text)
    user_id = message.from_user.id

    rieltor = Rieltors.objects.get(user_id=user_id)
    photo = images.get(str(user_id))
    images.pop(str(user_id))
    await state.update_data(townhouse_photo=photo)
    await state.update_data(
            townhouse_user_id=user_id,
            townhouse_rieltor_name=rieltor.name,
            townhouse_agency_name=rieltor.agency_name,
            townhouse_rieltor_phone_number=rieltor.phone_number
            )

    data = await state.get_data()

    # ЗАПИСЬ В БАЗУ И выдача
    await asyncio.sleep(2)
    if not DB_Worker.townhouse_to_db(data):
        await message.answer(
            message_texts.on.get('sorry_about_error')
        )
    else:
        album = MediaGroup()
        channel_album = MediaGroup()
        photo_list = data.get('townhouse_photo')
        for photo_id in photo_list:
            if photo_id == photo_list[-1]:
                album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.townhouse_adding_result_text(data)
                    ),
                    parse_mode='Markdown'
                )
                channel_album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.townhouse_message_for_channel(data)
                    ),
                    parse_mode='Markdown'
                )
            else:
                album.attach_photo(photo_id)
                channel_album.attach_photo(photo_id)
        await message.answer_media_group(media=album)
        await bot.send_media_group(TELEGRAM_CHANNEL_ID, channel_album)
    await state.finish()


# --------------------------------------------------------------------------
# ------------------- ОПРОС ПО УЧАСТКУ ------------------------------------
# --------------------------------------------------------------------------
@dp.callback_query_handler(text='Участок')
async def add_land(callback: CallbackQuery, state: FSMContext):
    """Ответ на кнопку добавления участка"""

    await state.update_data(land_reality_category=callback.data)
    await callback.message.edit_text(
        'Приготовьтесь ответить на несколько вопросов про ваш объект '
        + 'недвижимости. 😏 Это займёт не более 2-3х минут.\n\n'
        + '✏ *Укажите микрорайон расположения участка.*\n\n'
        + '✏ Если нужного микрорайона/села/деревни нет, напиши @davletelvir, добавлю.\n\n'
        + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
        reply_markup=keyboards.microregion_keyboard('object'),
        parse_mode='Markdown'
    )
    await LandCallbackStates.L1.set()


@dp.callback_query_handler(
    state=LandCallbackStates.L1,
    text=object_microregions.append('Отменить внесение объекта')
)
async def entering_land_street_name(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(land_microregion=callback.data)
        await callback.message.edit_text(
            '✏ *Напиши название улицы.*\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await LandCallbackStates.next()


@dp.message_handler(state=LandCallbackStates.L2)
async def entering_land_number(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(land_street_name=answer)
        await message.answer(
            '✏ *Напиши номер участка.*\n\n'
            + '🙅‍♂️ Чтобы отменить внесение объекта, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await LandCallbackStates.next()


@dp.message_handler(state=LandCallbackStates.L3)
async def entering_land_purpose(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if '"' in answer:
            formatting_answer = answer.replace('"', '')
            answer = formatting_answer

        if ' ' in answer:
            formatting_answer = answer.replace(' ', '')
            answer = formatting_answer

        answer = answer.upper()
        await state.update_data(land_number_name=answer)
        await message.answer(
            '✏ Укажи назначение участка',
            reply_markup=keyboards.purpose_choise_keyboard()
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L4,
    text=['ИЖС', 'СНТ, ДНТ', 'ЛПХ', 'Отменить внесение объекта']
)
async def entering_land_gas(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(land_purpose=callback.data)
        await callback.message.edit_text(
            '✏ По улице проходит газ',
            reply_markup=keyboards.yes_no_keyboard('land_gaz')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L5, text=[
        'yes_land_gaz',
        'no_land_gaz',
        'Отменить внесение объекта'
    ]
)
async def entering_land_waters(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_gaz':
            await state.update_data(land_gaz='Да')
        if callback.data == 'no_land_gaz':
            await state.update_data(land_gaz='Нет')
        await callback.message.edit_text(
            '✏ По улице проходит вода?',
            reply_markup=keyboards.yes_no_keyboard('land_water')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L6, text=[
        'yes_land_water',
        'no_land_water',
        'Отменить внесение объекта'
    ]
)
async def entering_land_sauna(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_water':
            await state.update_data(land_water='Да')
        if callback.data == 'no_land_water':
            await state.update_data(land_water='Нет')

        await callback.message.edit_text(
            '✏ На териитории участка баня или сауна',
            reply_markup=keyboards.yes_no_keyboard(item='land_sauna')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L7, text=[
        'yes_land_sauna',
        'no_land_sauna',
        'Отменить внесение объекта'
    ]
)
async def entering_land_garage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_sauna':
            await state.update_data(land_sauna='Есть')
        if callback.data == 'no_land_sauna':
            await state.update_data(land_sauna='Нет')

        await callback.message.edit_text(
            '✏ На териитории участка есть гараж?',
            reply_markup=keyboards.yes_no_keyboard(item='land_garage')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L8, text=[
        'yes_land_garage',
        'no_land_garage',
        'Отменить внесение объекта'
    ]
)
async def entering_land_fence(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_garage':
            await state.update_data(land_garage='Есть')
        if callback.data == 'no_land_garage':
            await state.update_data(land_garage='Нет')
        await callback.message.edit_text(
            '✏ Участок огорожен?',
            reply_markup=keyboards.yes_no_keyboard(item='land_fence')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L9, text=[
        'yes_land_fence',
        'no_land_fence',
        'Отменить внесение объекта'
    ]
)
async def entering_land_road(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_fence':
            await state.update_data(land_fence='Есть')
        if callback.data == 'no_land_fence':
            await state.update_data(land_fence='Нет')
        await callback.message.edit_text(
            '✏ К участку есть проезд?',
            reply_markup=keyboards.road_choice_keyboard()
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L10, text=[
        'Асфальт',
        'Неплохая насыпная дорога',
        'Неплохая грунтовая дорога',
        'Бездорожье, затрудняющее проезд',
        'Отменить внесение объекта'
    ]
)
async def entering_land_area(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        await state.update_data(land_road=callback.data)
        await callback.message.edit_text(
            '✏ *Введи площадь участка в сотках.* '
            + '(Значение площади из документации раздели на 100) '
            + 'Используйте разделитель "." для дробной и целой частей.',
            parse_mode='Markdown'
        )
        await LandCallbackStates.next()


@dp.message_handler(state=LandCallbackStates.L11)
async def entering_land_price(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = message.text
            if ',' in message.text:
                formatting_string = message.text.replace(',', '.')
                answer = float(formatting_string)
            else:
                answer = float(message.text)
            await state.update_data(land_area=answer)
            await message.answer(
                message_texts.on.get('enter_price'),
                parse_mode='Markdown'
            )
            await LandCallbackStates.next()
        except (ValueError) as e:
            await LandCallbackStates.L11.set()
            await message.answer(
                message_texts.on.get('area_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=LandCallbackStates.L12)
async def entering_land_description(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        try:
            answer = int(message.text)
            await state.update_data(land_price=answer)
            await message.answer(
                message_texts.entering_description_text('участка'),
                parse_mode='Markdown'
            )
            await LandCallbackStates.next()

        except (ValueError) as e:
            await LandCallbackStates.L12.set()
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


@dp.message_handler(state=LandCallbackStates.L13)
async def entering_land_encumbrance(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text
        if len(message.text) <= 200:
            await state.update_data(land_description=answer)
            await message.answer(
                '✏ На объекте есть обременение?',
                reply_markup=keyboards.yes_no_keyboard('land_encumbrance')
            )
            await LandCallbackStates.next()
        else:
            await message.answer(
                message_texts.character_limit(len(message.text))
            )
            logging.error('Превышение лимита знаков')
            await LandCallbackStates.L13.set()


@dp.callback_query_handler(
    state=LandCallbackStates.L14,
    text=[
        'yes_land_encumbrance',
        'no_land_encumbrance',
        'Отменить внесение объекта'
    ]
)
async def entering_land_children(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_encumbrance':
            await state.update_data(land_encumbrance=True)
        if callback.data == 'no_land_encumbrance':
            await state.update_data(land_encumbrance=False)
        await callback.message.edit_text(
            '✏ В собственности есть дети?',
            reply_markup=keyboards.yes_no_keyboard('land_children')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L15,
    text=[
        'yes_land_children',
        'no_land_children',
        'Отменить внесение объекта'
    ]
)
async def entering_land_mortage(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_children':
            await state.update_data(land_children=True)
        if callback.data == 'no_land_children':
            await state.update_data(land_children=False)
        await callback.message.edit_text(
            '✏ Дом возможно купить по иптоеке?',
            reply_markup=keyboards.yes_no_keyboard('land_mortage')
        )
        await LandCallbackStates.next()


@dp.callback_query_handler(
    state=LandCallbackStates.L16,
    text=[
        'yes_land_mortage',
        'no_land_mortage',
        'Отменить внесение объекта'
    ]
)
async def entering_land_phone_number(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отменить внесение объекта':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        if callback.data == 'yes_land_mortage':
            await state.update_data(land_mortage=True)
        if callback.data == 'no_land_mortage':
            await state.update_data(land_mortage=False)
        await callback.message.edit_text(
            message_texts.on.get('phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await LandCallbackStates.next()


@dp.message_handler(state=LandCallbackStates.L17)
async def entering_land_agency_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(land_owner_phone_number='+7' + message.text[1:])
            await message.answer(
                '✏ *Как зовут продавца участка?*\n\n'
                'Его имя будет видно только тебе\n\n'
                + 'Для отмены внесения объекта напиши "Стоп"',
                parse_mode='Markdown'
            )
            await LandCallbackStates.next()
        else:
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.phone_number_entering_error(message.text),
                parse_mode='Markdown'
            )
            logging.error(f'🧐 Ошибка при вводе номера телефона {message.text}')
            await LandCallbackStates.L17.set()


@dp.message_handler(state=LandCallbackStates.L18)
async def entering_land_rieltor_name(
    message: Message, state: FSMContext
):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
            'Действие отменено'
        )
        await state.finish()
    else:
        answer = message.text.title()
        await state.update_data(land_owner_name=answer)
        await message.answer(
            '✏ Загрузи до 6 фото участка\n\n'
        )
        await LandCallbackStates.L20.set()


@dp.message_handler(state=LandCallbackStates.L20, content_types=ContentType.PHOTO)
async def land_report_photo(message: Message):
    global images
    key = str(message.from_user.id)
    images.setdefault(key, [])

    if len(images[key]) == 0:
        images[key].append(message.photo[-1].file_id)
        await message.answer(message_texts.on.get('code_word_text'))
        await LandCallbackStates.L21.set()
    else:
        images[key].append(message.photo[-1].file_id)


@dp.message_handler(state=LandCallbackStates.L21)
async def land_base_updating(message: Message, state: FSMContext):

    await state.update_data(land_code_word=message.text)
    user_id = message.from_user.id

    rieltor = Rieltors.objects.get(user_id=user_id)
    photo = images.get(str(user_id))
    images.pop(str(user_id))
    await state.update_data(land_photo=photo)
    await state.update_data(
            land_user_id=user_id,
            land_rieltor_name=rieltor.name,
            land_agency_name=rieltor.agency_name,
            land_rieltor_phone_number=rieltor.phone_number
            )

    data = await state.get_data()

    # ЗАПИСЬ В БАЗУ И выдача
    await asyncio.sleep(2)
    if not DB_Worker.land_to_db(data):
        await message.answer(
            message_texts.on.get('sorry_about_error')
        )
    else:
        album = MediaGroup()
        channel_album = MediaGroup()
        photo_list = data.get('land_photo')
        for photo_id in photo_list:
            if photo_id == photo_list[-1]:
                album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.land_adding_result_text(data)
                    ),
                    parse_mode='Markdown'
                )
                channel_album.attach_photo(
                    photo_id,
                    caption='\n'.join(
                        message_texts.land_message_for_channel(data)
                    ),
                    parse_mode='Markdown'
                )
            else:
                album.attach_photo(photo_id)
                channel_album.attach_photo(photo_id)
        await message.answer_media_group(media=album)
        await bot.send_media_group(TELEGRAM_CHANNEL_ID, channel_album)
    await state.finish()

# -----------------------------------------------------------------------------
# -------------- МОИ ОБЪЕКТЫ --------------------------------------------------
# -----------------------------------------------------------------------------
@dp.message_handler(commands=['myobjects'])
async def entering_phone_number_for_searching(message: Message):
    DB_Worker.command_counting()

    apartment_queryset = Apartment.objects.filter(user_id=message.from_user.id)
    room_queryset = Room.objects.filter(user_id=message.from_user.id)
    house_queryset = House.objects.filter(user_id=message.from_user.id)
    townhouse_queryset = TownHouse.objects.filter(user_id=message.from_user.id)
    land_queryset = Land.objects.filter(user_id=message.from_user.id)

    apartment_count = apartment_queryset.count()
    room_count = room_queryset.count()
    house_count = house_queryset.count()
    townhouse_count = townhouse_queryset.count()
    land_count = land_queryset.count()

    total_count = apartment_count + room_count + house_count + townhouse_count + land_count

    data = {
        'total_count': total_count,
        'apartment_count': apartment_count,
        'room_count': room_count,
        'house_count': house_count,
        'townhouse_count': townhouse_count,
        'land_count': land_count,
    }

    await message.answer(
        message_texts.my_objects_text(data),
        disable_notification=True,
        parse_mode='Markdown'
    )
    for item in apartment_queryset:
        await asyncio.sleep(0.5)
        await message.answer(
            f'*{item.room_quantity} к.кв.* '
            + f'{item.street_name} д.{item.number_of_house}, '
            + f'{item.floor} этаж - *{int(item.price)} ₽*\n'
            + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
            disable_notification=True,
            parse_mode='Markdown'
        )

    for item in room_queryset:
        await asyncio.sleep(0.5)
        await message.answer(
            f'*Комната* {item.street_name} '
            + f'д.{item.number_of_house}, {item.floor} этаж - *{int(item.price)} ₽*\n'
            + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
            disable_notification=True,
            parse_mode='Markdown'
        )

    for item in house_queryset:
        await asyncio.sleep(0.5)
        await message.answer(
            f'*Дом* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
            + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
            disable_notification=True,
            parse_mode='Markdown'
        )

    for item in townhouse_queryset:
        await asyncio.sleep(0.5)
        await message.answer(
            f'*Таунхаус* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
            + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
            disable_notification=True,
            parse_mode='Markdown'
        )

    for item in land_queryset:
        await asyncio.sleep(0.5)
        await message.answer(
            f'*Участок* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
            + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
            disable_notification=True,
            parse_mode='Markdown'
        )
# -----------------------------------------------------------------------------
# --------------------УДАЛЕНИЕ ОБЪЕКТА-----------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['deleteobject'])
async def delete_object(message: Message):

    DB_Worker.command_counting()
    user_id = message.from_user.id

    cond1 = Apartment.objects.filter(user_id=user_id).exists()
    cond2 = Room.objects.filter(user_id=user_id).exists()
    cond3 = House.objects.filter(user_id=user_id).exists()
    cond4 = TownHouse.objects.filter(user_id=user_id).exists()
    cond5 = Land.objects.filter(user_id=user_id).exists()

    big_cond = cond1 or cond2 or cond3 or cond4 or cond5

    if big_cond:
        await message.answer(
            'Выбери объект для удаления:',
            reply_markup=keyboards.objects_list_keyboard(user_id)
        )
        await DeleteCallbackStates.D2.set()
    else:
        await message.answer(
            ' У тебя нет объектов в базе'
        )


@dp.callback_query_handler(state=DeleteCallbackStates.D2)
async def deleting_object(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        category = callback.data.split()[1]
        id = callback.data.split()[0]

        try:
            def get_number_of_house(category, obj):
                if (category == 'House') or (category == "TownHouse"):
                    return ''
                elif category == 'Lansd':
                    return obj.number_of_land
                return obj.number_of_house

            class_name = Output.str_to_class(category)
            obj = class_name.objects.get(pk=id)
            rieltor = Rieltors.objects.get(user_id=callback.from_user.id)
            Archive.objects.create(
                user_id=callback.from_user.id,
                rieltor_name=rieltor.name,
                agency_name=rieltor.agency_name,
                category=category,
                street_name=obj.street_name,
                object_number=get_number_of_house(category=category, obj=obj),
                owner_phone_number=obj.owner_phone_number,
                owner_name=obj.owner_name
            )
            class_name.objects.filter(pk=id).delete()
            await callback.message.edit_text(
                'Сделано!'
            )
            await state.finish()
        except Exception as e:
            await callback.message.answer(
                '❗ Во время удаления возникла ошибка, попробуй снова.'
                + 'Если ошибка поторится, напишиет об этом @davletelvir'
            )
            logging.error(
                f'Ошибка удаления объекта, {e}'
            )
            await DeleteCallbackStates.D2.set()
# -----------------------------------------------------------------------------
# -------------- РЕДАКТИРОВНАИЕ ЦЕНЫ-------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['editprice'])
async def edit_price(message: Message):

    DB_Worker.command_counting()
    user_id = message.from_user.id

    cond1 = Apartment.objects.filter(user_id=user_id).exists()
    cond2 = Room.objects.filter(user_id=user_id).exists()
    cond3 = House.objects.filter(user_id=user_id).exists()
    cond4 = TownHouse.objects.filter(user_id=user_id).exists()
    cond5 = Land.objects.filter(user_id=user_id).exists()

    big_cond = cond1 or cond2 or cond3 or cond4 or cond5

    if big_cond:
        await message.answer(
            '✏ Выберите объект, цену которого вы хотите изменить',
            reply_markup=keyboards.objects_list_keyboard(user_id)
        )
        await PriceEditCallbackStates.EP2.set()
    else:
        await message.answer(
            ' У тебя нет объектов в базе'
        )


@dp.callback_query_handler(
    state=PriceEditCallbackStates.EP2
)
async def entering_new_price(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        category = callback.data.split()[1]
        id = callback.data.split()[0]
        await state.update_data(searching_category=category)
        await state.update_data(searching_id=id)

        await callback.message.edit_text(
            '✏ *Напиши новую цену.*\n\nПолную цену цифрами, '
            + 'не сокращая, и без знаков Р, р, ₽, руб. и т.п.',
            parse_mode='Markdown'
        )
        await PriceEditCallbackStates.next()


@dp.message_handler(state=PriceEditCallbackStates.EP3)
async def price_updating_process(
    message: Message, state: FSMContext
):
    try:
        data = await state.get_data()
        class_name = Output.str_to_class(data.get('searching_category'))
        queryset = class_name.objects.get(pk=data.get('searching_id'))
        queryset.price = int(message.text)
        queryset.save()
        await message.answer(
            'Сделано!'
        )
        await state.finish()
    except Exception as e:
        await message.answer(
            '❗ Ошибка при вводе цены. \n\nВводимое значение должно '
            + 'быть числом. И не пиши "Р", "р", "руб". '
            + '\n\n✏ *Напиши новую цену заново*',
            parse_mode='Markdown'
        )
        logging.error(
            f'Ошибка при вводе новой цены, {e}'
        )
        await PriceEditCallbackStates.EP3.set()


@dp.callback_query_handler(text=['Отменить внесение объекта'])
async def cancel(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    await callback.message.edit_text('Действие отменено')
# -----------------------------------------------------------------------------
# -------------------ДОБАВЛЕНИЕ КЛИЕНТА----------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['addbuyer'])
async def add_buyer(message: Message):

    DB_Worker.command_counting()
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        await message.answer(
            '✏ *Введи имя покупателя.*\n\n'
            + '🙅‍♂️ Чтобы отменить внесение покупателя, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await Buyer.buyer_phone_number.set()


@dp.message_handler(state=Buyer.buyer_phone_number)
async def add_phone_number(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer('Действие по добавлению покупателя отменено')
        await state.finish()
    else:
        await state.update_data(buyer_name=message.text)
        await message.answer(
            message_texts.on.get('buyer_phone_number_entering_text'),
            parse_mode='Markdown'
        )
        await Buyer.category.set()


@dp.message_handler(state=Buyer.category)
async def add_category(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer('Действие по добавлению покупателя отменено')
        await state.finish()
    else:
        if re.match(r"^[0-9]+$", message.text):
            await state.update_data(buyer_phone_number=message.text)
            await message.answer(
                'В какой категории покупатель осуществляет поиск?\n\n'
                + 'Если ваш покупатель ищет в нескольких категориях, '
                + 'то заведи его требуемое количество раз с соответствующими категориями.',
                reply_markup=keyboards.buyer_searching_category(),
                parse_mode='Markdown'
            )
            await Buyer.limit.set()
        else:
            await message.answer(
                message_texts.phone_number_entering_error(
                    phone_number=message.text
                ),
                parse_mode='Markdown'
            )
            logging.error(f'Ошибка при вводе номера телефона {message.text}')
            await Buyer.category.set()


@dp.callback_query_handler(
    state=Buyer.limit,
    text=[
        'поиск_1к.кв.',
        'поиск_2к.кв.',
        'поиск_3к.кв.',
        'поиск_4к.кв.',
        'поиск_5к.кв.',
        'поиск_Комнаты, КГТ',
        'поиск_Дома',
        'поиск_Таунхаусы',
        'поиск_Участки',
        'Отменить внесение покупателя'
    ]
)
async def add_limit(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    if answer == 'Отменить внесение покупателя':
        await callback.message.edit_text(
            'Действие по добавлению покупателя отменено'
        )
        await state.finish()
    else:
        if answer in [
            'поиск_1к.кв.', 'поиск_2к.кв.', 'поиск_3к.кв.',
            'поиск_4к.кв.', 'поиск_5к.кв.'
        ]:
            await state.update_data(buyer_search_category=answer[6])
        elif answer == 'поиск_Комнаты, КГТ':
            await state.update_data(buyer_search_category='room')
        elif answer == 'поиск_Дома':
            await state.update_data(buyer_search_category='house')
        elif answer == 'поиск_Таунхаусы':
            await state.update_data(buyer_search_category='townhouse')
        else:
            await state.update_data(buyer_search_category='land')
        await callback.message.edit_text(
            '✏ Каков предел суммы покупателя?\n\n'
            + '*Напиши полное число со всеми нулями.*\n\n'
            + '🙅‍♂️ Чтобы отменить внесение покупателя, напиши "Стоп"',
            parse_mode='Markdown'
        )
        await Buyer.source.set()


@dp.message_handler(state=Buyer.source)
async def add_source(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer('Действие по добавлению покупателя отменено')
        await state.finish()
    else:
        try:
            await state.update_data(buyer_limit=int(message.text))
            await message.answer(
                '✏ Выбери форму расчёта покупателя',
                reply_markup=keyboards.buyer_source_choice_keyboard()
            )
            await Buyer.microregion.set()
        except (ValueError) as e:
            await Buyer.source.set()
            await bot.send_sticker(
                chat_id=message.from_user.id,
                sticker="CAACAgIAAxkBAAEHTQdjxlQRBRdVErSLTW969ee8S0hH1wACqiUAAvY9yUli7kZ2M0wiGC0E"
            )
            await message.answer(
                message_texts.on.get('price_entering_error'),
                parse_mode='Markdown'
            )
            logging.error(f'{e}')


checked = {}


@dp.callback_query_handler(
    state=Buyer.microregion,
    text=[
        'Ипотечный кредит',
        'Наличные деньги',
        'Только мат. кап.',
        'Др. сертификаты',
        'Отменить внесение покупателя'
        ]
)
async def add_microregion(callback: CallbackQuery, state: FSMContext):
    global checked
    key = str(callback.from_user.id)
    checked.setdefault(key, [])
    if callback.data == 'Отменить внесение покупателя':
        await callback.message.edit_text(
            'Действие по добавлению покупателя отменено'
        )
        await state.finish()
    else:
        await state.update_data(buyer_source=callback.data)
        data = await state.get_data()
        if data.get(
            'buyer_search_category'
        ) in ['1', '2', '3', '4', '5'] or data.get(
            'buyer_search_category'
        ) == 'room':
            await callback.message.edit_text(
                '✏ Укажи один или несколько микрорайонов поиска',
                reply_markup=keyboards.city_microregion_keyboard(checked_buttons=[])
            )
            checked[key] = []
            await Buyer.city_microregion.set()
        if data.get(
            'buyer_search_category'
        ) in ['house', 'townhouse', 'land']:
            await callback.message.edit_text(
                '✏ Укажи один или несколько микрорайонов поиска',
                reply_markup=keyboards.country_microregion_keyboard(checked_buttons=[])
            )
            checked[key] = []
            await Buyer.country_microregion.set()


@dp.callback_query_handler(
    state=Buyer.city_microregion,
    text=object_city_microregions_for_checking
)
async def city_microreg_checkbox(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    key = str(callback.from_user.id)
    if answer == 'Отменить внесение покупателя':
        await callback.message.edit_text(
            'Действие по добавлению покупателя отменено'
        )
        await state.finish()
    else:
        if answer == 'Подтвердить выбор':
            await state.update_data(microregions=checked[key])
            await callback.message.edit_text(
                '✏ *Добавь* необходимый, по твоему мнению, *комментарий* к покупателю'
                + '(банк, что продаёт, сумму ПВ, без ПВ, и т.п.)\n\n'
                + '🙅‍♂️ Чтобы отменить внесение покупателя, напиши "Стоп"',
                parse_mode='Markdown'
            )
            await Buyer.base_update.set()
        else:
            if '✅' in answer:
                checked[key].remove(answer.removeprefix('✅ '))
            else:
                checked[key].append(answer)
            await callback.message.edit_text(
                '✏ Укажи один или несколько микрорайонов поиска',
                reply_markup=keyboards.city_microregion_keyboard(checked_buttons=checked[key])
            )
            await Buyer.city_microregion.set()


@dp.callback_query_handler(
    state=Buyer.country_microregion,
    text=object_country_microregions_for_checking
)
async def country_microreg_checkbox(callback: CallbackQuery, state: FSMContext):
    answer = callback.data
    key = str(callback.from_user.id)
    if answer == 'Отменить внесение покупателя':
        await callback.message.edit_text(
            'Действие по добавлению покупателя отменено'
        )
        await state.finish()
    else:
        if answer == 'Подтвердить выбор':
            await state.update_data(microregions=checked[key])
            await callback.message.edit_text(
                '✏ *Добавь* необходимый, по твоему мнению, *комментарий* к покупателю'
                + '(банк, что продаёт, сумму ПВ, без ПВ, и т.п.)\n\n'
                + '🙅‍♂️ Чтобы отменить внесение покупателя, напиши "Стоп"',
                parse_mode='Markdown'
            )
            await Buyer.base_update.set()
        else:
            if '✅' in answer:
                checked[key].remove(answer.removeprefix('✅ '))
            else:
                checked[key].append(answer)
            await callback.message.edit_text(
                '✏ Укажи один или несколько микрорайонов поиска',
                reply_markup=keyboards.country_microregion_keyboard(checked_buttons=checked[key])
            )
            await Buyer.country_microregion.set()


@dp.message_handler(state=Buyer.base_update)
async def base_update(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer('Действие по добавлению покупателя отменено')
        await state.finish()
    else:
        if len(message.text) <= 500:
            await state.update_data(buyer_comment=message.text, buyer_user_id=message.from_user.id)
            data = await state.get_data()
            # добавление в базу субъекта
            if not DB_Worker.buyer_to_db(data):
                await message.answer(
                    message_texts.on.get('sorry_about_error')
                )
            else:
                await message.answer('\n'.join(message_texts.buyer_adding_result_text(data=data)))
                class_name = Output.str_to_class(data.get('buyer_search_category').title())
                if class_name == Apartment:
                    queryset = class_name.objects.filter(
                        price__lte=data.get('buyer_limit'),
                        room_quantity=data.get('buyer_search_category')
                    )
                else:
                    queryset = class_name.objects.filter(price__lte=data.get('buyer_limit'))
                if queryset.exists():
                    rieltor = Rieltors.objects.get(user_id=message.from_user.id)
                    for item in queryset:
                        await bot.send_message(
                            chat_id=item.user_id, text='🚀 У пользователя '
                            + f'@{message.from_user.username}, АН "{rieltor.agency_name}"'
                            + 'есть возможный '
                            + 'покупатель на твой объект\n'
                            + f'{Output.search_category_output(data.get("buyer_search_category"))}, '
                            + f'ул.{item.street_name}'
                        )

            await state.finish()
        else:
            await message.answer(
                'Комментарий по клиенту не должен превышать 500 знаков. '
                + '*Отредактируй и попробуй заново.*',
                parse_mode='Markdown'
            )
            await Buyer.base_update.set()
# -----------------------------------------------------------------------------
# -------------------УДАЛЕНИЕ КЛИЕНТА------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['deletebuyer'])
async def delete_buyer(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        if BuyerDB.objects.filter(user_id=user_id).exists():
            await message.answer(
                '✏ Выбери покупатея, которого вы хотите удалить',
                reply_markup=keyboards.buyer_list_keyboard(searching_user_id=user_id)
            )
            await DeleteBuyer.step2.set()
        else:
            await message.answer(
                '❗ У тебя нет клиентов в базе'
            )


@dp.callback_query_handler(state=DeleteBuyer.step2)
async def deleting_buyer(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        id = callback.data
        try:
            BuyerDB.objects.filter(pk=id).delete()
            await callback.message.edit_text(
                'Сделано!'
            )
            await state.finish()
        except Exception as e:
            await callback.message.answer(
                '❎ Во время удаления возникла ошибка, попробуй снова.'
                + 'Если ошибка поторится, напиши об этом @davletelvir'
            )
            logging.error(
                f'Ошибка удаления субъекта, {e}'
            )
            await DeleteBuyer.step2.set()
# -----------------------------------------------------------------------------
# -------------------МОИ КЛИЕНТЫ------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['mybuyers'])
async def my_buyers(message: Message):
    DB_Worker.command_counting()
    user_id = message.from_user.id
    queryset = BuyerDB.objects.filter(user_id=user_id)
    if queryset.exists():
        await message.answer(
            f'У тебя {queryset.count()} покупателя(-ей):'
        )
        for item in queryset:
            await asyncio.sleep(0.5)
            await message.answer(
                f'❇ _Дата внесения: {item.pub_date.date().strftime("%d-%m-%Y")}_\n'
                f'*Имя:* {item.buyer_name},\n'
                + f'*Тел:* {item.phone_number},\n\n'
                + f'*Объект поиска:* {Output.search_category_output(item.category)},\n'
                + f'*Область поиска:* {item.microregion},\n\n'
                + f'*Денежный лимит:* {item.limit} ₽,\n'
                + f'*Денежный ресурс:* {item.source},\n\n'
                + f'*Комментарий:* {item.comment}',
                disable_notification=True,
                parse_mode='Markdown'
            )
    else:
        await message.answer(
            '❗ У тебя нет клиентов в базе'
        )
# -----------------------------------------------------------------------------
# -------------------ОБЪЕКТЫ ДЛЯ КЛИЕНТА---------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['obj4mybuyer'])
async def obj_for_my_buyer(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        queryset = BuyerDB.objects.filter(user_id=user_id)
        if queryset.exists():
            await message.answer(
                '✏ Выбери покупатея, для которого ты хочешь посмотреть подходящие объекты',
                reply_markup=keyboards.buyer_list_keyboard(searching_user_id=user_id)
            )
            await ObjForBuyer.step2.set()
        else:
            await message.answer(
                '❗ У тебя нет клиентов в базе'
            )


@dp.callback_query_handler(state=ObjForBuyer.step2)
async def searching_for_buyer(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        id = callback.data
        buyer = BuyerDB.objects.filter(pk=id)
        buyer_category = await buyer.values('category').aget()
        buyer_limit = await buyer.values('limit').aget()

        class_name = Output.str_to_class(buyer_category.get('category').title())
        if class_name == Apartment:
            queryset = class_name.objects.filter(
                price__lte=(buyer_limit.get('limit')),
                room_quantity=buyer_category.get('category')
            )
        else:
            queryset = class_name.objects.filter(price__lte=(buyer_limit.get('limit')))

        if queryset.exists():
            await callback.message.edit_text('🔎 Возможно, покупателю подойдут такие варианты:')

            if class_name == House:
                for item in queryset:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.house_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await callback.message.answer_media_group(media=album)

            elif class_name == TownHouse:
                for item in queryset:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.townhouse_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await callback.message.answer_media_group(media=album)

            elif class_name == Land:
                for item in queryset:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.lands_search_result_text(
                                    item=item
                                ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await callback.message.answer_media_group(media=album)

            elif class_name == Apartment:
                for item in queryset:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.apartments_search_result_text(
                                        room_count=int(buyer_category.get('category')),
                                        item=item
                                    ),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await callback.message.answer_media_group(media=album)

            else:
                for item in queryset:
                    await asyncio.sleep(0.5)
                    album = MediaGroup()
                    photo_list = item.photo_id
                    for photo_id in photo_list:
                        if photo_id == photo_list[-1]:
                            album.attach_photo(
                                photo_id,
                                caption=message_texts.room_search_result_text(item=item),
                                parse_mode='Markdown'
                            )
                        else:
                            album.attach_photo(photo_id)
                    await callback.message.answer_media_group(media=album)
        else:
            await callback.message.edit_text(
                'К сожалению, ничего не нашёл в базе для твоего клиента'
            )
        await state.finish()
# -----------------------------------------------------------------------------
# -------------------КЛИЕНТЫ СОТРУДНИКОВ---------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['mycompbuyers'])
async def my_company_buyers(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        if Ceo.objects.filter(user_id=user_id).exists():
            await message.answer(
                'Выбери сотрудника',
                reply_markup=keyboards.worker_list(user_id)
            )
            await WorkersBuyers.step2.set()
        else:
            await message.answer(
                '❗ Этот раздел доступен только руководителю агентства. Ты не руководитель агентства'
            )


@dp.callback_query_handler(state=WorkersBuyers.step2)
async def worker_buyers(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        queryset = BuyerDB.objects.filter(user_id=callback.data)
        rieltor = Rieltors.objects.get(user_id=callback.data)
        if queryset.exists():
            await callback.message.answer(
                f'У *{rieltor.name}* {queryset.count()} покупателя(-ей):',
                disable_notification=True,
                parse_mode='Markdown'
            )
            for item in queryset:
                await asyncio.sleep(0.5)
                await callback.message.answer(
                    f'❇ _Дата внесения: {item.pub_date.date().strftime("%d-%m-%Y")}_\n'
                    f'*Имя:* {item.buyer_name},\n'
                    + f'*Тел:* {item.phone_number},\n\n'
                    + f'*Объект поиска:* {Output.search_category_output(item.category)},\n'
                    + f'*Область поиска:* {item.microregion},\n\n'
                    + f'*Денежный лимит:* {item.limit} ₽,\n'
                    + f'*Денежный ресурс:* {item.source},\n\n'
                    + f'*Комментарий:* {item.comment}',
                    disable_notification=True,
                    parse_mode='Markdown'
                )
            await state.finish()
        else:
            await callback.message.answer(
                f' У {rieltor.name} нет клиентов в базе'
            )
            await state.finish()
# -----------------------------------------------------------------------------
# -------------------ОБЪЕКТЫ СОТРУДНИКОВ---------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['mycompobjects'])
async def my_company_obj(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        if Ceo.objects.filter(user_id=user_id).exists():
            await message.answer(
                'Выбери сотрудника',
                reply_markup=keyboards.worker_list(user_id)
            )
            await WorkersObjects.step2.set()
        else:
            await message.answer(
                '❗ Этот раздел доступен только руководителю агентства. Ты не руководитель агентства'
            )


@dp.callback_query_handler(state=WorkersObjects.step2)
async def worker_objects(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        rieltor = Rieltors.objects.get(user_id=callback.data)

        apartment_queryset = Apartment.objects.filter(user_id=rieltor.user_id)
        room_queryset = Room.objects.filter(user_id=rieltor.user_id)
        house_queryset = House.objects.filter(user_id=rieltor.user_id)
        townhouse_queryset = TownHouse.objects.filter(user_id=rieltor.user_id)
        land_queryset = Land.objects.filter(user_id=rieltor.user_id)

        apartment_count = apartment_queryset.count()
        room_count = room_queryset.count()
        house_count = house_queryset.count()
        townhouse_count = townhouse_queryset.count()
        land_count = land_queryset.count()

        total_count = apartment_count + room_count + house_count + townhouse_count + land_count

        data = {
            'total_count': total_count,
            'apartment_count': apartment_count,
            'room_count': room_count,
            'house_count': house_count,
            'townhouse_count': townhouse_count,
            'land_count': land_count,
        }

        await callback.message.answer(
            message_texts.rieltors_objects_text(data, rieltor.name),
            disable_notification=True,
            parse_mode='Markdown'
        )
        for item in apartment_queryset:
            await asyncio.sleep(0.5)
            await callback.message.answer(
                f'✳ *{item.room_quantity} к.кв.* '
                + f'{item.street_name} д.{item.number_of_house}, '
                + f'{item.floor} этаж - *{int(item.price)} ₽*\n'
                # тут код для доступа к телефонам и именам
                + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                disable_notification=True,
                parse_mode='Markdown'
            )

        for item in room_queryset:
            await asyncio.sleep(0.5)
            await callback.message.answer(
                f'✳ *Комната* {item.street_name} '
                + f'д.{item.number_of_house}, {item.floor} этаж - *{int(item.price)} ₽*\n'
                + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                disable_notification=True,
                parse_mode='Markdown'
            )

        for item in house_queryset:
            await asyncio.sleep(0.5)
            await callback.message.answer(
                f'✳ *Дом* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
                + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                disable_notification=True,
                parse_mode='Markdown'
            )

        for item in townhouse_queryset:
            await asyncio.sleep(0.5)
            await callback.message.answer(
                f'✳ *Таунхаус* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
                + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                disable_notification=True,
                parse_mode='Markdown'
            )

        for item in land_queryset:
            await asyncio.sleep(0.5)
            await callback.message.answer(
                f'✳ *Участок* {item.microregion}, {item.street_name} - *{int(item.price)} ₽*\n'
                + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                disable_notification=True,
                parse_mode='Markdown'
            )
        await state.finish()
# -----------------------------------------------------------------------------
# -------------------АРХИВ---------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['archive'])
async def archive(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        if Ceo.objects.filter(user_id=user_id).exists():
            await message.answer(
                'Выбери сотрудника',
                reply_markup=keyboards.worker_list(user_id)
            )
            await ArchiveObjects.step2.set()
        else:
            await message.answer(
                '❗ Этот раздел доступен только руководителю агентства. Ты не руководитель агентства'
            )


@dp.callback_query_handler(state=ArchiveObjects.step2)
async def arcjive_objects(
    callback: CallbackQuery, state: FSMContext
):
    if callback.data == 'Отмена':
        await callback.message.edit_text(
            'Действие отменено'
        )
        await state.finish()
    else:
        rieltor = Rieltors.objects.get(user_id=callback.data)

        archive_qeryset = Archive.objects.filter(user_id=callback.data)
        if archive_qeryset.exists():
            await callback.message.answer(
                f'Список объектов, удалённых риелтором *{rieltor.name}*:',
                disable_notification=True,
                parse_mode='Markdown'
            )
            for item in archive_qeryset:
                await asyncio.sleep(0.5)
                await callback.message.answer(
                    f'*Категория: {item.category}*\n'
                    + f'*Название улицы:* {item.street_name} д.{item.object_number},\n'
                    + f'Продавец: {item.owner_name}, т.{item.owner_phone_number}',
                    disable_notification=True,
                    parse_mode='Markdown'
                )
        else:
            await callback.message.edit_text(
                f'❗ У риелтора {rieltor.name} нет удалённых объектов'
            )
        await state.finish()
# -----------------------------------------------------------------------------
# --------------------Регистрация руководителя---------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['ceoregistration'])
async def ceo_registration(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        if Ceo.objects.filter(user_id=message.from_user.id).exists():
            await message.answer(
                '❗ Ты уже зарегистрирован как руководитель'
            )
        else:
            await message.answer(
                ' ✏ *Введи кодовое слово* или напиши "Стоп" для отмены.\n\n'
                + 'Кодовые слова выдаются после проведения мероприятия по презентации бота в агентствах недвижимости\n\n'
                + 'Если у вас еще нет кодового слова, '
                + 'напишите @davletelvir.\n\n',
                parse_mode='Markdown'
            )
            await CeoRegistration.step2.set()


@dp.message_handler(state=CeoRegistration.step2)
async def ceo_reg_step2(message: Message, state: FSMContext):
    if message.text == 'Стоп' or message.text == 'стоп':
        await message.answer(
                'Действие отменено'
            )
        await state.finish()
    else:
        code_word = CodeWord.objects.filter(code_words=message.text)

        if code_word.exists():
            code_word.delete()

            rieltor = Rieltors.objects.get(user_id=message.from_user.id) # текущий пользователь регистрирующийся на руководителя
            rieltors = Rieltors.objects.filter(agency_name=rieltor.agency_name).exclude(user_id=message.from_user.id)

            cond_ceo = False
            cond_workers = False

            if DB_Worker.ceo_create(rieltor):
                cond_ceo = True

            if rieltors.exists():
                rieltors_list = []
                for item in rieltors:
                    if item.user_id != rieltor.user_id:
                        rieltors_list.append(item.name)
                rieltors_string = ', '.join(rieltors_list)
                if DB_Worker.workers_create(ceo_id=rieltor.user_id, rieltors=rieltors.exclude(user_id=rieltor.user_id)):
                    cond_workers = True

            if cond_ceo and cond_workers:
                await message.answer(
                    'ОК. Ты зарегистрирован как руководитель!'
                    + ' Приглашай своих сотрудников пользоваться ботом!\n\n'
                    + f'Ты уже можешь наблюдать за {rieltors_string}'
                )
            elif cond_ceo and not cond_workers:
                await message.answer(
                    'ОК. Ты зарегистрирован как руководитель!'
                    + ' Приглашай своих сотрудников пользоваться ботом!'
                )
            else:
                await message.answer(
                    '❎ Ошибка! Сообщи об этом @davletelvir'
                )
            await state.finish()
        else:
            await message.answer(
                '❎ Неверное кодово слово!\n\n'
                + 'Введи кодово слово или напиши "Стоп" для отмены.'
            )
            await CeoRegistration.step2.set()
# -----------------------------------------------------------------------------
# --------------------Мои сотрудники-------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['mycoworkers'])
async def my_coworkers(message: Message):
    if not Rieltors.objects.filter(user_id=message.from_user.id):
        await message.answer(
            '❗ Сначала надо зарегистрироваться. Для этого нажми на команду /registration'
        )
    else:
        DB_Worker.command_counting()
        user_id = message.from_user.id
        if Ceo.objects.filter(user_id=user_id).exists():
            ceo = Ceo.objects.get(user_id=user_id)
            rieltors = Rieltors.objects.filter(agency_name=ceo.agency_name).exclude(user_id=user_id)
            if rieltors.exists():
                for item in rieltors:
                    await message.answer(
                        text=f'У вас *{rieltors.count()}* сотрудник (-а, -ов) в системе:',
                        parse_mode='Markdown'
                    )
                    await message.answer(
                        text=f'username в телеграм: *@{item.username}*,\n'
                             + f'имя: *{item.name}*,\n'
                             + f'номер: *{item.phone_number}*',
                        parse_mode='Markdown'
                    )
            else:
                await message.answer(
                    'У вас нет зарегистрированных сотрудников в системе'
                )
        else:
            await message.answer(
                '❗ Этот раздел доступен только руководителю агентства. Ты не руководитель агентства'
            )
# -----------------------------------------------------------------------------
# --------------------агидель--------------------------------------------------
# -----------------------------------------------------------------------------


@dp.message_handler(commands=['aqidel'])
async def history_is_lie(message: Message):
    await message.answer(
        message_texts.aqidel()
    )


@dp.message_handler(commands=['speech'])
async def speech(message: Message):
    for item in message_texts.speech():
        await message.answer(
            item
        )
