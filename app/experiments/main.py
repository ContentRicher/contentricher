import psycopg2
import os
from dotenv import load_dotenv

import login
from login import start
import database_functions as dbf



def setup_database(dbname, user, password, host, port, testuser, testuserpassword):
    """Set up the database tables and initial data."""
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host  # Name of the database service in docker-compose
    )

    cursor = conn.cursor()

    ##TODO: better way: have different roles, to be adapted from current version (only users and topics table, no roles table):
    # # Create tables
    # cursor.execute("""
    # CREATE TABLE IF NOT EXISTS roles (
    #     id SERIAL PRIMARY KEY,
    #     name VARCHAR(255) NOT NULL
    # );
    # CREATE TABLE IF NOT EXISTS users (
    #     id SERIAL PRIMARY KEY,
    #     username VARCHAR(255) NOT NULL,
    #     password VARCHAR(255) NOT NULL,
    #     role_id INTEGER,
    #     FOREIGN KEY (role_id) REFERENCES roles (id)
    # );
    # """)

    # # Insert admin role and user
    # cursor.execute("""
    # INSERT INTO roles (name) VALUES ('admin') ON CONFLICT DO NOTHING;
    # INSERT INTO users (username, password, role_id) VALUES ('admin', 'adminpass', 1) ON CONFLICT DO NOTHING;
    # """)

    ##Current older version with two simple tables, to add date to have multiple entries for same topic:
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS topics
                (user_id INTEGER, topic_name TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id))''')

    topics = []
    dbf.insert_user_and_topics(dbname, user, password, host, port, testuser, testuserpassword, topics)


    # Commit changes and close connection
    conn.commit()
    cursor.close()
    conn.close()

def main():
    """Main entry point for the application."""

    # Assuming the .env file is two levels up from the current script
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)

    dbname = os.getenv("POSTGRES_DB")
    print(dbname)
    user = os.getenv("POSTGRES_ADMINUSER")
    print(user)
    password = os.getenv("POSTGRES_ADMINPASSWORD")

    host = os.getenv("POSTGRES_HOST", 'db') 
    port = os.getenv("POSTGRES_PORT")
    testuser = os.getenv("POSTGRES_NORMALUSER")
    print(testuser)
    testuserpassword = os.getenv("POSTGRES_NORMALUSERPASSWORD")
    print(testuserpassword)

    print("before setup")
    print(dbname)
    print(user)
    print(password)
    print(port)
    print(testuser)
    print(testuserpassword)

    # Set up the database
    setup_database(dbname, user, password, host, port, testuser, testuserpassword)

    # Import the app module and start the application

    #login.start()
    start()

if __name__ == "__main__":

    main()
