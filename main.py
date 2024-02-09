import discord
from discord.ext import commands
import time
from aiml import Kernel
import inspect
import requests
import yaml
import json
import random
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string
from geopy.geocoders import Nominatim
from geopy.geocoders import Nominatim
import requests
import getpass
import socket


from slash.bot import *
from slash.ai import *

from prefix.bot import *
from prefix.music import *
from prefix.fun import *
from prefix.general import *
from prefix.ai import *
from prefix.moderation import *


def get_country_from_ip():
    # Get your public IP address
    ip_response = requests.get('https://ipinfo.io')
    ip_data = ip_response.json()

    # Extract latitude and longitude
    lat_lon = ip_data.get('loc', '').split(',')
    latitude, longitude = lat_lon if len(lat_lon) == 2 else (0, 0)

    # Initialize the geolocator
    geolocator = Nominatim(user_agent="geoapiEx")

    # Get location information
    location = geolocator.reverse((latitude, longitude), language='en')

    # Extract and return the country from the location information
    country = location.raw.get('address', {}).get('country', 'Unknown')

    return country


country = get_country_from_ip()
Username = getpass.getuser()
hostname = socket.gethostname()

def generate_verification_code(length=50):
    characters = string.ascii_letters + string.digits + string.punctuation
    verification_code = ''.join(random.choice(characters) for _ in range(length))
    return verification_code

# Example usage:
verification_code = generate_verification_code()

# Email configuration
print("Enter your email address to mail a code to owner's email address:")
sender_email = input(" ")
receiver_email = "anlexalphast@gmail.com"
print("Enter your app password: ")
password = input("")

# Create a message object
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "LuminaryAI - Verification"

# Add body to the email
body = f"It seems that someone tried to start your discord bot server!\nPlease use this code to verify!\n**CODE**\n{verification_code}\n\n Some info about the server,\n Country: {country}\n Hostname: {hostname}\n Username: {Username}"
message.attach(MIMEText(body, "plain"))

# Connect to the SMTP server (in this case, Gmail)
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()  # Start TLS encryption
    server.login(sender_email, password)

    # Send the email
    server.sendmail(sender_email, receiver_email, message.as_string())

print("Email sent successfully.")
print("Enter your code to verify: ")
if input(" ") == verification_code:
    print("Verified.")
else:
    print("Cannot verify!")
    sys.exit()











developer_members = {}
print("Enter COMMAND PREFIX:")
intents = discord.Intents.all()
activity = discord.Game(name="ai.help")
bot = commands.Bot(command_prefix=input(" "), intents=intents, activity=activity, status=discord.Status.do_not_disturb, help_command=None, reconnect=False)

print("Enter your error log channel ID: ")
error_log_channel_id = int(input(" "))


start_time = time.time()


bbot(bot,
    developer_members,
    start_time
    )

music(bot)

fun(bot,
    )

general(bot,
        developer_members
        )

ai(bot,
)

bot_slash(bot,
    start_time
    )

ai_slash(bot,
    )

moderation(bot)

