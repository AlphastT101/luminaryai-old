import discord
from discord.ext import commands
import io
import random
from openai import AsyncOpenAI
from dotenv import load_dotenv
from bot_utilities.config_loader import load_current_language, config
import os
import requests
import aiohttp
from urllib.parse import quote


async def embed(ctx ,title, description, color):
    embed = discord.Embed(title=title, description=description, color=color)
    await ctx.send(embed=embed)

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

    
async def fetch_models():
    models = await openai_client.models.list()
    return models
    
async def generate_response(ctx, user_input, history=[]):
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
        model=config['GPT_MODEL'],
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


# Replace 'YOUR_GPT_MODEL' with your actual GPT model name
openai_client = AsyncOpenAI(
    api_key = os.getenv('CHIMERA_GPT_KEY'),
    base_url = "https://api.naga.ac/v1"
)



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







async def generate_image_prodia(prompt, model, sampler, seed, neg):
    async def create_job(prompt, model, sampler, seed, neg):
        url = 'https://api.prodia.com/generate'
        params = {
            'new': 'true',
            'prompt': f'{quote(prompt)}',
            'model': model,
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
            
    job_id = await create_job(prompt, model, sampler, seed, neg)
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
    if not detect_nsfw_request(query):
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
    else:
        return "Bad"





aiml_folder = "data"

# Dictionary to store server-specific data
server_data_aiml = {}
aiml_channels = {}


server_data_ai = {}
ai_channels = {}


def ai(bot):

    ###### aiml #########
    @bot.command(name='aiml.start')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def start(ctx):
        # Get or create server-specific data and set AI responses as false
        server_id = ctx.guild.id
        if server_id not in server_data_ai:
            server_data_ai[server_id] = {'response_enabled': False}
        if server_id not in server_data_aiml:
            server_data_aiml[server_id] = {'response_enabled': False}

        # Check if the user is a moderator, administrator, or has a specific role
        if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:
    
            if server_data_aiml[server_id]['response_enabled'] == False and server_data_ai[server_id]['response_enabled'] == True:
                server_data_ai[server_id]['response_enabled'] = False # set ai false
                server_data_aiml[server_id]['response_enabled'] = True # set aiml true
                aiml_channels[server_id] = ctx.channel.id  # Store the channel ID
                await ctx.send(f'AIML enabled & disabled AI. AIML responses will be sent in <#{ctx.channel.id}>.')
    
            elif server_data_aiml[server_id]['response_enabled'] == False and server_data_ai[server_id]['response_enabled'] == False:
                # No need to ai_channels to false bcz its already set to false
                server_data_aiml[server_id]['response_enabled'] = True # set aiml true
                aiml_channels[server_id] = ctx.channel.id  # Store the channel ID
                await ctx.send(f'AIML enabled. AIML responses will be sent in <#{ctx.channel.id}>.')
        else:
            await ctx.send("You don't have permission to use this command.")


    @bot.command(name='aiml.stop')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        server_id = ctx.guild.id
        # Check if the user is a moderator, administrator, or has a specific role
        if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:
            server_data_aiml[server_id]['response_enabled'] = False
            await ctx.send("AIML disabled.")
        else:
            await ctx.send("You don't have permission to use this command.")





    ############### ai ##############
    # @bot.command(name='activate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def start(ctx):
    #     # Get or create server-specific data and set AI responses as false
    #     server_id = ctx.guild.id
    #     if server_id not in server_data_ai:
    #         server_data_ai[server_id] = {'response_enabled': False}
    #     if server_id not in server_data_aiml:
    #         server_data_aiml[server_id] = {'response_enabled': False}

    #     # Check if the user is a moderator, administrator, or has a specific role
    #     if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:

    #         if ctx.channel.slowmode_delay >= 10:
    #             if server_data_ai[server_id]['response_enabled'] == False and server_data_aiml[server_id]['response_enabled'] == True:
    #                 server_data_aiml[server_id]['response_enabled'] = False #set aiml to false
    #                 server_data_ai[server_id]['response_enabled'] = True #set ai to true
    #                 ai_channels[server_id] = ctx.channel.id  # Store the channel ID
    #                 await ctx.send(f'AI enabled & disabled AIML. AI responses will be sent in <#{ctx.channel.id}>.')

    #             elif server_data_ai[server_id]['response_enabled'] == False and server_data_aiml[server_id]['response_enabled'] == False:
    #                 # No need to set aiml_channel to false bcz its already false.
    #                 server_data_ai[server_id]['response_enabled'] = True #set ai to true
    #                 ai_channels[server_id] = ctx.channel.id  # Store the channel ID
    #                 await ctx.send(f'AI enabled. AI responses will be sent in <#{ctx.channel.id}>.')
    #         else:
    #             await ctx.send("Enable 10s slow mode first.")
    #     else:
    #         await ctx.send("You don't have permission to use this command.")

    #     await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used start command in {ctx.guild.name}")


    # @bot.command(name='deactivate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def stop(ctx):
    #     server_id = ctx.guild.id
    #     # Check if the user is a moderator, administrator, or has a specific role
    #     if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:
    #         server_data_ai[server_id]['response_enabled'] = False
    #         await ctx.send("AI disabled.")
    #     else:
    #         await ctx.send("You don't have permission to use this command.")

    #     await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used stop command in {ctx.guild.name}")




    # @bot.command(name="img")
    # @commands.cooldown(1, 60, commands.BucketType.user)
    # async def img(ctx):

    #     img_premium = discord.Embed(
    #         title="LuminaryAI premium",
    #         description="Elevate your creative experience to new heights with LuminaryAI Premium! Unleash the full power of AI-driven text and image generation for unparalleled results. Connect with Alphast101 through direct message to discover the exclusive details and take your creative endeavors to the next level!",
    #         color=0x99ccff
    #     )
    #     img_premium.set_footer(text="LuminaryAI")
    #     img_premium.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/855ee174beb05d89a42fd4ff5c19dcab.webp?size=80")

    #     img_premium.set_image(url="attachment://ai_premium.png")
    #     filename = "ai_premium.png"
    #     # Send the embed without the file parameter
    #     await ctx.send(embed=img_premium, file=discord.File(filename, filename="ai_premium.png"))
    #     await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used img command in {ctx.guild.name}")


    # @bot.command(name="ai")
    # @commands.cooldown(1, 60, commands.BucketType.user)
    # async def ai(ctx):

    #     ai_premium = discord.Embed(
    #         title="LuminaryAI premium",
    #         description="Elevate your creative experience to new heights with LuminaryAI Premium! Unleash the full power of AI-driven text and image generation for unparalleled results. Connect with Alphast101 through direct message to discover the exclusive details and take your creative endeavors to the next level!",
    #         color=0x99ccff
    #     )
    #     ai_premium.set_footer(text="LuminaryAI")
    #     ai_premium.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/855ee174beb05d89a42fd4ff5c19dcab.webp?size=80")



    #     ai_premium.set_image(url="attachment://ai_premium.png")
    #     filename = "ai_premium.png"
    #     # Send the embed without the file parameter
    #     await ctx.send(embed=ai_premium, file=discord.File(filename, filename="ai_premium.png"))

    #     await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used ai command in {ctx.guild.name}")


    member_histories = {}  # Dictionary to store conversation history for each member
    @bot.command(name='response')
    @commands.cooldown(1, 80, commands.BucketType.user)
    async def answer_command(ctx, *, args: str = None):
        if args is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your question.", color=0x99ccff)
            return
        # Get or create member-specific history
        member_id = str(ctx.author.id)  # Using member ID as the key
        history = member_histories.get(member_id, [])

        answer_embed = discord.Embed(
            title="LuminaryAI - answer generation",
            description="Generating answer...",
            color=0x99ccff
        )
        answer = await ctx.reply(embed=answer_embed)

        user_input = args
        generated_message, updated_history = await generate_response(ctx, user_input, history)

        # Update member-specific history
        member_histories[member_id] = updated_history

        answer_generated = discord.Embed(
            title="LumianryAI - answer generation",
            description=generated_message,
            color=0x99ccff
        )
        await answer.edit(embed=answer_generated)



    @bot.command(name='imagine')
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def imagine_command(ctx, *, prompt: str = None):
        if prompt is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your prompt", color=0x99ccff)
            return
        embed_img_generation = discord.Embed(
            title="LuminaryAI image generation",
            description="Image generating...",
            color=0x99ccff
        )
        msg = await ctx.reply(embed=embed_img_generation)  # Add await here
        try:
            image_url = await sdxl(prompt) 
            # Create an embed with the image
            embed_final = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: {ctx.author}\nPrompt: {prompt}",
                color=0x99ccff
            )
            embed_final.set_footer(text="LuminaryAI encourages positive interactions. It disclaims responsibility for content generated based on user inputs.")
            embed_final.set_image(url=image_url)
            
            # Send the embed
            await msg.edit(embed=embed_final)

        except:
            error_embed = discord.Embed(
                title="Luminary - image generation",
                description="ERROR: 403\n\nThis error occurs when the user's request contains inappropriate content, leading to restricted access. Please ensure your input adheres to community guidelines to avoid this issue.",
                color=0xFF0000
            )
            await msg.edit(embed=error_embed)


    @bot.command(name="search")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def search(ctx,*, query: str = None):
        if query is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your prompt", color=0x99ccff)
            return
        result = web_search(query)
        if result == "":
            result = "No results found"
        web_embed = discord.Embed(
            title="Luminary - web search",
            description=result,
            color=0x99ccff
        )
        file = discord.File("web_search.png", filename="web_search.png")
        web_embed.set_thumbnail(url="attachment://web_search.png")
        web_embed.set_footer(text="LumianryAI")
        await ctx.reply(embed=web_embed, file=file)

    @bot.command(name='imagine.p')
    @commands.cooldown(1, 40, commands.BucketType.user)
    async def imagine_m2_command(ctx, *, prompt: str = None):
        if prompt is None:
            await ctx.reply("**Please enter your prompt!**", delete_after=3)
            return
        generating = discord.Embed(
            title="LuminaryAI - Image generation",
            description=f"Generating image...",
            color=0x99ccff
        )
        delete_msg = await ctx.send(embed=generating)
        async with aiohttp.ClientSession() as session:
            try:
                send_embed = discord.Embed(
                    title="LuminaryAI - Image generation",
                    description=f"Requested by: {ctx.author}\nPrompt: {prompt}",
                    color=0x99ccff
                )
                image = await poly_image_gen(session, prompt)
                file=discord.File(image, 'generated_image.png')
                send_embed.set_image(url=f'attachment://generated_image.png')
                await delete_msg.delete()
                await ctx.reply(embed=send_embed, file=file)
            except Exception as e:
                print(f"An error occurred: {e}")
                await ctx.reply("An error occurred while generating the image. Please try again.")


    @bot.command(name='prodia')
    @commands.cooldown(1, 40, commands.BucketType.user)
    async def prodia_command(ctx,*,prompt: str = None):
        if prompt is None:
            await ctx.reply("**Invalid command!**", delete_after=3)
            return
        embed_prodia = discord.Embed(
            title="LuminaryAI - Image generation using prodia",
            description="Generating image...",
            color=0x99ccff
        )
        msg = await ctx.reply(embed=embed_prodia)
        try:
            models = [
                "Realistic_Vision_V2.0.safetensors [79587710]",
                "portrait+1.0.safetensors [1400e684]",
                "revAnimated_v122.safetensors [3f4fefd9]",
                "analog-diffusion-1.0.ckpt [9ca13f02]",
                "AOM3A3_orangemixs.safetensors [9600da17]",
                "dreamlike-diffusion-1.0.safetensors [5c9fd6e0]",
                "dreamlike-diffusion-2.0.safetensors [fdcf65e7]",
                "dreamshaper_5BakedVae.safetensors [a3fbf318]",
                "mechamix_v10.safetensors [ee685731]",
                "meinamix_meinaV9.safetensors [2ec66ab0]",
                "sdv1_4.ckpt [7460a6fa]",
                "v1-5-pruned-emaonly.ckpt [81761151]",
                "shoninsBeautiful_v10.safetensors [25d8c546]",
                "theallys-mix-ii-churned.safetensors [5d9225a4]",
                "timeless-1.0.ckpt [7c4971d4]",
                "elldreths-vivid-mix.safetensors [342d9d26]",
                "openjourney_V4.ckpt [ca2f377f]",
                "deliberate_v2.safetensors [10ec4b29]",
                "dreamshaper_6BakedVae.safetensors [114c8abb]",
                "lyriel_v16.safetensors [68fceea2]",
                "anything-v4.5-pruned.ckpt [65745d25]",
                "openjourney_V4.ckpt [ca2f377f]",
            ]
            model = random.choice(models)
            seed = random.randint(10000, 99999)
            sampler = "Euler"
            img_file_obj = await generate_image_prodia(prompt, model, sampler, seed, None)
            prodia_final = discord.Embed(
                title="LuminaryAI - Image generation using prodia",
                color=0x99ccff,
                description=f"Model: {model}\n Seed: {seed}\n Model and seed is randomly selected. Please use slash command `/imagine` to customize."
            )
            prodia_final.set_footer(text="LuminaryAI encourages positive interactions. It disclaims responsibility for content generated based on user inputs.")

            # Attach the image directly to the embed
            file=discord.File(img_file_obj, 'generated_image.png')
            prodia_final.set_image(url=f'attachment://generated_image.png')

            # Send the embed with the attached image
            await msg.delete()
            await ctx.send(embed=prodia_final, file=file)

        except Exception as e:
            print(e)
            error_embed = discord.Embed(
                title="Luminary - prodia Image generation",
                description="ERROR: 403\n\nThis error can occurs when the user's request contains inappropriate content, leading to restricted access. Please ensure your input adheres to community guidelines to avoid this issue.",
                color=0xFF0000
            )
            await msg.edit(embed=error_embed)


    @bot.command(name='searchimg')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def searchimg(ctx,* , query):
        a = search_photo(query)
        if a == "Bad":
            bad_embd = discord.Embed(
                title="LuminaryAI - Image search",
                description=f"Requested by: {ctx.author}\nPrompt: {query}\n\n ⚠️ Can't search for image.",
                color="0xFF0000"
            )
            file = discord.File("web_search.png", filename="web_search.png")
            bad_embd.set_thumbnail(url="attachment://web_search.png")
            await ctx.send(bad_embd, file=file)
        else:
            embed = discord.Embed(
                title="LuminaryAI - Image search",
                description=f'Requested by: {ctx.author}\nPrompt: {query}',
                color=0x99ccff,
            )
            embed.set_image(url=a)
            await ctx.send(embed=embed)