import streamlit as st
import psycopg2
import pandas as pd

import os
from dotenv import load_dotenv

# Function to connect to the database
def connect_to_db(dbname, user, password, host, port):
    conn = psycopg2.connect(
        dbname=dbname, 
        user=user, 
        password=password, 
        host=host, 
        port=port
    )
    return conn

import psycopg2
import pandas as pd
import bcrypt

from datetime import date

def fetch_data(host, dbname, user, password, port, query):
    """
    Fetches data from a PostgreSQL database based on the provided query and connection details.
    
    Parameters:
    - host: Database host address
    - dbname: Database name
    - user: Username for the database
    - password: Password for the database
    - port: Port number for the database
    - query: SQL query to execute
    
    Returns:
    - A DataFrame containing the fetched data.
    """
    try:
        # Establishing the connection using the provided parameters
        conn = psycopg2.connect(
            host=host,
            dbname=dbname,
            user=user,
            password=password,
            port=port
        )
        # Creating a cursor and executing the query
        cur = conn.cursor()
        cur.execute(query)

        # Fetching all rows from the query result
        rows = cur.fetchall()

        # Getting column names
        colnames = [desc[0] for desc in cur.description]

        # Closing the cursor and the connection
        cur.close()
        conn.close()

        # Creating a DataFrame from the query result
        df = pd.DataFrame(rows, columns=colnames)
        return df
    except Exception as e:
        print(f"Database connection failed due to {e}")    
        return pd.DataFrame()  # Return an empty DataFrame in case of error


# Streamlit UI
def main(host, dbname, user, password, port):
    st.title("User Topics")

    # SQL query to fetch data
    query = "SELECT * FROM topics"
    
    # Fetching data
    data = fetch_data(host, dbname, user, password, port, query)
    
    # Display data
    #print(data)
    if not data.empty:
        df = pd.DataFrame(data, columns=['user_id', 'topic_name'])
        st.write(df)
    else:
        st.write("No data found.")

    if not data.empty:
        topic_list = df['topic_name'].tolist()
        print(topic_list)
        st.sidebar.selectbox('Wahl des Topics', options = topic_list)
    


# Streamlit UI
def main(host, dbname, user, password, port):
    st.title("User Topics")

    # SQL query to fetch data
    query = "SELECT * FROM topics"
    
    # Fetching data
    data = fetch_data(host, dbname, user, password, port, query)
    
    # Display data
    #print(data)
    if not data.empty:
        df = pd.DataFrame(data, columns=['user_id', 'topic_name'])
        st.write(df)
    else:
        st.write("No data found.")

    if not data.empty:
        topic_list = df['topic_name'].tolist()
        print(topic_list)
        st.sidebar.selectbox('Wahl des Topics', options = topic_list)


# Streamlit UI users
def main2(host, dbname, user, password, port):
    st.title("Users")

    # SQL query to fetch data
    query = "SELECT * FROM users"
    
    # Fetching data
    data = fetch_data(host, dbname, user, password, port, query)
    
    # Display data
    #print(data)
    if not data.empty:
        df = pd.DataFrame(data, columns=['user_id', 'username'])
        st.write(df)
    else:
        st.write("No data found.")

    if not data.empty:
        user_list = df['username'].tolist()
        print(user_list)
        st.sidebar.selectbox('Wahl des Users', options = user_list)


def insert_user_and_topics(dbname, user, password, host, port, username, user_password, topics):
    try:
        # Connect to your database
        conn = psycopg2.connect(
            dbname=dbname, 
            user=user, 
            password=password, 
            host=host, 
            port=port
        )
        conn.autocommit = False  # Start transaction control
        cur = conn.cursor()

        # Check if the user already exists
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        user_id = cur.fetchone()
        
        if user_id:
            print("User already exists.")
            user_id = user_id[0]  # Extract the user ID
        else:
            # Hash the user's password
            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt())

            # Insert a new user with the hashed password
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id;",
                        (username, hashed_password))
            user_id = cur.fetchone()[0]  # Get the id of the newly inserted user
            print("User added successfully.")

        # Insert topics for the user, checking for duplicates
        for topic in topics:
            # Check if the topic already exists for the user
            cur.execute("SELECT * FROM topics WHERE user_id = %s AND topic_name = %s;", (user_id, topic))
            if cur.fetchone():
                print(f"Topic '{topic}' already exists for user '{username}'.")
            else:
                cur.execute("INSERT INTO topics (user_id, topic_name) VALUES (%s, %s);",
                            (user_id, topic))
                print(f"Topic '{topic}' added for user '{username}'.")

        conn.commit()  # Commit the transaction

    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback the transaction on error
    finally:
        if conn:
            cur.close()
            conn.close()


