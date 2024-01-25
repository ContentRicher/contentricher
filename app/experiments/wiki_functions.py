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

# set the folder name where images will be stored
my_folder = "../img/"#'wiki_images'

# create the folder in the current working directory
# in which to store the downloaded images
os.makedirs(my_folder, exist_ok=True)

# front part of each Wikipedia URL
base_url = 'https://en.wikipedia.org/wiki/'

# Wikipedia API query string to get the main image on a page
# (partial URL will be added to the end)
query = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='


load_dotenv()

API_KEY=os.getenv("API_KEY")
client = OpenAI(api_key = API_KEY)

MISTRAL_API_KEY=os.getenv("MISTRAL_API_KEY")
mistral_model = "mistral-small"
mistral_temperature = 0.15
mistral_client = MistralClient(api_key=MISTRAL_API_KEY)

chosen_model = 'GPT-3.5'#'Mistral Small'

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
#llm = OpenAI(openai_api_key="...")
model_name = "gpt-3.5-turbo"
temperature = 0.0
#model = OpenAI(openai_api_key=API_KEY, model_name=model_name, temperature=temperature)
model = ChatOpenAI(openai_api_key=API_KEY, model_name=model_name, temperature=temperature)

class URL_entry(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all URL suggestions.")
    title: str = Field(description = "This is the title of the Wikipedia page")
    url: str = Field(description = "This is the URL of the suggested Wikipedia page")
    language: str = Field(description = "This is the language of the Wikipedia page, written in abbreviation")

class URL_propositions(BaseModel):
    urls: List[URL_entry]

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

class RankedEntry(BaseModel):
    rank: int = Field(description = "This is the rank of probability among all URL suggestions.")
    title: str = Field(description = "This is the title of the Wikipedia page")
    url: str = Field(description = "This is the URL of the suggested Wikipedia page")
    HTML_line: str = Field(description = "The actual HTML line stated in the html that links to the url")

class RankedWikiEntries(BaseModel):
    query: str = Field(description = "This is the entity that is to be disambiguated.")
    rankedLinks: List[RankedEntry] 


def ask_GPT(system_intel, prompt, chosen_model='GPT-3.5'): 
    if chosen_model == 'GPT-3.5':
        return ask_openai(system_intel, prompt)
    elif chosen_model == 'Mistrall Small': ##model is Mistral
        return ask_mistral(system_intel, prompt)
    else: 
        return ''

def ask_openai(system_intel, prompt):
    result = client.chat.completions.create(model="gpt-4-1106-preview",#"gpt-3.5-turbo-1106",#"gpt-3.5-turbo",
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

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=URL_propositions) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


def get_all_wiki_urls(context):

    system_intel = """You are an expert researcher and an expert in Wikipedia."""
    prompt = f"""Given the context {context}, find the distinct people mentioned and for each the most probable two Wikipedia pages for it.""" 

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

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=Entities) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


##Catching disambiguation error, can be improved
def get_page_content(context, title):
    try: 
        p = wikipedia.page(title, auto_suggest=False, redirect=True, preload=False)
    except wikipedia.DisambiguationError as e: 
        response = requests.get(
        'https://en.wikipedia.org/w/api.php',
            params={
                'action': 'parse',
                'page': title,
                'format': 'json',
            }
        ).json()
        best_entries = get_best_entry(context, response, title)
        s = best_entries.rankedLinks[0].title
        ##before:
        #s = random.choice(e.options)
        p = wikipedia.page(s)
    #print(p.content)
    return p.content


def get_relevant_parts(context, text, wiki_title):
    ##try getting most relevant part for the given context:
    ##maybe add target_group later:
    #target_group = 'Young adults'
    json_template = """{
  "relevant_parts": [
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

    system_intel = f"""You are an expert on {wiki_title} and great in explaining and understanding people."""# and {target_group}."""
    prompt = f"""Given the context below, interpret the ARTICLE that follows it and then return only the sentences from the ARTICLE that contain relevant additional information/facts that are not present in the context

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

    Article: 
    {context}

    Information:
    {text}

    Group the selected relevant information in coherent chunks of information as short paragraphs.
    """ 

    prompt+=f"""
    Return your answer in an ordered form, with the most relevant information parts first:

    Return your answer as plain JSON, following the following format:
    {json_template}
    """
    ##later add to prompt:
    #    and that is relevant for the target group {target_group}.

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=RelevantParts) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


