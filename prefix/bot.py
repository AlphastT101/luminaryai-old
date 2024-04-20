import logging
import traceback
import asyncio
import discord
from discord.ext import commands, tasks
from discord.ui import Select, View
import datetime
from datetime import datetime

import time
import psutil
import io
import contextlib
import pymongo

import data


import motor.motor_asyncio
from pymongo import MongoClient


# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



# import button_paginator as pg
# from button_paginator import PaginatorView


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    return psutil.virtual_memory().percent


cpu_percent = get_cpu_usage()
ram_percent = get_ram_usage()

# CPU calculation
cpu_cores = psutil.cpu_count(logical=False)
cpu_text = f"{cpu_percent:.0f}% of {cpu_cores} cores"

# RAM calculation
total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)  # Convert to GB
ram_text = f"{ram_percent:.0f}% of {total_ram_gb:.0f}GB ({total_ram_gb * ram_percent / 100:.0f}GB)"

async def loading_animation(ctx, loading_length=10):
    # Create the loading message with initial state
    loading_message = await ctx.reply(f"⏳ Loading: {' ' * loading_length} | 0%")
    
    # Define the progress bar segments
    progress_bar_full = "█"
    progress_bar_empty = "░"
    
    # Update the progress bar during loading
    for i in range(loading_length + 1):
        progress = i / loading_length  # Calculate the progress percentage
        bar = progress_bar_full * i + progress_bar_empty * (loading_length - i)
        percentage = int(progress * 100)
        
        # Update the loading message with the current progress
        await loading_message.edit(content=f"⏳ Loading: {bar} | {percentage}%")
        
        # Wait for a short duration before updating again
        await asyncio.sleep(0.4)  # Adjust the sleep time as needed

    # Return the final loading message
    return loading_message



