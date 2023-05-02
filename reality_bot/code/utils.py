import sys

from aiogram.types import InlineKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton
from bot.models import (Apartment, Buyer, Ceo, House, Land, Rieltors, Room,
                        TownHouse)

object_country_microregions_for_checking = [
    'Актанышбаш',
    'Амзя',
    'Арлан',
    'Барьязибаш',
    'Восточный 1,2,3,4,5',
    'Зубовка',
    'Илистанбетово',
    'Калегино',
    'Калтаево',
    'Калтасы',
    'Кариево',
    'Карманово',
    'Касёво',
    'Краснохолмский',
    'Крым-Сараево',
    'Кумово',
    'Кутерем',
    'Кутлинка',
    'Лесная поляна',
    'Марино',
    'Михайловка',
    'Можары',
    'Музяк',
    'Николо-Берёзовка',
    'Новонагаево',
    'Раздолье',
    'Ротково',
    'С.Буртюк',
    'Саклово',
    'Саузбаш',
    'Староянзигитово',
    'Ташкиново',
    'Янаул',
    '✅ Актанышбаш',
    '✅ Амзя',
    '✅ Арлан',
    '✅ Барьязибаш',
    '✅ Восточный 1,2,3,4,5',
    '✅ Зубовка',
    '✅ Илистанбетово',
    '✅ Калегино',
    '✅ Калтаево',
    '✅ Калтасы',
    '✅ Кариево',
    '✅ Карманово',
    '✅ Касёво',
    '✅ Краснохолмский',
    '✅ Крым-Сараево',
    '✅ Кумово',
    '✅ Кутерем',
    '✅ Кутлинка',
    '✅ Лесная поляна',
    '✅ Марино',
    '✅ Михайловка',
    '✅ Можары',
    '✅ Музяк',
    '✅ Николо-Берёзовка',
    '✅ Новонагаево',
    '✅ Раздолье',
    '✅ Ротково',
    '✅ С.Буртюк',
    '✅ Саклово',
    '✅ Саузбаш',
    '✅ Староянзигитово',
    '✅ Ташкиново',
    '✅ Янаул',
    'Отменить внесение покупателя',
    'Подтвердить выбор'
]

object_microregions = [
    'Актанышбаш',
    'Амзя',
    'Арлан',
    'Барьязибаш',
    'Восточный 1,2,3,4,5',
    'Зубовка',
    'Илистанбетово',
    'Калегино',
    'Калтаево',
    'Калтасы',
    'Кариево',
    'Карманово',
    'Касёво',
    'Краснохолмский',
    'Крым-Сараево',
    'Кумово',
    'Кутерем',
    'Кутлинка',
    'Лесная поляна',
    'Марино',
    'Михайловка',
    'Можары',
    'Музяк',
    'Николо-Берёзовка',
    'Новонагаево',
    'Раздолье',
    'Ротково',
    'С.Буртюк',
    'Саклово',
    'Саузбаш',
    'Староянзигитово',
    'Ташкиново',
    'Янаул',
]

object_microregions_for_buyer = [
    'Актанышбаш',
    'Амзя',
    'Арлан',
    'Барьязибаш',
    'Восточный 1,2,3,4,5',
    'Зубовка',
    'Илистанбетово',
    'Калегино',
    'Калтаево',
    'Калтасы',
    'Кариево',
    'Карманово',
    'Касёво',
    'Краснохолмский',
    'Крым-Сараево',
    'Кумово',
    'Кутерем',
    'Кутлинка',
    'Лесная поляна',
    'Марино',
    'Михайловка',
    'Можары',
    'Музяк',
    'Николо-Берёзовка',
    'Новонагаево',
    'Раздолье',
    'Ротково',
    'С.Буртюк',
    'Саклово',
    'Саузбаш',
    'Староянзигитово',
    'Ташкиново',
    'Янаул',
]

