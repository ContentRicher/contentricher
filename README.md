# ContentRicher

ContentRicher - Enriching editorial content to address different knowledge levels

## Overview

ContentRicher enables media professionals, journalists and editors, to reach a wider audience by adding additional information to articles for different target groups with different levels of knowledge.

It is a web- and AI-based system that detects relevant parts in given texts that would benefit from additional explanation. It then retrieves additional information, identifies the most relevant parts and enriches the text seamlessly.

## Features
**- AI-based Retrieval of facts:** Based on state-of-the-art Large Language Models (choose between GPT-3.5 and Mistral) and Multimodal Models ContentRicher identifies persons in the text and retrieves relevant facts about them from Wikipedia and Instagram (from both text and images). 

**- Human-AI collaboration:** While the presented facts are already relevant to journalists and editors in the writing process, we also offer automatic integration of the facts: The relevant facts are proposed to the user, who can then select which facts they want to automatically integrate into the text (still to be implemented).

**- Userfriendly Interface:** Based on Streamlit, it offers a browser-based interface, with intuitive controls and display of the results.

## Running it

To run the app, in a .env file in the app/experiments folder, put API_KEY = "[YOUR API KEY HERE]"
Then run the app from the experiments folder with: 
streamlit run frontend_experiments.py
  
## 📘 License

ContentRicher is licensed under the MIT license. For more information check the LICENSE file for details.

## 🙏 Supported by

- Media Tech Lab [`media-tech-lab`](https://github.com/media-tech-lab)

<a href="https://www.media-lab.de/en/programs/media-tech-lab">
    <img src="https://raw.githubusercontent.com/media-tech-lab/.github/main/assets/mtl-powered-by.png" width="240" title="Media Tech Lab powered by logo">
</a>
