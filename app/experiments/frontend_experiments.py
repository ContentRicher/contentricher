import streamlit as st
import wiki_functions as wf
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


load_dotenv()

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
    
if "insta_lines" not in st.session_state:
    st.session_state.insta_lines = None


def set_clicked():
    st.session_state.clicked = True

def set_relevant_parts_to_show(context, wiki_title, language='de', translate=True):
    print('in set_relevant_parts_to_show')
    try:
        text = wf.get_page_content(context, wiki_title, language)
        st.session_state.relevant_parts_to_show = wf.get_relevant_parts(context, text[:8000], wiki_title, translate)#wf.translate_content(wf.get_relevant_parts(context, text[:8000], wiki_title), 'en', 'de')
    except:
        text = ''
        st.session_state.relevant_parts_to_show = None
        #print('could not retrieve page')
    st.session_state.clicked = True
    st.session_state.isall = False


def set_relevant_parts_to_show_insta(context, insta_name, person_name, post_links, post_filepaths, language='de', translate=True):
    try:
        st.session_state.relevant_parts_to_show_insta = None ##initialize to none
        text = vf.get_infos_from_insta_posts(insta_name, person_name, post_links, post_filepaths)
        st.session_state.relevant_parts_to_show_insta = wf.get_relevant_parts(context, text[:8000], person_name, translate)
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
    #lang = 'de'
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
    return wiki_line

def get_insta_line(ent):
    st.session_state.found_a_insta_entry = False
    #lang = 'de'
    ##for now, taking the first entry, TODO: check if URL valid, else probably also the rest is not existing
    num_iter = 0            


    while st.session_state.found_a_insta_entry == False and num_iter <= 2 and num_iter < len(ent.urls):
        insta_line = f"""- Kein Eintrag auf Instagram MM gefunden."""
        insta_url = ""
        try:
            insta_url = ent.urls[num_iter].url
            #insta_title = ent.urls[num_iter].title

            ##TODO: ensure Insta session works or else try a different method to check validity or show anyways
            #st.session_state.found_a_insta_entry = True##TODO: find the right call to longer version of: wf.check_insta_valid(insta_url)
            
            ##TODO: think of when not to verify, e.g. if no Insta Sessio provided, but avert user it's not sure
            if st.session_state.check_insta == True:
                try: 
                    insta_valid, insta_verified = wf.check_insta_valid_and_verified(insta_url)
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
            elif st.session_state.check_insta and (num_iter == 2 or num_iter == len(ent.urls)): ##= we tried all suggestions, none was verified
                ##if already all options were checked and none was verified, then return the first entry suggested, just do not declare it as verified
                ##TODO: ideally check also validity of entry
                insta_url = ent.urls[0].url
                insta_username = wf.extract_insta_username(insta_url)
                return f"""- [Instagram]({insta_url}) - {insta_username}""", insta_url
            else: 
                ##return in any case, verification not requested
                if insta_valid:
                    st.session_state.found_a_insta_entry = True
                    
            ##only if url is valid:
            if st.session_state.found_a_insta_entry: 
                if not (insta_valid == None) and insta_valid == True:
                    #insta_title = ent.urls[num_iter].title
                    insta_username = wf.extract_insta_username(insta_url)
                    #lang = ent.urls[num_iter].language
                    #insta_line = f"""- [Instagram]({insta_url}) - {insta_title}"""
                    if not (insta_verified == None) and insta_verified == True:
                        insta_line = f"""- [Instagram]({insta_url}) - {insta_username} :white_check_mark:"""
                    else: 
                        insta_line = f"""- [Instagram]({insta_url}) - {insta_username}"""
                    #text = wf.get_page_content(context, insta_title, lang)
                else:
                    print('insta url not valid')
                    insta_url = ''
                    insta_title = ''
                    insta_line = f"""- Kein Eintrag auf Instagram gefunden."""                      
            #else: 
            #    insta_line = f"""- Kein Eintrag auf Instagram gefunden."""

        except: 
            insta_url = ''
            #insta_title = ''
            insta_line = f"""- Kein Eintrag auf Instagram gefunden."""

        num_iter += 1
    return insta_line, insta_url, insta_username


