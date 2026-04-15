import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="event_management",
        user="postgres",
        password="Dani@2318"
    )