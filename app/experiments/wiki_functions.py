import openai
import os
from IPython.display import Markdown
from openai import OpenAI
from dotenv import load_dotenv
import os

import langchain_core
#from langchain.llms import OpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
#from langchain.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field, validator
from typing import List

import wikipedia
#import random

import requests
from PIL import Image

##for Mistral:
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

##for getting the links on a Wikipedia adisambiguation page: 
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote 

import instaloader
from os.path import exists

from datetime import datetime, timedelta
from itertools import dropwhile, takewhile

from a615_import_firefox_session import import_session_from_firefox, username

# set the folder name where images will be stored
my_folder = "../img/"

# create the folder in the current working directory
# in which to store the downloaded images
os.makedirs(my_folder, exist_ok=True)

# front part of each Wikipedia URL
base_url = 'https://en.wikipedia.org/wiki/'

# Wikipedia API query string to get the main image on a page
# (partial URL will be added to the end)
query = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='

from load_insta import sessionfile, load_sessionfile, L2
session_loaded = False

load_dotenv()

API_KEY=os.getenv("API_KEY")
client = OpenAI(api_key = API_KEY)

MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
mistral_model = "mistral-small"
mistral_temperature = 0.15
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

chosen_model = 'Mistral Small'#'GPT-3.5'

if API_KEY != "[PUT YOUR OPENAI API KEY HERE]" and MISTRAL_API_KEY !="[PUT YOUR MISTRAL API KEY HERE]":
    options = ['Mistral Small', 'GPT-3.5']
elif API_KEY != "[PUT YOUR OPENAI API KEY HERE]":
    options = ['GPT-3.5']
elif MISTRAL_API_KEY != "[PUT YOUR MISTRAL API KEY HERE]":
    options = ['Mistral Small']
else: 
    options = []


#from langchain.llms import OpenAI
from langchain_community.chat_models import ChatOpenAI 
from langchain_mistralai.chat_models import ChatMistralAI

#llm = OpenAI(openai_api_key="...")
model_name = "gpt-3.5-turbo"
temperature = 0.0
#model = OpenAI(openai_api_key=API_KEY, model_name=model_name, temperature=temperature)
openai_model = ChatOpenAI(openai_api_key=API_KEY, model_name=model_name, temperature=temperature)

mistral_model_name = "mistral-small"
mistral_model = ChatMistralAI(mistral_api_key=MISTRAL_API_KEY, model_name=mistral_model_name, temperature=mistral_temperature)

##not here:
def get_model(chosen_model):
    if chosen_model ==  'Mistral Small': 
        model = mistral_model ##TODO: only works with OpenAI so far, need to get LangChain Mistral Client, not handing over client from API
    elif chosen_model == 'GPT-3.5':
        model = openai_model
    else: 
        ##TODO handle this case
        model = openai_model
    return model

##will be replaced by user's choice in frontend later
model = get_model(chosen_model)

