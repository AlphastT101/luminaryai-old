import aiohttp
import io
from datetime import datetime
import re
import asyncio
import time
import random
import asyncio
from urllib.parse import quote
from bot_utilities.config_loader import load_current_language, config
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv

load_dotenv()
current_language = load_current_language()
internet_access = config['INTERNET_ACCESS']

openai_client = AsyncOpenAI(
    api_key = os.getenv('CHIMERA_GPT_KEY'),
    base_url = "https://api.naga.ac/v1"
)

async def sdxl(prompt):
    response = await openai_client.images.generate(
        model="sdxl",
        prompt=prompt,
        n=1,  # images count
        size="1024x1024"
    )
    return response.data[0].url

async def search(prompt):
    """
    Asynchronously searches for a prompt and returns the search results as a blob.

    Args:
        prompt (str): The prompt to search for.

    Returns:
        str: The search results as a blob.

    Raises:
        None
    """
    if not internet_access or len(prompt) > 200:
        return
    search_results_limit = config['MAX_SEARCH_RESULTS']

    if url_match := re.search(r'(https?://\S+)', prompt):
        search_query = url_match.group(0)
    else:
        search_query = prompt

    if search_query is not None and len(search_query) > 200:
        return

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    blob = f"Search results for: '{search_query}' at {current_time}:\n"
    if search_query is not None:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get('https://ddg-api.awam.repl.co/api/search',
                                       params={'query': search_query, 'maxNumResults': search_results_limit}) as response:
                    search = await response.json()
        except aiohttp.ClientError as e:
            print(f"An error occurred during the search request: {e}")
            return

        for index, result in enumerate(search):
            try:
                blob += f'[{index}] "{result["Snippet"]}"\n\nURL: {result["Link"]}\n'
            except Exception as e:
                blob += f'Search error: {e}\n'
            blob += "\n\n"
        return blob
    else:
        blob = ""
    return blob
    
async def fetch_models():
    models = await openai_client.models.list()
    return models
    
async def generate_response(instructions, search, history):
    search_results = search if search is not None else ""
    messages = [
            {"role": "system", "name": "instructions", "content": instructions},
            *history,
            {"role": "system", "name": "search_results", "content": search_results},
        ]
    response = await openai_client.chat.completions.create(
        model=config['GPT_MODEL'],
        messages=messages
    )
    message = response.choices[0].message.content
    return message

async def generate_gpt4_response(prompt):
    messages = [
            {"role": "system", "name": "admin_user", "content": prompt},
        ]
    response = await openai_client.chat.chat.completions.create(
        model='gpt-4',
        messages=messages
    )
    message = response.choices[0].message.content
    return message

async def poly_image_gen(session, prompt):
    seed = random.randint(1, 100000)
    image_url = f"https://image.pollinations.ai/prompt/{prompt}?seed={seed}"
    async with session.get(image_url) as response:
        image_data = await response.read()
        return io.BytesIO(image_data)

# async def fetch_image_data(url):
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as response:
#             return await response.read()

async def dall_e_gen(model, prompt, size, num_images):
    response = await openai_client.chat.images.generate(
        model=model,
        prompt=prompt,
        n=num_images,
        size=size,
    )
    imagefileobjs = []
    for image in response.data:
        image_url = image.url
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                content = await response.content.read()
                img_file_obj = io.BytesIO(content)
                imagefileobjs.append(img_file_obj)
    return imagefileobjs
    

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
