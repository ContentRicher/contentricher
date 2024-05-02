import streamlit as st

import sys
sys.path.append("..") # Adds higher directory to python modules path.
import wiki_functions as wf
import database_functions as dbf
from wiki_functions import options, chosen_model
import vision_functions as vf

import langchain_core
#from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
#from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List

import os
from dotenv import load_dotenv
import os

import markdownify
import extra_streamlit_components as stx

import pandas as pd

#load_dotenv()
# Assuming the .env file is one level up from the current script
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

API_KEY=os.getenv("API_KEY")
MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")

chosen_model = 'GPT-3.5'#'Mistral Small'


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

if "relevant_parts_to_show_insta" not in st.session_state:
    st.session_state.relevant_parts_to_show_insta = None

if "parsed_ents" not in st.session_state:
    st.session_state.parsed_ents = None

if "parsed_instas" not in st.session_state:
    st.session_state.parsed_instas = None

if "insta_valids" not in st.session_state:
    st.session_state.insta_valids = dict()

if "insta_verifieds" not in st.session_state:
    st.session_state.insta_verifieds = dict()

if "wiki_images" not in st.session_state:
    st.session_state.wiki_images = None

if "model" not in st.session_state:
    st.session_state.model = None

if "isall" not in st.session_state:
    st.session_state.isall = False

if "button_find_disabled" not in st.session_state:
    st.session_state.button_find_disabled = False

if "found_a_wiki_entry" not in st.session_state:
    st.session_state.found_a_wiki_entry = False

if "include_insta" not in st.session_state:
    st.session_state.include_insta = True

if "check_insta" not in st.session_state:
    st.session_state.check_insta = False

if "wiki_lines" not in st.session_state:
    st.session_state.wiki_lines = None

if "wiki_lines_langs" not in st.session_state:
    st.session_state.wiki_lines_langs = None
    
if "insta_lines" not in st.session_state:
    st.session_state.insta_lines = None

if "person_sought" not in st.session_state:
    st.session_state.person_sought = None

if "integrated_text" not in st.session_state:
    st.session_state.integrated_text = None

# if 'active_tab' not in st.session_state:
#     st.session_state.active_tab = 'tab2'  # Set initial tab ID here

if 'btn_label' not in st.session_state:
    st.session_state.btn_label = "Edit Text"

if "user_edited_text" not in st.session_state:
    st.session_state.user_edited_text = st.session_state.user_input

if "diff_text" not in st.session_state:
    st.session_state.diff_text  = ""#st.session_state.user_input
if "diff_text2" not in st.session_state:
    st.session_state.diff_text2 = ""#st.session_state.user_input

# Initialize session state variables
if 'editing' not in st.session_state:                
    st.session_state.editing = False  # Track whether we are currently editing
if 'markdown_content' not in st.session_state:
    st.session_state.markdown_content = st.session_state.user_edited_text #"This is **Markdown** content."  # The Markdown text

if 'editing2' not in st.session_state:                
    st.session_state.editing2 = False  # Track whether we are currently editing
if 'markdown_content2' not in st.session_state:
    if 'diff_text2' in st.session_state:
        st.session_state.markdown_content2 = st.session_state.diff_text2
    else:
        st.session_state.markdown_content2 = st.session_state.user_edited_text #"This is **Markdown** content."  # The Markdown text

if 'editing4' not in st.session_state:                
    st.session_state.editing4 = False  # Track whether we are currently editing
if 'markdown_content4' not in st.session_state:
    st.session_state.markdown_content4 = st.session_state.user_input

if 'editing5' not in st.session_state:                
    st.session_state.editing5 = True#False  # Track whether we are currently editing; Set to true if we make it all one area
if 'markdown_content5' not in st.session_state:
    st.session_state.markdown_content5 = st.session_state.user_input
if 'last_confirmed' not in st.session_state:    
    ##maybe need to set it once I change it            
    st.session_state.last_confirmed = st.session_state.user_input

if 'first_edit' not in st.session_state:                
    st.session_state.first_edit = True  # Track whether we are currently editing


if 'integrated_text_tmp' not in st.session_state:
    st.session_state.integrated_text_tmp = ""
