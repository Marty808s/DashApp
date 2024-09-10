from importlib import metadata
import requests
import pymysql
import json
from datetime import datetime
import threading
from sqlalchemy import create_engine, Table, Column, Integer, String, Date, MetaData, text, insert  

# API pro generování random uživatelů a jejich dajů
url = 'https://randomuser.me/api/'

# Připojení k databázi
def get_database_connection():
    engine = create_engine('mysql+pymysql://admin:heslo@database:3306/random_users')
    return engine.connect()

# Inicializace MetaData
metadata = MetaData()

tab_users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('gender', String(10)),
                  Column('first_name', String(100)),
                  Column('last_name', String(100)),
                  Column('email', String(255)),
                  Column('dob', String(64)),
                  Column('registered', String(64)),
                  Column('phone', String(20)),
                  Column('nationality', String(10)),
                  Column('country', String(100)),
                  Column('postcode', String(20)),
                  autoload_with=get_database_connection()
                  )

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
    connection = get_database_connection()
    try:
        result = connection.execute(text("SELECT * FROM users"))
        data = result.fetchall()
        return data
    except Exception as e:
        print("Získání dat - chyba:", e)
    finally:
        connection.close()


def add_user():
    connection = get_database_connection()
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
        stmt = insert(tab_users).values(insert_data)
        connection.execute(stmt)
        print("Uživatel přidán!")
        connection.commit()
    except Exception as e:
        print("Chyba při insertu", e)
    finally:
        connection.close()


# Asynchroní přidávání uživatelů - v časovém intervalu
def schedule_user_addition():
    print("__Operace na vlákně__")
    threading.Timer(120, schedule_user_addition).start()
    add_user()

if __name__ == "__main__":
    db = get_database_connection()
    if db:
        print("Připojení k databázi")
        schedule_user_addition()
    else:
        print("Chyba při připojení k databázi")