async def error_mongo_embed(bot, ctx, e):
        # Create an error embed after catching the exception
        
        error_embed = discord.Embed(
            description=f'```bash\n{e}```',
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        error_embed.set_author(name=f'{bot.user.display_name.title()} - Mongo Error',icon_url='https://cdn.iconscout.com/icon/free/png-512/free-mongodb-3-1175138.png?f=webp&w=256')
        # Get the last traceback frame from the exception
        line_number = traceback.extract_tb(e.__traceback__)[-1].lineno
        tb_frame = traceback.extract_tb(e.__traceback__)[-1]
        file_location = tb_frame.filename  # File location

        print("Error found in line", line_number)
        error_embed.add_field(
         name=" ",
         value = f":warning: **Potential issue found:**\n- **File:** `{file_location}`\n- **Line:** `{line_number}`",
         inline=False
        )
        error_embed.set_footer(icon_url=bot.user.avatar, text='Error Found')
            
        # Inform the user about the error
        return error_embed

async def send_success_messages(ctx, db_info, collection_info):
    # Create a success embed for database information
    db_embed = discord.Embed(title="Gathering Database Information", color=discord.Color.green())
    db_embed.add_field(name=":file_cabinet: - Database Details:", value=f"```bash\n{db_info}```\nCompleted 1/2 - :white_check_mark:", inline=False)
    
    # Create a success embed for collection information
    collection_embed = discord.Embed(title="Gathering Collection Information:", color=discord.Color.green())
    collection_embed.add_field(name="🗃️ - Collection Details:", value=f"```bash\n{collection_info}```\nCompleted 2/2 - :white_check_mark:", inline=False)
    
    # Return the success Embed objects
    return db_embed, collection_embed




def bbot(bot, developer_members, start_time, blacklisted_servers, member_histories_msg, ai_channels, server_data_ai, blacklisted_users):
    
    @bot.command(name="test_mb")
    async def test_mb(ctx):
        try:
            # Connect to the database and collection
            db = bot.mongoConnect['Database']
            collection = db['Collection']

            logger.info("Testing database connection.")
            # Start loading animation
            loading_message = await loading_animation(ctx, loading_length=10)   
            db_embed, collection_embed = await send_success_messages(ctx, db, collection) 
            # Send the success messages
            db_message = await ctx.send(embed=db_embed)
            collection_message = await ctx.send(embed=collection_embed)
            
            # Edit the loading message
            await loading_message.delete()
            
            # Check if user has an entry in the collection
            user_id = ctx.message.author.id
            user_entry = await collection.find_one({"_id": user_id})
            
            # If user does not have an entry, create one
            if user_entry is None:
                new_data = {
                    "_id": user_id,
                    "check": 1
                }
                await collection.insert_one(new_data)
                logger.info(f"New data inserted: {new_data}")
                await ctx.send(f"Data inserted: {new_data}")
            else:
                # Inform the user about the data found for the user
                await ctx.send(f"User entry: {user_entry}")
        
        except Exception as e:
            # Log any exceptions that occur
            logger.error(f"An error occurred: {e}")
            
            # Create an error embed after catching the exception
            error_embed = await error_mongo_embed(bot, ctx, e)

            # Inform the user about the error
            await ctx.reply(f"Sorry {ctx.message.author.mention}, there has been an error.")
            await ctx.send(embed=error_embed)

    ####### return message ######
    @bot.command(name="say")
    async def m(ctx, *, message: str = None):
        # 900436346420732065 - toast
		# 1026388699203772477 - alphast101
		# 973461136680845382 - wqypp
        # 885977942776246293 -jeydalio
        if message is None:
            return
        allowed = [973461136680845382, 1026388699203772477, 900436346420732065, 885977942776246293]
        if ctx.author.id in allowed:
            bot_member = ctx.guild.me
            if bot_member.guild_permissions.manage_messages:
                await ctx.message.delete()
                await ctx.send(message)
            else:
                await ctx.send(message)
        else:
            await ctx.send("**This command is restricted**", delete_after=3)

    @bot.command(name="mp")
    async def mp(ctx,*,message):
        if ctx.author.id == 1026388699203772477:
            print(message)
            await ctx.message.delete()
            await ctx.send(message)
        else:
            await ctx.send("**This command is restricted**", delete_after=3)

    @bot.command(name="serverinv")
    async def list_serversinv(ctx):
        if ctx.author.id == 1026388699203772477:
            servers = bot.guilds

            if not servers:
                await ctx.send("The bot is not a member of any servers.")
                return

            embed = discord.Embed(
                title="Server List",
                color=0x99ccff
            )

            for server in servers:
                try:
                    invite = await server.text_channels[0].create_invite()
                    embed.add_field(name=server.name, value=f"Invite: {invite}", inline=False)
                except discord.errors.Forbidden:
                    embed.add_field(name=server.name, value="Unable to create invite (missing permissions)", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("**This command is restricted**", delete_after=3)


    @bot.command(name="sync")
    async def sync(ctx):
        if ctx.author.id == 1026388699203772477:
            await ctx.send("**<@1026388699203772477> Syncing slash commands...**")
            await bot.tree.sync()
            await ctx.send("**<@1026388699203772477> Slash commands synced!**")
        else:
            return

    @bot.command(name="blacklist.server")
    async def blacklist_server(ctx, *, serverid):
        guild = bot.get_guild(int(serverid))  # Convert serverid to integer

        if ctx.author.id == 1026388699203772477:
            if guild:  # Check if guild is found
                if int(serverid) not in blacklisted_servers:
                    blacklisted_servers.append(int(serverid))
                    await ctx.send(f"**`{guild.name}` has been blacklisted!**")
                else:
                    await ctx.send("**This server is already blacklisted!**")
            else:
                await ctx.send("**Guild not found!**")
        else:
            return

    @bot.command(name="unblacklist.server")
    async def ublacklist_server(ctx, *, serverid):
        guild = bot.get_guild(int(serverid))  # Convert serverid to integer

        if ctx.author.id == 1026388699203772477:
            if guild:  # Check if guild is found
                if int(serverid) in blacklisted_servers:
                    blacklisted_servers.remove(int(serverid))
                    await ctx.send(f"**`{guild.name}` has been unblacklisted!**")
                else:
                    await ctx.send("**This server is not blacklisted!**")
            else:
                await ctx.send("**Guild not found!**")
        else:
            return


    @bot.command(name="blacklist.user")
    async def blacklist_user(ctx, *, userid):
        user = bot.get_user(int(userid))  # Convert userid to integer

        if ctx.author.id == 1026388699203772477:
            if user:  # Check if guild is found
                if int(userid) not in blacklisted_users:
                    blacklisted_users.append(int(userid))
                    await ctx.send(f"**`{user.name}` has been blacklisted!**")
                else:
                    await ctx.send("**This user is already blacklisted!**")
            else:
                await ctx.send("**user not found!**")
        else:
            return
    @bot.command(name="unblacklist.user")
    async def ublacklist_user(ctx, *, userid):
        user = bot.get_user(int(userid))  # Convert userid to integer

        if ctx.author.id == 1026388699203772477:
            if user:  # Check if guild is found
                if int(userid) in blacklisted_users:
                    blacklisted_users.remove(int(userid))
                    await ctx.send(f"**`{user.name}` has been unblacklisted!**")
                else:
                    await ctx.send("**This user is not blacklisted!**")
            else:
                await ctx.send("**user not found!**")
        else:
            return

    @bot.command(name="save")
    async def save(ctx):
        if ctx.author.id == 1026388699203772477:
            # Open the "data.py" file in write mode

            with open("data.py", "w") as file:
                # Write the content with the provided variable
                file.write(f"blacklisted_servers = {blacklisted_servers}\nblacklisted_users = {blacklisted_users}\n\nmember_histories_msg = {member_histories_msg}\n\nserver_data_ai = {server_data_ai}\nai_channels = {ai_channels}")
                file.close()
            await ctx.send("**Data saved successfully!**")
        else:
            return
        
    @bot.command(name="developer")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def developer(ctx, choice: str):
        # Check if developer mode is enabled for the user
        developer_mode = ctx.author.id in developer_members and developer_members[ctx.author.id]

        if choice.lower() == "true":
            developer_members[ctx.author.id] = True
            await ctx.send(f"Developer mode enabled for {ctx.author}")
        elif choice.lower() == "false":
            developer_members[ctx.author.id] = False
            await ctx.send(f"Developer mode disabled for {ctx.author}")
        else:
            await ctx.send("Invalid choice.")


    @bot.command(name="eval")
    async def eval(ctx, *, code: str):

        if ctx.author.id == 1026388699203772477:
            # Remove backticks from the code block
            code = code.strip('` ')
            # Check if the code is in a python code block
            if code.startswith('python'):
                code = code[6:]
            code = '\n'.join(f'    {i}' for i in code.splitlines())

            # Prepare the environment for the code execution
            local_variables = {
                "discord": discord,
                "commands": commands,
                "bot": bot,
                "ctx": ctx,
                "__import__": __import__
            }

            # Prepare stdout to capture output
            stdout = io.StringIO()

            # Define the wrapped exec
            def wrapped_exec():
                try:
                    exec(f"async def func():\n{code}", local_variables)
                except Exception as e:
                    stdout.write(f"{type(e).__name__}: {e}")

            # Capture the output of the exec
            with contextlib.redirect_stdout(stdout):
                wrapped_exec()
                if 'func' in local_variables:
                    func = local_variables['func']
                    try:
                        await func()
                    except Exception as e:
                        stdout.write(f"{type(e).__name__}: {e}")

            # Send the output back to the Discord channel
            await ctx.send(f'{stdout.getvalue()}')
        else:
            return





















    @bot.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
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



    ############### About ########################
    @bot.command(name='about', aliases=["!about", "/about"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def about(ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        about = discord.Embed(
            title='About',
            description="[support server](<https://discord.com/invite/hmMBe8YyJ4>)\n[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n[Site](<https://luminaryai.netlify.app>)\n[Terms of Service](<https://luminaryai.netlify.app/tos>)\n\nLuminaryAI is your Discord bot powered by artificial intelligence. It utilizes cutting-edge AI features to enrich your server's experience, providing automated moderation, text filtering, image generation, and more!",
            color=0x99ccff  # Convert hex color to integer
        )
        about.add_field(name='Owner', value="alphast101", inline=True)
        about.add_field(name='Used languages', value="Python 3.11 | discord.py 2.3.2", inline=True)
        about.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/8964c60e7cd3dd4b919811e566e5ccb7.webp?size=80")
        about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
        about.add_field(name='AI engine', value="Luminary", inline=True)
        about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
        about.add_field(name='Members', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
        about.add_field(name='RAM usage', value=f"{ram_text}", inline=True)
        about.add_field(name='CPU usage', value=f"{cpu_text}", inline=True)
        about.set_image(url="attachment://ai.png")
        filename = "ai.png"
        # Send the embed without the file parameter
        await ctx.send(embed=about, file=discord.File(filename, filename="ai.png"))


    ############### info ########################
    @bot.command(name='info')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_command(ctx, command_info: str = None):
        rps = discord.Embed(
            title="Help: ai.rps",
            description="Play RPS with the bot",
            color=0x99ccff
        )
        rps.add_field(name='Syntax:', value='```ai.rps {your move}```',inline=False)

        cat = discord.Embed(
            title="Help: ai.cat",
            description="Shows a random cat picture",
            color=0x99ccff
        )
        cat.add_field(name='Syntax:', value='```ai.cat```',inline=False)


        randomfact = discord.Embed(
            title="Help: ai.randomfact",
            description="shows a randomfact about the world",
            color=0x99ccff
        )
        randomfact.add_field(name='Syntax:', value='```ai.randomfact```',inline=False)

        user = discord.Embed(
            title="Help: ai.user",
            description="Shows user ID, username, user avatar. \n user_mention is optional",
            color=0x99ccff
        )
        user.add_field(name='Syntax:', value='```ai.user {user_mention}```',inline=False)

        imagine = discord.Embed(
            title="Help: ai.imagine",
            description="Generate images!",
            color=0x99ccff
        )
        imagine.add_field(name='Syntax:', value='```ai.imagine {prompt}```',inline=False)
        imagine.add_field(name='Example:', value='```ai.imagine bmw m4```',inline=False)

        imagine_p = discord.Embed(
            title="Help: ai.imagine.p",
            description="Generate images using pollonations.ai",
            color=0x99ccff
        )
        imagine_p.add_field(name='Syntax:', value='```ai.imagine.p {prompt}```',inline=False)
        imagine_p.add_field(name='Example:', value='```ai.imagine.p bmw m4```',inline=False)

        search = discord.Embed(
            title="Help: ai.search",
            description="Search the Wiki",
            color=0x99ccff
        )
        search.add_field(name='Syntax:', value='```ai.search {prompt}```',inline=False)
        search.add_field(name='Example:', value='```ai.search what is hydrogen?```',inline=False)

        searchimg = discord.Embed(
            title="Help: ai.searchimg",
            description="Search the web for images",
            color=0x99ccff
        )
        searchimg.add_field(name='Syntax:', value='```ai.searchimg {prompt}```',inline=False)
        searchimg.add_field(name='Example:', value='```ai.searchimg apple```',inline=False)

        purge = discord.Embed(
            title="Help: ai.purge",
            description="Purge recent messages. Both you and LuminaryAI need the 'Manage Messages' permission",
            color=0x99ccff
        )
        purge.add_field(name='Syntax:', value='```ai.purge {number of messages}```',inline=False)
        purge.add_field(name='Example:', value='```ai.purge 50```',inline=False)

        ai = discord.Embed(
            title="Help: ai.response",
            description="Generate answers!",
            color=0x99ccff
        )
        ai.add_field(name='Syntax:', value='```ai.response {prompt}```',inline=False)
        ai.add_field(name='Example:', value='```ai.response What is discord.py?```',inline=False)

        loop = discord.Embed(
            title="Help: ai.loop",
            description="Loop the current music",
            color=0x99ccff
        )
        loop.add_field(name='Syntax:', value='```ai.loop```',inline=False)

        play = discord.Embed(
            title="Help: ai.play",
            description="Play a music from the internet, YouTube links are accepted.",
            color=0x99ccff
        )
        play.add_field(name='Syntax:', value='```ai.play {song name}```',inline=False)
        play.add_field(name='Example:', value='```ai.play Cruel summer```',inline=False)


        leave = discord.Embed(
            title="Help: ai.leave",
            description="Stop the playback and leave the voice channel.",
            color=0x99ccff
        )
        leave.add_field(name='Syntax:', value='```ai.leave```',inline=False)

        join = discord.Embed(
            title="Help: ai.join",
            description="Join your voice channel.",
            color=0x99ccff
        )
        join.add_field(name='Syntax:', value='```ai.join```',inline=False)
    


        developer = discord.Embed(
            title="Help: ai.developer",
            description="Enable developer mode. This will display a bit more detail in the outputs.",
            color=0x99ccff
        )
        developer.add_field(name='Syntax:', value='```ai.developer {choice}```',inline=False)
        developer.add_field(name='Syntax:', value='```ai.developer true```',inline=False)

        uptime = discord.Embed(
            title="Help: ai.uptime",
            description="Shows bot uptime.",
            color=0x99ccff
        )
        uptime.add_field(name='Syntax:', value='```ai.uptime```',inline=False)


        ban = discord.Embed(
            title="Help: ai.ban",
            description="Ban a member, you and LuminaryAI needs proper permissions to perform this action (ban members).",
            color=0x99ccff
        )
        ban.add_field(name='Syntax:', value='```ai.ban {member} {reason}```',inline=False)
        ban.add_field(name='Example:', value='```ai.ban @noob Using self bots```',inline=False)

        unban = discord.Embed(
            title="Help: ai.unban",
            description="unban a member, you and LuminaryAI needs proper permissions to perform this action (ban members).",
            color=0x99ccff
        )
        unban.add_field(name='Syntax:', value='```ai.unban {member} {reason}```')
        unban.add_field(name='Example:', value='```ai.unban @noob Appeal application accepted!```',inline=False)


        kick = discord.Embed(
            title="Help: ai.kick",
            description="kick a member, you and LuminaryAI needs proper permissions to perform this action (kick members).",
            color=0x99ccff
        )
        kick.add_field(name='Syntax:', value='```ai.kick {member} {reason}```',inline=False)
        kick.add_field(name='Example:', value='```ai.kick @gamer alt accounts are not allowed```',inline=False)


        timeout = discord.Embed(
            title="Help: ai.timeout",
            description="timeout a member, you and LuminaryAI needs proper permissions to perform this action.",
            color=0x99ccff
        )
        timeout.add_field(name='Syntax:', value='```ai.timeout {member} {duration} {reason}```')
        timeout.add_field(name='Example 1:', value='```ai.timeout @gamer 1d spamming, please dont spam!```',inline=False)
        timeout.add_field(name='Example 2:', value='```ai.timeout @idiot 10h stop posting images```',inline=False)


        purgelinks = discord.Embed(
            title="Help: ai.purgelinks",
            description="Purge messages that contains links.",
            color=0x99ccff
        )
        purgelinks.add_field(name='Syntax:', value='```ai.purgelinks {ammount of messages}```')
        purgelinks.add_field(name='Example:', value='```ai.purgelinks 100```',inline=False)


        purgefiles = discord.Embed(
            title="Help: ai.purgefiles",
            description="Purge messages that contains files/attachments.",
            color=0x99ccff
        )
        purgefiles.add_field(name='Syntax:', value='```ai.purgefiles {ammount of messages}```')
        purgefiles.add_field(name='Example:', value='```ai.purgefiles 100```',inline=False)

        unmute = discord.Embed(
            title="Help: ai.unmute",
            description="Unmute/remove timeout from a member.",
            color=0x99ccff
        )
        unmute.add_field(name='Syntax:', value='```ai.unmute {member} {reason}```')
        unmute.add_field(name='Example:', value='```ai.unmute @nerd Application accepted!```',inline=False)

        resume = discord.Embed(
            title="Help: ai.resume",
            description="Resume the playback.",
            color=0x99ccff
        )

        stop = discord.Embed(
            title="Help: ai.stop",
            description="stop the playback.",
            color=0x99ccff
        )

        pause = discord.Embed(
            title="Help: ai.pause",
            description="pause the playback.",
            color=0x99ccff
        )
        volume = discord.Embed(
            title="Help: ai.volume",
            description="Increase or decrease the volume of the playback.",
            color=0x99ccff
        )

        vision = discord.Embed(
            title="Help: /vision",
            description="Vision an image. This command is Slash only.",
            color=0x99ccff
        )
        vision.add_field(name='Syntax:', value='```/vision {message} {image_link}```',inline=False)
        if command_info is None:
            await ctx.send("**Invalid command**", delete_after=3)
        elif command_info.lower() == "rps":
            await ctx.send(embed=rps)
        elif command_info.lower() == "cat":
            await ctx.send(embed=cat)
        elif command_info.lower() == "randomfact":
            await ctx.send(embed=randomfact)
        elif command_info.lower() == "user":
            await ctx.send(embed=user)
        elif command_info.lower() == "imagine":
            await ctx.send(embed=imagine)
        elif command_info.lower() == "imagine.p":
            await ctx.send(embed=imagine_p)
        elif command_info.lower() == "purge":
            await ctx.send(embed=purge)
        elif command_info.lower() == "search":
            await ctx.send(embed=search)
        elif command_info.lower() == "searchimg":
            await ctx.send(embed=searchimg)
        elif command_info.lower() == "response":
            await ctx.send(embed=ai)
        elif command_info.lower() == "join":
            await ctx.send(embed=join)
        elif command_info.lower() == "loop":
            await ctx.send(embed=loop)
        elif command_info.lower() == "leave":
            await ctx.send(embed=leave)
        elif command_info.lower() == "join":
            await ctx.send(embed=join)
        elif command_info.lower() == "uptime":
            await ctx.send(embed=uptime)
        elif command_info.lower() == "ban":
            await ctx.send(embed=ban)
        elif command_info.lower() == "unban":
            await ctx.send(embed=unban)
        elif command_info.lower() == "timeout":
            await ctx.send(embed=timeout)
        elif command_info.lower() == "kick":
            await ctx.send(embed=kick)
        elif command_info.lower() == "unmute":
            await ctx.send(embed=unmute)
        elif command_info.lower() == "purgefiles":
            await ctx.send(embed=purgefiles)
        elif command_info.lower() == "purgelinks":
            await ctx.send(embed=purgelinks)
        elif command_info.lower() == "resume":
            await ctx.send(embed=resume)
        elif command_info.lower() == "stop":
            await ctx.send(embed=stop)
        elif command_info.lower() == "pause":
            await ctx.send(embed=pause)
        elif command_info.lower() == "volume":
            await ctx.send(embed=volume)
        elif command_info.lower() == "vision":
            await ctx.send(embed=vision)
        else:
            await ctx.send("**invalid command**",delete_after=3)

    


    @bot.command(name="help")
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def developer(ctx):
        embed_bot = discord.Embed(
            title="Bot related commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_bot.add_field(name="`developer {choice}`", value="Enable developer mode. choices - true & false", inline=False)
        embed_bot.add_field(name="`about`", value="about the bot", inline=False)
        embed_bot.add_field(name="`help`", value="command list", inline=False)
        embed_bot.add_field(name="`uptime`", value="Bot uptime", inline=False)
        embed_bot.add_field(name="`support`", value="Support server link", inline=False)
        embed_bot.add_field(name="`owner`", value="shows owner of the bot", inline=False)




        embed_ai = discord.Embed(
            title="AI commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_ai.add_field(name='`ai.imagine {prompt}`', value="Generates images using SDXL according to user-inputes. We prefer to use the slash command `/imagine`", inline=False)
        embed_ai.add_field(name='`ai.imagine.p {prompt}`', value="Generates images using pollinations.ai according to user-inputes. We prefer to use the slash command `/imagine`", inline=False)
        embed_ai.add_field(name='`ai.response {prompt}`', value="Generates answers according to user-inputes. Message history available", inline=False)
        embed_ai.add_field(name='`ai.aiml.start`', value="Enable AIML responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.aiml.stop`', value="Disable AIML responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.activate` **[DISABLED]**', value="Enable AI responses, You need a role with manage messages to run this command.\nModel: *Luminary*", inline=False)
        embed_ai.add_field(name='`ai.deactivate` **[DISABLED]**', value=" Disable AI responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.searchimg {prompt}`', value="Search the web for images.", inline=False)
        embed_ai.add_field(name='`ai.search {prompt}`', value="Search the web.", inline=False)
        embed_ai.add_field(name='`ai.vision {prompt}`', value="Vision an image.", inline=False)
        embed_ai.add_field(name='`@luminaryai {prompt}`', value="Ping LuminaryAI to generate text and images.", inline=False)
        embed_ai.add_field(name='`@luminaryai activate`', value="Enable AI responses using Luminary-ultra. You need admin permissions to run this command.", inline=False)
        embed_ai.add_field(name='`@luminaryai deactivate`', value="Disable AI responses. You need admin permissions to run this command..", inline=False)



        embed_general = discord.Embed(
            title="general commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_general.add_field(name='`ai.user {mention}`', value="Shows username & avatar. if you enable developer mode, then it also displays userID, account creation date & guild join date.", inline=False)



        embed_fun = discord.Embed(
            title="fun commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_fun.add_field(name='`ai.rps {your move}`', value="play RPS with the bot", inline=False)
        embed_fun.add_field(name='`ai.cat`', value="shows a cat", inline=False)
        embed_fun.add_field(name='`ai.randomfact`', value="Shows a random fact", inline=False)



        embed_moderation = discord.Embed(
            title="Moderation commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_moderation.add_field(name='`ai.purge {number of messages}`', value="Purge messages, you need proper permissions to use this command.", inline=False)
        embed_moderation.add_field(name='`ai.ban {user} {reason}`', value="Ban a member, you need the ban members permission to take this action.", inline=False)
        embed_moderation.add_field(name='`ai.unban {user} {reason}`', value="Unban a member.", inline=False)
        embed_moderation.add_field(name='`ai.kick {user} {reason}`', value="kick a member.", inline=False)
        embed_moderation.add_field(name='`ai.purgefiles {amount of messages}`', value="Purge messages that contains files/attachments.", inline=False)
        embed_moderation.add_field(name='`ai.purgelinks {amount of messages}`', value="Purge messages that contains links.", inline=False)
        embed_moderation.add_field(name='`ai.unmute {member} {reason}`', value="Unmute/remove time out from a member.", inline=False)
        embed_moderation.add_field(name='`ai.timeout {user} {duration} {reason}`', value="timeout a member. A valid time duration required.(eg. 1d,10m,5h)", inline=False)



        embed_automod = discord.Embed(
            title="automod commands - under development",
            color=0x99ccff  # Convert hex color to integer
        )



        embed_admin = discord.Embed(
            title="admin commands - under development",
            color=0x99ccff  # Convert hex color to integer
        )



        embed_music = discord.Embed(
            title="Music commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_music.add_field(name='`ai.join`', value="Join your voice channel", inline=False)
        embed_music.add_field(name='`ai.play {song name}`', value="Play a song from internet", inline=False)
        embed_music.add_field(name='`ai.loop`', value="Enable loop", inline=False)
        embed_music.add_field(name='`ai.stop`', value="Stop the playback", inline=False)
        embed_music.add_field(name='`ai.resume`', value="Resume the plaback", inline=False)
        embed_music.add_field(name='`ai.pause`', value="Pause the playback", inline=False)
        embed_music.add_field(name='`ai.volume`', value="Increase or decrease the volume of the playback.", inline=False)
        embed_music.add_field(name='`ai.leave`', value="Stop the playback and leave. **Do NOT force LuminaryAI to leave the voice channel. Just use this command.**", inline=False)

        help_select = Select(placeholder="Make a selection", options=[
            discord.SelectOption(label="Bot related", emoji="🤖", description="Bot related commands"),
            discord.SelectOption(label="AI", emoji="✨", description="AI commands"),
            discord.SelectOption(label="General", emoji="🪶", description="General commands"),
            discord.SelectOption(label="Fun", emoji="😂", description="Fun commands"),
            discord.SelectOption(label="Moderation", emoji="🛠️", description="Moderation commands"),
            discord.SelectOption(label="Automod", emoji="⚒️", description="Automod commands"),
            discord.SelectOption(label="Admin", emoji="⚙️", description="Admin commands"),
            discord.SelectOption(label="Music", emoji="🎧", description="Music commands"),
        ])

        help_view = View()
        help_view.add_item(help_select)

        help_embbed = discord.Embed(
            title="LuminaryAI - help",
            description="[support server](<https://discord.com/invite/hmMBe8YyJ4>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n\nLuminaryAI is like a smart friend on Discord, using a powerful AI engine called 'Luminary' made by AlphasT101. It's here to help everyone in the Discord group with anything you need.",
            color=0x99ccff  # Convert hex color to integer
        )
        help_msg = await ctx.send(embed=help_embbed, view=help_view)
        async def help_callback(interaction):
            if help_select.values[0] == "Bot related":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_bot, view=help_view)

            elif help_select.values[0] == "AI":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_ai, view=help_view)

            elif help_select.values[0] == "General":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_general, view=help_view)

            elif help_select.values[0] == "Fun":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_fun, view=help_view)

            elif help_select.values[0] == "Moderation":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_moderation, view=help_view)

            elif help_select.values[0] == "Automod":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_automod, view=help_view)

            elif help_select.values[0] == "Admin":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_admin, view=help_view)

            elif help_select.values[0] == "Music":
                await interaction.response.defer()
                await help_msg.edit(embed=embed_music, view=help_view)



        help_select.callback = help_callback
