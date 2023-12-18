import streamlit as st
import wiki_functions as wf

# Text input for article with default text
default_text = """Hier kann ein Artikel eingetragen werden...:
Heidi Klum
Vorgezogenes Weihnachtsfest mit ihrer Familie

Heidi Klum hat mit ihrem Liebsten Tom Kaulitz und der Familie ein vorgezogenes Weihnachtsfest gefeiert. Auf Instagram gewährte das Model seinen Fans einen Einblick.
Eigentlich dauert es noch ein paar Tage bis zum Heiligabend. Doch Heidi Klum, 50, hat zusammen mit ihrem Mann Tom Kaulitz, 34, das Weihnachtsfest vorgezogen und bereits am Freitagabend, 15. Dezember, gefeiert. Eindrücke des Familienfestes teilte das Model in den sozialen Medien.

Heidi Klum: Raclette essen mit ihren Liebsten
Auf ihrem Instagram-Profil postete die vierfache Mama einen Clip vom gemeinsamen Weihnachtsessen. Auf einem festlich geschmückten runden Tisch ist alles für ein reichhaltiges Raclette gedeckt. Zwischen weihnachtlich grüner und roter Deko brutzeln sich die Gäste ihr Pfännchen mit allerlei leckeren Zutaten. "Familie Time", kommentiert Klum ihr Video und setzt ein Herz-Emoji dazu. Daraus ist zu schließen, dass neben Ehemann Tom auch die Kinder der GNTM-Jurorin dabei sind. Auch Toms Bruder Bill Kaulitz, 34, ist in einer Einstellung zu erahnen.
"""


default_wiki = """Informationen von Wikipedia...:
Heidi Klum

Heidi Klum (* 1. Juni 1973 in Bergisch Gladbach, bürgerlich von 2009 bis 2012 Heidi Samuel, seit 2019 Heidi Kaulitz[1][2]) ist ein deutsches Model. Seit 2008 besitzt sie auch die US-amerikanische Staatsbürgerschaft. Sie arbeitet als Jurorin, Moderatorin bzw. Produzentin der Castingshows Germany’s Next Topmodel, Queen of Drags und America’s Got Talent. Bis 2018 war sie bei Project Runway Mit-Produzentin, Moderatorin und Jury-Vorsitzende.
Leben
Klum wurde 1973 in Bergisch Gladbach geboren und wuchs dort auch auf. Sie besuchte die Integrierte Gesamtschule Paffrath bis zum Abitur. Ihr Vater Günther Klum ist gelernter Chemiefacharbeiter und ehemaliger Produktionsleiter beim Parfümhersteller 4711, ihre Mutter Erna Klum ist ausgebildete Friseurin.[1][3] Aus einer früheren Beziehung ihrer Mutter stammt ein 1964 geborener Halbbruder.[4]

Entdeckung und Karriere
Klums Karriere begann 1992 mit der Teilnahme am Wettbewerb Model ’92, der in Zusammenarbeit mit der Frauenzeitschrift Petra, der New Yorker Modelagentur Metropolitan Models[5][6][7] und dem Koordinator Christian Seidel[8] in der von Holm Dressler und Thomas Gottschalk produzierten RTL-Show Gottschalk Late Night stattfand. Bei diesem Wettbewerb setzte sich die damals 18-jährige Schülerin gegen 25.000[8] Konkurrentinnen durch und gewann einen mit 300.000 US-Dollar dotierten dreijährigen Vertrag als Fotomodell.[9] Nach dem bestandenen Abitur verzichtete sie auf einen Ausbildungsplatz als Modedesignerin in Düsseldorf, um als Model zu arbeiten.[10] Weil damals in Europa sehr dünne Models gefragt waren, zog sie in die Vereinigten Staaten, wo sie seit 1993 lebt.[11]

1997 gelang ihr hier der Durchbruch, als sie von Victoria’s Secret engagiert wurde und 1998 ein Titelfoto auf der Bademodenausgabe der US-amerikanischen Zeitschrift Sports Illustrated mit 55 Millionen Lesern folgte. Sie erschien auf den Titelseiten von Zeitschriften wie Vogue und Elle und wurde ein international gefragtes Model und Werbegesicht.[12] Klums Vater ist auch ihr Manager. Er gründete in Bergisch Gladbach die Heidi Klum GmbH & Co. KG und betreibt dort auch deren Büro.[3]
"""

if "user_input" not in st.session_state:
    st.session_state.user_input = default_text
if "wiki_input" not in st.session_state:
    st.session_state.wiki_input = ''#None#' '#default_wiki
if "find_person_clicked" not in st.session_state:
    st.session_state.find_person_clicked = None

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

    st.markdown("""___""")

    if st.session_state.find_person_clicked == True:
        # Rows for identified persons and related articles
        for i in range(3):

            if i == 0:
                person_name = f"Heidi Klum"
                #st.write(person_name)
                col1, col2, col3 = st.columns([1, 2, 1])

                # Left column for face image
                with col1:
                    st.write(person_name)
                    st.image("./img/Heidi_Klum_by_Glenn_Francis.jpg", width=100, caption=person_name)

                # Right column for articles related to the person
                with col2:
                    #st.write(f"Artikel zu {person_name}")
                    st.write(f"Artikel zu {person_name}")
                    #	    Relevant Articles in Database:
                    st.markdown("""
                - [Wikipedia](https://de.wikipedia.org/wiki/Heidi_Klum) - Heidi Klum
                - [Instagram](https://www.instagram.com/heidiklum/) - @heidiklum
                """)
                    
                with col3:
                    st.write(f"Show")
                    if st.button(f"Show summary"):
                        wikicontent = wf.get_wikipage_content()
                        st.session_state.wiki_input = wikicontent#"""abcdefg"""

            else:
                person_name = f"Person {i+1}"
                #st.write(person_name)
                col1, col2 = st.columns([1, 2])

                # Left column for face image
                with col1:
                    st.write(person_name)
                    st.image(create_dummy_image(), width=100, caption=person_name)

                # Right column for articles related to the person
                with col2:
                    #st.write(f"Artikel zu {person_name}")
                    st.write(f"Artikel zu {person_name}")
                    #	    Relevant Articles in Database:
                    st.markdown("""
                - [Article Title 1](#) - 24.10.2023
                - [Article Title 2](#) - 01.09.2023
                - [Article Title 3](#) - 29.09.2023
                """)
                
        # Button below the text area
        #if st.button('Artikel speichern'):
        #    st.success('Artikel gespeichert.')


# Rightmost column with Wikipedia information and buttons
with right_column:
    if not st.session_state.wiki_input == '':#None:

        #st.title("_")
        #st.markdown("")
        #st.markdown("")

        original_title = '<p style="font-family:Courier; color:White; font-size: 45px;">_</p>'
        st.markdown(original_title, unsafe_allow_html=True)
        #st.subheader("Wikipedia Informationen")

        text_area_input = st.text_area("Wikipedia Artikel", height=600, placeholder = default_wiki, value = st.session_state.wiki_input)#"Text not yet retrieved")
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

# Save this as app.py and run it with `streamlit run app.py` in your terminal.
