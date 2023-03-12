from django.contrib.postgres.fields import ArrayField
from django.db import models


class Individuals(models.Model):
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Имя'
    )

    class Meta:
        verbose_name = 'Частный риелтор'
        verbose_name_plural = 'Частные риелторы'


class Subscriptors(models.Model):
    user_id = models.CharField(
        max_length=15,
        verbose_name='Подписчики'
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Агентство недвижимости'
    )

    class Meta:
        verbose_name = 'Подписчики'
        verbose_name_plural = 'Подписчики'


class Ceo(models.Model):
    user_id = models.CharField(
        max_length=15,
        verbose_name='id_руководителя'
    )
    name = models.CharField(
        verbose_name='Имя рукводителя',
        blank=True,
        max_length=200
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Агентство недвижимости'
    )
    workers = ArrayField(
        models.CharField(max_length=20),
        blank=True
    )

    class Meta:
        verbose_name = 'Руководитель'
        verbose_name_plural = 'Руководители'


class CodeWord(models.Model):
    code_words = models.CharField(
        blank=True,
        max_length=8,
        verbose_name='Код'
    )

    class Meta:
        verbose_name = 'Кодовое слово'
        verbose_name_plural = 'Кодовые слова'


class Rieltors(models.Model):
    user_id = models.CharField(
        max_length=15,
        verbose_name='id_риелтора'
    )
    name = models.CharField(
        verbose_name='Имя',
        blank=True,
        max_length=200
    )
    username = models.CharField(
        verbose_name='Username',
        blank=True,
        max_length=200
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Агентство недвижимости'
    )
    phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона',
        blank=True
    )

    class Meta:
        verbose_name = 'Риелтор'
        verbose_name_plural = 'Риелторы'


class Counter(models.Model):
    counter = models.BigIntegerField(
        default=0,
        verbose_name='Количество'
    )

    class Meta:
        verbose_name = 'Счётчик'
        verbose_name_plural = 'Счётчики'


class Apartment(models.Model):
    room_quantity = models.IntegerField(
        verbose_name='Количество комнат'
    )
    street_name = models.CharField(
        max_length=100,
        verbose_name='Название улицы'
    )
    number_of_house = models.CharField(
        max_length=10,
        verbose_name='Номер дома'
    )
    floor = models.IntegerField(
        verbose_name='Этаж'
    )
    number_of_floors = models.IntegerField(
        verbose_name='Этажность дома'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='площадь квартиры'
    )
    category = models.CharField(
        max_length=100,
        verbose_name='Категория',
        blank=True
    )
    description = models.TextField(
        max_length='1000',
        help_text='Описание',
        verbose_name='Описание квартиры'
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        verbose_name='Цена',
        blank=True
    )
    author = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    rieltor_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона риелтора',
        blank=True
    )
    agency = models.CharField(
        max_length=100,
        verbose_name='Название агентства',
        blank=True
    )
    encumbrance = models.BooleanField(
        verbose_name='Обременение',
        default='False'
    )
    children = models.BooleanField(
        verbose_name='Дети в доле',
        default='False'
    )
    mortage = models.BooleanField(
        verbose_name='Ипотека',
        default='False'
    )
    pub_date = models.DateTimeField(
        auto_now_add=False,
        verbose_name='Дата публикации'
    )
    photo_id = ArrayField(
        models.CharField(max_length=100),
        blank=True
    )
    code_word = models.CharField(
        max_length=200,
        verbose_name='кодовое слово',
        default='слово'
    )
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )
    visible = models.BooleanField(
        verbose_name='Видимость д/др. агентов',
        default='True'
    )

    class Meta:
        verbose_name = 'Квартира'
        verbose_name_plural = 'Квартиры'