st.set_page_config(page_title='MTLab WIP', layout="wide")#, initial_sidebar_state="expanded")#"collapsed")
# Set up the sidebar with links and a search bar
st.sidebar.title('Navigation')
st.sidebar.write('Informationen zu Personen')

if ('GPT-3.5' in wf.options) and ('Mistral Small' in wf.options):
    st.session_state.model = st.sidebar.selectbox(
        'Wahl des Sprachmodells',
        ('Mistral Small', 'GPT-3.5'))
elif 'GPT-3.5' in wf.options:
    st.session_state.model = st.sidebar.selectbox(
    'Wahl des Sprachmodells',
    ('GPT-3.5', 'Key für Mistral fehlt'))
elif 'Mistral Small' in wf.options:
    st.session_state.model = st.sidebar.selectbox(
    'Wahl des Sprachmodells',
    ('Mistral Small', 'Key für GPT-3.5 fehlt'))
else: 
    st.session_state.model = None
    ##deactivate buttons:
    st.session_state.button_find_disabled = True
wf.chosen_model = st.session_state.model

#st.sidebar.write('Login')
#st.sidebar.write('Weitere Links...')
#search_term = st.sidebar.text_input('Suchbegriff eingeben', '')
#if st.sidebar.button('Suche starten'):
#    st.sidebar.write('Suche nach:', search_term)

# Main area layout with two columns
left_column, middle_column, right_column = st.columns([1, 6, 3])

#wiki_images = dict()
my_folder = "../img/"#'wiki_images'#wf.my_folderwf.my_folder

