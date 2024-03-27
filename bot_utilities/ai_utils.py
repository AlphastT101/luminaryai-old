import aiohttp
import io
from datetime import datetime
import re
import asyncio
import time
import random
import asyncio
from urllib.parse import quote
import datetime
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import requests



load_dotenv()
GPT_KEY = os.getenv('GPT_KEY')

openai_client = AsyncOpenAI(
    api_key = GPT_KEY,
    base_url = "https://api.naga.ac/v1"
)

async def sdxl(prompt):
    response = await openai_client.images.generate(
        model="playground-v2.5",
        prompt=prompt,
        n=1,  # images count
        size="4096x4096"
    )
    return response.data[0].url

# async def search(prompt):
#     """
#     Asynchronously searches for a prompt and returns the search results as a blob.

#     Args:
#         prompt (str): The prompt to search for.

#     Returns:
#         str: The search results as a blob.

#     Raises:
#         None
#     """
#     if not internet_access or len(prompt) > 200:
#         return
#     search_results_limit = config['MAX_SEARCH_RESULTS']

#     if url_match := re.search(r'(https?://\S+)', prompt):
#         search_query = url_match.group(0)
#     else:
#         search_query = prompt

#     if search_query is not None and len(search_query) > 200:
#         return

#     current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#     blob = f"Search results for: '{search_query}' at {current_time}:\n"
#     if search_query is not None:
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get('https://ddg-api.awam.repl.co/api/search',
#                                        params={'query': search_query, 'maxNumResults': search_results_limit}) as response:
#                     search = await response.json()
#         except aiohttp.ClientError as e:
#             print(f"An error occurred during the search request: {e}")
#             return

#         for index, result in enumerate(search):
#             try:
#                 blob += f'[{index}] "{result["Snippet"]}"\n\nURL: {result["Link"]}\n'
#             except Exception as e:
#                 blob += f'Search error: {e}\n'
#             blob += "\n\n"
#         return blob
#     else:
#         blob = ""
#     return blob

def fetch_chat_models():
    models = []
    headers = {
        'Authorization': f'Bearer {GPT_KEY}',
        'Content-Type': 'application/json'
    }

    response = requests.get('https://api.naga.ac/v1/models', headers=headers)
    if response.status_code == 200:
        ModelsData = response.json()
        models.extend(
            model['id']
            for model in ModelsData.get('data')
            if "max_images" not in model
        )
    else:
        print(f"Failed to fetch chat models. Status code: {response.status_code}")

    return models
    
async def generate_response_cmd(ctx, user_input, history=[]):
    # Create a system message with combined instructions
    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": "AlphasT101 is my owner. I am powered by an AI engine created by AlphasT101 called Luminary . AlphasT101 is a programmer and developer. alphast101 lives in the USA. I am an AI language model created by AlphasT101. Today's date is {datetime.date.today()}.",
    }

    # Extract relevant member information
    member_info = {
        "id": str(ctx.author.id),
        "name": str(ctx.author),
        # Add any other relevant member information
    }

    # User message with only the member ID
    user_message = {"role": "user", "name": member_info["name"], "content": user_input}

    # Add user message to history
    history.append(user_message)

    # Other messages in the conversation history
    messages = [system_message, *history]

    # Asynchronously generate a response using OpenAI Chat API
    response = await openai_client.chat.completions.create(
        model=os.getenv('GPT_MODEL'),
        messages=messages
    )

    # Extract and return the generated message content
    generated_message = response.choices[0].message.content

    # Bot message
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}

    # Add bot message to history
    history.append(bot_message)

    return generated_message, history



async def generate_response_msg(message, user_input, history=[]):
    # Create a system message with combined instructions
    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": f"AlphasT101 is my owner. I am powered by an AI engine created by AlphasT101 called Luminary . AlphasT101 is a programmer and developer. alphast101 lives in the USA. I am an AI language model created by AlphasT101. Today's date is {datetime.date.today()}.",
    }

    # Extract relevant member information
    member_info = {
        "id": str(message.author.id),
        "name": str(message.author),
        # Add any other relevant member information
    }

    # User message with only the member ID
    user_message = {"role": "user", "name": member_info["id"], "content": user_input}

    # Add user message to history
    history.append(user_message)

    # Other messages in the conversation history
    messages = [system_message, *history]

    # Asynchronously generate a response using OpenAI Chat API
    response = await openai_client.chat.completions.create(
        model=os.getenv('GPT_MODEL'),
        messages=messages
    )

    # Extract and return the generated message content
    generated_message = response.choices[0].message.content

    # Bot message
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}

    # Add bot message to history
    history.append(bot_message)

    return generated_message, history