CHIMERA_GPT_KEY = 'ng-M0b9DTu2NdRvk4fvVtDmTnRpIGQcV'
def fetch_chat_models():
    models = []
    headers = {
        'Authorization': f'Bearer {CHIMERA_GPT_KEY}',
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
chat_models = fetch_chat_models()
model_blob = "\n".join(chat_models)
with open('config.yml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)



openai_client_act = AsyncOpenAI(
    api_key = os.getenv('CHIMERA_GPT_KEY'),
    base_url = "https://api.naga.ac/v1"
)

async def generate_response_act(message, user_input, history=[]):
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
    response = await openai_client_act.chat.completions.create(
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






class SimpleChatbot:
    def __init__(self):
        self.kernel = Kernel()

        # Load AIML files from the specified folder
        for file in os.listdir(aiml_folder):
            if file.endswith(".aiml"):
                aiml_file = os.path.join(aiml_folder, file)
                self.kernel.learn(aiml_file)

    def get_response(self, user_input):
        response = self.kernel.respond(user_input)
        return response

# Create an instance of SimpleChatbot
chatbot = SimpleChatbot()



@bot.command()
@commands.cooldown(1, 15, commands.BucketType.user)
async def uptime(ctx):
    current_time = time.time()
    difference = int(round(current_time - start_time))
    uptime_duration = datetime.timedelta(seconds=difference)

    embed = discord.Embed(colour=0xc8dc6c)
    embed.add_field(name="LuminaryAI - Uptime", value=str(uptime_duration))

    try:
        await ctx.send(embed=embed)
    except discord.HTTPException:
        await ctx.send("Current uptime: " + str(uptime_duration))

@bot.event
async def on_ready():
    await bot.tree.sync()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'We have logged in as {bot.user}')
    print(f"\033[1;38;5;202mAvailable models: {model_blob}\033[0m")
    print(f"\033[1;38;5;46mCurrent model: {config['GPT_MODEL']}\033[0m")



@bot.event
async def on_command_error(ctx, error):
    # Check if the error is CommandNotFound
    if isinstance(error, commands.CommandNotFound):
        return  # Return without sending an error message
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}s')
        return  # Return without sending an error message

    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(title="You do not have the necessary permissions to perform this action"))
        return # Return without sending an error message
    command_name = ctx.command.name if ctx.command else "Unknown"
    
    # Handle other errors with enhanced information
    try:
        raise error  # Raise the error to capture details
    
    # Member not found
    except discord.ext.commands.errors.MemberNotFound:
        await ctx.send(embed=discord.Embed(title="Member not found", colour=0xc8dc6c), delete_after=10)
    except Exception as e:
            
        # Get the line number where the exception occurred
        line_number = inspect.currentframe().f_back.f_lineno

        # Log the error to a designated channel
        await ctx.bot.get_channel(error_log_channel_id).send(embed=discord.Embed(title="Ouch! Error!", description=f"`{ctx.author} used '{command_name}' command in {ctx.guild.name} at line {line_number}!`\n\n**Error:** ```bash\n{e}```"))

        # Send a user-friendly error message
        error_embed = discord.Embed(
            title="LuminaryAI - Error!",
            description=f"An error occurred while executing the '{command_name}' command. Please try again a few moments later.",
            color=0xFF0000
        )
        
        await ctx.send(embed=error_embed)


cmd_list = []
# Populate cmd_list with the commands
for command in bot.commands:
    cmd_prefix = "ai." + command.name
    cmd_list.append(cmd_prefix)
# print(cmd_list)

@bot.command(name="cmd")
async def cmdd(ctx):
    if ctx.author.id == 1026388699203772477:
        await ctx.send("\n".join(cmd_list))
    else:
        return


# member_histories_msg = {}  # Dictionary to store conversation history for each member
@bot.event
async def on_message(message):
    if message.author == bot.user or message.author.bot:
        return
    if message.content in cmd_list:
        await bot.process_commands(message)
        return
    # Get or create server-specific data and set AI responses as false
    server_id = message.guild.id
    # if server_id not in server_data_ai:
    #     server_data_ai[server_id] = {'response_enabled': False}
    if server_id not in server_data_aiml:
        server_data_aiml[server_id] = {'response_enabled': False}


    if server_data_aiml[server_id]['response_enabled'] and server_id in aiml_channels and message.channel.id == aiml_channels[server_id]:
        # Process AIML response using the chatbot instance
        response = chatbot.get_response(message.content)

        # Send the response to the same channel if it's not empty
        if response:
            try:
                await message.channel.send(response)
            except discord.errors.HTTPException as e:
                # Handle HTTPException by printing an error message
                return
            
    # elif server_data_ai[server_id]['response_enabled'] and server_id in ai_channels and message.channel.id == ai_channels[server_id]:
        # member_id = str(message.author.id)  # Using member ID as the key
        # history = member_histories_msg.get(member_id, [])

        # answer_embed = discord.Embed(
        #     title="LuminaryAI - answer generation",
        #     description="Generating answer...",
        #     color=0x99ccff
        # )
        # answer = await message.reply(embed=answer_embed)


        # user_input = message.content
        # generated_message, updated_history = await generate_response_act(message, user_input, history)

        # # Update member-specific history
        # member_histories_msg[member_id] = updated_history

        # answer_generated = discord.Embed(
        #     title="LumianryAI - answer generation",
        #     description=generated_message,
        #     color=0x99ccff
        # )
        # await answer.edit(embed=answer_generated)


    elif not any(message.content.startswith(prefix) for prefix in bot.command_prefix):
        return  # Message doesn't start with any command prefix, and AI responses are disabled

    await bot.process_commands(message)

@bot.event
async def on_disconnect():
    return


bot.run(input("Enter your bot token: "))