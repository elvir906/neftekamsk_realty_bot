import datetime as dt
import logging

from aiogram.dispatcher import FSMContext

from bot.models import (Apartment, Buyer, Ceo, Counter, House, Land, Rieltors,
                        Room, TownHouse)


class DB_Worker():
    def apartment_to_db(state_data: FSMContext) -> bool:
        try:
            Apartment.objects.create(
                room_quantity=state_data.get('room_count'),
                street_name=state_data.get('street_name'),
                number_of_house=state_data.get('house_number'),
                floor=state_data.get('floor'),
                area=state_data.get('area'),
                number_of_floors=state_data.get('floors'),
                price=state_data.get('price'),
                category=state_data.get('category'),
                description=state_data.get('description'),
                encumbrance=state_data.get('encumbrance'),
                children=state_data.get('children'),
                mortage=state_data.get('mortage'),
                rieltor_phone_number=state_data.get('rieltor_phone_number'),
                owner_phone_number=state_data.get('owner_phone_number'),
                owner_name=state_data.get('owner_name'),
                agency=state_data.get('agency_name'),
                author=state_data.get('rieltor_name'),
                photo_id=state_data.get('photo'),
                code_word=state_data.get('code_word'),
                user_id=state_data.get('user_id'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def room_to_db(state_data: FSMContext) -> bool:
        try:
            Room.objects.create(
                street_name=state_data.get('room_street_name'),
                number_of_house=state_data.get('room_house_number'),
                floor=state_data.get('room_floor'),
                area=state_data.get('room_area'),
                number_of_floors=state_data.get('room_floors'),
                price=state_data.get('room_price'),
                description=state_data.get('room_description'),
                encumbrance=state_data.get('room_encumbrance'),
                children=state_data.get('room_children'),
                mortage=state_data.get('room_mortage'),
                rieltor_phone_number=state_data.get('room_rieltor_phone_number'),
                owner_phone_number=state_data.get('room_owner_phone_number'),
                owner_name=state_data.get('room_owner_name'),
                agency_name=state_data.get('room_agency_name'),
                author=state_data.get('room_rieltor_name'),
                photo_id=state_data.get('room_photo'),
                code_word=state_data.get('room_code_word'),
                user_id=state_data.get('room_user_id'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def house_to_db(state_data: FSMContext) -> bool:
        try:
            House.objects.create(
                microregion=state_data.get('house_microregion'),
                street_name=state_data.get('house_street_name'),
                purpose=state_data.get('house_purpose'),
                finish=state_data.get('house_finish'),
                material=state_data.get('house_material'),
                gaz=state_data.get('house_gaz'),
                water=state_data.get('house_water'),
                sauna=state_data.get('house_sauna'),
                garage=state_data.get('house_garage'),
                fence=state_data.get('house_fence'),
                road=state_data.get('house_road'),
                area=state_data.get('house_area'),
                area_of_land=state_data.get('house_land_area'),
                price=state_data.get('house_price'),
                description=state_data.get('house_description'),
                encumbrance=state_data.get('house_encumbrance'),
                children=state_data.get('house_children'),
                mortage=state_data.get('house_mortage'),
                owner_phone_number=state_data.get('house_owner_phone_number'),
                owner_name=state_data.get('house_owner_name'),
                rieltor_phone_number=state_data.get('house_rieltor_phone_number'),
                agency_name=state_data.get('house_agency_name'),
                author=state_data.get('house_rieltor_name'),
                photo_id=state_data.get('house_photo'),
                code_word=state_data.get('house_code_word'),
                user_id=state_data.get('house_user_id'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def townhouse_to_db(state_data: FSMContext) -> bool:
        try:
            TownHouse.objects.create(
                microregion=state_data.get('townhouse_microregion'),
                street_name=state_data.get('townhouse_street_name'),
                purpose=state_data.get('townhouse_purpose'),
                finish=state_data.get('townhouse_finish'),
                material=state_data.get('townhouse_material'),
                gaz=state_data.get('townhouse_gaz'),
                water=state_data.get('townhouse_water'),
                sauna=state_data.get('townhouse_sauna'),
                garage=state_data.get('townhouse_garage'),
                fence=state_data.get('townhouse_fence'),
                road=state_data.get('townhouse_road'),
                area=state_data.get('townhouse_area'),
                area_of_land=state_data.get('townhouse_land_area'),
                price=state_data.get('townhouse_price'),
                description=state_data.get('townhouse_description'),
                encumbrance=state_data.get('townhouse_encumbrance'),
                children=state_data.get('townhouse_children'),
                mortage=state_data.get('townhouse_mortage'),
                owner_phone_number=state_data.get('townhouse_owner_phone_number'),
                owner_name=state_data.get('townhouse_owner_name'),
                rieltor_phone_number=state_data.get('townhouse_rieltor_phone_number'),
                agency_name=state_data.get('townhouse_agency_name'),
                author=state_data.get('townhouse_rieltor_name'),
                photo_id=state_data.get('townhouse_photo'),
                code_word=state_data.get('townhouse_code_word'),
                user_id=state_data.get('townhouse_user_id'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def land_to_db(state_data: FSMContext) -> bool:
        try:
            Land.objects.create(
                microregion=state_data.get('land_microregion'),
                street_name=state_data.get('land_street_name'),
                number_of_land=state_data.get('land_number_name'),
                purpose=state_data.get('land_purpose'),
                gaz=state_data.get('land_gaz'),
                water=state_data.get('land_water'),
                sauna=state_data.get('land_sauna'),
                garage=state_data.get('land_garage'),
                fence=state_data.get('land_fence'),
                road=state_data.get('land_road'),
                area_of_land=state_data.get('land_area'),
                price=state_data.get('land_price'),
                description=state_data.get('land_description'),
                encumbrance=state_data.get('land_encumbrance'),
                children=state_data.get('land_children'),
                mortage=state_data.get('land_mortage'),
                owner_phone_number=state_data.get('land_owner_phone_number'),
                owner_name=state_data.get('land_owner_name'),
                rieltor_phone_number=state_data.get('land_rieltor_phone_number'),
                agency_name=state_data.get('land_agency_name'),
                author=state_data.get('land_rieltor_name'),
                photo_id=state_data.get('land_photo'),
                code_word=state_data.get('land_code_word'),
                user_id=state_data.get('land_user_id'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def buyer_to_db(state_data: FSMContext) -> bool:
        try:
            Buyer.objects.create(
                user_id=state_data.get('buyer_user_id'),
                phone_number=state_data.get('buyer_phone_number'),
                buyer_name=state_data.get('buyer_name'),
                category=state_data.get('buyer_search_category'),
                limit=state_data.get('buyer_limit'),
                source=state_data.get('buyer_source'),
                microregion=", ".join(state_data.get('microregions')),
                comment=state_data.get('buyer_comment'),
                pub_date=dt.datetime.now()
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def rieltor_to_db(state_data: FSMContext) -> bool:
        try:
            Rieltors.objects.create(
                user_id=state_data.get('user_id'),
                agency_name=state_data.get('agency_name'),
                name=state_data.get('rieltor_name'),
                username=state_data.get('username'),
                phone_number=state_data.get('phone_number')
            )
            # выставляю к руководителю зарегистрированного риелтора
            ceo_list = Ceo.objects.filter(agency_name=state_data.get('agency_name'))
            if ceo_list.exists():
                for item in ceo_list:
                    worker_list = list(item.workers)
                    worker_list.append(state_data.get('user_id'))
                if '' in worker_list:
                    worker_list.remove('')
                item.workers = worker_list
                item.save()
            else:
                print('not exist')
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def ceo_create(rieltor):
        try:
            Ceo.objects.create(
                user_id=rieltor.user_id,
                name=rieltor.name,
                agency_name=rieltor.agency_name,
                workers=['']
            )
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def workers_create(ceo_id, rieltors):
        try:
            ids = []
            for item in rieltors:
                ids.append(item.user_id)
            ceo = Ceo.objects.get(user_id=ceo_id)
            ceo.workers = ids
            ceo.save()
            return True
        except Exception as e:
            logging.error(f'{e}')
            return False

    def command_counting():
        try:
            query_set = Counter.objects.get(pk=1)
            count = query_set.counter + 1
            query_set.counter = count
            query_set.save()
        except Exception as e:
            logging.error(f'{e}')