async def poly_image_gen(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)


    

async def generate_image_prodia(prompt, model, sampler, seed):
    async def create_job(prompt, model, sampler, seed):
        negative = "DO NOT INCLUDE NSFW OR ANYTHING AGE RESTRICTED. NO PORN"
        url = 'https://api.prodia.com/generate'
        params = {
            'new': 'true',
            'prompt': f'{quote(prompt)}',
            'model': model,
            'negative_prompt': f"{negative}",
            'steps': '100',
            'cfg': '9.5',
            'seed': f'{seed}',
            'sampler': sampler,
            'upscale': 'True',
            'aspect_ratio': 'square'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
                return data['job']
            
    job_id = await create_job(prompt, model, sampler, seed)
    url = f'https://api.prodia.com/job/{job_id}'
    headers = {
        'authority': 'api.prodia.com',
        'accept': '*/*',
    }

    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers) as response:
                json = await response.json()
                if json['status'] == 'succeeded':
                    async with session.get(f'https://images.prodia.xyz/{job_id}.png?download=1', headers=headers) as response:
                        content = await response.content.read()
                        img_file_obj = io.BytesIO(content)
                        return img_file_obj

def detect_nsfw_request(query):
    nsfw_keywords = [
        'nsfw', 'adult', 'explicit', '18+', 'porn', 'xxx', 'sexual', 'indecent', 'lewd', 
        'obscene', 'raunchy', 'risqué', 'sensual', 'vulgar', 'naughty', 'kinky', 'dirty', 
        'lustful', 'provocative', 'stimulating', 'sultry', 'titillating', 'unwholesome', 
        'filthy', 'smutty', 'offensive', 'lascivious', 'carnal', 'salacious', 'X-rated', 
        'prurient', 'perverted', 'lecherous', 'horny', 'fetish', 'erogenous', 'nude', 
        'sordid', 'scandalous', 'private parts', 'intimate areas', 'sensitive anatomy',
        'naked','boob','boobies','anal','dick','fucker','fuck','fucking','without clothes','pornhub','blowjob','cum','boobjob','xxxx','xxxxx','xxxxxxx','xxxxxxxx'
    ]


    # Convert query to lowercase for case-insensitive matching
    query_lower = query.lower()

    # Check if any NSFW keyword is present in the query
    for keyword in nsfw_keywords:
        if keyword in query_lower:
            return True  # NSFW request detected

    return False  # Safe request


def search_photo(query):

    base_url = "https://www.googleapis.com/customsearch/v1"
    api_key = 'AIzaSyAh3oa-_3Zron_GNpXKnwxzIeuTrYrluFs'
    cx = '126be3d6257454161'
    params = {
        'q': f"{query} image",
        'searchType': 'image',
        'key': api_key,
        'cx': cx,
    }

    # Make the request to Google Custom Search API
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # Parse the JSON response
        result = response.json()

        # Check if there are image results
        if 'items' in result and result['items']:
            # Extract the URL of the first image
            photo_url = result['items'][0]['link']
            return photo_url
        else:
            return "No image found."
    else:
        return f"Error: {response.status_code}"
    

def web_search(query):
    # DuckDuckGo Instant Answers API endpoint
    api_url = 'https://api.duckduckgo.com/'

    # Parameters for the search query
    params = {
        'q': query,
        'format': 'json',
        'no_html': 1,
        'skip_disambig': 1
    }

    try:
        # Make the API request
        response = requests.get(api_url, params=params)
        data = response.json()

        # Check if there are relevant results
        if 'AbstractText' in data:
            result = data['AbstractText']
        elif 'Definition' in data:
            result = data['Definition']
        else:
            result = None

        return result

    except requests.RequestException as e:
        return f"An error occurred: {e}"