def translate_content(parsed_input, lang_in, lang_out):
    if lang_in == "en": 
        lang_in = "English"
    elif lang_in == "fr": 
        lang_in = "French"

    if lang_out == "de":
        lang_out = "German"

    json_template = """{
        "relevant_parts": [
            {
            "rank": 1,
            "fact": "Sam Altman, CEO of OpenAI, was unexpectedly fired on a Friday. Since then, OpenAI and its main investor, Microsoft, experienced turmoil. Two successors, Mira Murati and Emmett Shear, temporarily took over his job. It's now confirmed that Sam Altman has returned to his position.",
            },
            {
            "rank": 2,
            "fact": "On November 17, 2023, OpenAI's board decided to remove Sam Altman as CEO. In response, a significant number of employees reacted, resulting in an agreement in principle for Altman's return as CEO.",
            },
            {
            "rank": 3,
            "fact": "Sam Altman has been involved in various ventures outside of OpenAI, including being the CEO of Reddit for a short period, supporting COVID-19 research, and investing in startups and nuclear energy companies. He has also been engaged in political activities and philanthropy.",
            }
        ]
        }"""

    system_intel = f"""You are an expert translator from {lang_in} to {lang_out}."""
    prompt = f"""Given the following json object, translate any elements within the 'fact' part that are not in {lang_out} into {lang_out}, except for short direct quotes. 
    For longer quotes, do translate them, but also put the original quote in original language.
    Pay attention to use correct German formulations and grammar, as you would find them in a news article.

    json object: 
    {parsed_input}

    Return the altered json object in JSON, use the following format (not content):
    JSON:
    {json_template}
    """

    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)
    #print(result) 

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=RelevantParts) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


def concatenate_relevant_parts_to_show(relevant_parts_to_show):
    string_to_show = ""
    print('relevant_parts_to_show in concatenation call:')
    print(relevant_parts_to_show)
    print(type(relevant_parts_to_show))
  
    for rp in relevant_parts_to_show.relevantparts:
        if string_to_show == "":
            string_to_show = rp.fact
        else:
            string_to_show += "\n\n" + rp.fact
    return string_to_show

## get JSON data w/ API and extract image URL
def get_image_url(partial_url):
    try:
        api_res = requests.get(query + partial_url).json()
        first_part = api_res['query']['pages']
        # this is a way around not knowing the article id number
        for key, value in first_part.items():
            if (value['original']['source']):
                data = value['original']['source']
                return data
    except Exception as exc:
        print(exc)
        print("Partial URL: " + partial_url)
        data = None
    return data

## download one image with URL obtained from API
def download_image(the_url, the_page):
    headers = {'User-Agent': 'CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)'}
    res = requests.get(the_url, headers=headers)
    res.raise_for_status()

    ## get original file extension for image
    ## by splitting on . and getting the final segment
    file_ext = '.' + the_url.split('.')[-1].lower()

    ## save the image to folder - binary file - with desired filename
    image_file = open(os.path.join(my_folder, os.path.basename(the_page + file_ext)), 'wb')

    # download the image file 
    # HT to Automate the Boring Stuff with Python, chapter 12 
    for chunk in res.iter_content(100000):
        image_file.write(chunk)
    image_file.close()


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


def get_best_entry(context, html, title):
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
    prompt = f"""Interpret the following html and then return only the links that are most appropriate to represent the real link page
    for {title} given the context below, in order of relevance, in a numbered list.

    HTML:
    {html}

    Context: 
    {context}

    Return your answer as plain JSON, following the following format, return the Json only:
    {json_template}

    JSON:
    """

    res = ask_GPT(system_intel, prompt)

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=RankedWikiEntries) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


if __name__ == "__main__":
    pass