class Room(models.Model):
    street_name = models.CharField(
        max_length=100,
        verbose_name='Название улицы'
    )
    number_of_house = models.CharField(
        max_length=10,
        verbose_name='Номер дома'
    )
    floor = models.IntegerField(
        verbose_name='Этаж'
    )
    number_of_floors = models.IntegerField(
        verbose_name='Этажность дома'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='площадь комнаты'
    )
    description = models.TextField(
        max_length='1000',
        help_text='Описание',
        verbose_name='Описание комнаты'
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        verbose_name='Цена',
        blank=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    rieltor_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона риелтора',
        blank=True
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Название агентства'
    )
    encumbrance = models.BooleanField(
        verbose_name='Обременение'
    )
    children = models.BooleanField(
        verbose_name='Дети в доле'
    )
    mortage = models.BooleanField(
        verbose_name='Ипотека'
    )
    photo_id = ArrayField(
        models.CharField(max_length=100),
        blank=True
    )
    code_word = models.CharField(
        max_length=200,
        verbose_name='кодовое слово',
        default='слово'
    )
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )
    visible = models.BooleanField(
        verbose_name='Видимость д/др. агентов',
        default='True'
    )

    class Meta:
        verbose_name = 'Комната'
        verbose_name_plural = 'Комнаты'


class House(models.Model):
    street_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Название улицы'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='Площадь дома'
    )
    description = models.TextField(
        max_length='1000',
        help_text='Описание',
        verbose_name='Описание дома'
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        verbose_name='Цена',
        blank=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    rieltor_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона риелтора',
        blank=True
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Название агентства'
    )
    encumbrance = models.BooleanField(
        verbose_name='Обременение'
    )
    children = models.BooleanField(
        verbose_name='Дети в доле'
    )
    mortage = models.BooleanField(
        verbose_name='Ипотека'
    )
    microregion = models.CharField(
        max_length=200,
        verbose_name='Микрорайон'
    )
    gaz = models.CharField(
        max_length=200,
        verbose_name='Степень газификации'
    )
    water = models.CharField(
        max_length=200,
        verbose_name='Водоснабжение'
    )
    road = models.CharField(
        max_length=200,
        verbose_name='Подъезд к участку'
    )
    area_of_land = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='Площадь участка'
    )
    material = models.CharField(
        max_length=200,
        verbose_name='Материал изготовления'
    )
    finish = models.CharField(
        max_length=200,
        verbose_name='Степень завершённости'
    )
    purpose = models.CharField(
        max_length=200,
        verbose_name='Назначение участка'
    )
    sauna = models.CharField(
        max_length=200,
        verbose_name='Наличие бани'
    )
    garage = models.CharField(
        max_length=200,
        verbose_name='Наличие гаража'
    )
    fence = models.CharField(
        max_length=200,
        verbose_name='Ограждение'
    )
    photo_id = ArrayField(
        models.CharField(max_length=100),
        blank=True
    )
    code_word = models.CharField(
        max_length=200,
        verbose_name='кодовое слово',
        default='слово'
    )
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )
    visible = models.BooleanField(
        verbose_name='Видимость д/др. агентов',
        default='True'
    )

    class Meta:
        verbose_name = 'дом'
        verbose_name_plural = 'Дома'


class TownHouse(models.Model):
    street_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Название улицы'
    )
    area = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='Площадь дома'
    )
    description = models.TextField(
        max_length='1000',
        help_text='Описание',
        verbose_name='Описание дома'
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        verbose_name='Цена',
        blank=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    rieltor_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона риелтора',
        blank=True

    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Название агентства'
    )
    encumbrance = models.BooleanField(
        verbose_name='Обременение'
    )
    children = models.BooleanField(
        verbose_name='Дети в доле'
    )
    mortage = models.BooleanField(
        verbose_name='Ипотека'
    )
    microregion = models.CharField(
        max_length=200,
        verbose_name='Микрорайон'
    )
    gaz = models.CharField(
        max_length=200,
        verbose_name='Степень газификации'
    )
    water = models.CharField(
        max_length=200,
        verbose_name='Водоснабжение'
    )
    road = models.CharField(
        max_length=200,
        verbose_name='Подъезд к участку'
    )
    area_of_land = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='Площадь участка'
    )
    material = models.CharField(
        max_length=200,
        verbose_name='Материал изготовления'
    )
    finish = models.CharField(
        max_length=200,
        verbose_name='Степень завершённости'
    )
    purpose = models.CharField(
        max_length=200,
        verbose_name='Назначение участка'
    )
    sauna = models.CharField(
        max_length=200,
        verbose_name='Наличие бани'
    )
    garage = models.CharField(
        max_length=200,
        verbose_name='Наличие гаража'
    )
    fence = models.CharField(
        max_length=200,
        verbose_name='Ограждение'
    )
    photo_id = ArrayField(
        models.CharField(max_length=100),
        blank=True
    )
    code_word = models.CharField(
        max_length=200,
        verbose_name='кодовое слово',
        default='слово'
    )
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )
    visible = models.BooleanField(
        verbose_name='Видимость д/др. агентов',
        default='True'
    )

    class Meta:
        verbose_name = 'Таунхаус'
        verbose_name_plural = 'Таунхаусы'