if 'last_confirmed_tmp' not in st.session_state:
    st.session_state.last_confirmed_tmp = ""
if 'diff_text_tmp' not in st.session_state:
    st.session_state.diff_text_tmp = ""
if 'diff_text2_tmp' not in st.session_state:
    st.session_state.diff_text2_tmp = ""


if 'article_text' not in st.session_state: 
    st.session_state.article_text = default_text 



def set_clicked():
    st.session_state.clicked = True


def set_relevant_parts_to_show(context, wiki_title, language='de', translate=True):
    print('in set_relevant_parts_to_show')
    try:
        text = wf.get_page_content(context, wiki_title, language)
        if len(text) > 0:
            st.session_state.relevant_parts_to_show = wf.get_relevant_parts(context, text[:8000], wiki_title, translate, chosen_model=st.session_state.model)#wf.translate_content(wf.get_relevant_parts(context, text[:8000], wiki_title), 'en', 'de')
    except:
        text = ''
        st.session_state.relevant_parts_to_show = None
        #print('could not retrieve page')
    st.session_state.clicked = True
    st.session_state.isall = False

def set_relevant_parts_to_show_insta(context, insta_name, person_name, post_links, post_filepaths, language='de', translate=True):
    try:
        st.session_state.relevant_parts_to_show_insta = None ##initialize to none
        text = vf.get_infos_from_insta_posts(insta_name, person_name, post_links, post_filepaths, include_source=True)
        if len(text) > 0:
            st.session_state.relevant_parts_to_show_insta = wf.get_relevant_parts(context, text[:8000], person_name, translate, source_insta_posts=True, chosen_model=st.session_state.model)
    except:
        text = ''
        st.session_state.relevant_parts_to_show_insta = None
        #print('could not retrieve page')
    st.session_state.clicked = True
    st.session_state.isall = False


# Function to create dummy images
def create_dummy_image():
    # This function would create and return a dummy image
    # Here we just use a placeholder from the web for demonstration
    return 'https://via.placeholder.com/150'

def sel_callback():
    st.session_state.isall = False#st.session_state.sel

def insta_callback():
    if st.session_state.include_insta == False:
        st.session_state.include_insta = True
    else:
        st.session_state.include_insta = False
    ##tmp for debugging:
    #st.session_state.include_insta = True
        
def get_wiki_line(ent):
    st.session_state.found_a_wiki_entry = False
    lang = None
    ##starting from the first entry, check if URL valid, else try the next ones
    num_iter = 0            
    while st.session_state.found_a_wiki_entry == False and num_iter <= 2 and num_iter < len(ent.urls):
        try:
            wiki_url = ent.urls[num_iter].url
            wiki_title = ent.urls[num_iter].title
            ##TODO: ensure Insta session works or else try a different method to check validity or show anyways
            st.session_state.found_a_wiki_entry = wf.check_wiki_valid(wiki_url)
            ##only if url is valid:
            if st.session_state.found_a_wiki_entry: 
                wiki_title = ent.urls[num_iter].title
                lang = ent.urls[num_iter].language
                wiki_line = f"""- [Wikipedia]({wiki_url}) - {wiki_title}"""
                #text = wf.get_page_content(context, wiki_title, lang)
            else: 
                wiki_line = f"""- Kein Eintrag auf Wikipedia gefunden."""

        except: 
            wiki_url = ''
            wiki_title = ''
            wiki_line = f"""- Kein Eintrag auf Wikipedia gefunden."""

        num_iter += 1
    return wiki_line, lang


