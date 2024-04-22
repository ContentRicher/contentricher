import streamlit as st
import pages.login as login
import pages.frontend_experiments#main

# Define your pages
PAGES = {
    "Login Page": login.show,
    "Main Page": pages.frontend_experiments.show,
}

# Optional: Create a sidebar menu for navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

# Page loading based on selection
page = PAGES[selection]
page()