import os

#os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

import base64
import time
import openai
import os
import requests
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

API_KEY=os.getenv("API_KEY")
client = OpenAI(api_key = API_KEY)

import base64
import requests

import glob

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')




orig_prompt = "Describe what’s in this image in detail as a story?"
prompt_sv = 'Describe this image and make sure to include anything notable about it (include text you see in the image). Return your answer in German, make sure you use correct German.'


def get_vision_response(base64_image, prompt=prompt_sv):
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": f"{prompt}"
            },
            {
                "type": "image_url",
                "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
            ]
        }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    #print(response.json())
    res = response.json()['choices'][0]['message']['content']
    #print(res)
    return res


def get_txt_files(folder_path):
    return glob.glob(f"{folder_path}/*.txt")


##Note: I changed it so it also takes the txt_filename as part of the search for the related images
def get_jpg_files(path_part):
    return glob.glob(f"{path_part}*.jpg")


def get_gpt4_new(system_intel, prompt, temperature=0.7):
    completion = client.chat.completions.create(
      model="gpt-4-1106-preview",#"gpt-3.5-turbo-1106",
      #response_format={"type": "json_object"},
      temperature = temperature,
      messages=[
        {"role": "system", "content": f"""{system_intel}"""},
        {"role": "user", "content": f"""{prompt}"""}
      ]
    )
    res = completion.choices[0].message.content
    return res


def get_infos_from_insta_posts(insta_name, person_name, post_links, post_filepaths, include_source=False):
    txt_files = get_txt_files('./'+insta_name)#'./heidiklum')
    txt_files.sort(reverse=True)
    #print(txt_files[:2])
    all_res = ""
    ##TODO: Only go through the most recent three ones, not old ones that were gathered before (--> delete old posts in call where downloading posts)
    ##NOTE: ordered by date ascending, therefore taking the last three post texts
    for txt_filename in txt_files[:3]:#reversed(txt_files)[:3]:
        txt_filename_timestamp_text = txt_filename[:len(txt_filename)-4]
        #print(txt_filename_timestamp_text)
        ##find the index of the post  
        try:
            index_of_file = post_filepaths.index(txt_filename_timestamp_text)
            post_link = post_links[index_of_file]
            #print(post_link)
        except:
            post_link = ''
        ##TODO: handle passing over of post_link
        all_res += "Source post:"+ post_link+"\n"

        text_object = open(txt_filename,"r")
        insta_text = text_object.read()
        #print(insta_text)

        jpg_files = get_jpg_files(txt_filename_timestamp_text)#('./heidiklum')
        jpg_files.sort()
        #print(jpg_files)

        image_texts = []
        for jpg_filename in jpg_files:
            if jpg_filename.startswith(txt_filename_timestamp_text):
                #print(jpg_filename)
                encoded_image = encode_image(jpg_filename)
                answer = get_vision_response(base64_image=encoded_image, prompt=prompt_sv)
                #print(answer)
                image_texts.append(answer)

        image_description = str(image_texts)

        system_intel = """You are a helpful assistant."""
        prompt = f"""You are given the description of one or several images for an instagram post, a text for the post/s, and the name of the person as
        well as the Instagram Profile name of the person who posted it. Make sense of it and provide your insights as a text for a journalist who would like to include the information in an article.
        Provide your answer in German and use a rather factual 'news'-style tone.
        Do not invent anything, do not generalize your findings, only describe what you see in the image and use the information provided on whom you see.

        description of image: 
        {image_description}

        text: 
        {insta_text}

        person name: 
        {person_name}

        profile name: 
        @{insta_name}
        """
        #print(prompt)

        ##TODO: replace with GPT-3.5 and Mistral calls, put them in a separate file
        res = get_gpt4_new(system_intel, prompt)

        all_res += ("\n"+res)
    return all_res


if __name__ == "__main__":
    #pass
    print(get_infos_from_insta_posts("heidiklum", "Heidi Klum"))

    ##TODO: delete old posts (in cron job?)

    # txt_files = get_txt_files('./heidiklum')
    # txt_files.sort()
    # print(txt_files[:2])
    # for txt_filename in txt_files:
    #     txt_filename_timestamp_text = txt_filename[:len(txt_filename)-4]
    #     print(txt_filename_timestamp_text)
    #     text_object = open(txt_filename,"r")
    #     insta_text = text_object.read()
    #     print(insta_text)

    #     jpg_files = get_jpg_files(txt_filename_timestamp_text)#('./heidiklum')
    #     jpg_files.sort()
    #     print(jpg_files)

    #     image_texts = []
    #     for jpg_filename in jpg_files:
    #         if jpg_filename.startswith(txt_filename_timestamp_text):
    #             print(jpg_filename)
    #             encoded_image = encode_image(jpg_filename)
    #             answer = get_vision_response(base64_image=encoded_image, prompt=prompt_sv)
    #             print(answer)
    #             image_texts.append(answer)
    #     print('---------')
    #     image_description = str(image_texts)

    #     system_intel = """You are a helpful assistant."""
    #     prompt = f"""You are given the description of one or several images for an instagram post, a text for the post/s, and the name of the person as
    #     well as the Instagram Profile name of the person who posted it. Make sense of it and provide your insights as a text for a journalist who would like to include the information in an article.
    #     Provide your answer in German and use a rather factual 'news'-style tone.

    #     description of image: 
    #     {image_description}

    #     text: 
    #     {insta_text}

    #     person name: 
    #     Heidi Klum

    #     profile name: 
    #     @heidiklum
    #     """
    #     print(prompt)

    #     ##TODO: replace with GPT-3.5 and Mistral calls, put them in a separate file
    #     res = get_gpt4_new(system_intel, prompt)
    #     print(res)
    #     print('ooooooooooooooooooooooooooooooo')

    # # Path to your image
    # #image_path = "./heidiklum/2024-02-15_02-05-27_UTC_1.jpg"#"./heidiklum/2024-02-13_14-33-37_UTC.jpg"#"meditating_cats.png"#"/content/meditating_cats.png"
    # for image_path in jpg_files:
    #     # Getting the base64 string
    #     encoded_image = encode_image(image_path)
    #     answer = get_vision_response(base64_image=encoded_image, prompt=prompt_sv)
    #     print(answer)