def check_login(dbname, user, password, host, port, username, user_password):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        dbname=dbname, user=user, password=password, host=host
    )
    cur = conn.cursor()

    try:
        # Fetch the hashed password from the database for the given username
        cur.execute("SELECT password FROM users WHERE username = %s;", (username,))
        stored_password = cur.fetchone()  # fetchone() returns a tuple or None
        print('a')

        if stored_password:
            stored_password = stored_password[0]  # Extract the hashed password
            print('Stored password format:', type(stored_password), stored_password)

            # Convert the double escaped string to bytes if necessary
            if isinstance(stored_password, str) and stored_password.startswith('\\x'):
                stored_password = bytes.fromhex(stored_password[2:])
                print('Converted to bytes:', stored_password)
            elif isinstance(stored_password, str):
                # Convert string directly to bytes (if not double escaped)
                stored_password = stored_password.encode('utf-8')

            # Check if the provided password matches the stored hashed password
            if bcrypt.checkpw(user_password.encode('utf-8'), stored_password):#_bytes.encode('utf-8')):
                print('c')
                print("Login successful.")
                return True
            else:
                print('d')
                print("Invalid username or password.")
                return False
        else:
            print('e')
            print("Username does not exist.")
            return False
    except Exception as e:
        print('f')
        print(f"An error occurred: {e}")
        return False
    # finally:
    #     cur.close()
    #     conn.close()


def change_password(dbname, user, password, host, port, username, new_password):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    try:
        # Hash the new password
        new_hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        # Update the user's password in the database
        cur.execute("UPDATE users SET password = %s WHERE username = %s;", (new_hashed_password, username))
        conn.commit()  # Commit the transaction to save changes

        print("Password updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
    finally:
        cur.close()
        conn.close()


def add_topic_date(dbname, user, password, host, port, username, topic_name, topic_date=None):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    if topic_date is None:
        topic_date = date.today()  # Use today's date if no date is provided

    try:
        # Retrieve user ID based on username
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        user_id = cur.fetchone()
        if user_id is None:
            print("Username not found.")
            return

        # Insert new topic with date into the database
        cur.execute("INSERT INTO topics (user_id, topic_name, created_date) VALUES (%s, %s, %s);",
                    (user_id[0], topic_name, topic_date))
        conn.commit()  # Commit the transaction to save changes

        print("Topic added successfully with date.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
    finally:
        cur.close()
        conn.close()


def delete_user(dbname, user, password, host, port, username):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    try:
        # Delete user and all related topics by username
        # Start transaction
        cur.execute("BEGIN;")

        # Delete from topics first due to foreign key constraint
        cur.execute("DELETE FROM topics WHERE user_id IN (SELECT id FROM users WHERE username = %s);", (username,))
        
        # Delete the user
        cur.execute("DELETE FROM users WHERE username = %s;", (username,))

        conn.commit()  # Commit the transaction to save changes

        print("User and related topics deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
    finally:
        cur.close()
        conn.close()


def delete_topics_by_name(dbname, user, password, host, port, topic_name):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    try:
        # Delete topics by topic name
        cur.execute("DELETE FROM topics WHERE topic_name = %s;", (topic_name,))
        conn.commit()  # Commit the transaction to save changes

        print("Topics deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
    finally:
        cur.close()
        conn.close()


def delete_all_topics_for_user(dbname, user, password, host, port, username):
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    try:
        # Retrieve user ID based on username
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        user_id = cur.fetchone()
        if user_id is None:
            print("Username not found.")
            return

        # Delete all topics for the given user ID
        cur.execute("DELETE FROM topics WHERE user_id = %s;", (user_id[0],))
        conn.commit()  # Commit the transaction to save changes

        print("All topics for the user deleted successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()  # Rollback in case of error
    finally:
        cur.close()
        conn.close()

    


if __name__ == "__main__":

    #load_dotenv()
    # Assuming the .env file is one level up from the current script
    #dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    load_dotenv(dotenv_path)

    dbname = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST", 'db') 
    port = os.getenv("POSTGRES_PORT")

    # # Connect to your PostgreSQL database
    # conn = psycopg2.connect("dbname=dbname user=user password=password")
    # c = conn.cursor()

    # # Create tables, similar to the SQLite example
    # c.execute('''CREATE TABLE IF NOT EXISTS users
    #             (id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
    # c.execute('''CREATE TABLE IF NOT EXISTS topics
    #             (user_id INTEGER, topic_name TEXT,
    #             FOREIGN KEY(user_id) REFERENCES users(id))''')

    # # Commit and close
    # conn.commit()
    # c.close()
    # conn.close()


    # # Connect to the database with these details
    # conn = connect_to_db(dbname, user, password, host, port)

    main(host, dbname, user, password, port)

    main2(host, dbname, user, password, port)