def get_insta_line(instaent):
    st.session_state.found_a_insta_entry = False
    #lang = 'de'
    ##for now, taking the first entry, TODO: check if URL valid, else probably also the rest is not existing
    num_iter = 0            


    while st.session_state.found_a_insta_entry == False and num_iter <= 2 and num_iter < len(ent.urls):
        insta_line = f"""- Kein Eintrag auf Instagram gefunden."""
        insta_url = ""
        try:
            insta_url = instaent.urls[num_iter].url
            #insta_title = instaent.urls[num_iter].title

            ##TODO: ensure Insta session works or else try a different method to check validity or show anyways
            #st.session_state.found_a_insta_entry = True##TODO: find the right call to longer version of: wf.check_insta_valid(insta_url)
            
            ##TODO: think of when not to verify, e.g. if no Insta Sessio provided, but avert user it's not sure
            if st.session_state.check_insta == True:
                try: 
                    insta_valid, insta_verified = wf.check_insta_valid_and_verified(insta_url, entered_insta_username, entered_insta_password)
                except: 
                    ##Put default values if check_insta is into desired:
                    insta_valid = True
                    insta_verified = False
            else:
                ##Put default values if check_insta is into desired:
                insta_valid = True
                insta_verified = False

            ##if checking is desired, return only if also verified
            if st.session_state.check_insta and insta_valid and insta_verified: 
                st.session_state.found_a_insta_entry = True
            elif st.session_state.check_insta and (num_iter == 2 or num_iter == len(instaent.urls)): ##= we tried all suggestions, none was verified
                ##if already all options were checked and none was verified, then return the first entry suggested, just do not declare it as verified
                ##TODO: ideally check also validity of entry
                insta_url = instaent.urls[0].url
                insta_username = wf.extract_insta_username(insta_url)
                return f"""- [Instagram]({insta_url}) - {insta_username}""", insta_url
            else: 
                ##return in any case, verification not requested
                if insta_valid:
                    st.session_state.found_a_insta_entry = True
                    
            ##only if url is valid:
            if st.session_state.found_a_insta_entry: 
                if not (insta_valid == None) and insta_valid == True:
                    #insta_title = instaent.urls[num_iter].title
                    insta_username = wf.extract_insta_username(insta_url)
                    #lang = instaent.urls[num_iter].language
                    #insta_line = f"""- [Instagram]({insta_url}) - {insta_title}"""
                    if not (insta_verified == None) and insta_verified == True:
                        insta_line = f"""- [Instagram]({insta_url}) - {insta_username} :white_check_mark:"""
                    else: 
                        insta_line = """"""#f"""- [Instagram]({insta_url}) - {insta_username}"""
                    #text = wf.get_page_content(context, insta_title, lang)
                else:
                    print('insta url not valid')
                    insta_url = ''
                    #insta_title = ''
                    insta_line = f"""- Kein Eintrag auf Instagram gefunden."""                      
            #else: 
            #    insta_line = f"""- Kein Eintrag auf Instagram gefunden."""

        except: 
            insta_url = ''
            #insta_title = ''
            insta_line = f"""- Kein Eintrag auf Instagram gefunden."""

        num_iter += 1
    return insta_line, insta_url, insta_username

def remember_params(type, wiki_title, insta_username, person_name, post_links, post_filepaths):
    st.session_state.person_sought = dict()
    st.session_state.person_sought["type"] = type ##wiki or insta
    st.session_state.person_sought["wiki_title"] = wiki_title
    st.session_state.person_sought["insta_username"] = insta_username
    st.session_state.person_sought["person_name"] = person_name
    st.session_state.person_sought["post_links"] = post_links
    st.session_state.person_sought["post_filepaths"] = post_filepaths


def recalc_images():
    with col1:                     
        st.write(f"{person_name}")
        if person_name == 'Heidi Klums': ##tmp only, to replace with retrieved image
            st.image("../img/Heidi_Klum_by_Glenn_Francis.jpg", width=100)#, caption=person_name)
        else:
            #st.image(create_dummy_image(), width=100, caption=person_name)
            try: 
                st.image(st.session_state.wiki_images[i], width = 100)#, caption=person_name)
            except: ##e.g. no image found before
                st.image(create_dummy_image(), width=100)#, caption=person_name)


def reset_field(placeholder):#, edit_btn):
    with placeholder:
        placeholder.empty()
        placeholder.text_area("Editable field 2",value=st.session_state.user_input, height=500, key="aaab")

        if st.session_state.btn_label == "Edit Text":
            st.session_state.btn_label = "Save Text"  # Update this to your desired new label
        elif st.session_state.btn_label == "Save Text":
            st.session_state.btn_label = "Edit Text"
        else: 
            st.session_state.btn_label = "Edit Text"


