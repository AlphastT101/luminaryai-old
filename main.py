import discord
from discord.ext import commands, tasks
# from aiml import Kernel
import inspect
import requests
import yaml
from data import blacklisted_servers, member_histories_msg, blacklisted_users
from bot_utilities.ai_utils import generate_response_msg, fetch_chat_models


from slash.bot import *
from slash.ai import *

from prefix.bot import *
from prefix.music import *
from prefix.fun import *
from prefix.general import *
from prefix.ai import *
from prefix.moderation import *














developer_members = {}
intents = discord.Intents.all()
intents.presences = False
activity = discord.Game(name="ai.help")
bot = commands.Bot(command_prefix="ai.", intents=intents, activity=activity, help_command=None, reconnect=False)


error_log_channel_id = 1191754729592717383
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

fun(bot,
    )

general(bot,
        developer_members
        )

ai(bot,
   member_histories_msg
)

bot_slash(bot,
    start_time
    )

ai_slash(bot,
    )

moderation(bot)


chat_models = fetch_chat_models()
model_blob = "\n".join(chat_models)
with open('config.yml', 'r', encoding='utf-8') as config_file:
    config = yaml.safe_load(config_file)


# class SimpleChatbot:
#     def __init__(self):
#         self.kernel = Kernel()

#         # Load AIML files from the specified folder
#         for file in os.listdir(aiml_folder):
#             if file.endswith(".aiml"):
#                 aiml_file = os.path.join(aiml_folder, file)
#                 self.kernel.learn(aiml_file)

#     def get_response(self, user_input):
#         response = self.kernel.respond(user_input)
#         return response

# # Create an instance of SimpleChatbot
# chatbot = SimpleChatbot()

@tasks.loop(seconds=60)  # Task to run every 60 seconds
async def save_data():
    with open("data.py", "w") as file:
        # Write the content with the provided variable
        file.write(f"blacklisted_servers = {blacklisted_servers}\nblacklisted_users = {blacklisted_users}\n\nmember_histories_msg = {member_histories_msg}\n\nserver_data_ai = {server_data_ai}\nai_channels = {ai_channels}")
        file.close()

@tasks.loop(seconds=120)  # Task to run every 2 minutes
async def sync_slash_cmd():
    await bot.tree.sync()



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
    save_data.start()
    sync_slash_cmd.start()



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



@bot.event
async def on_message(message):
    if message.guild is None:
        return
    server_id = message.guild.id

    # delete shapes commands
    if message.content == "hello im LuminaryAI. @ me to talk w me or DM me." and message.author == bot.user:
        await message.delete()
        return
    elif message.content.startswith("there are 4 ways you can interact with me:") and message.author == bot.user:
        await message.delete()
        if message.guild.id not in blacklisted_servers:
            await message.channel.send("**Please use ai.help or /help!**")
        else:
            return
    elif message.content.startswith("hello im LuminaryAI. to start chatting, just tag me") and message.author == bot.user:
        await message.delete()
    elif message.content.startswith("uhh my head hurts") and message.author == bot.user:
        await message.delete()
        if message.guild.id not in blacklisted_servers:
            await message.channel.send("**Wacked successfully!**")
        else:
            return
    

    if message.author == bot.user or message.author.bot:
        return
    if message.content.startswith(tuple(cmd_list)) and message.guild.id not in blacklisted_servers and message.author.id not in blacklisted_users:
        await bot.process_commands(message)
        return



    elif server_data_ai.get(server_id, {}).get('response_enabled', False) and server_id in ai_channels and message.channel.id == ai_channels.get(server_id, 0):

        member_id = str(message.author.id)  # Using member ID as the key
        history = member_histories_msg.get(member_id, [])

        answer_embed = discord.Embed(
            title="LuminaryAI - answer generation",
            description="Generating answer...",
            color=0x99ccff
        )
        answer = await message.reply(embed=answer_embed)


        user_input = message.content
        generated_message, updated_history = await generate_response_msg(message, user_input, history)

        # Update member-specific history
        member_histories_msg[member_id] = updated_history

        answer_generated = discord.Embed(
            title="LumianryAI - answer generation",
            description=generated_message,
            color=0x99ccff
        )
        await answer.edit(embed=answer_generated)


    elif not any(message.content.startswith(prefix) for prefix in bot.command_prefix):
        return  # Message doesn't start with any command prefix, and AI responses are disabled


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


bot.run()
