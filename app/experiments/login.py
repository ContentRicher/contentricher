import streamlit as st
from PIL import Image
from time import sleep

# if 'check_pw_page' not in st.session_state:
#     st.session_state.check_pw_page = {}



from check_password import check_password

def start():
    # set sidebar collapsed before login
    if 'sidebar_state' not in st.session_state:
        #st.session_state.sidebar_state = 'collapsed'
        st.session_state.sidebar_state = 'expanded'


    st.set_page_config(page_title='🔐 Login', layout='centered', initial_sidebar_state=st.session_state.sidebar_state)

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

    ##checking the streamlit version:
    #st.write("Streamlit version:", st.__version__)
    if check_password()==True:
        #print(st.session_state["username"])
        # print('x')
        # username = st.session_state["username"]
        # print(username)
        # st.session_state.login_page.username = username#st.session_state["username"]

        #st.markdown(show_bar, unsafe_allow_html=True)

        #st.session_state.sidebar_state = 'expanded'

        col1, col2 = st.columns([1.5, 1])

        with col1:
            # Welcome message
            st.title("Welcome!")

        #sleep(0.25)
        st.switch_page("pages/frontend_experiments.py")#"pages/page1.py")


        # with col2:

        #     # Company logo
        #     st.write("")
        #     #st.image(Image.open('./images/Logo_WeDaVinci-01--small.png'), width=200)


def check():
    if check_password()==True:
        print(st.session_state["username"])
        print('y')

        #username = st.session_state["username"]
        #st.markdown(show_bar, unsafe_allow_html=True)

        #st.session_state.sidebar_state = 'expanded'

        col1, col2 = st.columns([1.5, 1])

        with col1:
            # Welcome message
            st.title("Welcome!")

        #sleep(0.25)
        st.switch_page("pages/frontend_experiments.py")#"pages/page1.py")


        # with col2:

        #     # Company logo
        #     st.write("")
        #     #st.image(Image.open('./images/Logo_WeDaVinci-01--small.png'), width=200)

if __name__ == "__main__":

    start()