def create_diff_wo_deletes(baseline=st.session_state.user_input, new_text=st.session_state.integrated_text):
    html = new_text#st.session_state.integrated_text ##replace with diff
    if html is not None:
        st.session_state.diff_text = wf.show_diff(baseline, new_text)
        st.session_state.diff_text2 = wf.remove_del_tags(st.session_state.diff_text)
    return st.session_state.diff_text, st.session_state.diff_text2


def start_editing5():
    st.session_state.editing5 = True


def stop_editing5(calc_diff=True):
    st.session_state.editing5 = False
    
    st.session_state.markdown_content5 = st.session_state.new_content5  # Update the Markdown content
    if calc_diff:
        st.session_state.diff_text, st.session_state.diff_text2 = create_diff_wo_deletes(baseline=st.session_state.user_input, new_text=st.session_state.new_content5)
    else: 
        st.session_state.diff_text = ''
        st.session_state.diff_text2 = ''
    st.session_state.last_confirmed = st.session_state.article_text


def set_texts(text=st.session_state.user_input):
    print('in set_texts with text:')
    print(text)

    facts_to_integrate = []
    if not st.session_state.relevant_parts_to_show == None:
        for i in range(len(st.session_state.relevant_parts_to_show.relevantparts)):#2):
            if st.session_state.get("checkbox"+str(i)) == True:
                ##TODO: integrate that fact, possibly first collect aall facts to be integrated:
                print('True')
                facts_to_integrate.append("Fact: "+ st.session_state.relevant_parts_to_show.relevantparts[i].fact)
            else:
                print(False)
    if not st.session_state.relevant_parts_to_show_insta == None:
        for i in range(len(st.session_state.relevant_parts_to_show_insta.relevantparts)):#2):
            if st.session_state.get("checkbox"+str(i)) == True:
                ##TODO: integrate that fact, possibly first collect aall facts to be integrated:
                print('True')
                facts_to_integrate.append("Fact: " + st.session_state.relevant_parts_to_show_insta.relevantparts[i].fact)
            else:
                print(False)
    print(facts_to_integrate)

    st.session_state.integrated_text = wf.integrate_facts(text, facts_to_integrate, chosen_model=st.session_state.model, temperature=0)
    st.session_state.article_text = st.session_state.integrated_text

    st.session_state.last_confirmed = st.session_state.integrated_text ##Abrakadabra

    with middle_column:
        st.session_state.active_tab = "tab3"
        pass

    st.session_state.diff_text, st.session_state.diff_text2 = create_diff_wo_deletes(st.session_state.user_input, st.session_state.integrated_text)
    st.session_state.editing5 = False ##show result as markdown with diff


def reset_texts():
    st.session_state.integrated_text_tmp = st.session_state.integrated_text
    st.session_state.integrated_text = st.session_state.user_input

    st.session_state.last_confirmed_tmp = st.session_state.last_confirmed#st.session_state.new_content5#st.session_state.last_confirmed
    st.session_state.last_confirmed = st.session_state.user_input

    st.session_state.diff_text_tmp = st.session_state.diff_text
    st.session_state.diff_text = st.session_state.user_input
    
    st.session_state.diff_text2_tmp = st.session_state.diff_text2
    st.session_state.diff_text2 = st.session_state.user_input

    st.session_state.article_text_tmp = st.session_state.article_text
    st.session_state.article_text = st.session_state.user_input


def clear():
    print('in clear')
    st.session_state.current_iteration = 0
    st.session_state.editing5 = True
    st.session_state.diff_text = ''
    st.session_state.diff_text2 = ''
    st.session_state.article_text = ''
    st.session_state.integrated_text = ''
    st.session_state.last_confirmed = ''
    st.session_state.user_input = ''


def repeat():
    if 'integrated_text_tmp' in st.session_state:
        st.session_state.integrated_text = st.session_state.integrated_text_tmp
    else:
        st.session_state.integrated_text = st.session_state.user_input
    if 'last_confirmed_tmp' in st.session_state:
        #st.session_state.last_confirmed = st.session_state.last_confirmed_tmp
        st.session_state.new_content5 = st.session_state.last_confirmed_tmp
    else:
        st.session_state.last_confirmed = st.session_state.user_input
    if 'diff_text_tmp' in st.session_state:
        st.session_state.diff_text = st.session_state.diff_text_tmp
    else:
        st.session_state.diff_text = st.session_state.user_input
    if 'diff_text2_tmp' in st.session_state:
        st.session_state.diff_text2 = st.session_state.diff_text2_tmp
    else:
        st.session_state.diff_text2 = st.session_state.user_input