object_city_microregions_for_checking = [
    'НФ БГУ', '2 шк', '3 шк', '4 шк', 'Белем',
    '6 шк', '7 шк', '8 шк', '9 шк', '10 шк',
    '11 шк', '12 шк', '13 шк', '14 шк', '16 шк',
    '17 шк', 'Башкирская гимназия',
    '✅ НФ БГУ', '✅ 2 шк', '✅ 3 шк', '✅ 4 шк', '✅ Белем',
    '✅ 6 шк', '✅ 7 шк', '✅ 8 шк', '✅ 9 шк', '✅ 10 шк',
    '✅ 11 шк', '✅ 12 шк', '✅ 13 шк', '✅ 14 шк', '✅ 16 шк',
    '✅ 17 шк', '✅ Башкирская гимназия', 'Отменить внесение покупателя',
    'Подтвердить выбор'
]

object_city_microregions = [
    'НФ БГУ', '2 шк', '3 шк', '4 шк', 'Белем',
    '6 шк', '7 шк', '8 шк', '9 шк', '10 шк',
    '11 шк', '12 шк', '13 шк', '14 шк', '16 шк',
    '17 шк', 'Башкирская гимназия'
]

agency_list = [
    'Азбука жилья',
    'Веста',
    'Визит',
    'Высота',
    'Доверие',
    'Доверие+',
    'Дом',
    'Империя недв.',
    'Квадро',
    'Квартал',
    'Кварт. вопр.',
    'Лидер',
    'Мегаполис',
    'Мир квартир',
    'Мой город',
    'Недвиж. и .',
    'Проспект',
    'Регион',
    'Резиденция',
    'Риелт',
    'Самолёт+',
    'Своё жильё',
    'SDELKA.DA',
    'Согласие',
    'Таунхаус',
    'Эксперт',
    'Этажи',
    'Частный риелтор'
]

apartment_category = [
    'МЖК',
    'Старой планировки',
    'Улучшенной планировки',
    'Новые дома',
    'Новые дома с инд.отоплением'
]

checked_apartment_category = [
    'МЖК',
    'Старой планировки',
    'Улучшенной планировки',
    'Новые дома',
    'Новые дома с инд.отоплением',
    '✅ МЖК',
    '✅ Старой планировки',
    '✅ Улучшенной планировки',
    '✅ Новые дома',
    '✅ Новые дома с инд.отоплением',
    '✴ Подтвердить выбор',
    '❇ Показать все'
]

# vk_club_ids = [196141794, ]  # тестовые сообщества
vk_club_ids = [
    196141794, 63457783, 63537905,
    29428739, 86544563, 64607782,
    65334690, 134547488, 89874972,
    20247557, 96536503, 139607111,
    123413608, 184458122, 119878560,
    48391487, 103044161, 110598482,
    132862886, 120068525,
]


