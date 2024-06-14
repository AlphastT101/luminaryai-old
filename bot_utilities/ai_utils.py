import aiohttp
import io
import random
from urllib.parse import quote
from openai import AsyncOpenAI
from PIL import Image
import requests
from io import BytesIO
import requests
from dotenv import load_dotenv
import asyncio
from bot_utilities.prompt_sys import prompt
import yaml
from bot_utilities.start_util import *
import imagehash


filename_to_encrypt = '.env'
file_to_save_key = 'binary'
key_size = 50
if is_file_encrypted(filename_to_encrypt):
    key = get_key(file_to_save_key)
    decrypt_aes(key, filename_to_encrypt)
    load_dotenv()
    GPT_KEY = os.getenv('GPT_KEY')
    new_key = gen_key(file_to_save_key, 50)
    encrypt_aes(new_key, filename_to_encrypt)
else:
    load_dotenv()
    GPT_KEY = os.getenv('GPT_KEY')
    new_key = gen_key(file_to_save_key, 50)
    encrypt_aes(new_key, filename_to_encrypt)


with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)
GPT_MODEL = config["bot"]["text_model"]
image_model = config["bot"]["image_model"]
request_queue = asyncio.Queue()

openai_client = AsyncOpenAI(
    api_key = GPT_KEY,
    base_url = "https://api.naga.ac/v1"
)

async def sdxl(prompt):
    response = await openai_client.images.generate(
        model=image_model,
        prompt=prompt,
        n=1,  # images count
        size="4096x4096"
    )
    return response.data[0].url




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

    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": prompt,
    }

    member_info = {
        "id": str(ctx.author.id),
        "name": str(ctx.author),
    }

    user_message = {"role": "user", "name": member_info["name"], "content": user_input}
    history.append(user_message)

    messages = [system_message, *history]
    response = await openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )

    generated_message = response.choices[0].message.content
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}
    history.append(bot_message)

    return generated_message, history



async def generate_response_msg(message, user_input, history=[]):
    system_message = {
        "role": "system",
        "name": "LuminaryAI",
        "content": prompt,
    }
    member_info = {
        "id": str(message.author.id),
        "name": str(message.author),
    }
    user_message = {"role": "user", "name": member_info["id"], "content": user_input}
    history.append(user_message)
    messages = [system_message, *history]
    await request_queue.put((messages, history))

    response = await openai_client.chat.completions.create(
        model=GPT_MODEL,
        messages=messages
    )
    generated_message = response.choices[0].message.content
    bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}

    history.append(bot_message)
    return generated_message, history


async def process_queue():
    while True:
        messages, history = await request_queue.get()
        response = await openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=messages
        )
        generated_message = response.choices[0].message.content
        bot_message = {"role": "system", "name": "LuminaryAI", "content": generated_message}
        history.append(bot_message)
        request_queue.task_done()



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
    

# Define your Google Custom Search API key and search engine ID
API_KEY = 'AIzaSyBNCNpIH26nsO_umj1LHMSMCo1jzmgkuaI'
SEARCH_ENGINE_ID = 'a1d15feaa6af94024'

# Function to search for images
def search_image(query):
    search_url = f"https://www.googleapis.com/customsearch/v1?key={API_KEY}&cx={SEARCH_ENGINE_ID}&searchType=image&q={query}"

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        
        # Extract image URLs from the search results
        image_urls = [item['link'] for item in data.get('items', [])[:10]]
        
        return image_urls
    except requests.exceptions.RequestException as e:
        print(f"Error searching for images: {e}")
        return None


def create_composite_image(image_urls, images_per_row=5, spacing=10, target_size=(256, 256)):
    images = []
    hashes = set()

    for url in image_urls:
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            img = img.resize(target_size, Image.LANCZOS)
            img_hash = imagehash.average_hash(img)

            if img_hash not in hashes:
                hashes.add(img_hash)
                images.append(img)
            else:
                print(f"Skipped image: {url} - Duplicate image detected")
        except Exception as e:
            print(f"Skipped image: {url} - Cannot identify image: {e}")

    if not images:
        print("No valid images found.")
        return None

    # Calculate dimensions for composite image
    img_width, img_height = target_size
    row_height = img_height + spacing
    total_rows = (len(images) + images_per_row - 1) // images_per_row
    composite_width = img_width * images_per_row + spacing * (images_per_row - 1)
    composite_height = row_height * total_rows

    # Create the composite image
    composite_image = Image.new('RGBA', (composite_width, composite_height), color=(255, 255, 255, 0))

    # Paste images onto the composite image
    x_offset = 0
    y_offset = 0
    for i, img in enumerate(images):
        composite_image.paste(img, (x_offset, y_offset))
        x_offset += img_width + spacing
        if (i + 1) % images_per_row == 0:
            y_offset += row_height
            x_offset = 0

    # Create the directory if it doesn't exist
    directory = 'luminaryai/images'
    os.makedirs(directory, exist_ok=True)

    # Save the composite image
    file_path = os.path.join(directory, 'composite_image.png')
    composite_image.save(file_path)

    # Log the link to the file
    print(f"Composite image saved at: {os.path.abspath(file_path)}")

    return file_path


async def vision(prompt, image_link):
    try:
        response = await openai_client.chat.completions.create(
            model="gemini-pro-vision",
            messages=[
            {
                "role": "user",
                "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                    "url": image_link
                    },
                },
                ],
            }
            ],

        )
        return response.choices[0].message.content
    except:
        return "Ouch! Something went wrong!"