import streamlit as st
from PIL import Image

import os
from dotenv import load_dotenv

from database_functions import check_login, insert_user_and_topics

if 'check_pw_page' not in st.session_state:
    st.session_state.check_pw_page = {}

if 'username' not in st.session_state.check_pw_page:
    st.session_state.check_pw_page["username"] = ""

if 'user_password' not in st.session_state.check_pw_page:
    st.session_state.check_pw_page["user_password"] = ""


hide_bar = """
           <style>
           [data-testid="stSidebar"] {display: none}
           [data-testid='collapsedControl'] {visibility:hidden;}
           </style>
           """

show_bar = """
           <style>
           [data-testid="stSidebar"] {display: block}
           [data-testid='collapsedControl'] {visibility:visible;}
           </style>
           """


def register_user(username, password):
    # Here implement the logic to register a new user in database
    # handle any errors that may occur during registration
    try:
        # Insert code to add user to database
        st.success("Registration successful! You can now login.")
        st.session_state["password_correct"] = True
    except Exception as e:
        st.error(f"Error occurred during registration: {e}")
        st.session_state["password_correct"] = False


def register():
    st.header("Registration")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if new_password != confirm_password:
        st.error("Passwords do not match.")
        return
    if st.button("Register"):
        # Call the register_user function to handle the registration
        register_user(new_username, new_password)


def register_user_page():
    st.header("Registration")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if new_password != confirm_password:
        st.error("Passwords do not match.")
        return
    if st.button("Register", key="reg2"):
        # Call the register_user function to handle the registration
        register_user(new_username, new_password)


def check_password():
    """Returns `True` if the user had the correct password."""

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

    def password_entered():
        st.session_state["password_correct"] = check_login(dbname, user, password, host, port, st.session_state["username"], st.session_state["password"])
        #print(st.session_state["password_correct"])
        del st.session_state["password"]  # don't store password
        #return res


    if "password_correct" not in st.session_state:
        # First run, show input for password.

        col1, col2 = st.columns([2.4, 1])

        with col1:
            st.header("Login")

        with col2:
            st.write("")


        username = st.text_input("**Username**", key="username")

        if 'check_pw_page' not in st.session_state:
            st.session_state.check_pw_page = {}

        if 'username' not in st.session_state.check_pw_page:
            st.session_state.check_pw_page["username"] = ""

        if 'user_password' not in st.session_state.check_pw_page:
            st.session_state.check_pw_page["user_password"] = ""

        st.session_state.check_pw_page["username"] = username

        password_input = st.text_input(
            "**Password**", type="password", on_change=password_entered, key="password"
        )
        st.session_state.check_pw_page["user_password"] = password_input
    

        st.markdown(hide_bar, unsafe_allow_html=True)

        # if st.button("Register"):
        #     # ## Redirect to registration page
        #     # #st.experimental_rerun()
        #     # ## Add redirection logic here
        #     # #register()
        #     # register_user_page()

        #     ##OR: insert new user with that password for now, with no topics:
        #     insert_user_and_topics(dbname, user, password, host, port, st.session_state["username"], st.session_state["password"], topics = [])

        #     pass

        return False
    elif not st.session_state["password_correct"]:

        col1, col2 = st.columns([2.4, 1])

        with col1:
            st.header("Login")

        with col2:
            pass
            #st.image(Image.open('./images/Logo_WeDaVinci-01--ultra_small_2.jpg'), width=200)
            # st.image(Image.open('./images/wdv_logo.png'))


        # Password not correct, show input + error.
        username = st.text_input("**Username**", key="username")#on_change=password_entered, key="username")

        password_input = st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )

        st.error("Invalid username or password")

        # if st.button("Register"):
        #     # ## Redirect to registration page
        #     # #st.experimental_rerun()
        #     # ## Add redirection logic here
        #     # #register()
        #     # register_user_page()

        #     ##Or insert new user with that password for now, with no topics:
        #     insert_user_and_topics(dbname, user, password, host, port, st.session_state["username"], st.session_state["password"], topics = [])

        #     st.success("New user created")
        # ###
        st.markdown(hide_bar, unsafe_allow_html=True)

        return False
    else:
        # Password correct.

        #st.success("Login successful!")

        ###
        st.markdown(show_bar, unsafe_allow_html=True)

        return True