tiles_left = []
tiles_middle = []
tiles_right = []
tiles = []

st.set_page_config(page_title='MTLab WIP', layout="wide")#, initial_sidebar_state="expanded")#"collapsed")
# Set up the sidebar with links and a search bar
st.sidebar.title('Navigation')
st.sidebar.write('Informationen zu Personen')

entered_insta_username = st.sidebar.text_input(
    "Insta Username (email)", type="default", help="Set this to run Insta analyses."
)
entered_insta_password = st.sidebar.text_input(
    "Insta Password", type="password", help="Set your Instsa PW to run Insta analyses."
)
print("entered insta username:")
print(entered_insta_username)
 
if entered_insta_username:
    #openai_api_key = entered_insta_username
    enable_custom = True
else:
    entered_insta_username = "not_supplied"
    enable_custom = False

##TODO: Handle missing keys
if len(wf.options) == 0:
    st.session_state.button_find_disabled = True
else:
    st.session_state.model = st.sidebar.selectbox('Wahl des Sprachmodells', options = wf.options)

##not working to hand it over
wf.chosen_model = st.session_state.model
chosen_model = st.session_state.model
#st.markdown(wf.chosen_model)
wf.set_model(st.session_state.model)

#st.sidebar.write('Login')
#st.sidebar.write('Weitere Links...')
#search_term = st.sidebar.text_input('Suchbegriff eingeben', '')
#if st.sidebar.button('Suche starten'):
#    st.sidebar.write('Suche nach:', search_term)

dbname = os.getenv("POSTGRES_DB")
user = os.getenv("POSTGRES_ADMINUSER")
password = os.getenv("POSTGRES_ADMINPASSWORD")
host = os.getenv("POSTGRES_HOST") 
port = os.getenv("POSTGRES_PORT")
try: 
    username = st.session_state.check_pw_page["username"]
    user_password = st.session_state.check_pw_page["user_password"]  # Plain-text password to be hashed
except: 
    username = ''
    user_password = ''
    pass




#topic_list_tmp = ["Abc", "Def", "Ghi"]
# SQL query to fetch data
query = "SELECT * FROM topics WHERE user_id = "+username

query = f"""SELECT t.topic_name
    FROM topics t
    JOIN users u ON t.user_id = u.id
    WHERE u.username = '{username}';"""

topic_list = [] ##initialize it here but overwrite it after db search

print(query)

# Fetching data
data = dbf.fetch_data(host, dbname, user, password, port, query)
    
# Display data
#print(data)
if not data.empty:
    df = pd.DataFrame(data, columns=['user_id', 'topic_name'])
    #st.write(df)
#else:
    #st.write("No data found.")

if not data.empty:
    topic_list = df['topic_name'].tolist()[-5:]
    #print(topic_list)
    #st.sidebar.selectbox('Wahl des Topics', options = topic_list)
topic_list_tmp = topic_list

placeholder_radio1 = st.sidebar.empty()

placeholder_radio1.radio(
    "Your recent searches",
    topic_list_tmp)#,
    #captions = ["Caption1", "Caption2", "Caption3"])
 #session_state.check_pw_page["username"]

# Main area layout with two columns
left_column, middle_column, right_column = st.columns([1, 6, 3])

#wiki_images = dict()
my_folder = "../img/"#'wiki_images'#wf.my_folderwf.my_folder

#print('USERNAME:')
#st.markdown(st.session_state.check_pw_page["username"])

