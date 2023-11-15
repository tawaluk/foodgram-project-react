import json
import psycopg2
from psycopg2 import Error

try:
    connection = psycopg2.connect(
        user="postgres",
        password="postgres",
        host="db",
        port="5432",
        database="postgres"
    )
    cursor = connection.cursor()

    with open('./data/ingredients.json') as json_file:
        data = json.load(json_file)

    columns = ['name', 'measurement_unit']
    for row in data:
        keys = tuple(row[c] for c in columns)
        cursor.execute(
            "INSERT INTO recipes_ingredient (name, measurement_unit)"
            "VALUES (%s, %s)", keys
        )

    connection.commit()


except (Exception, Error) as error:
    print("Что-то пошло не так! Ингредиенты", error)

finally:
    if connection:
        cursor.close()
        connection.close()
        print("ready for work")