class Land(models.Model):
    street_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Название улицы'
    )
    number_of_land = models.CharField(
        max_length=10,
        verbose_name='Номер дома'
    )
    description = models.TextField(
        max_length='1000',
        help_text='Описание',
        verbose_name='Описание'
    )
    price = models.DecimalField(
        decimal_places=2,
        max_digits=15,
        verbose_name='Цена',
        blank=True
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    rieltor_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона риелтора',
        blank=True
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Название агентства'
    )
    encumbrance = models.BooleanField(
        verbose_name='Обременение'
    )
    children = models.BooleanField(
        verbose_name='Дети в доле'
    )
    mortage = models.BooleanField(
        verbose_name='Ипотека'
    )
    microregion = models.CharField(
        max_length=200,
        verbose_name='Микрорайон'
    )
    gaz = models.CharField(
        max_length=200,
        verbose_name='Степень газификации'
    )
    water = models.CharField(
        max_length=200,
        verbose_name='Водоснабжение'
    )
    road = models.CharField(
        max_length=200,
        verbose_name='Подъезд к участку'
    )
    area_of_land = models.DecimalField(
        max_digits=10,
        decimal_places=1,
        verbose_name='Площадь участка'
    )
    purpose = models.CharField(
        max_length=200,
        verbose_name='Назначение участка'
    )
    fence = models.CharField(
        max_length=200,
        verbose_name='Ограждение'
    )
    sauna = models.CharField(
        max_length=200,
        verbose_name='Наличие бани',
        default='Нет'
    )
    garage = models.CharField(
        max_length=200,
        verbose_name='Наличие гаража',
        default='Нет'
    )
    photo_id = ArrayField(
        models.CharField(max_length=100),
        blank=True
    )
    code_word = models.CharField(
        max_length=200,
        verbose_name='кодовое слово',
        default='слово'
    )
    user_id = models.BigIntegerField(
        verbose_name='id',
        default=1
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )
    visible = models.BooleanField(
        verbose_name='Видимость д/др. агентов',
        default='True'
    )

    class Meta:
        verbose_name = 'Участок'
        verbose_name_plural = 'Участки'


class Buyer(models.Model):
    user_id = models.BigIntegerField(
        verbose_name='id'
    )
    phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона'
    )
    buyer_name = category = models.CharField(
        max_length=200,
        verbose_name='Имя покупателя',
        default='Не спросил'
    )
    category = models.CharField(
        max_length=100,
        verbose_name='Категория поиска',
    )
    limit = models.BigIntegerField(
        verbose_name='Предел суммы'
    )
    source = models.CharField(
        max_length=100,
        verbose_name='Источник оплаты',
    )
    microregion = models.CharField(
        max_length=100,
        verbose_name='микрорайон поиска',
    )
    comment = models.TextField(
        max_length='500',
        help_text='Описание',
        verbose_name='Описание'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата внесения'
    )

    class Meta:
        verbose_name = 'Покупатель'
        verbose_name_plural = 'Покупатели'


class Archive(models.Model):
    user_id = models.BigIntegerField(
        verbose_name='id'
    )
    rieltor_name = models.CharField(
        verbose_name='Риелтор',
        blank=True,
        max_length=200
    )
    agency_name = models.CharField(
        max_length=200,
        verbose_name='Название агентства',
        blank=True
    )
    category = models.CharField(
        verbose_name='Категория',
        blank=True,
        max_length=200
    )
    street_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Название улицы'
    )
    object_number = models.CharField(
        max_length=10,
        verbose_name='Номер дома'
    )
    owner_phone_number = models.CharField(
        max_length=13,
        verbose_name='Номер телефона продавца',
        blank=True
    )
    owner_name = models.CharField(
        verbose_name='Продавец',
        blank=True,
        max_length=200
    )

    class Meta:
        verbose_name = 'Архив'
        verbose_name_plural = 'Архив'
