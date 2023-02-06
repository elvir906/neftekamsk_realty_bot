from django.contrib import admin

from .models import (Apartment, Archive, Buyer, Ceo, CodeWord, Counter, House,
                     Individuals, Land, Rieltors, Room, Subscriptors,
                     TownHouse)


class ApartmentAdmin(admin.ModelAdmin):
    list_display = (
        'room_quantity',
        'street_name',
        'number_of_house',
        'floor',
        'number_of_floors',
        'area',
        'category',
        'description',
        'encumbrance',
        'children',
        'mortage',
        'price',
        'owner_phone_number',
        'owner_name',
        'pub_date',
        'author',
        'rieltor_phone_number',
        'agency',
        'code_word',
        'user_id',
        'photo_id',
    )


class RoomAdmin (admin.ModelAdmin):
    list_display = (
        'street_name',
        'number_of_house',
        'floor',
        'number_of_floors',
        'area',
        'description',
        'encumbrance',
        'children',
        'mortage',
        'price',
        'owner_phone_number',
        'owner_name',
        'pub_date',
        'author',
        'rieltor_phone_number',
        'agency_name',
        'code_word',
        'user_id',
        'photo_id',
    )


class HouseAdmin(admin.ModelAdmin):
    list_display = (
        'microregion',
        'street_name',
        'area',
        'area_of_land',
        'purpose',
        'material',
        'finish',
        'gaz',
        'water',
        'road',
        'description',
        'sauna',
        'garage',
        'fence',
        'encumbrance',
        'children',
        'mortage',
        'price',
        'owner_phone_number',
        'owner_name',
        'pub_date',
        'author',
        'rieltor_phone_number',
        'agency_name',
        'code_word',
        'user_id',
        'photo_id',
    )


class TownHouseAdmin(admin.ModelAdmin):
    list_display = (
        'microregion',
        'street_name',
        'area',
        'area_of_land',
        'purpose',
        'material',
        'finish',
        'gaz',
        'water',
        'road',
        'description',
        'sauna',
        'garage',
        'fence',
        'encumbrance',
        'children',
        'mortage',
        'price',
        'owner_phone_number',
        'owner_name',
        'pub_date',
        'author',
        'rieltor_phone_number',
        'agency_name',
        'code_word',
        'user_id',
        'photo_id',
    )


class LandAdmin(admin.ModelAdmin):
    list_daisplay = (
        'microregion',
        'street_name',
        'area_of_land',
        'purpose',
        'gaz',
        'water',
        'road',
        'description',
        'fence',
        'encumbrance',
        'children',
        'mortage',
        'price',
        'owner_phone_number',
        'owner_name',
        'pub_date',
        'author',
        'rieltor_phone_number',
        'agency_name',
        'code_word',
        'user_id',
        'photo_id',
    )


class SubscriptorsAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'agency_name'
    )


class IndividualsAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'name'
    )


class BuyerAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'phone_number',
        'buyer_name',
        'category',
        'limit',
        'source',
        'microregion',
        'comment',
        'pub_date',
    )


class CeoAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'name',
        'agency_name',
        'workers'
    )


class RieltorAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'name',
        'username',
        'agency_name',
        'phone_number'
    )


class ArchiveAdmin(admin.ModelAdmin):
    list_display = (
        'user_id',
        'rieltor_name',
        'agency_name',
        'category',
        'street_name',
        'object_number',
        'owner_phone_number',
        'owner_name'
    )


class CodeWordsAdmin(admin.ModelAdmin):
    list_display = (
        'code_words',
    )


class CounterAdmin(admin.ModelAdmin):
    list_display = (
        'counter',
    )


admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(House, HouseAdmin)
admin.site.register(TownHouse, TownHouseAdmin)
admin.site.register(Land, LandAdmin)
admin.site.register(Subscriptors, SubscriptorsAdmin)
admin.site.register(Individuals, IndividualsAdmin)
admin.site.register(Buyer, BuyerAdmin)
admin.site.register(Ceo, CeoAdmin)
admin.site.register(Rieltors, RieltorAdmin)
admin.site.register(Archive, ArchiveAdmin)
admin.site.register(CodeWord, CodeWordsAdmin)
admin.site.register(Counter, CounterAdmin)
