from importlib import metadata
import requests
import pymysql
import json
from datetime import datetime
import threading
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, text, insert, select  

# API pro generování random uživatelů a jejich dajů
url = 'https://randomuser.me/api/'

# Připojení k db
# nebo localhost:9906/database:3306
def get_database_connection():
    engine = create_engine('mysql+pymysql://admin:heslo@database:3306/random_users')
    return engine.connect()

# Session
session = Session(get_database_connection())

class Base(DeclarativeBase):
    pass

# ORM - tabulka users
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    gender = Column(String(10))
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255))
    dob = Column(String(64))
    registered = Column(String(64))
    phone = Column(String(20))
    nationality = Column(String(10))
    country = Column(String(100))
    postcode = Column(String(20))


# Vstup z API
def get_user():
    response = requests.get(url)
    data = response.json()
    user = data['results'][0]
    values = (
        user['gender'],
        user['name']['first'],
        user['name']['last'],
        user['email'],
        user['dob']['date'],
        user['registered']['date'],
        user['phone'],
        user['nat'],
        user['location']['country'],
        user['location']['postcode']  
    )
    return values


# API pro vizualizaci dat
def get_data():
    try:
        stmt = select(User)
        result = session.execute(stmt)
        users = result.scalars().all() # vrátím seznam objektů
        print(len(users))
        users_dict = {}  # slovník pro výstup

        for user in users:
            user_dict = {
                'id': user.id,
                'gender': user.gender,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'dob': user.dob,
                'registered': user.registered,
                'phone': user.phone,
                'nationality': user.nationality,
                'country': user.country,
                'postcode': user.postcode
            }
            users_dict[user.id] = user_dict

        print(users_dict)
        return users_dict

    except Exception as e:
        print("Získání dat - chyba:", e)
    finally:
        session.close()


def add_user():
    print("Připojení k databázi pro přidání uživatele.")
    values = get_user()
    print(f"Získané hodnoty z API: {values}")

    # Formátuji data
    dob_original = values[4]
    registered_original = values[5]

    # Pokus o formátování data, pokud selže, použij původní řetězec
    try:
        dob_formatted = datetime.strptime(dob_original, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except ValueError:
        dob_formatted = dob_original  # Ponechávám původní řetězec, pokud formátování selže
        print(f"Error formatting DOB: {dob_original}")

    try:
        registered_formatted = datetime.strptime(registered_original, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    except ValueError:
        registered_formatted = registered_original  # Ponechávám původní řetězec, pokud formátování selže
        print(f"Error formatting registered date: {registered_original}")

    values = values[:4] + (dob_formatted, registered_formatted) + values[6:]

    # Slovník pro insert
    insert_data = {
        'gender': values[0],
        'first_name': values[1],
        'last_name': values[2],
        'email': values[3],
        'dob': values[4],
        'registered': values[5],
        'phone': values[6],
        'nationality': values[7],
        'country': values[8],
        'postcode': values[9]
    }

    for i in insert_data:
        print(f"{i}: {insert_data[i]}")

    # Vložení do DB
    try:
        user = User(**insert_data)
        session.add(user)
        session.commit()
        print("Uživatel přidán!")
    except Exception as e:
        print("Chyba při insertu", e)
        session.rollback()
    finally:
        session.close()


# Asynchroní přidávání uživatelů - v časovém intervalu
def schedule_user_addition():
    print("__Operace na vlákně__")
    threading.Timer(600, schedule_user_addition).start()
    add_user()

if __name__ == "__main__":
    db = get_database_connection()
    if db:
        print("Připojení k databázi")
        schedule_user_addition()
    else:
        print("Chyba při připojení k databázi")