# Middle column for the article input and identified persons
with middle_column:
    st.title('Artikel und Personen')
    
    if 1 == 1:

        if st.session_state.editing5:
            st.session_state.article_text = st.text_area("Edit the text", value=st.session_state.last_confirmed, key='new_content5',height=400)
            #st.session_state.article_text = article_text
            
            ##only if already did at least one integration or edit to the text: ##TBD if I type the text what happens
            if 'diff_text' in st.session_state and st.session_state.diff_text != '':
                st.button("Save", on_click=stop_editing5)  # Clicking this will save the content and exit editing mode
            text_contents = st.session_state.new_content5
        else:
            if 'diff_text' in st.session_state and not st.session_state.diff_text == '': ##TBD: maybe not show deletions, then take diff_text2 instead
                st.markdown(st.session_state.diff_text.replace("\n", "<br>"), unsafe_allow_html=True)
            else: 
                st.markdown(st.session_state.last_confirmed, unsafe_allow_html=True)
            st.button("Edit", on_click=start_editing5)  # Clicking this will switch to editing mode
            text_contents = st.session_state.markdown_content5#st.session_state.new_content5
        st.button("Clear", on_click=clear) 
        st.download_button('Download', text_contents) 


    if st.session_state.button_find_disabled == True: ##Button disabled
        st.markdown('No Key found. Please insert your key in the .env file.')

    col1a, col2a, col3a = st.columns([1, 1.5, 2.5])
    with col2a:
        ##Setting a variable that says whether instagram pages are being shown
        st.session_state.include_insta = st.checkbox('Inklusive Instagram Links', key = "checkbox_includeinsta", value=True)#, on_change = insta_callback)

    with col3a:
        ##Setting a variable that says whether instagram pages are being checked
        st.session_state.check_insta = st.checkbox('Analysiere Instagram Seiten', key = "checkbox_checkinsta", value=False)#, on_change = insta_callback)

    with col1a:

        # Button below the text area right
        if st.button('Finde Personen', disabled=st.session_state.button_find_disabled):
            #st.success('Personen hervorgehoben.')
            st.session_state.find_person_clicked = True
            st.session_state.clicked = False ##reset, not showing elements that have nothing to do with new selection
            try:
                st.session_state.user_input = st.session_state.new_content5#article_text ##TODO check if it always gets the current text
            except:
                st.session_state.user_input = st.session_state.markdown_content5

            print('chosen_model when calling get_all_wiki_urls:')
            print(chosen_model)
            st.session_state.parsed_ents = wf.get_all_wiki_urls(st.session_state.user_input, chosen_model=st.session_state.model)
            st.session_state.parsed_instas = dict()

            people = dict()
            people = st.session_state.parsed_ents.entities
            st.session_state.wiki_images = dict()
            st.session_state.wiki_lines = dict()
            st.session_state.wiki_lines_langs = dict()
            st.session_state.insta_lines = dict()

            topics = []
            for i in range(len(people)):
                #st.markdown('i')
                ent = people[i]

                st.session_state.wiki_lines[i], st.session_state.wiki_lines_langs[i] = get_wiki_line(ent)
                print(st.session_state.wiki_lines[i])

                person_name = ent.name

                ##for now, taking the first entry, TODO: possibly improve wikipedia disambiguation in backend function
                try:
                    wiki_title = ent.urls[0].title
                    wiki_url = ent.urls[0].url

                    the_page = wiki_title
                    topics.append(the_page)

                    the_page =  the_page.replace(' ', '_')
                    # get JSON data and extract image URL
                    the_url = wf.get_image_url(the_page)

                    # if the URL is not None ...
                    if (the_url):  #not the_url == None: #
                        # download that image
                        file_ext = wf.download_image(the_url, the_page)
                        input_image_path = my_folder+the_page.replace(' ', '_')+file_ext 
                        output_image_path = my_folder+the_page.replace(' ', '_')+'_sm'+file_ext 

                        wf.shrink_image(input_image_path, output_image_path)
                        st.session_state.wiki_images[i] = output_image_path
                    else:

                        ## Managing to get some additional images, though not all   
                        try:
                            
                            image_url, path_saved = wf.get_image_url_backup(wiki_url, the_page)
                            file_ext = '.' + image_url.split('.')[-1].lower()
                            input_image_path = my_folder+the_page.replace(' ', '_')+file_ext#'.jpg'
                            output_image_path = my_folder+the_page.replace(' ', '_')+"_sm"+file_ext#'_sm.jpg'
                            wf.shrink_image(input_image_path, output_image_path)
                            st.session_state.wiki_images[i] = output_image_path
                        except:
                            print("No image file for " + the_page)


                    ##Getting insta profiles:
                    ##Done: Only do this ad-hoc when the insta-info is desired. It takes longer otherwise to show any results at the beginning
                    st.session_state.parsed_instas[i] = None       

                    if st.session_state.include_insta == True:
                        
                        insta_ent = wf.get_insta_urls(wiki_title, st.session_state.user_input, chosen_model=st.session_state.model)                        
                        try:
                            st.session_state.parsed_instas[i] = insta_ent
                        except:
                            st.session_state.parsed_instas[i] = None

                    else:
                        st.session_state.parsed_instas[i] = None

                except: 
                    pass ##will take default image below in 'except' if an image is not found


            ##Adding new topics to db
            ##TODO: Add a timestamp, so also new searches for a previous search are added (and shown in recent searches)
            dbf.insert_user_and_topics(dbname, user, password, host, port, username, user_password, topics)



    st.markdown("""___""")

    if st.session_state.find_person_clicked == True:

        parsed_ents = st.session_state.parsed_ents

        #with st.form(key='columns_in_form'):
        # Rows for identified persons and related articles
        col1, col2, col3 = st.columns([1, 2, 1])

        context = st.session_state.user_input

        ##not sure if this is helpful or obsolete...
        people = dict()
        people = st.session_state.parsed_ents.entities

        ##New: one line instead of repeating elements: 
        col1b, col2b, col3b = st.columns([1, 2, 1])
        with col1b:
            st.write('**Name**')
        with col2b:
            st.write(f"**Informationsquellen**")
        with col3b: 
            st.write(f"**Hole Infos**")

        #with st.form(key='column_people', border=False):
        col1y, col2y, col3y = st.columns([1, 2, 1])
        if 1 == 1:

            tiles = []
            tiles_left = []
            tiles_middle = []
            tiles_right = []
            for i in range(len(people)):
                col1y, col2y, col3y = st.columns([1, 2, 1])
                with col2y:
                    tile = st.container(border=False)#True)
                    tiles.append(tile)
                    tiles_middle.append(tile)

                with col1y: 
                    tile = st.container(border=False)#True)
                    tiles_left.append(tile)
                with col3y: 
                    tile = st.container(border=False)#True)
                    tiles_right.append(tile)

            ##delete original large-size images
            for file in os.listdir(my_folder): 
                if file.endswith('.jpg') and not file.endswith('_sm.jpg'):
                    file = os.path.join(my_folder, file)
                    os.remove(file)

            st.session_state.found_ents = True

            # Button below the text area
            #if st.button('Artikel speichern'):
            #    st.success('Artikel gespeichert.')

