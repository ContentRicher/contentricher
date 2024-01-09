import streamlit as st
import wiki_functions as wf

import langchain_core
#from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
#from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import Literal, List


# Text input for article with default text
default_text = """Heidi Klum
Vorgezogenes Weihnachtsfest mit ihrer Familie

Heidi Klum hat mit ihrem Liebsten Tom Kaulitz und der Familie ein vorgezogenes Weihnachtsfest gefeiert. Auf Instagram gewährte das Model seinen Fans einen Einblick.
Eigentlich dauert es noch ein paar Tage bis zum Heiligabend. Doch Heidi Klum, 50, hat zusammen mit ihrem Mann Tom Kaulitz, 34, das Weihnachtsfest vorgezogen und bereits am Freitagabend, 15. Dezember, gefeiert. Eindrücke des Familienfestes teilte das Model in den sozialen Medien.

Heidi Klum: Raclette essen mit ihren Liebsten
Auf ihrem Instagram-Profil postete die vierfache Mama einen Clip vom gemeinsamen Weihnachtsessen. Auf einem festlich geschmückten runden Tisch ist alles für ein reichhaltiges Raclette gedeckt. Zwischen weihnachtlich grüner und roter Deko brutzeln sich die Gäste ihr Pfännchen mit allerlei leckeren Zutaten. "Familie Time", kommentiert Klum ihr Video und setzt ein Herz-Emoji dazu. Daraus ist zu schließen, dass neben Ehemann Tom auch die Kinder der GNTM-Jurorin dabei sind. Auch Toms Bruder Bill Kaulitz, 34, ist in einer Einstellung zu erahnen.
"""



if "user_input" not in st.session_state:
    st.session_state.user_input = default_text
if "wiki_input" not in st.session_state:
    st.session_state.wiki_input = ''
if "find_person_clicked" not in st.session_state:
    st.session_state.find_person_clicked = None

if "clicked" not in st.session_state:
    st.session_state.clicked = False

if "found_ents" not in st.session_state:
    st.session_state.found_ents = False

if "relevant_parts_to_show" not in st.session_state:
    st.session_state.relevant_parts_to_show = None

if "parsed_ents" not in st.session_state:
    st.session_state.parsed_ents = None


def set_clicked():
    st.session_state.clicked = True

def set_relevant_parts_to_show(context, wiki_title):
    text = wf.get_page_content(wiki_title)
    st.set_relevant_parts_to_show = st.session_state.relevant_parts_to_show = wf.get_relevant_parts(context, text[:8000], wiki_title)
    st.session_state.clicked = True

# Function to create dummy images
def create_dummy_image():
    # This function would create and return a dummy image
    # Here we just use a placeholder from the web for demonstration
    return 'https://via.placeholder.com/150'

st.set_page_config(page_title='MTLab WIP', layout="wide")#, initial_sidebar_state="expanded")#"collapsed")
# Set up the sidebar with links and a search bar
st.sidebar.title('Navigation')
st.sidebar.write('Login')
st.sidebar.write('Weitere Links...')
search_term = st.sidebar.text_input('Suchbegriff eingeben', '')
if st.sidebar.button('Suche starten'):
    st.sidebar.write('Suche nach:', search_term)

# Main area layout with two columns
left_column, middle_column, right_column = st.columns([1, 6, 3])

# Middle column for the article input and identified persons
with middle_column:
    st.title('Artikel und Personen')

    article_text = st.text_area("Artikel Text", height=400, value = st.session_state.user_input)


    # Button below the text area right
    if st.button('Finde Personen'):
        #st.success('Personen hervorgehoben.')
        st.session_state.find_person_clicked = True
        st.session_state.user_input = article_text ##TODO check if it always gets the current text
        st.session_state.parsed_ents = wf.get_all_wiki_urls(st.session_state.user_input)


    st.markdown("""___""")

    if st.session_state.find_person_clicked == True:

        parsed_ents = st.session_state.parsed_ents

        # Rows for identified persons and related articles
        col1, col2, col3 = st.columns([1, 2, 1])

        context = st.session_state.user_input

        ##not sure if this is helpful or obsolete...
        people = dict()
        people = st.session_state.parsed_ents.entities

        i = 0
        for i in range(len(people)):

            ent = people[i]

            person_name = ent.name

            col1, col2, col3 = st.columns([1, 2, 1])

            # Left column for face image
            with col1:                        
                st.write(person_name)
                if person_name == 'Heidi Klum': ##tmp only, to replace with retrieved image
                    st.image("../img/Heidi_Klum_by_Glenn_Francis.jpg", width=100, caption=person_name)
                else:
                    st.image(create_dummy_image(), width=100, caption=person_name)

            # Right column for articles related to the person
            with col2:

                st.write(f"Informationen zu {person_name}")
                # Relevant Information:

                ##for now, taking the first entry, TODO: possibly improve wikipedia disambiguation in backend function
                try:
                    wiki_url = ent.urls[0].url
                    wiki_url_title = ent.urls[0].title
                    wiki_line = f"""- [Wikipedia]({wiki_url}) - {wiki_url_title}"""
                except: 
                    wiki_url = ''
                    wiki_url_title = ''
                    wiki_line = f"""- Kein Eintrag auf Wikipedia gefunden."""


                insta_line = f""""""#- Instagram Eintrag - TODO"""
                    

                st.markdown(f"""
                """+ wiki_line +"""
                """+ insta_line + """
                """)

            with col3:
                st.write(f"Aktion")
                st.button(f"Relevante Auszüge", on_click=set_relevant_parts_to_show, args=(context, wiki_url_title), key = "button"+str(i))


            i += 1   

        st.session_state.found_ents = True

        # Button below the text area
        #if st.button('Artikel speichern'):
        #    st.success('Artikel gespeichert.')



# Rightmost column with Wikipedia information and buttons
with right_column:
    ##todo: It's not just about wiki_input

    if st.session_state.found_ents == True:

        original_title = '<p style="font-family:Courier; color:White; font-size: 45px;">_</p>'
        st.markdown(original_title, unsafe_allow_html=True)

        i = 0
        if st.session_state.clicked:# and not st.session_state.found_ents:


            text_to_show = wf.concatenate_relevant_parts_to_show(st.session_state.relevant_parts_to_show)
            text_area_input = st.text_area("Wikipedia Artikel", height=int(150*len(text_to_show)/(38*5)), placeholder = "", value = text_to_show)#st.session_state.wiki_input)
            st.session_state.text_area_input = text_area_input

            # Two buttons, one active and one inactive
            if st.button('Quelle anzeigen'):
                st.info('Quelle: Wikipedia')
            rcol1, rcolmid, rcol2 = st.columns([1, 1.4, 1])
            with rcol1:
                st.button('Rückgängig', disabled=True)
            with rcol2:
                if st.button('Integrieren', disabled=False):
                    st.session_state.user_input = "ABC"
                    st.experimental_rerun() ##Seite neu laden, nicht erst unten anzeigen.


            
print(st.session_state)