class keyboards():
    def apartment_plan_category():
        keyboard = InlineKeyboardMarkup()

        for i in range(0, len(apartment_category)):
            keyboard.add(
                InlineKeyboardButton(
                    apartment_category[i],
                    callback_data=f'{apartment_category[i]}'
                    )
            )
        return keyboard

    def get_category_keyboard():
        """генерация клавиатуры выбора по категориям"""

        mc_count = Room.objects.filter(visible=True).count()
        house_count = House.objects.filter(visible=True).count()
        townhouse_count = TownHouse.objects.filter(visible=True).count()
        land_count = Land.objects.filter(visible=True).count()
        apartment_count = Apartment.objects.filter(visible=True).count()

        buttons_names = ['Квартиры', 'Комнаты', 'Дома', 'Таунхаусы', 'Участки']
        quantitative_indicator = [
            apartment_count,
            mc_count,
            house_count,
            townhouse_count,
            land_count
        ]
        keyboard = InlineKeyboardMarkup()

        for i in range(0, len(buttons_names)):
            keyboard.add(
                InlineKeyboardButton(
                    buttons_names[i]+' ('+str(quantitative_indicator[i])+')',
                    callback_data=f'{buttons_names[i]}'
                    )
            )
        return keyboard

    def get_rooms_count_keyboard():
        """Генерация клавиатуры выбора по количеству комнат квартир"""

        one_room_quantity = Apartment.objects.filter(room_quantity=1, visible=True).count()
        two_room_quantity = Apartment.objects.filter(room_quantity=2, visible=True).count()
        three_room_quantity = Apartment.objects.filter(room_quantity=3, visible=True).count()
        four_room_quantity = Apartment.objects.filter(room_quantity=4, visible=True).count()
        five_room_quantity = Apartment.objects.filter(room_quantity=5, visible=True).count()

        keyboard = InlineKeyboardMarkup()

        buttons = [
            '1-комнатные', '2-комнатные', '3-комнатные',
            '4-комнатные', '5-комнатные', '⏪ Назад'
        ]

        quantity = [
            one_room_quantity, two_room_quantity,
            three_room_quantity, four_room_quantity, five_room_quantity
        ]
        # кнопки количества квартир
        for i in range(0, len(buttons)-1):
            keyboard.add(
                InlineKeyboardButton(
                    buttons[i]+' ('+str(quantity[i])+')',
                    callback_data=f'{buttons[i]}'
                )
            )
        # кнопка назад
        keyboard.add(
            InlineKeyboardButton(
                buttons[len(buttons)-1],
                callback_data=f'{buttons[len(buttons)-1]}'
            )
        )
        return keyboard

    def add_category_keyboard():
        """Генерация клавиатуры для добавления объекта"""

        keyboard = InlineKeyboardMarkup()
        buttons = [
            'Квартиру', 'Комнату', 'Дом',
            'Таунхаус', 'Участок'
        ]

        for i in range(0, len(buttons)):
            keyboard.add(
                InlineKeyboardButton(
                    buttons[i], callback_data=f'{buttons[i]}'
                    )
            )
        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def add_rooms_count_keyboard():
        """
        Генерация клавиатуры на выбор количества
        комнат при добавления квартиры.
        """

        keyboard = InlineKeyboardMarkup()
        # Генерация кнопок с указанием этажей 1-5
        buttons = [InlineKeyboardButton(
            text=str(i),
            callback_data=f'add_{str(i)}_room'
        ) for i in range(1, 6)]
        keyboard.row(*buttons)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def floor_number_or_count_keyboard(object: str):
        """Генерация клавиатуры на выбор этажа или этажности дома"""

        #  Генерация названий кнопок и коллбэк_дат. Количество кнопок = 18
        keyboard = InlineKeyboardMarkup()
        buttons_text = [str(i) for i in range(1, 19)]
        if object == 'apartment_floor':
            callback_data = [str(i) + '_afloor' for i in range(1, 19)]
        if object == 'apartment_house_floors':
            callback_data = [str(i) + '_afloors' for i in range(1, 19)]
        if object == 'room_floor':
            callback_data = [str(i) + '_rfloor' for i in range(1, 19)]
        if object == 'room_house_floors':
            callback_data = [str(i) + '_rfloors' for i in range(1, 19)]

        # Генерация кнопок 18 этажей, шесть в три ряда.
        for j in range(0, 3):
            buttons = [InlineKeyboardButton(
                text=buttons_text[i],
                callback_data=callback_data[i]
            ) for i in range(j * 6, 6 + 6 * j)]
            keyboard.row(*buttons)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def yes_no_keyboard(item: str):
        """Генерация клавиатуры на да/нет по различным вопросам"""
        keyboard = InlineKeyboardMarkup()
        key_1 = InlineKeyboardButton(
            text='Да', callback_data=f'yes_{item}'
        )
        key_2 = InlineKeyboardButton(
            text='Нет', callback_data=f'no_{item}'
        )
        keyboard.row(key_1, key_2)
        if item == 'initial_payment':
            cancel_button = 'Отменить внесение клиента'
        else:
            cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def microregion_keyboard(item: str):
        """Генерация клавиатуры на выбор микрорайона при добавлении объекта"""

        keyboard = InlineKeyboardMarkup()

        buttons = [
            InlineKeyboardButton(
                text=object_microregions[i],
                callback_data=object_microregions[i]
                ) for i in range(0, len(object_microregions))
        ]

        keyboard.add(*buttons)
        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(text=cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def city_microregion_keyboard(checked_buttons: list):
        """Генерация клавиатуры на выбор микрорайона города"""
        keyboard = InlineKeyboardMarkup()
        new_kbd_btns = ['✅ ' + x if x in checked_buttons else x for x in object_city_microregions]
        buttons = [
            InlineKeyboardButton(
                text=new_kbd_btns[i],
                callback_data=new_kbd_btns[i]
                ) for i in range(0, len(new_kbd_btns) - 1)
        ]
        keyboard.add(*buttons)
        accept_button = 'Подтвердить выбор'
        keyboard.row(
            InlineKeyboardButton(text=accept_button, callback_data=accept_button)
        )
        cancel_button = 'Отменить внесение покупателя'
        keyboard.row(
            InlineKeyboardButton(text=cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def country_microregion_keyboard(checked_buttons: list):
        """Генерация клавиатуры на выбор района"""
        keyboard = InlineKeyboardMarkup()
        new_kbd_btns = ['✅ ' + x if x in checked_buttons else x for x in object_microregions_for_buyer]
        buttons = [
            InlineKeyboardButton(
                text=new_kbd_btns[i],
                callback_data=new_kbd_btns[i]
                ) for i in range(0, len(new_kbd_btns))
        ]
        keyboard.add(*buttons)
        accept_button = 'Подтвердить выбор'
        keyboard.row(
            InlineKeyboardButton(text=accept_button, callback_data=accept_button)
        )
        cancel_button = 'Отменить внесение покупателя'
        keyboard.row(
            InlineKeyboardButton(text=cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def apartment_plan_category_choice(checked_buttons: list, room_count):

        mjk_quantity = Apartment.objects.filter(category='МЖК', visible=True, room_quantity=room_count).count()
        stpl_quantity = Apartment.objects.filter(category='Старой планировки', visible=True, room_quantity=room_count).count()
        ulpl_quantity = Apartment.objects.filter(category='Улучшенной планировки', visible=True, room_quantity=room_count).count()
        new_house_quantity = Apartment.objects.filter(category='Новые дома', visible=True, room_quantity=room_count).count()
        ind_otopl_quantity = Apartment.objects.filter(category='Новые дома с инд.отоплением', visible=True, room_quantity=room_count).count()

        category_count = [
            mjk_quantity,
            stpl_quantity,
            ulpl_quantity,
            new_house_quantity,
            ind_otopl_quantity
        ]

        keyboard = InlineKeyboardMarkup()
        new_kbd_btns = ['✅ ' + x if x in checked_buttons else x for x in apartment_category]
        buttons = [
            InlineKeyboardButton(
                text=new_kbd_btns[i] + '  (' + str(category_count[i]) + ')',
                callback_data=new_kbd_btns[i]
                ) for i in range(0, len(new_kbd_btns))
        ]
        keyboard.row(buttons[0])
        keyboard.row(buttons[1])
        keyboard.row(buttons[2])
        keyboard.row(buttons[3])
        keyboard.row(buttons[4])
        accept_button = '❇ Показать все'
        keyboard.row(
            InlineKeyboardButton(text=accept_button, callback_data=accept_button)
        )
        accept_button = '✴ Подтвердить выбор'
        keyboard.row(
            InlineKeyboardButton(text=accept_button, callback_data=accept_button)
        )
        return keyboard

    def purpose_choise_keyboard():
        keyboard = InlineKeyboardMarkup()
        key_1 = InlineKeyboardButton(text='ИЖС', callback_data='ИЖС')
        key_2 = InlineKeyboardButton(text='СНТ, ДНТ', callback_data='СНТ, ДНТ')
        key_3 = InlineKeyboardButton(text='ЛПХ', callback_data='ЛПХ')

        keyboard.row(key_1, key_2, key_3)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def gaz_choise_keyboard():
        keyboard = InlineKeyboardMarkup()
        key_1 = InlineKeyboardButton(
            text='Газифицирован, дом отапливается',
            callback_data='Газифицирован, дом отапливается'
        )
        key_3 = InlineKeyboardButton(
            text='Улица газифицировна, дом - нет',
            callback_data='Улица газифицировна, дом - нет'
        )
        key_4 = InlineKeyboardButton(
            text='Улица не газифицирована',
            callback_data='Улица не газифицирована'
        )

        keyboard.row(key_1)
        keyboard.row(key_3)
        keyboard.row(key_4)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def material_choice_keyboard():
        keyboard = InlineKeyboardMarkup()
        material_buttons_text = [
            'Кирпич',
            'Заливной',
            'Блок',
            'Блок, облицованный кирпичом',
            'Дерево',
            'Дерево, облицованное кирпичом',
            'Другое'
        ]
        buttons = [
            InlineKeyboardButton(
                text=material_buttons_text[i],
                callback_data=material_buttons_text[i]
                ) for i in range(0, len(material_buttons_text) - 1)
        ]

        for i in range(0, len(buttons)):
            keyboard.row(buttons[i])

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def water_choice_keyboard():
        keyboard = InlineKeyboardMarkup()
        key_1 = InlineKeyboardButton(
            text='Да, центральное водоснабжение',
            callback_data='Водоснабжение центральное'
        )
        key_2 = InlineKeyboardButton(
            text='На участке есть колодец',
            callback_data='Колодец'
        )
        key_3 = InlineKeyboardButton(
            text='Вода проходит по улице, в дом - нет',
            callback_data='Вода по улице'
        )
        key_4 = InlineKeyboardButton(text='Воды нет', callback_data='Воды нет')

        keyboard.row(key_1)
        keyboard.row(key_2)
        keyboard.row(key_3)
        keyboard.row(key_4)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def road_choice_keyboard():
        keyboard = InlineKeyboardMarkup()
        key_1 = InlineKeyboardButton(
            text='Да, асфальт',
            callback_data='Асфальт'
        )
        key_2 = InlineKeyboardButton(
            text='Да, неплохая насыпная дорога',
            callback_data='Неплохая насыпная дорога'
        )
        key_3 = InlineKeyboardButton(
            text='Да, неплохая грунтовая дорога',
            callback_data='Неплохая грунтовая дорога'
        )
        key_4 = InlineKeyboardButton(
            text='Движение к дому затруднено',
            callback_data='Бездорожье, затрудняющее проезд'
        )
        keyboard.row(key_1)
        keyboard.row(key_2)
        keyboard.row(key_3)
        keyboard.row(key_4)

        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def objects_list_keyboard(searching_user_id: int):
        keyboard = InlineKeyboardMarkup()

        apartment_queryset = Apartment.objects.filter(
            user_id=searching_user_id
        )
        room_queryset = Room.objects.filter(
            user_id=searching_user_id
        )
        house_queryset = House.objects.filter(
            user_id=searching_user_id
        )
        townhouse_queryset = TownHouse.objects.filter(
            user_id=searching_user_id
        )
        land_queryset = Land.objects.filter(
            user_id=searching_user_id
        )

        buttons = []
        callback_data_string = []

        for item in apartment_queryset:
            buttons.append(f'{item.room_quantity}к.кв. '
                           + f'{item.street_name} {item.number_of_house} '
                           + f'- {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Apartment'])

        for item in room_queryset:
            buttons.append(f'Комната {item.street_name} '
                           + f'{item.number_of_house} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Room'])

        for item in house_queryset:
            buttons.append(f'Дом {item.microregion} '
                           + f'{item.street_name} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'House'])

        for item in townhouse_queryset:
            buttons.append(f'Таунхаус {item.microregion} '
                           + f'{item.street_name} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'TownHouse'])

        for item in land_queryset:
            buttons.append(f'Участок {item.microregion} '
                           + f'{item.street_name} {item.number_of_land} - '
                           + f'{int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Land'])

        for i in range(0, len(buttons)):
            keyboard.row(
                InlineKeyboardButton(
                    buttons[i],
                    callback_data=f'{callback_data_string[i][0]} '
                    + f'{callback_data_string[i][1]}'
                )
            )

        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def objects_list_autopost_keyboard(checked_buttons: list, searching_user_id: int):

        rieltor = Rieltors.objects.get(user_id=searching_user_id)

        # apartment_queryset = Apartment.objects.filter(
        #     user_id=searching_user_id
        # )
        # room_queryset = Room.objects.filter(
        #     user_id=searching_user_id
        # )
        # house_queryset = House.objects.filter(
        #     user_id=searching_user_id
        # )
        # townhouse_queryset = TownHouse.objects.filter(
        #     user_id=searching_user_id
        # )
        # land_queryset = Land.objects.filter(
        #     user_id=searching_user_id
        # )

        apartment_queryset = Apartment.objects.filter(
            agency=rieltor.agency_name, visible=True
        )
        room_queryset = Room.objects.filter(
            agency_name=rieltor.agency_name, visible=True
        )
        house_queryset = House.objects.filter(
            agency_name=rieltor.agency_name, visible=True
        )
        townhouse_queryset = TownHouse.objects.filter(
            agency_name=rieltor.agency_name, visible=True
        )
        land_queryset = Land.objects.filter(
            agency_name=rieltor.agency_name, visible=True
        )

        buttons = []
        callback_data_string = []

        for item in apartment_queryset:
            buttons.append(f'{item.room_quantity}к.кв. '
                           + f'{item.street_name}'[:3] + '.,'
                           + f' {item.number_of_house} '
                           + f'- {int(item.price)} ₽, '
                           + f'{item.author}'[:4])
            callback_data_string.append([item.pk, 'Apartment'])

        for item in room_queryset:
            buttons.append('Комн. '
                           + f'{item.street_name}'[:3] + '.,'
                           + f' {item.number_of_house} - {int(item.price)} ₽, '
                           + f'{item.author}'[:4])
            callback_data_string.append([item.pk, 'Room'])

        for item in house_queryset:
            buttons.append('Дом ' + f'{item.microregion}'[:4] + '.,'
                           + f' {item.street_name}'[:4] + '.,'
                           + f' - {int(item.price)} ₽, '
                           + f'{item.author}'[:4])
            callback_data_string.append([item.pk, 'House'])

        for item in townhouse_queryset:
            buttons.append('Тх. ' + f'{item.microregion}'[:4] + '.,'
                           + f' {item.street_name}'[:4] + '.,'
                           + f' - {int(item.price)} ₽, '
                           + f'{item.author}'[:4])
            callback_data_string.append([item.pk, 'TownHouse'])

        for item in land_queryset:
            buttons.append('Уч. ' + f'{item.microregion}'[:4] + '.,'
                           + f' {item.street_name}'[:4] + '.,'
                           + f' {item.number_of_land} - '
                           + f'{int(item.price)} ₽, '
                           + f'{item.author}'[:4])
            callback_data_string.append([item.pk, 'Land'])

        new_kbd_btns = ['✅ ' + x if x in checked_buttons else x for x in buttons]

        keyboard = InlineKeyboardMarkup()
        db_item = []

        for i in range(0, len(new_kbd_btns)):
            keyboard.row(
                InlineKeyboardButton(
                    text=new_kbd_btns[i],
                    callback_data=new_kbd_btns[i]
                )
            )
            if '✅' in new_kbd_btns[i]:
                db_item.append(f'{callback_data_string[i][0]} {callback_data_string[i][1]}')

        accept_button = '💫 Подтвердить выбор'
        keyboard.row(
            InlineKeyboardButton(accept_button, callback_data=accept_button)
        )

        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )

        return keyboard, db_item

    def objects_list_keyboard_for_change_visibleness(searching_user_id: int, visible: bool):
        keyboard = InlineKeyboardMarkup()

        apartment_queryset = Apartment.objects.filter(
            user_id=searching_user_id, visible=visible
        )
        room_queryset = Room.objects.filter(
            user_id=searching_user_id, visible=visible
        )
        house_queryset = House.objects.filter(
            user_id=searching_user_id, visible=visible
        )
        townhouse_queryset = TownHouse.objects.filter(
            user_id=searching_user_id, visible=visible
        )
        land_queryset = Land.objects.filter(
            user_id=searching_user_id, visible=visible
        )

        buttons = []
        callback_data_string = []

        for item in apartment_queryset:
            buttons.append(f'{item.room_quantity}к.кв. '
                           + f'{item.street_name} {item.number_of_house} '
                           + f'- {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Apartment'])

        for item in room_queryset:
            buttons.append(f'Комната {item.street_name} '
                           + f'{item.number_of_house} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Room'])

        for item in house_queryset:
            buttons.append(f'Дом {item.microregion} '
                           + f'{item.street_name} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'House'])

        for item in townhouse_queryset:
            buttons.append(f'Таунхаус {item.microregion} '
                           + f'{item.street_name} - {int(item.price)} ₽')
            callback_data_string.append([item.pk, 'TownHouse'])

        for item in land_queryset:
            buttons.append(f'Участок {item.microregion} '
                           + f'{item.street_name} {item.number_of_land} - '
                           + f'{int(item.price)} ₽')
            callback_data_string.append([item.pk, 'Land'])

        for i in range(0, len(buttons)):
            keyboard.row(
                InlineKeyboardButton(
                    buttons[i],
                    callback_data=f'{callback_data_string[i][0]} '
                    + f'{callback_data_string[i][1]}'
                )
            )

        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def pagination_keyboard(page, pages, category):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(text='⬅', callback_data=f'{category}_prev'),
            InlineKeyboardButton(text=f'{page} из {pages}', callback_data='1'),
            InlineKeyboardButton(text='➡', callback_data=f'{category}_next')
        )
        return keyboard

    def carousel_or_cascade_keyboard():
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(text='Каскадная с фото', callback_data='cascade'),
            InlineKeyboardButton(text='Карусель без фото', callback_data='carousel')
        )
        return keyboard

    def cancel_button():
        keyboard = InlineKeyboardMarkup()
        cancel_button = 'Отменить внесение объекта'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def buyer_searching_category():
        keyboard = InlineKeyboardMarkup()
        buttons_text = [
            '1к.кв.',
            '2к.кв.',
            '3к.кв.',
            '4к.кв.',
            '5к.кв.',
            'Комнаты, КГТ',
            'Дома',
            'Таунхаусы',
            'Участки'
        ]
        buttons = [InlineKeyboardButton(
            text=buttons_text[i],
            callback_data='поиск_' + buttons_text[i]
        ) for i in range(0, 5)]
        keyboard.row(*buttons)

        buttons = [InlineKeyboardButton(
            text=buttons_text[i],
            callback_data='поиск_' + buttons_text[i]
        ) for i in range(5, len(buttons_text))]
        keyboard.add(*buttons)

        cancel_button = 'Отменить внесение покупателя'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def buyer_source_choice_keyboard():
        keyboard = InlineKeyboardMarkup()
        buttons_text = [
            'Наличные деньги',
            'Ипотечный кредит',
            'Только мат. кап.',
            'Др. сертификаты',
        ]
        buttons = [
            InlineKeyboardButton(
                text=buttons_text[i],
                callback_data=buttons_text[i]
            ) for i in range(0, len(buttons_text))
        ]
        for i in range(0, len(buttons)):
            keyboard.row(buttons[i])

        cancel_button = 'Отменить внесение покупателя'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def buyer_list_keyboard(searching_user_id):
        buyer_queryset = Buyer.objects.filter(
            user_id=searching_user_id
        )
        buttons = []
        callback_data_string = []
        for item in buyer_queryset:
            buttons.append(f'👤 {item.buyer_name}, '
                           + f'ищет {Output.search_category_output(item.category)} за {item.limit} ₽')
            callback_data_string.append(item.pk)

        keyboard = InlineKeyboardMarkup()
        for i in range(0, len(buttons)):
            keyboard.row(
                InlineKeyboardButton(
                    buttons[i],
                    callback_data=callback_data_string[i]
                )
            )
        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def worker_list(ceo_user_id):
        worker_queryset = Ceo.objects.filter(user_id=ceo_user_id)
        worker_list = worker_queryset.values('workers').get()
        buttons = []
        callback_data_string = []
        for item in worker_list.get('workers'):
            rieltor_name = Rieltors.objects.get(user_id=item)
            buttons.append(f'👤 {rieltor_name.name}')
            callback_data_string.append(item)

        keyboard = InlineKeyboardMarkup()
        for i in range(0, len(buttons)):
            keyboard.row(
                InlineKeyboardButton(
                    buttons[i],
                    callback_data=callback_data_string[i]
                )
            )
        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def agency_choice_kb():
        buttons = []
        callback_data_string = []
        for item in agency_list:
            buttons.append(item)
            callback_data_string.append(item)
        keyboard = InlineKeyboardMarkup()

        row_count = (len(agency_list) // 3) + 1
        lastrow_len = len(agency_list) - ((len(agency_list) // 3) * 3)

        btn_cnt = 0

        for rc in range(0, row_count - 1):
            btns = []
            for i in range(rc * 3, rc * 3 + 3):
                btn_cnt += 1
                btns.append(
                    InlineKeyboardButton(
                        buttons[i],
                        callback_data=callback_data_string[i]
                    )
                )
            keyboard.row(*btns)

        btns = []
        if lastrow_len != 0:
            for i in range(0, lastrow_len):
                btns.append(
                    InlineKeyboardButton(
                        buttons[btn_cnt + i],
                        callback_data=callback_data_string[btn_cnt + i]
                    )
                )
            keyboard.row(*btns)

        cancel_button = 'Отмена'
        keyboard.row(
            InlineKeyboardButton(cancel_button, callback_data=cancel_button)
        )
        return keyboard

    def visible_or_not_kb():
        keyboard = InlineKeyboardMarkup()
        buttons = [
            'Да, сделать видимым для всех',
            'Нет, сделать видимым только мне',
            'Отмена'
        ]
        callback_data_string = ['True', 'False', 'Cancel']
        keyboard.row(InlineKeyboardButton(text=buttons[0], callback_data=callback_data_string[0]))
        keyboard.row(InlineKeyboardButton(text=buttons[1], callback_data=callback_data_string[1]))
        keyboard.row(InlineKeyboardButton(text=buttons[2], callback_data=callback_data_string[2]))
        return keyboard


class Output():
    def false_or_true(item: bool) -> str:
        if item:
            return 'Есть'
        return 'Нет'

    def false_or_true2(item: str) -> bool:
        if item == 'True':
            return True
        return False

    # Строку в название класса
    def str_to_class(str):
        if str in ['1', '2', '3', '4', '5']:
            str = 'Apartment'
        if str == 'Townhouse':
            str = 'TownHouse'
        return getattr(sys.modules[__name__], str)

    def search_category_output(item):
        if item == '1':
            return '1к.кв.'
        if item == '2':
            return '2к.кв.'
        if item == '3':
            return '3к.кв.'
        if item == '4':
            return '4к.кв.'
        if item == '5':
            return '5к.кв.'
        if item == 'room':
            return 'Комнату или КГТ'
        if item == 'house':
            return 'Дом'
        if item == 'townhouse':
            return 'Таунхаус'
        if item == 'land':
            return 'Участок'
        if item == 'apartment':
            return 'Квартира'