i = 0
for t in tiles_left: 
    with t:
        ent = people[i]
        person_name = ent.name
        st.write(f"""{person_name}""")
        try: 
            st.image(st.session_state.wiki_images[i], width = 100)#, caption=person_name)
        except: ##e.g. no image found before
            st.image(create_dummy_image(), width=100)#, caption=person_name)
    i += 1

i = 0
for tile in tiles_middle: 

    with tile: 
        instas = st.session_state.parsed_instas
        try:
            insta_ent = instas[i]
            insta_line, insta_url, insta_username = get_insta_line(insta_ent)
        except:
            insta_line = """"""
        wiki_line = st.session_state.wiki_lines[i]
        st.markdown(f"""{wiki_line}
        """)
        st.markdown(f"""{insta_line}
        """)
    i += 1

i = 0
for t in tiles_right: 
    with t:
        ##TODO: Show button only if url is valid and displayed
        ent = people[i]
        wiki_title = ent.urls[0].title
        person_name = ent.name
        if st.button(f"Analysiere Wikipedia", key = "buttonyy"+str(i), on_click = sel_callback):
            ##reset:
            st.session_state.relevant_parts_to_show = None
            st.session_state.relevant_parts_to_show_insta = None
            lang = st.session_state.wiki_lines_langs[i]
            set_relevant_parts_to_show(context, wiki_title, lang, True)

        verified = False
        try:
            insta_ent = instas[i]
            insta_line, insta_url, dest_username = get_insta_line(insta_ent)
            if ":white_check_mark:" in insta_line: ##verified
                verified = True
        except: 
            pass
        if verified: ##only for verified Instagram sites
            if st.button(f"Analysiere Instagram", key = "buttonyy"+str(i)+"b"):
                try:
                    ##reset:
                    st.session_state.relevant_parts_to_show = None
                    st.session_state.relevant_parts_to_show_insta = None
                    #insta_ent = instas[i]
                    #insta_line, insta_url, dest_username = get_insta_line(insta_ent)
                    ##downloading posts to a folder named like the dest username
                    post_links, post_filepaths = wf.download_posts(dest_username, entered_insta_username, entered_insta_password, limit=3)#5)
                    #print(post_links)
                    #print(post_filepaths)
                    set_relevant_parts_to_show_insta(context, dest_username, person_name, post_links, post_filepaths, language='de', translate=True)
                except:
                    print("downloading of instaposts did not work")
    i += 1

