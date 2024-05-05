import discord
from discord.ext import commands, tasks
from data import blacklisted_servers, member_histories_msg, blacklisted_users
from bot_utilities.ai_utils import fetch_chat_models
import os
import sys


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


bot_token = sys.argv[1]




developer_members = {}
intents = discord.Intents.all()
intents.presences = False
activity = discord.Game(name="/help")
bot = commands.Bot(command_prefix="ai.", intents=intents, activity=activity, help_command=None, reconnect=False)



start_time = time.time()



bbot(bot,
    developer_members,
    start_time,
    blacklisted_servers,
    member_histories_msg,
    ai_channels,
    server_data_ai,
    blacklisted_users
)
music(bot)
fun(bot)
general(bot, developer_members)
ai(bot, member_histories_msg)
moderation(bot)


bot_slash(bot, start_time)
ai_slash(bot)

on_cmd_error(bot)
member_join(bot)

chat_models = fetch_chat_models()
model_blob = "\n".join(chat_models)




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

on_messages(bot, cmd_list, blacklisted_users, member_histories_msg, blacklisted_servers)






@tasks.loop(seconds=60)  # Task to run every 60 seconds
async def save_data():
    with open("data.py", "w") as file:
        # Write the content with the provided variable
        file.write(f"blacklisted_servers = {blacklisted_servers}\nblacklisted_users = {blacklisted_users}\n\nmember_histories_msg = {member_histories_msg}\n\nserver_data_ai = {server_data_ai}\nai_channels = {ai_channels}")
        file.close()

@tasks.loop(seconds=300) # keep the slash commands synced
async def sync_slash_cmd():
    await bot.tree.sync()


@tasks.loop(seconds=480)
async def send_data_file():
    # Task to run every 8 minutes (480 seconds)
    channel = bot.get_channel(1227153352228601877)
    file = discord.File("data.py", filename="data.py")
    await channel.send(file=file)


bio = """
Smart AI bot packed with features on Discord.

Site: https://luminaryai.netlify.app
Support: https://discord.gg/hmMBe8YyJ4
TOS: https://luminaryai.netlify.app/tos
"""

@tasks.loop(seconds=30)
async def update_bio():
    # Update the description via PATCH request
    url = "https://discord.com/api/v9/applications/@me"
    headers = {"Authorization": f"Bot {bot_token}"}
    data = {"description": bio}
    response = requests.patch(url=url, headers=headers, json=data)


@bot.event
async def on_ready():
    await bot.tree.sync()
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'We have logged in as {bot.user}')
    print(f"\033[1;38;5;202mAvailable models: {model_blob}\033[0m")
    print(f"\033[1;38;5;46mCurrent model: {os.getenv('GPT_MODEL')}\033[0m")
    save_data.start()
    sync_slash_cmd.start()
    update_bio.start()
    send_data_file.start()


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
