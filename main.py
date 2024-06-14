import discord
from discord.ext import commands, tasks
import os
from pymongo.mongo_client import MongoClient
import yaml
import asyncio
# from dotenv import load_dotenv
from threading import Thread

from slash.bot import *
from slash.ai import *

from prefix.bot import *
from prefix.music import *
from prefix.fun import *
from prefix.general import *
from prefix.ai import *
from prefix.moderation import *

from events.on_cmd_error import *
from events.on_messages import *
from events.member_join import *

from bot_utilities.ai_utils import process_queue
from bot_utilities.start_util import *

from api import app

def run_flask_app():
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port, debug=False)

with open("config.yml", "r") as config_file:
    config = yaml.safe_load(config_file)
mongodb, bot_token = collect_data_start("envv.env", "binary", 50)

member_histories_msg = {}
intents = discord.Intents.all()
intents.presences = False
activity = discord.Game(name="/help")
bot = commands.Bot(command_prefix=config["bot"]["prefix"], intents=intents, activity=activity, help_command=None, reconnect=False)
client = MongoClient(mongodb)
start_time = time.time()

bbot(bot, start_time, client)
music(bot)
fun(bot)
general(bot)
ai(bot, member_histories_msg, client)
moderation(bot)

bot_slash(bot, start_time)
ai_slash(bot)

on_cmd_error(bot)
member_join(bot)

@bot.command(name="cmd")
async def cmdd(ctx):
    if ctx.author.id == 1026388699203772477:
        await ctx.send("\n".join(cmd_list))
    else:
        return

cmd_list = []
# Populate cmd_list with the commands
for command in bot.commands:
    cmd_prefix = "ai." + command.name
    cmd_list.append(cmd_prefix)

on_messages(bot, cmd_list, member_histories_msg, client)

@tasks.loop(seconds=300) # keep the slash commands synced
async def sync_slash_cmd():
    await bot.tree.sync()

bio = """
Smart AI bot packed with features on Discord.

Site: https://luminaryai.netlify.app
Support: https://discord.gg/hmMBe8YyJ4
TOS: https://luminaryai.netlify.app/tos"""

@tasks.loop(seconds=30)
async def update_bio():
    url = "https://discord.com/api/v9/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    data = {"description": bio}
    response = requests.patch(url=url, headers=headers, json=data)

@bot.event
async def on_ready():
    await bot.tree.sync()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'We have logged in as {bot.user}')
    print(f"\033[1;38;5;46mCurrent model: {config['bot']['text_model']}\033[0m")
    client.admin.command('ping')
    print("Pinged your deployment. You are successfully connected to MongoDB!")
    sync_slash_cmd.start()
    update_bio.start()
    asyncio.create_task(process_queue())

    # Run Flask app in a separate thread
    flask_thread = Thread(target=run_flask_app)
    flask_thread.start()
    
    print("API Engine has been started!")

@bot.event
async def on_guild_join(guild):
    channel = bot.get_channel(1189110778599575592)
    embed = discord.Embed(title="Guild Joined", description=f"The bot has joined the server {guild.name}", color=0x00ff00)
    await channel.send(embed=embed)

@bot.event
async def on_guild_remove(guild):
    channel = bot.get_channel(1189110778599575592)
    embed = discord.Embed(title="Guild Left", description=f"The bot has left the server {guild.name}", color=0xff0000)
    await channel.send(embed=embed)

bot.run(bot_token)