# Rightmost column with Wikipedia or Insta information and buttons
with right_column:

    with st.form(key='column_relevantparts', border=False):
        #submitted = st.form_submit_button("Submit")
        #placeholder_for_reset = st.empty()
        if st.session_state.found_ents == True:

            ##original_title = '<p style="font-family:Courier; color:White; font-size: 45px;">_</p>'
            #original_title = '<p style="font-family:Arial; color:Black; font-size: 45px;">Informationen</p>'
            #st.markdown(original_title, unsafe_allow_html=True)
            st.title('Relevante Inhalte')
            
            if st.session_state.clicked and st.session_state.found_a_wiki_entry:# and not st.session_state.found_ents:

                i = 0

                ##it's either one or the other currently:
                if not st.session_state.relevant_parts_to_show ==  None and not st.session_state.relevant_parts_to_show == '':  
                    for rp in st.session_state.relevant_parts_to_show.relevantparts:

                        col1b, col2b = st.columns([0.5, 10])
                        with col1b:
                            st.checkbox('', key = "checkbox"+str(i), value=st.session_state.isall)#, on_change = sel_callback)#False)

                        with col2b:
                            ##adapting to usually 42 characters * 6 rows fitting a height 150 text_area
                            text_area_input = st.text_area("Wikipedia Artikel", height=int(150*len(rp.fact)/(38*5)), placeholder = "", value = rp.fact, key = "text_area"+str(i))#"Text not yet retrieved")
                            st.session_state.text_area_input = text_area_input
                        i += 1
                if not st.session_state.relevant_parts_to_show_insta ==  None:
                    for rp in st.session_state.relevant_parts_to_show_insta.relevantparts:

                        col1b, col2b = st.columns([0.5, 10])
                        with col1b:
                            st.checkbox('', key = "checkbox"+str(i), value=st.session_state.isall)#, on_change = sel_callback)#False)

                        with col2b:
                            ##adapting to usually 42 characters * 6 rows fitting a height 150 text_area
                            text_area_input = st.text_area("Insta Information", height=int(150*len(rp.fact)/(38*5)), placeholder = "", value = rp.fact, key = "text_area"+str(i))#"Text not yet retrieved")
                            st.markdown(rp.source_url)
                            st.session_state.text_area_input = text_area_input
                        i += 1

        #placeholder_for_radio = st.empty()
        placeholder_for_reset = st.empty()
                
        submitted = st.form_submit_button("Integriere Fakten", on_click=set_texts, args=[st.session_state.article_text])#new_content5])#article_text])#last_confirmed])#new_content5])#last_confirmed])
        

    with placeholder_for_reset: 
        #radio_option = st.radio("`st.radio`", ["select all", "select all"], horizontal=True, on_change = sel_callback)
        radio_checkbox = st.checkbox('selektiere / deselektiere alle', key='sel2', value=False, on_change = sel_callback)

    rcol1, rcolmid, rcol2 = st.columns([2.6, 2.3, 2.3])
    with rcolmid:
        did_reset = st.button('Alles rückgängig', on_click=reset_texts)#disabled=True)
    with rcol2:
        #pass
        if not st.session_state.integrated_text_tmp:#did_reset:
            st.button('Wiederhole', on_click=repeat, disabled=True)
        else:
            st.button('Wiederhole', on_click=repeat, disabled=False)



print(st.session_state)