class URL_entry(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all URL suggestions.")
    title: str = Field(description = "This is the title of the Wikipedia page")
    url: str = Field(description = "This is the URL of the suggested Wikipedia page")
    language: str = Field(description = "This is the language of the Wikipedia page, written as abbreviation")

class URL_propositions(BaseModel):
    urls: List[URL_entry]

class Insta_URL_entry(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all Insta URL suggestions.")
    title: str = Field(description = "This is the title/name of the Instagram profile")
    url: str = Field(description = "This is the URL of the suggested Instagram page")
    language: str = Field(description = "This is the language of the Instagram page, written as abbreviation")

class Insta_URL_propositions(BaseModel):
    urls: List[Insta_URL_entry]

class Entity(BaseModel):
    name: str = Field(description = "This is the full name of the person")
    urls: List[URL_entry]

class Entities(BaseModel):
    entities: List[Entity]


class RelevantPart(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all relevant parts suggestions.")
    fact: str = Field(description = "This is the relevant fact, an extracted fact or short paragraph from the entire text.")

class RelevantParts(BaseModel):
    relevantparts: List[RelevantPart]  

class RelevantPartDe(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all relevant parts suggestions.")
    fact: str = Field(description = "This is the relevant fact, an extracted fact or short paragraph from the entire text, in German.")

# class RelevantPartDe2(BaseModel):
#     rank: int = Field(description = "This is the rank of probability among all relevant parts suggestions.")
#     fact: str = Field(description = "Dies ist ein relevanter Fakt oder sehr kurzer Paragraph, auf deutsch.")
    
class RelevantPartsDe(BaseModel):
    relevantparts: List[RelevantPartDe]  

class RelevantPartInsta(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all relevant parts suggestions.")
    fact: str = Field(description = "This is the relevant fact, an extracted fact or short paragraph from the entire text.")
    source_url: str = Field(description = "This is the url of the Instagram post the relevant fact is from.")

class RelevantPartsInsta(BaseModel):
    relevantparts: List[RelevantPartInsta]  

class RankedEntry(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all URL suggestions.")
    title: str = Field(description = "This is the title of the Wikipedia page")
    url: str = Field(description = "This is the URL of the suggested Wikipedia page")
    HTML_line: str = Field(description = "The actual HTML line stated in the html that links to the url")

class RankedWikiEntries(BaseModel):
    query: str = Field(description = "This is the entity that is to be disambiguated.")
    rankedLinks: List[RankedEntry] 


def ask_openai(system_intel, prompt):
    result = client.chat.completions.create(model="gpt-3.5-turbo-0125",#"gpt-4-1106-preview",#"gpt-3.5-turbo-1106",#"gpt-3.5-turbo",
                                messages = [{"role": "system", "content": system_intel},
                                        {"role": "user", "content": prompt}],
                                        stream=False
            )
    #display(Markdown(result['choices'][0]['message']['content']))
    return result.choices[0].message.content
    
def ask_mistral(system_intel, prompt): 
    messages = [
        ChatMessage(role="system", content=system_intel),
        ChatMessage(role="user", content=prompt)
    ]
    ## No streaming yet
    chat_response = mistral_client.chat(
        model=mistral_model,
        messages=messages,
        temperature = mistral_temperature
    )
    return chat_response.choices[0].message.content

def ask_GPT(system_intel, prompt, chosen_model='GPT-3.5'): 
    if chosen_model == 'GPT-3.5':
        return ask_openai(system_intel, prompt)
    elif chosen_model == 'Mistral Small': ##model is Mistral
        return ask_mistral(system_intel, prompt)
    else:
        return ''


def parse_results(res, pydantic_object, llm=model):
    ##temporarily overwriting input variable to use openai model for parsing:
    #llm = openai_model

    try: 
        parser = PydanticOutputParser(pydantic_object=pydantic_object) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
        parsed = fixing_parser.invoke(res)

    return parsed


def get_wiki_urls(entity, context):

    system_intel = """You are an expert researcher and an expert in Wikipedia."""
    prompt = f"""Given the entity {entity} and the context {context}, find the most probable Wikipedia pages for it.""" 

    json_template = """{
  "urls": [
    {
      "rank": 1,
      "title": "Heidi Klum",
      "url": "https://de.wikipedia.org/wiki/Heidi_Klum",
      "language": "de"
    },
    {
      "rank": 2,
      "title": "Heidi Klum",
      "url": "https://en.wikipedia.org/wiki/Heidi_Klum",
      "language": "en"    },
    {
      "rank": 3,
      "title": "Heidi Klum",
      "url": "https://de.wikipedia.org/wiki/Leni_Klum",
      "language": "de"
    }
  ]
}"""

    prompt += f"""Return your answer as plain JSON, and following the following format, return only the JSON object:
    {json_template}"""

    res = ask_GPT(system_intel, prompt) ##DONE: wrapper around OpenAI and Mistral models
    model = get_model(chosen_model)

    ##Parse results
    parsed = parse_results(res, pydantic_object=URL_propositions, llm=model)

    return parsed


def get_all_wiki_urls(context):

    system_intel = """You are an expert researcher and an expert in Wikipedia."""
    prompt = f"""Given the context {context}, find the distinct people mentioned and for each the most probable two Wikipedia pages for it.
    Note: Wikipedia page urls are usually starting with 'https://de.wikipedia.org/wiki/' + Page Title for German pages and with 'https://en.wikipedia.org/wiki/' + Page Title for English pages.
    If only one person is found, only return one entity (with name and urls).""" 

    json_template = """{
    "entities": [ 
        {   "name": "Heidi Klum",
            "urls": [
                {
                "rank": 1,
                "title": "Heidi Klum",
                "url": "https://de.wikipedia.org/wiki/Heidi_Klum",
                "language": "de"
                },
                {
                "rank": 2,
                "title": "Heidi Klum",
                "url": "https://en.wikipedia.org/wiki/Heidi_Klum",
                "language": "en"
                }
            ]
        },
            "name": "Tom Kaulitz",
            "urls": [
                {
                "rank": 1,
                "title": "Tom Kaulitz",
                "url": "https://de.wikipedia.org/wiki/Tom_Kaulitz",
                "language": "de"
                },
                {
                "rank": 2,
                "title": "Heidi Klum",
                "url": "https://en.wikipedia.org/wiki/Tokio_Hotel",
                "language": "en"
                }
            ]
        }
    ]
    }"""

    prompt += f"""Return your answer as plain JSON, and following the following format, return only the JSON object:
    {json_template}"""

    res = ask_GPT(system_intel, prompt) 
    model = get_model(chosen_model)

    ##Parse results
    parsed = parse_results(res, pydantic_object=Entities, llm=model)

    return parsed


##NOTE: it may invent a page,  mostly for the fanpage, e.g. if no such fanpage exists
##TODO: put a try except block in the call that uses the results
def get_insta_urls(entity, context):

    system_intel = """You are an expert researcher and an expert in Instagram and Influencers."""
    prompt = f"""Given the following person and the textual context, find the most probable Instagram profile/s with the URL/s that belong to that same person.
    
    Person: 
    {entity}

    Context: 
    {context}
    """


    json_template = """{
  "urls": [
    {
      "rank": 1,
      "title": "Heidi Klum",
      "profile": "@heidiklum",
      "url": "https://www.instagram.com/heidiklum/",
      "language": "en"
    },
    {
      "rank": 2,
      "title": "Heidi Klum Fanpage",
      "url": "https://www.instagram.com/heidiklumly/",
      "language": "en"
    }
  ]
}"""

    prompt += f"""
    
    Return your answer as plain JSON, following the following format:
    JSON Template:
    {json_template}"""

    res = ask_GPT(system_intel, prompt)
    #print(res)

    model = get_model(chosen_model)

    ##Parse results
    parsed = parse_results(res, pydantic_object=Insta_URL_propositions, llm=model)

    return parsed


def get_options_string(title, language='de'):

    if language == 'en':
        base_url = "https://en.wikipedia.org" 

        response = requests.get('https://en.wikipedia.org/w/api.php',
            params={
                'action': 'parse',
                'page': title,
                'format': 'json',
            },
            headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
        )
    elif language == 'de':
        base_url = "https://de.wikipedia.org" 

        response = requests.get('https://de.wikipedia.org/w/api.php',
            params={
                'action': 'parse',
                'page': title,
                'format': 'json',
            },
            headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
        )
    else: 
        return ''

    soup = BeautifulSoup(response.text, 'html.parser')#, features="lxml") 

    li_tags = soup.find_all('li') 

    options_string = """"""

    for li in li_tags:
        text = li.get_text()#strip=True, separator=' ')
        link = li.find('a')  # Find the <a> element within the <li>
                    
        if link and text: 
            href = link.get('href', '')
            
            ##for some reason, I need to strip start and end characters:
            href = href[2:-2]
            
            text = text.strip().encode('utf-8').decode('unicode_escape')

            absolute_url = urljoin(base_url, unquote(href))#base_url + href#urljoin(base_url, unquote(href))  # Combine base_url and href to get the absolute URL
            
            options_string += text + ": URL = "+absolute_url+"\n"
 
    return options_string


##Catching disambiguation error, can be improved
##TODO: e.g. for Alexei Nawalny, it didn't get the page content: https://en.wikipedia.org/wiki/Alexei_Navalny
def get_page_content(context, title, language='de'):

    res = ''
    try: 
        wikipedia.set_lang(language)
        p = wikipedia.page(title, auto_suggest=False, redirect=True, preload=False)
        res = p.content
    except: 
        try: 
            options_string = get_options_string(title, language)
            best_entries = get_best_entry(context, options_string, title)
            s = best_entries.rankedLinks[0].title
            p = wikipedia.page(s)
            res = p.content
        except: 
            res = ''

    return res#p.content


def get_relevant_parts(context, text, wiki_title, translate=True, source_insta_posts=False):
    ##try getting most relevant part for the given context:
    ##maybe add target_group later:
    #target_group = 'Young adults'

    ##keep for later, in case English is desired:
    json_template = """{
  "relevantparts": [
    {
      "rank": 1,
      "fact": "Sam Altman, CEO of OpenAI, was unexpectedly fired on a Friday. Since then, OpenAI and its main investor, Microsoft, experienced turmoil. Two successors, Mira Murati and Emmett Shear, temporarily took over his job. It's now confirmed that Sam Altman has returned to his position."
    },
    {
      "rank": 2,
      "fact": "On November 17, 2023, OpenAI's board decided to remove Sam Altman as CEO. In response, a significant number of employees reacted, resulting in an agreement in principle for Altman's return as CEO."
    },
    {
      "rank": 3,
      "fact": "Sam Altman has been involved in various ventures outside of OpenAI, including being the CEO of Reddit for a short period, supporting COVID-19 research, and investing in startups and nuclear energy companies. He has also been engaged in political activities and philanthropy."
    }
  ]
}"""

    json_template = """"relevantparts": [
    {
      "rank": 1,
      "fact": "Sam Altman, CEO von OpenAI, wurde an einem Freitag unerwartet entlassen. Seitdem sind OpenAI und sein Hauptinvestor, Microsoft, in Aufruhr. Zwei Nachfolger, Mira Murati und Emmett Shear, übernahmen vorübergehend seinen Job. Nun wurde bestätigt, dass Sam Altman in seine Position zurückgekehrt ist."
    },
    {
      "rank": 2,
      "fact": "Am 17. November 2023 beschloss der Vorstand von OpenAI, Sam Altman als CEO abzuberufen. Daraufhin reagierte eine große Anzahl von Mitarbeitern, was zu einer grundsätzlichen Einigung über Altmans Rückkehr als CEO führte."
    },
    {
      "rank": 3,
      "fact": "Sam Altman war an verschiedenen Unternehmungen außerhalb von OpenAI beteiligt, u. a. war er für kurze Zeit CEO von Reddit, unterstützte die COVID-19-Forschung und investierte in Start-ups und Kernenergieunternehmen. Er hat sich auch in politischen Aktivitäten und Philanthropie engagiert."
    }
  ]
}"""

    json_template_insta = """"relevantparts": [
    {
      "rank": 1,
      "fact": "Sam Altman, CEO von OpenAI, wurde an einem Freitag unerwartet entlassen. Seitdem sind OpenAI und sein Hauptinvestor, Microsoft, in Aufruhr. Zwei Nachfolger, Mira Murati und Emmett Shear, übernahmen vorübergehend seinen Job. Nun wurde bestätigt, dass Sam Altman in seine Position zurückgekehrt ist."
      "source_url": 'https://www.instagram.com/p/D2abx7e15Nv'
    },
    {
      "rank": 2,
      "fact": "Am 17. November 2023 beschloss der Vorstand von OpenAI, Sam Altman als CEO abzuberufen. Daraufhin reagierte eine große Anzahl von Mitarbeitern, was zu einer grundsätzlichen Einigung über Altmans Rückkehr als CEO führte."
      "source_url": 'https://www.instagram.com/p/D3ayd3e12Au'
    },
    {
      "rank": 3,
      "fact": "Sam Altman war an verschiedenen Unternehmungen außerhalb von OpenAI beteiligt, u. a. war er für kurze Zeit CEO von Reddit, unterstützte die COVID-19-Forschung und investierte in Start-ups und Kernenergieunternehmen. Er hat sich auch in politischen Aktivitäten und Philanthropie engagiert."
      "source_url": 'https://www.instagram.com/p/B4xac8c43Oq'
    }
  ]
}"""

    if translate == True:
        translate_instruction = """Before returning the JSON, translate any 'fact' values in the json into grammatically correct German sentences, if they are not yet in German."""
    else:
        translate_instruction = ""

    system_intel = f"""You are an expert on {wiki_title} and great in explaining and understanding people."""# and {target_group}."""
    prompt = f"""Given the context below, interpret the ARTICLE that follows it and then return only the sentences from the ARTICLE that contain relevant additional information/facts that are not present in the context. 

    Context: 
    {context}

    ARTICLE:
    {text}

    Group the information in coherent information chunks as short paragraphs.
    """

    ##Alternative prompt, was better
    prompt = f"""Your task is to make the article given below understandable to people who have not heard of {wiki_title} before.
    Given the article below, interpret the following information and then return only the sentences from the information text that contains relevant additional information that is not present in the article
    and that may be relevant for people who do not know {wiki_title} and read the article. 
    Do not return any facts from the context, unless a sentence from the information you select really needs it for further explanation or reference within the same sentence.

    Article: 
    {context}

    Information:
    {text}

    Group the selected relevant information in coherent chunks of information as short paragraphs. 
    """ 

    if source_insta_posts == True:
        prompt+=f"""
        You received the information as a list of instagram posts, including the url of the source post (=where the information is taken from). 
        Return the relevant part of each post as a coherent chunk in one relevantparts element, with a rank and a fact and the respective source_url."""
    ##TODO: maybe say: only maximum n posts


    prompt+=f"""
    Return your answer in an ordered form, with the most relevant information parts first. 

    Return your answer as plain JSON, following the following format below. {translate_instruction}"""

    ##maybe add different template and add a different parsing later:
    if source_insta_posts == False: 
        prompt += f"""
        JSON format:
        {json_template}

        JSON:
        """
    else: 
        prompt += f"""
        JSON format:
        {json_template_insta}

        JSON:
        """

    ##later add to prompt:
    #    and that is relevant for the target group {target_group}.

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    #res = translate_content_new(res)

    model = get_model(chosen_model)


    ##Parse results
    if source_insta_posts == True:
        parsed = parse_results(res, pydantic_object=RelevantPartsInsta, llm=model)
    else:
        if translate==True:
            parsed = parse_results(res, pydantic_object=RelevantPartsDe, llm=model)
        else: 
            parsed = parse_results(res, pydantic_object=RelevantParts, llm=model)

    #print(parsed)
    return parsed


def translate_content(parsed_input, lang_in, lang_out):
    if lang_in == "en": 
        lang_in = "English"
    elif lang_in == "fr": 
        lang_in = "French"

    if lang_out == "de":
        lang_out = "German"

    json_template = """{
        "relevantparts": [
            {
            "rank": 1,
            "fact": "Sam Altman, Geschäftsführer von OpenAI, wurde am Freitag unerwartet gefeuert. Seitdem erfuhr OpenAI und dessen Hauptinvestor, Microsoft, große Unruhe. Zwei Nachfolger, Mira Murati und Emmett Shear, übernahmen zeitweise seinen Job. Es wurde nun bestätigt, dass Sam Altman in seine Position zurückgekehrt ist.",
            },
            {
            "rank": 2,
            "fact": "Am 17. November 2023, entschied der Aufsichtsrat von OpenAI Sam Altman als Geschäftsführer abzubestellen. Als Antwort darauf reagierten eine signifikante Anzahl an Mitarbeitern, was in einem Abkommen zur Rückkehr von Altman als Geschäftsführer resultierte.",
            },
            {
            "rank": 3,
            "fact": "Sam Altman war in verschiedene Unternehmumgen außerhalb von OpenAI involviert, u.a. als Geschäftsführer von Reddit für einen kurzen Zeitraum, als Unterstützer der Forschung zu COVID-19, und als Investor in Startups und Unternehmen für nukleare Energie. Er engagierte sich außerdem in politischen Aktivitäten und zu Philanthropie.",
            }
        ]
        }"""

    system_intel = f"""You are an expert translator from {lang_in} to {lang_out}."""
    prompt = f"""If the 'fact' part in the json object is already in {lang_out}, then ignore the following instructions and return the original json object as-is. 
    Otherwise: Given the following json object, translate any elements within the 'fact' part that are not in {lang_out} into {lang_out}, except for short direct quotes. 
    For longer quotes, do translate them, but also put the original quote in original language.
    Pay attention to use correct German formulations and grammar, as you would find them in a news article.

    json object: 
    {parsed_input}

    Return the altered json object in JSON, use the following format (not content):
    JSON:
    {json_template}
    """

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    return res


def translate_content_new(parsed_input, lang_in, lang_out):
    if lang_in == "en": 
        lang_in = "English"
    elif lang_in == "fr": 
        lang_in = "French"

    if lang_out == "de":
        lang_out = "German"

    json_template_in = """{
        "relevantparts": [
            {
            "rank": 1,
            "fact": "Sam Altman, CEO of OpenAI, was unexpectedly fired on a Friday. Since then, OpenAI and its main investor, Microsoft, experienced turmoil. Two successors, Mira Murati and Emmett Shear, temporarily took over his job. It's now confirmed that Sam Altman has returned to his position.",
            "reasoning": "Provides context about the recent events regarding his role at OpenAI."
            },
            {
            "rank": 2,
            "fact": "On November 17, 2023, OpenAI's board decided to remove Sam Altman as CEO. In response, a significant number of employees reacted, resulting in an agreement in principle for Altman's return as CEO.",
            "reasoning": "Details the reason behind his brief departure and the process leading to his reinstatement."
            },
            {
            "rank": 3,
            "fact": "Sam Altman has been involved in various ventures outside of OpenAI, including being the CEO of Reddit for a short period, supporting COVID-19 research, and investing in startups and nuclear energy companies. He has also been engaged in political activities and philanthropy.",
            "reasoning": "Shows Altman's diverse interests and influence beyond his role at OpenAI."
            }
        ]
        }"""

    json_template_out = """{
        "relevantparts": [
            {
            "rank": 1,
            "fact": "Sam Altman, Geschäftsführer von OpenAI, wurde am Freitag unerwartet gefeuert. Seitdem erfuhr OpenAI und dessen Hauptinvestor, Microsoft, große Unruhe. Zwei Nachfolger, Mira Murati und Emmett Shear, übernahmen zeitweise seinen Job. Es wurde nun bestätigt, dass Sam Altman in seine Position zurückgekehrt ist.",
            },
            {
            "rank": 2,
            "fact": "Am 17. November 2023, entschied der Aufsichtsrat von OpenAI Sam Altman als Geschäftsführer abzubestellen. Als Antwort darauf reagierten eine signifikante Anzahl an Mitarbeitern, was in einem Abkommen zur Rückkehr von Altman als Geschäftsführer resultierte.",
            },
            {
            "rank": 3,
            "fact": "Sam Altman war in verschiedene Unternehmumgen außerhalb von OpenAI involviert, u.a. als Geschäftsführer von Reddit für einen kurzen Zeitraum, als Unterstützer der Forschung zu COVID-19, und als Investor in Startups und Unternehmen für nukleare Energie. Er engagierte sich außerdem in politischen Aktivitäten und zu Philanthropie.",
            }
        ]
        }"""

    system_intel = f"""You are an expert translator from {lang_in} to {lang_out}."""
    prompt = f"""You are given a json object. If the 'fact' part in the json object is already in {lang_out}, then ignore the following instructions and return the original json object as-is. 
    Otherwise: Given the json input, translate any elements within the 'fact' part of the json object that are not in {lang_out} into {lang_out}, except for direct quotes from a person. 
    Pay attention to use correct {lang_out} formulations and grammar, as you would find them in a news article.

    Here is an example: 
    
    Given the following json input, you would return the json output with the translated 'fact' part:
    
    json input:
    {json_template_in}

    json output:
    {json_template_out}

    Now to the same task (translating the 'fact' part to German from any given language) with the following json object:
    json input: 
    {parsed_input}

    json output:
    """

    template_in = """[RelevantPart(rank=1, fact='Joseph Robinette Biden Jr. is the 46th and current president of the United States, a member of the Democratic Party, and has previously served as the 47th vice president from 2009 to 2017 under President Barack Obama.'), RelevantPart(rank=2, fact='Before his presidency, Biden represented Delaware in the United States Senate from 1973 to 2009, and during his tenure, he was known for drafting legislation such as the Violent Crime Control and Law Enforcement Act and the Violence Against Women Act.'), RelevantPart(rank=3, fact="Biden ran for the Democratic presidential nomination in 1988 and 2008, and he was chosen as Barack Obama's running mate in 2008. He served two terms as vice president, acting as a close counselor to Obama."), RelevantPart(rank=4, fact='In the 2020 presidential election, Biden and his running mate, Kamala Harris, defeated Donald Trump and Mike Pence, becoming the oldest president in U.S. history and appointing the first female vice president.'), RelevantPart(rank=5, fact='As president, Biden has signed numerous significant bills including the American Rescue Plan Act, bipartisan bills on infrastructure, and the Inflation Reduction Act. He has also appointed a justice to the U.S. Supreme Court and was involved in major foreign policy actions such as withdrawing troops from Afghanistan and responding to the Russian invasion of Ukraine.')]"""

    template_out = """[RelevantPart(rank=1, fact='Joseph Robinette Biden Jr. ist der 46te und aktuelle Präsident der Vereinigten Staaten, ein Mitglieder der Partei der Demokraten, und war zuvor der 47te Vize-Präsident von 2009 bis 2017 unter Präsident Barack Obama.'), RelevantPart(rank=2, fact='Vor seiner Zeit als Präsident, repräsenntierte Biden Delaware im Senat der USA von 1973 bis 2009, und während seiner Amtszeit war er dafür bekannt, Gesetzgebung zu entwerfen, wie den Violent Crime Control and Law Enforcement Act und der Violence Against Women Act.'), RelevantPart(rank=3, fact="Biden kandidierte 1988 und 2008 für die Präsidentschaftskandidatur der Demokraten und wurde 2008 als Kandidat von Barack Obama ausgewählt. Er diente zwei Amtszeiten als Vizepräsident und war ein enger Berater von Obama."), RelevantPart(rank=4, fact='Bei den Präsidentschaftswahlen 2020 besiegten Biden und seine Kandidatin Kamala Harris Donald Trump und Mike Pence, wurden der älteste Präsident in der Geschichte der USA und ernannten die erste weibliche Vizepräsidentin.'), RelevantPart(rank=5, fact='Als Präsident hat Biden zahlreiche wichtige Gesetze unterzeichnet, darunter den American Rescue Plan Act, überparteiliche Gesetze zur Infrastruktur und den Inflation Reduction Act. Außerdem hat er einen Richter in den Obersten Gerichtshof der USA berufen und war an wichtigen außenpolitischen Maßnahmen wie dem Truppenabzug aus Afghanistan und der Reaktion auf die russische Invasion in der Ukraine beteiligt.')]"""

    prompt2 = f"""You are given a list of Pydantic objects. Given that input of Pydantic objects, translate elements named 'fact' witih the list of Pydantic Objects that are not in {lang_out} into {lang_out}, except for direct quotes from a person. 
    Pay attention to use correct {lang_out} formulations and grammar, as you would find them in a news article.

    Here is an example: 
    
    Given the following list of Pydantic Objects as input, you would return an almost identical list of Pydantic Objects as output, with the translated 'fact' part:
    
    Input list of Pydantic Objects:
    {template_in}

    Output list of Pydantic Objects:
    {template_out}

    Now do the same task (translating the 'fact' part to German from any given language) with the following list of Pydantic Objects:
    Input list of Pydantic Objects: 
    {parsed_input}

    Output list of Pydantic Objects:
    """

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    return res


def concatenate_relevant_parts_to_show(relevant_parts_to_show):
    string_to_show = ""
  
    for rp in relevant_parts_to_show.relevantparts:
        if string_to_show == "":
            string_to_show = rp.fact
        else:
            string_to_show += "\n\n" + rp.fact
    return string_to_show


## get JSON data w/ API and extract image URL
def get_image_url(partial_url):
    try:
        api_res = requests.get(query + partial_url, headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}).json()
        first_part = api_res['query']['pages']
        # this is a way around not knowing the article id number
        for key, value in first_part.items():
            if (value['original']['source']):
                data = value['original']['source']
                return data
    except Exception as exc:
        print(exc)

        data = None
    return data


def get_image_url_backup(url, title):

    response = requests.get(url, headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'})
    soup = BeautifulSoup(response.text, 'lxml')#'html.parser')

    ##can be both:
    title_part = title.split('_')[0].lower()
    title_part = title_part.split(' ')[0].lower()
    found = False
    first_image_tag = soup.find('img')
    image_url = first_image_tag.get('src').lower()

    if title_part in image_url:
        found = True
        first_image_tag = first_image_tag

    # Extract the URL from the src attribute
    image_url = ''
    if first_image_tag and found == True:
        image_url = first_image_tag.get('src')
        # Check if the URL is complete; if not, you might need to prepend the domain
        if image_url:
            if not image_url.startswith(('http:', 'https:')):
                image_url = f"https:{image_url}"
            print(f"First image URL: {image_url}")
        else:
            print("Image src attribute is missing.")
    else:
        print("No image found in the HTML content.")

    response2 = requests.get(image_url, headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'})
    # Ensure the request was successful
    output_path = ''
    if response2.status_code == 200:

        ## get original file extension for image
        ## by splitting on . and getting the final segment
        file_ext = '.' + image_url.split('.')[-1].lower()

        ## save the image to folder - binary file - with desired filename
        output_path = os.path.join(my_folder, os.path.basename(title.replace(' ', '_') + file_ext))
        with open(output_path, 'wb') as file:

            for chunk in response2.iter_content(100000):
                file.write(chunk)
            file.close()

    else: 
        print('could not get image from url')
    return image_url, output_path


## download one image with URL obtained from API
def download_image(the_url, the_page):
    headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
    res = requests.get(the_url, headers=headers)
    res.raise_for_status()

    ## get original file extension for image
    ## by splitting on . and getting the final segment
    file_ext = '.' + the_url.split('.')[-1].lower()

    ## save the image to folder - binary file - with desired filename
    image_file = open(os.path.join(my_folder, os.path.basename(the_page.replace(' ', '_') + file_ext)), 'wb')

    ## download the image file 
    for chunk in res.iter_content(100000):
        image_file.write(chunk)
    image_file.close()

    return file_ext


def shrink_image(input_path, output_path, max_dimension=512):
    ## Open the image
    original_image = Image.open(input_path)
 
    ## Get original width and height
    original_width, original_height = original_image.size
 
    ## Calculate the new dimensions while maintaining the aspect ratio
    if original_width > original_height:
        new_width = max_dimension
        new_height = int((original_height / original_width) * max_dimension)
    else:
        new_width = int((original_width / original_height) * max_dimension)
        new_height = max_dimension
 
    ## Resize the image
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
 
    ## Save the resized image
    resized_image.save(output_path)

    return resized_image


def get_best_entry(context, options_string, title):
    json_template = """
    {
    "query": "Sustainable gardening",
    "rankedLinks": [
        {
        "rank": 1,
        "title": "Sustainable Gardening Techniques",
        "url": "https://en.wikipedia.org/wiki/sustainable-techniques",
        "HTML line": "Sustainable Gardening Techniques, comprehensive gardening tips"
        },
        {
        "rank": 2,
        "title": "Sustainable Gardening 101",
        "url": "https://www.ecogarden.com/beginners-guide",
        "HTML line": "Sustainable Gardening 101: Getting Started, guide for beginners"
        },
        {
        "rank": 3,
        "title": "The Environmental Impact of Gardening",
        "url": "https://en.wikipedia.org/wiki/environmental-impact",
        "HTML line": "The Environmental Impact of Gardening, environmental insights"
        },
        {
        "rank": 4,
        "title": "Innovative Gardening Products",
        "url": "https://www.moderngardeningtools.com/innovative-products",
        "HTML line": "Innovative Gardening Products, sustainable product recommendations"
        }
    ]
    }"""

    system_intel = f"""You are an expert on {title} and HTML."""
    prompt = f"""Interpret the following list of options for a wikipedia page (composed of a description of the option and its url) and then return only the links that are most appropriate to represent the real link page
    for {title} given the context below, in order of relevance, in a numbered list.

    List of options:
    {options_string}

    Context: 
    {context}

    Return your answer as plain JSON, following the following format, return the Json only:
    {json_template}

    JSON:
    """

    res = ask_GPT(system_intel, prompt)
    model = get_model(chosen_model)

    ##Parse results
    parsed = parse_results(res, pydantic_object=RankedWikiEntries, llm=model)

    return parsed


##check if a Wikipedia page exists, returns True or False
def check_wiki_valid(url):
    r = requests.head(url)
    return r.ok


def extract_insta_username(insta_url):
    dest_username = insta_url.replace('https://www.instagram.com/', '')
    if dest_username[-1] == '/':
        dest_username = dest_username[:-1]
    return dest_username


def get_sessionfile_from_firefox():
    #load_sessionfile(sessionfile)
    ##Alternative to the above, getting session after a firefox insta login
    session_directory = "../instaloader"
    filename = "{}session-{}".format(session_directory, username)
    import_session_from_firefox(cookiefile=None, sessionfile=filename, username=username)#f"{session_directory}/{filename}", username=username)
    #import_session_from_firefox(None, username)
    #print(cookiefile)
    print(username)


##TODO: Also try getting the sessionfile after firefox login, more flexible with regards to different users and no need to put password into .env
def get_sessionfile():
    print(sessionfile)
    if not exists(sessionfile):
        get_sessionfile_from_firefox()
    else:
        print('sessionfile exists')

        ##NOTE TODO: I probably need to delete the sessionfile if it is > 24 hours old and create a new one
        last_modified = check_sessionfile_date()
        time_delta = datetime.now() - last_modified
        print('age of sessionfile:')
        print(time_delta)

        # Calculate total hours
        total_hours = time_delta.days * 24 + time_delta.seconds // 3600  # Use integer division for hours

        # Check if greater than 24 hours
        if total_hours > 24:
            print('Sessionfile is more than 24h old, replacing it')
            get_sessionfile_from_firefox()


def check_insta_valid_and_verified(url):
    ##returning values for 'valid' and 'verified' insta profile
    print('in check_insta')
    print(sessionfile)
    print(session_loaded)

    get_sessionfile()
    load_sessionfile(sessionfile)

    print(url)

    dest_username = extract_insta_username(url)

    profile = None

    try:
        #profile = instaloader.Profile.from_username(L2.context, dest_username)
        #get_insta_profile_infos(L, profile)
        try:
            print('getting insta_verified status:')
            if get_insta_verified_status(dest_username) == True:#profile) == True:
                return True, True
            else:
                return True, False
        except: ##sometimes Insta Login not working, still return true for valid Insta_page:
            print('in except')
            return True, False
    except instaloader.exceptions.LoginRequiredException:
        print("Login required to access this profile.")
        # Handle LoginRequiredException
        profile = None
        return False, False
    except instaloader.exceptions.ProfileNotExistsException:
        print("The requested profile does not exist.")
        # Handle ProfileNotExistsException
        profile = None
        return False, False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # Handle other exceptions
        profile = None
        return False, False
    
def get_insta_verified_status(dest_username):#profile):

    get_sessionfile()
    load_sessionfile(sessionfile)
    try: 
        profile = instaloader.Profile.from_username(L2.context, dest_username)
    except Exception as e:
        print(f"The following error occurred: {e}")

    profile = instaloader.Profile.from_username(L2.context, dest_username)
    if profile.is_verified:
        return True
    else:
        return False

def get_insta_profile_infos(L, profile):
    #profile = instaloader.Profile.from_username(L.context, pro)
    print('got profile')
    main_followers = profile.followers
    no_posts = profile.mediacount
    idx = profile.userid
    print('The profile UserID')
    print(idx)
    print('The number of followers')
    print(main_followers)
    print('The total number of posts')
    print(no_posts)
    print('The profile is a verified profile?')
    print(profile.is_verified)
    print('before getting posts')
    posts = profile.get_posts()
    print(posts)
    i = 0
    for p in posts:
        print(p.date)
        if i == 3:
            break
        i += 1 
    print('after getting posts')
    print('\n')


##TBD if it can be improved to work, then checking valid urls for insta at least would not necessarily require session-id
def check_insta_valid2(url):   

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    #headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
    try:
        response = requests.get(url, headers=headers)#, allow_redirects=True)
        
        #print(response.text)
        if response.text == '':
            print('response text empty')
        else: 
            print('response text not empty')
        # Check if the status code is 200
        if response.status_code == 200 and not "Diese Seite ist leider nicht verfügbar." in response.text and not "Etwas ist schiefgelaufen" in response.text and not "This page" in response.text:
            pass
            #return True
        else:
            pass
            #return False
        
        print('response.status_code')
        print(response.status_code)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        if soup.find(text="Diese Seite ist leider nicht verfügbar."):
            print("The page might not exist or is unavailable.")
        else:
            print("The page exists or the content is not directly accessible.")

    except requests.exceptions.RequestException as e:
        print(f"Error checking URL: {e}")
        return False
    

##TODO: also delete older posts, e.g. > 120 days old
def download_posts(profilename, limit=5):
    post_links = []
    post_filepaths = []

    get_sessionfile()
    load_sessionfile(sessionfile)

    posts = instaloader.Profile.from_username(L2.context, profilename).get_posts()

    SINCE = datetime.now()- timedelta(days=60)#(2023, 10, 1)
    UNTIL = datetime.now()#(2024, 2, 8)
    print('from - to:')
    print(SINCE)
    print(UNTIL)

    i = 1
    #j = 0

    ##need to be logged in: 
    #Note: It stores it in a folder with the insta-profile-name of the person
    ##TODO: Limit the timeframe
    for post in posts:#takewhile(lambda p: p.date > UNTIL, dropwhile(lambda p: p.date > SINCE, posts)):
        #print(post.date)
        #print(str(i))
        L2.download_post(post, profilename)
        #post_links.append(post.url) ##image link
        post_links.append("https://www.instagram.com/p/"+post.shortcode) ## = post link
        filename = './' + profilename + '/' + L2.format_filename(post, target=profilename)
        post_filepaths.append(filename)
        if i == limit:
            break
        i += 1
    return post_links, post_filepaths


def check_sessionfile_date():
    # Specify the file path
    session_directory = "../instaloader/" ##TODO: specify it 1x only
    file_path = "{}session-{}".format(session_directory, username)
    print('file_path:')
    print(file_path)

    # Get the creation and modification datetime of the file
    stat_info = os.stat(file_path)
    creation_time = datetime.fromtimestamp(stat_info.st_ctime)
    modification_time = datetime.fromtimestamp(stat_info.st_mtime)

    # Print the datetime information
    print(f"Creation datetime: {creation_time}")
    print(f"Modification datetime: {modification_time}")
    return modification_time


if __name__ == "__main__":
    pass