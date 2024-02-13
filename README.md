# ContentRicher

ContentRicher - Enriching editorial content to address different knowledge levels

## Overview

ContentRicher enables media professionals, journalists and editors, to reach a wider audience by adding additional information to articles for different target groups with different levels of knowledge.

It is a web- and AI-based system that detects relevant parts in given texts that would benefit from additional explanation. It then retrieves additional information, identifies the most relevant parts and enriches the text seamlessly.

## Features
**- AI-based Retrieval of facts:** Based on state-of-the-art Large Language Models (choose between GPT-3.5 and Mistral) and Multimodal Models ContentRicher identifies persons in the text and retrieves relevant facts about them from Wikipedia and Instagram (from both text and images). 

**- Human-AI collaboration:** While the presented facts are already relevant to journalists and editors in the writing process, we also offer automatic integration of the facts: The relevant facts are proposed to the user, who can then select which facts they want to automatically integrate into the text (still to be implemented).

**- Userfriendly Interface:** Based on Streamlit, it offers a browser-based interface, with intuitive controls and display of the results.

[![video](https://img.youtube.com/vi/CmhNdeESqKs/maxresdefault.jpg)](https://youtu.be/CmhNdeESqKs)

## Running it

To run the app, create a virtual environment with python==3.9.11 as the python version:  
```conda create --name [PUT YOUR ENVIROMENT NAME HERE] python=3.9.11```  
Activate the environment with: 
```conda activate [PUT YOUR ENVIROMENT NAME HERE]```  
Then change to the ./app folder  
```cd app/```  
and install the libraries from the requirements.txt via:  
```pip install -r requirements.txt```  
Change into the experiments folder  
```cd experiments/```  
Then, open the .env file in the experiments folder. You may need to press ```CMD + SHIFT + .``` to show the file.  Insert your key/s in the placeholders
```API_KEY = "[YOUR OPENAI API KEY HERE]"``` (for using GPT-3.5 from OpenAI) and/or put   
```MISTRAL_API_KEY = "[YOUR MISTRAL_API KEY HERE]"``` (for using the Mistral Small Model).  
Finally, run the app from the experiments folder with:  
```streamlit run frontend_experiments.py```

## Current state of development

Currently, we retrieve information from Wikipedia. The next step will be to include information from Instagram (both from text and images).
  
## 📘 License

ContentRicher is licensed under the MIT license. For more information check the LICENSE file for details.

## 🙏 Supported by

- Media Tech Lab [`media-tech-lab`](https://github.com/media-tech-lab)

<a href="https://www.media-lab.de/en/programs/media-tech-lab">
    <img src="https://raw.githubusercontent.com/media-tech-lab/.github/main/assets/mtl-powered-by.png" width="240" title="Media Tech Lab powered by logo">
</a>