# Middle column for the article input and identified persons
with middle_column:
    st.title('Artikel und Personen')

    article_text = st.text_area("Artikel Text", height=400, value = st.session_state.user_input)

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
            st.session_state.user_input = article_text ##TODO check if it always gets the current text
            st.session_state.parsed_ents = wf.get_all_wiki_urls(st.session_state.user_input)
            st.session_state.parsed_instas = dict()

            people = dict()
            people = st.session_state.parsed_ents.entities
            st.session_state.wiki_images = dict()
            st.session_state.wiki_lines = dict()
            st.session_state.insta_lines = dict()


            for i in range(len(people)):
                ent = people[i]

                st.session_state.wiki_lines[i] = get_wiki_line(ent)
                print(st.session_state.wiki_lines[i])

                person_name = ent.name
                ##for now, taking the first entry, TODO: possibly improve wikipedia disambiguation in backend function
                try:
                    wiki_title = ent.urls[0].title
                    wiki_url = ent.urls[0].url

                    the_page = wiki_title

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
                        
                        insta_ent = wf.get_insta_urls(wiki_title, st.session_state.user_input)                        
                        try:
                            st.session_state.parsed_instas[i] = insta_ent
                        except:
                            st.session_state.parsed_instas[i] = None

                    else:
                        st.session_state.parsed_instas[i] = None

                except: 
                    pass ##will take default image below in 'except' if an image is not found


    st.markdown("""___""")

    if st.session_state.find_person_clicked == True:

        parsed_ents = st.session_state.parsed_ents

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
            st.write(f"**Aktion**")


        for i in range(len(people)):

            ent = people[i]

            person_name = ent.name

            col1, col2, col3 = st.columns([1, 2, 1])

            ##st.session_state.relevant_parts_to_show = None
            #st.session_state.found_a_wiki_entry = False
            lang = 'de'
        

            # Right column for articles related to the person
            with col2:

                wiki_line = st.session_state.wiki_lines[i]

                ##no matter whether it turned out to exist or not, take the title received as most probable wikipedia title
                wiki_title = ent.urls[0].title

                if st.session_state.include_insta == True:

                    if not (wiki_title == '' or wiki_title == None):

                        instas = dict()
                        instas = st.session_state.parsed_instas
                        insta_url = None

                        try:

                            insta_ent = instas[i]
                            insta_line, insta_url, insta_username = get_insta_line(insta_ent)
                            print(insta_url)

                        except: 
                            print('in except for insta url')
                            insta_url = ''
                            insta_title = ''
                            insta_line = f"""- Kein Eintrag auf Instagram gefunden."""
                            insta_username = ''


                    else:
                        insta_line = f""""""#- Instagram Eintrag - TODO"""
                        
                else:
                    insta_line = f""""""#- Instagram Eintrag - TODO"""

                st.markdown(f"""
                """+ wiki_line +"""
                """+ insta_line + """
                """)

            # Left column for face image
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

            if st.session_state.found_a_wiki_entry:
                with col3:
                    ##TODO: Show button only if url is valid and displayed
                    #st.write(f"Aktion")
                    if st.button(f"Relevante Auszüge", key = "button"+str(i), on_click = sel_callback):
                        set_relevant_parts_to_show(context, wiki_title, lang, True)
                    if st.button(f"Analysiere Instagram", key = "button"+str(i)+"b"):
                        try:
                            ##downloading posts to a folder named like the insta username
                            post_links, post_filepaths = wf.download_posts(insta_username, limit=3)#5)
                            #print(post_links)
                            #print(post_filepaths)
                            set_relevant_parts_to_show_insta(context, insta_username, person_name, post_links, post_filepaths, language='de', translate=True)
                        except:
                            print("downloading of instaposts did not work")

        ##delete original large-size images
        for file in os.listdir(my_folder): 
            if file.endswith('.jpg') and not file.endswith('_sm.jpg'):
                file = os.path.join(my_folder, file)
                os.remove(file)

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

        
        if st.session_state.clicked and st.session_state.found_a_wiki_entry:# and not st.session_state.found_ents:

            i = 0

            #text_to_show = wf.concatenate_relevant_parts_to_show(st.session_state.relevant_parts_to_show)
            #text_area_input = st.text_area("Wikipedia Artikel", height=int(150*len(text_to_show)/(38*5)), placeholder = "", value = text_to_show)#st.session_state.wiki_input)
            #st.session_state.text_area_input = text_area_input

            st.session_state.isall = st.checkbox('selektiere / deselektiere alle', key='sel', value=False)

            ##it's either one or the other currently:
            if not st.session_state.relevant_parts_to_show ==  None:  
                for rp in st.session_state.relevant_parts_to_show.relevantparts:

                    col1b, col2b = st.columns([0.5, 10])
                    with col1b:
                        st.checkbox('', key = "checkbox"+str(i), value=st.session_state.isall, on_change = sel_callback)#False)

                    with col2b:
                        ##adapting to usually 42 characters * 6 rows fitting a height 150 text_area
                        text_area_input = st.text_area("Wikipedia Artikel", height=int(150*len(rp.fact)/(38*5)), placeholder = "", value = rp.fact, key = "text_area"+str(i))#"Text not yet retrieved")
                        st.session_state.text_area_input = text_area_input
                    i += 1
            if not st.session_state.relevant_parts_to_show_insta ==  None:
                for rp in st.session_state.relevant_parts_to_show_insta.relevantparts:

                    col1b, col2b = st.columns([0.5, 10])
                    with col1b:
                        st.checkbox('', key = "checkbox"+str(i), value=st.session_state.isall, on_change = sel_callback)#False)

                    with col2b:
                        ##adapting to usually 42 characters * 6 rows fitting a height 150 text_area
                        text_area_input = st.text_area("Insta Information", height=int(150*len(rp.fact)/(38*5)), placeholder = "", value = rp.fact, key = "text_area"+str(i))#"Text not yet retrieved")
                        st.session_state.text_area_input = text_area_input
                    i += 1

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

