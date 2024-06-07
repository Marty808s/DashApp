import requests
import pymysql
import json
from datetime import datetime
import threading

# API pro generování random uživatelů a jejich údajů
url = 'https://randomuser.me/api/'

# Připojení k databázi
def get_database_connection():
    return pymysql.connect(host='database',
                            user='admin',
                            password='heslo',
                            database='random_users',
                            port=3306)

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
    # Vytvořím spojení s databází
    cnx = get_database_connection()
    cursor = cnx.cursor()
    cursor.execute("SELECT * FROM users")
    # Získám všechna data z databáze - pomocí cursoru
    data = cursor.fetchall()
    cursor.close()
    return data


def add_user():
    cnx = get_database_connection()
    # Získám data uživatele z API
    values = get_user()
    sql = """
    INSERT INTO users (gender, first_name, last_name, email, dob, registered, phone, nationality, country, postcode)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    dob_original = values[4]
    registered_original = values[5]

    # Formátuji data
    try:
        dob_formatted = datetime.strptime(dob_original, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        registered_formatted = datetime.strptime(registered_original, "%Y-%m-%dT%H:%M:%S.%fZ").date()
        values = values[:4] + (dob_formatted, registered_formatted) + values[6:]
    except ValueError as e:
        print(f"Error formatting date: {e}")
        return

    cursor = cnx.cursor()
    try:
        # Vložím do DB
        cursor.execute(sql, values)
        print('Příkaz se vykonal!')
        cnx.commit()
    except Exception as e:
        print("Chyba při insertu", e)
    finally:
        cursor.close()
        cnx.close()


# Asynchroní přidávání uživatelů - v časovém intervalu
def schedule_user_addition():
    threading.Timer(10, schedule_user_addition).start()
    add_user()
    print("Uživatel přidán")
    get_data()

if __name__ == "__main__":
    db = get_database_connection()
    if db:
        print("Připojení k databázi")
        schedule_user_addition()
    else:
        print("Chyba při připojení k databázi")

