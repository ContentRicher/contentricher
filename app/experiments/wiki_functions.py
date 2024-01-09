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
from typing import Literal, List

import wikipedia
import random


load_dotenv()

API_KEY=os.getenv("API_KEY")

client = OpenAI(api_key = API_KEY)

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


def ask_GPT(system_intel, prompt): 
    result = client.chat.completions.create(model="gpt-4-1106-preview",#"gpt-3.5-turbo-1106",#"gpt-3.5-turbo",
                                 messages = [{"role": "system", "content": system_intel},
                                           {"role": "user", "content": prompt}],
                                           stream=False
            )
    #display(Markdown(result['choices'][0]['message']['content']))
    return result.choices[0].message.content


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
    #print(res)

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
    #print(res)

    ##Parse results
    try: 
        parser = PydanticOutputParser(pydantic_object=Entities) 
        parsed = parser.invoke(res)
    except:
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        parsed = fixing_parser.invoke(res)

    return parsed


##Catching disambiguation error, can be improved
def get_page_content(title):
    try: 
        p = wikipedia.page(title, auto_suggest=False, redirect=True, preload=False)
    except wikipedia.DisambiguationError as e:
        s = random.choice(e.options)
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
    #print(system_intel)
    #print(prompt)
    res = ask_GPT(system_intel, prompt) ##TODO replace by langchain generic call (llm replaceable)
    #print(res)

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

if __name__ == "__main__":
    pass


