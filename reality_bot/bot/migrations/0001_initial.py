# Generated by Django 4.1.6 on 2023-03-10 09:45

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_quantity', models.DecimalField(decimal_places=0, max_digits=1, verbose_name='Количество комнат')),
                ('street_name', models.CharField(max_length=100, verbose_name='Название улицы')),
                ('number_of_house', models.CharField(max_length=10, verbose_name='Номер дома')),
                ('floor', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Этаж')),
                ('number_of_floors', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Этажность дома')),
                ('area', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='площадь квартиры')),
                ('category', models.CharField(blank=True, max_length=100, verbose_name='Категория')),
                ('description', models.TextField(help_text='Описание', max_length='1000', verbose_name='Описание квартиры')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, verbose_name='Цена')),
                ('author', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('rieltor_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона риелтора')),
                ('agency', models.CharField(blank=True, max_length=100, verbose_name='Название агентства')),
                ('encumbrance', models.BooleanField(default='False', verbose_name='Обременение')),
                ('children', models.BooleanField(default='False', verbose_name='Дети в доле')),
                ('mortage', models.BooleanField(default='False', verbose_name='Ипотека')),
                ('pub_date', models.DateTimeField(verbose_name='Дата публикации')),
                ('photo_id', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('code_word', models.CharField(default='слово', max_length=200, verbose_name='кодовое слово')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
                ('visible', models.BooleanField(default='True', verbose_name='Видимость д/др. агентов')),
            ],
            options={
                'verbose_name': 'Квартира',
                'verbose_name_plural': 'Квартиры',
            },
        ),
        migrations.CreateModel(
            name='Archive',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(verbose_name='id')),
                ('rieltor_name', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('agency_name', models.CharField(blank=True, max_length=200, verbose_name='Название агентства')),
                ('category', models.CharField(blank=True, max_length=200, verbose_name='Категория')),
                ('street_name', models.CharField(blank=True, max_length=100, verbose_name='Название улицы')),
                ('object_number', models.CharField(max_length=10, verbose_name='Номер дома')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
            ],
            options={
                'verbose_name': 'Архив',
                'verbose_name_plural': 'Архив',
            },
        ),
        migrations.CreateModel(
            name='Buyer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(verbose_name='id')),
                ('phone_number', models.CharField(max_length=13, verbose_name='Номер телефона')),
                ('buyer_name', models.CharField(default='Не спросил', max_length=200, verbose_name='Имя покупателя')),
                ('category', models.CharField(max_length=100, verbose_name='Категория поиска')),
                ('limit', models.BigIntegerField(verbose_name='Предел суммы')),
                ('source', models.CharField(max_length=100, verbose_name='Источник оплаты')),
                ('microregion', models.CharField(max_length=100, verbose_name='микрорайон поиска')),
                ('comment', models.TextField(help_text='Описание', max_length='500', verbose_name='Описание')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата внесения')),
            ],
            options={
                'verbose_name': 'Покупатель',
                'verbose_name_plural': 'Покупатели',
            },
        ),
        migrations.CreateModel(
            name='Ceo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=15, verbose_name='id_руководителя')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Имя рукводителя')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Агентство недвижимости')),
                ('workers', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), blank=True, size=None)),
            ],
            options={
                'verbose_name': 'Руководитель',
                'verbose_name_plural': 'Руководители',
            },
        ),
        migrations.CreateModel(
            name='CodeWord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code_words', models.CharField(blank=True, max_length=8, verbose_name='Код')),
            ],
            options={
                'verbose_name': 'Кодовое слово',
                'verbose_name_plural': 'Кодовые слова',
            },
        ),
        migrations.CreateModel(
            name='Counter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('counter', models.BigIntegerField(default=0, verbose_name='Количество')),
            ],
            options={
                'verbose_name': 'Счётчик',
                'verbose_name_plural': 'Счётчики',
            },
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(blank=True, max_length=100, verbose_name='Название улицы')),
                ('area', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Площадь дома')),
                ('description', models.TextField(help_text='Описание', max_length='1000', verbose_name='Описание дома')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, verbose_name='Цена')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('rieltor_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона риелтора')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Название агентства')),
                ('encumbrance', models.BooleanField(verbose_name='Обременение')),
                ('children', models.BooleanField(verbose_name='Дети в доле')),
                ('mortage', models.BooleanField(verbose_name='Ипотека')),
                ('microregion', models.CharField(max_length=200, verbose_name='Микрорайон')),
                ('gaz', models.CharField(max_length=200, verbose_name='Степень газификации')),
                ('water', models.CharField(max_length=200, verbose_name='Водоснабжение')),
                ('road', models.CharField(max_length=200, verbose_name='Подъезд к участку')),
                ('area_of_land', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Площадь участка')),
                ('material', models.CharField(max_length=200, verbose_name='Материал изготовления')),
                ('finish', models.CharField(max_length=200, verbose_name='Степень завершённости')),
                ('purpose', models.CharField(max_length=200, verbose_name='Назначение участка')),
                ('sauna', models.CharField(max_length=200, verbose_name='Наличие бани')),
                ('garage', models.CharField(max_length=200, verbose_name='Наличие гаража')),
                ('fence', models.CharField(max_length=200, verbose_name='Ограждение')),
                ('photo_id', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('code_word', models.CharField(default='слово', max_length=200, verbose_name='кодовое слово')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
                ('visible', models.BooleanField(default='True', verbose_name='Видимость д/др. агентов')),
            ],
            options={
                'verbose_name': 'дом',
                'verbose_name_plural': 'Дома',
            },
        ),
        migrations.CreateModel(
            name='Individuals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('name', models.CharField(max_length=200, verbose_name='Имя')),
            ],
            options={
                'verbose_name': 'Частный риелтор',
                'verbose_name_plural': 'Частные риелторы',
            },
        ),
        migrations.CreateModel(
            name='Land',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(blank=True, max_length=100, verbose_name='Название улицы')),
                ('number_of_land', models.CharField(max_length=10, verbose_name='Номер дома')),
                ('description', models.TextField(help_text='Описание', max_length='1000', verbose_name='Описание')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, verbose_name='Цена')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('rieltor_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона риелтора')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Название агентства')),
                ('encumbrance', models.BooleanField(verbose_name='Обременение')),
                ('children', models.BooleanField(verbose_name='Дети в доле')),
                ('mortage', models.BooleanField(verbose_name='Ипотека')),
                ('microregion', models.CharField(max_length=200, verbose_name='Микрорайон')),
                ('gaz', models.CharField(max_length=200, verbose_name='Степень газификации')),
                ('water', models.CharField(max_length=200, verbose_name='Водоснабжение')),
                ('road', models.CharField(max_length=200, verbose_name='Подъезд к участку')),
                ('area_of_land', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Площадь участка')),
                ('purpose', models.CharField(max_length=200, verbose_name='Назначение участка')),
                ('fence', models.CharField(max_length=200, verbose_name='Ограждение')),
                ('sauna', models.CharField(default='Нет', max_length=200, verbose_name='Наличие бани')),
                ('garage', models.CharField(default='Нет', max_length=200, verbose_name='Наличие гаража')),
                ('photo_id', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('code_word', models.CharField(default='слово', max_length=200, verbose_name='кодовое слово')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
                ('visible', models.BooleanField(default='True', verbose_name='Видимость д/др. агентов')),
            ],
            options={
                'verbose_name': 'Участок',
                'verbose_name_plural': 'Участки',
            },
        ),
        migrations.CreateModel(
            name='Rieltors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=15, verbose_name='id_риелтора')),
                ('name', models.CharField(blank=True, max_length=200, verbose_name='Имя')),
                ('username', models.CharField(blank=True, max_length=200, verbose_name='Username')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Агентство недвижимости')),
                ('phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона')),
            ],
            options={
                'verbose_name': 'Риелтор',
                'verbose_name_plural': 'Риелторы',
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(max_length=100, verbose_name='Название улицы')),
                ('number_of_house', models.CharField(max_length=10, verbose_name='Номер дома')),
                ('floor', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Этаж')),
                ('number_of_floors', models.DecimalField(decimal_places=0, max_digits=2, verbose_name='Этажность дома')),
                ('area', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='площадь комнаты')),
                ('description', models.TextField(help_text='Описание', max_length='1000', verbose_name='Описание комнаты')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, verbose_name='Цена')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('rieltor_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона риелтора')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Название агентства')),
                ('encumbrance', models.BooleanField(verbose_name='Обременение')),
                ('children', models.BooleanField(verbose_name='Дети в доле')),
                ('mortage', models.BooleanField(verbose_name='Ипотека')),
                ('photo_id', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('code_word', models.CharField(default='слово', max_length=200, verbose_name='кодовое слово')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
                ('visible', models.BooleanField(default='True', verbose_name='Видимость д/др. агентов')),
            ],
            options={
                'verbose_name': 'Комната',
                'verbose_name_plural': 'Комнаты',
            },
        ),
        migrations.CreateModel(
            name='Subscriptors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=15, verbose_name='Подписчики')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Агентство недвижимости')),
            ],
            options={
                'verbose_name': 'Подписчики',
                'verbose_name_plural': 'Подписчики',
            },
        ),
        migrations.CreateModel(
            name='TownHouse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street_name', models.CharField(blank=True, max_length=100, verbose_name='Название улицы')),
                ('area', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Площадь дома')),
                ('description', models.TextField(help_text='Описание', max_length='1000', verbose_name='Описание дома')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=15, verbose_name='Цена')),
                ('pub_date', models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')),
                ('author', models.CharField(blank=True, max_length=200, verbose_name='Риелтор')),
                ('rieltor_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона риелтора')),
                ('agency_name', models.CharField(max_length=200, verbose_name='Название агентства')),
                ('encumbrance', models.BooleanField(verbose_name='Обременение')),
                ('children', models.BooleanField(verbose_name='Дети в доле')),
                ('mortage', models.BooleanField(verbose_name='Ипотека')),
                ('microregion', models.CharField(max_length=200, verbose_name='Микрорайон')),
                ('gaz', models.CharField(max_length=200, verbose_name='Степень газификации')),
                ('water', models.CharField(max_length=200, verbose_name='Водоснабжение')),
                ('road', models.CharField(max_length=200, verbose_name='Подъезд к участку')),
                ('area_of_land', models.DecimalField(decimal_places=1, max_digits=10, verbose_name='Площадь участка')),
                ('material', models.CharField(max_length=200, verbose_name='Материал изготовления')),
                ('finish', models.CharField(max_length=200, verbose_name='Степень завершённости')),
                ('purpose', models.CharField(max_length=200, verbose_name='Назначение участка')),
                ('sauna', models.CharField(max_length=200, verbose_name='Наличие бани')),
                ('garage', models.CharField(max_length=200, verbose_name='Наличие гаража')),
                ('fence', models.CharField(max_length=200, verbose_name='Ограждение')),
                ('photo_id', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, size=None)),
                ('code_word', models.CharField(default='слово', max_length=200, verbose_name='кодовое слово')),
                ('user_id', models.BigIntegerField(default=1, verbose_name='id')),
                ('owner_phone_number', models.CharField(blank=True, max_length=13, verbose_name='Номер телефона продавца')),
                ('owner_name', models.CharField(blank=True, max_length=200, verbose_name='Продавец')),
                ('visible', models.BooleanField(default='True', verbose_name='Видимость д/др. агентов')),
            ],
            options={
                'verbose_name': 'Таунхаус',
                'verbose_name_plural': 'Таунхаусы',
            },
        ),
    ]