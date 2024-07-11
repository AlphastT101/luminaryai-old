import discord
from discord.ext import commands, tasks
from discord.ui import Select, View, Button

import datetime
import time
import psutil
import io
import contextlib
from bot_utilities.owner_utils import *


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



def bbot(bot, start_time, mongodb):

    @bot.command(name="ping")
    async def ping(ctx):
        wait = await ctx.send("**Please wait while I calculate my latency.**")
        latency_ms = round(bot.latency * 1000)
        await wait.edit(content=f'**Pong! My Latency is `{latency_ms}ms`.**')


    @bot.command(name="server")
    async def list_guilds(ctx):
        """Lists all the guilds the bot is in along with their IDs."""
        guilds = ctx.bot.guilds
        per_page = 15  # Number of guilds to display per page
        total_pages = (len(guilds) + per_page - 1) // per_page  # Calculate total pages
        pages = []
        for i in range(0, len(guilds), per_page):
            page = "\n".join([f"{guild.name} - `{guild.id}`" for guild in guilds[i:i + per_page]])
            pages.append(page)
        current_page = 0

        async def update_message(interaction):
            embed = discord.Embed(title="Guilds List", color=discord.Color.blue())
            embed.description = pages[current_page]
            embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

            # Disable buttons as needed
            previous_button.disabled = current_page == 0
            next_button.disabled = current_page == total_pages - 1

            await interaction.response.defer()
            await interaction.message.edit(embed=embed, view=view)

        async def previous_callback(interaction):
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                await update_message(interaction)

        async def next_callback(interaction):
            nonlocal current_page
            if current_page < len(pages) - 1:
                current_page += 1
                await update_message(interaction)

        async def stop_callback(interaction):
            await paginator_message.edit(embed=initial_embed, view=None)
            view.stop()

        async def on_timeout():
            await paginator_message.edit(embed=initial_embed, view=None)
            view.stop()

        initial_embed = discord.Embed(title="Guilds List", color=discord.Color.blue())
        initial_embed.description = pages[current_page]
        initial_embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

        previous_button = discord.ui.Button(label="⬅️", style=discord.ButtonStyle.primary)
        next_button = discord.ui.Button(label="➡️", style=discord.ButtonStyle.primary)
        stop_button = discord.ui.Button(label="❌", style=discord.ButtonStyle.danger)

        view = discord.ui.View(timeout=20)
        view.add_item(previous_button)
        view.add_item(next_button)
        view.add_item(stop_button)



        
        # Disable buttons initially for first page
        previous_button.disabled = True
        paginator_message = await ctx.send(embed=initial_embed, view=view)

        previous_button.callback = previous_callback
        next_button.callback = next_callback
        stop_button.callback = stop_callback

        view.timeout_callback = on_timeout



    ####### return message ######
    @bot.command(name="say")
    async def m(ctx, *, message: str = None):
		# 1026388699203772477 - alphast101
		# 973461136680845382 - wqypp
        # 885977942776246293 -jeydalio
        if message is None:
            return
        allowed = [973461136680845382, 1026388699203772477, 885977942776246293]
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


    @bot.command(name="sync")
    async def sync(ctx):
        if ctx.author.id == 1026388699203772477:
            await ctx.send("**<@1026388699203772477> Syncing slash commands...**")
            await bot.tree.sync()
            await ctx.send("**<@1026388699203772477> Slash commands synced!**")


        
    @bot.command(name="blist")
    async def blist(ctx, object, id = None):
        if ctx.author.id != 1026388699203772477:
            return

        try:
            id = int(id)
        except TypeError:
            await ctx.send("Invalid Command or ID")
            return

        if object == "server":
            guild = bot.get_guild(id)
            if guild:
                insert = await insertdb('blist-servers', id, mongodb)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = bot.get_user(id)
            if user:
                insert = await insertdb('blist-users', id, mongodb)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"Invalid object")

    @bot.command(name="unblist")
    async def unblist(ctx, object, id = None):
        if ctx.author.id != 1026388699203772477:
            return

        try:
            id = int(id)
        except TypeError:
            await ctx.send("Invalid Command or ID")
            return

        if object == "server":
            guild = bot.get_guild(id)
            if guild:
                insert = await deletedb('blist-servers', id, mongodb)
                await ctx.send(f"**{guild} is {insert}.**")
            else:
                await ctx.send(f"**Guild not found, `{guild}`**")

        elif object == 'user':
            user = bot.get_user(id)
            if user:
                insert = await deletedb('blist-users', id, mongodb)
                await ctx.send(f"**{user} is {insert}**")
            else:
                await ctx.send(f"**User not found, `{user}`**")
        else:
            await ctx.send(f"Invalid object")



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
        filename = 'images/ai.png'
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
    async def developer(ctx):
     # Function to get a chunk of commands
     def get_chunk(embed, commands_list, start, count=5):
        embed.clear_fields()
        for name, value in commands_list[start:start + count]:
            embed.add_field(name=name, value=value, inline=False)
        current_page = (start // count) + 1
        total_pages = (len(commands_list) + count - 1) // count
        embed.set_footer(text=f"Page {current_page} of {total_pages} | Type ai.info <command> for more command information")
        return embed

     bot_related_commands = [
        ("developer {choice}", "❯ Enable developer mode. choices - true & false"),
        ("about", "❯ About the bot"),
        ("help", "❯ Command list"),
        ("uptime", "❯ Bot uptime"),
        ("support", "❯ Support server link"),
        ("owner", "❯ Shows owner of the bot")
     ]

     ai_commands = [
        ('ai.imagine {prompt}', "❯ Generates images using SDXL according to user-inputs. We prefer to use the slash command `/imagine`"),
        ('ai.imagine.p {prompt}', "❯ Generates images using pollinations.ai according to user-inputs. We prefer to use the slash command `/imagine`"),
        ('ai.response {prompt}', "❯ Generates answers according to user-inputs. Message history available"),
        ('ai.aiml.start', "❯ Enable AIML responses, You need a role with manage messages to run this command."),
        ('ai.aiml.stop', "❯ Disable AIML responses, You need a role with manage messages to run this command."),
        ('ai.activate **[DISABLED]**', "❯ Enable AI responses, You need a role with manage messages to run this command.\nModel: *Luminary*"),
        ('ai.deactivate **[DISABLED]**', "❯ Disable AI responses, You need a role with manage messages to run this command."),
        ('ai.searchimg {prompt}', "❯ Search the web for images."),
        ('ai.search {prompt}', "❯ Search the web."),
        ('ai.vision {prompt}', "❯ Vision an image."),
        ('@luminaryai {prompt}', "❯ Ping LuminaryAI to generate text and images."),
        ('@luminaryai activate', "❯ Enable AI responses using Luminary-ultra. You need admin permissions to run this command."),
        ('@luminaryai deactivate', "❯ Disable AI responses. You need admin permissions to run this command.")
     ]

     general_commands = [
        ('ai.user {mention}', "❯ Shows username & avatar. if you enable developer mode, then it also displays userID, account creation date & guild join date.")
     ]

     fun_commands = [
        ('ai.rps {your move}`', "❯ Play RPS with the bot"),
        ('ai.cat', "❯ Shows a cat"),
        ('ai.randomfact', "❯ Shows a random fact")
     ]

     moderation_commands = [
        ('ai.purge {number of messages}', "❯ Purge messages, you need proper permissions to use this command."),
        ('ai.ban {user} {reason}', "❯ Ban a member, you need the ban members permission to take this action."),
        ('ai.unban {user} {reason}', "❯ Unban a member."),
        ('ai.kick {user} {reason}', "❯ Kick a member."),
        ('ai.purgefiles {amount of messages}', "❯ Purge messages that contain files/attachments."),
        ('ai.purgelinks {amount of messages}', "❯ Purge messages that contain links."),
        ('ai.unmute {member} {reason}', "❯ Unmute/remove time out from a member."),
        ('ai.timeout {user} {duration} {reason}', "❯ Timeout a member. A valid time duration required.(eg. 1d,10m,5h)")
     ]

     automod_commands = [
        # Placeholder for future commands
     ]

     admin_commands = [
        # Placeholder for future commands
     ]

     music_commands = [
        ('ai.join', "❯ Join your voice channel"),
        ('ai.play {song name}', "❯ Play a song from the internet"),
        ('ai.loop', "❯ Enable loop"),
        ('ai.stop', "❯ Stop the playback"),
        ('ai.resume', "❯ Resume the playback"),
        ('ai.pause', "❯ Pause the playback"),
        ('ai.volume', "❯ Increase or decrease the volume of the playback."),
        ('ai.leave', "❯ Stop the playback and leave. **Do NOT force LuminaryAI to leave the voice channel. Just use this command.**")
     ]

     embed_bot = discord.Embed(
        title="Bot related commands",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_ai = discord.Embed(
        title="AI commands",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_general = discord.Embed(
        title="General commands",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_fun = discord.Embed(
        title="Fun commands",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_moderation = discord.Embed(
        title="Moderation commands",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_automod = discord.Embed(
        title="Automod commands - under development",
        color=0x99ccff  # Convert hex color to integer
     ) 

     embed_admin = discord.Embed(
        title="Admin commands - under development",
        color=0x99ccff  # Convert hex color to integer
     )

     embed_music = discord.Embed(
        title="Music commands",
        color=0x99ccff  # Convert hex color to integer
     )
     """
     # Set thumbnails for each embed
     bot_thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMqcwdPNaGunh0E1J4YV2O5ch0jbFPL8dw1Q&s"
     ai_thumbnail = "https://www.nibib.nih.gov/sites/default/files/inline-images/AI%20600%20x%20400.jpg"
     general_thumbnail = "https://example.com/general_thumbnail.png"
     fun_thumbnail = "https://i.pinimg.com/736x/9e/80/9a/9e809ad17207f4a040855cd9ebe24713.jpg"
     moderation_thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRfDhCKqD1Pusxa3sFILJsY0AaFvsN_E-14s9CBqyuq0tYV7_L1VWk2L9bhJPd83Fko6uw&usqp=CAU"
     automod_thumbnail = "https://img.freepik.com/free-vector/robot-arm-concept-illustration_114360-8436.jpg?size=338&ext=jpg&ga=GA1.1.2008272138.1720483200&semt=sph"
     admin_thumbnail = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSQmO27HNo399ZS89SSJl3DfmfZjUhY-6Bm4Q&s"
     music_thumbnail = "https://t3.ftcdn.net/jpg/02/23/60/54/360_F_223605406_nGKtPp42ZRx4ZxvrcVeT3Ek6V5Uw4ETh.jpg"

     embed_bot.set_thumbnail(url=bot_thumbnail)
     embed_ai.set_thumbnail(url=ai_thumbnail)
     embed_general.set_thumbnail(url=general_thumbnail)
     embed_fun.set_thumbnail(url=fun_thumbnail)
     embed_moderation.set_thumbnail(url=moderation_thumbnail)
     embed_automod.set_thumbnail(url=automod_thumbnail)
     embed_admin.set_thumbnail(url=admin_thumbnail)
     embed_music.set_thumbnail(url=music_thumbnail)
    """
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
     about_bot = "LuminaryAI is like a smart friend on Discord, using a powerful AI engine called 'Luminary' made by AlphasT101. It's here to help everyone in the Discord group with anything you need."
     help_embbed = discord.Embed(
        title="LuminaryAI - Help",
        description=f"{about_bot}\n\n[support server](<https://discord.com/invite/hmMBe8YyJ4>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)",
        color=0x99ccff  # Convert hex color to integer
     )
     help_embbed.set_thumbnail(url=bot.user.avatar)
     help_msg = await ctx.send(embed=help_embbed, view=help_view)

     # Pagination buttons
     buttons = [
        Button(label="Previous", style=discord.ButtonStyle.primary, custom_id='Previous'),
        Button(label="Next", style=discord.ButtonStyle.primary, custom_id='Next')
     ]

     help_view.add_item(buttons[0])
     help_view.add_item(buttons[1])

     # Variables to track current state
     current_page = 0
     current_commands = bot_related_commands
     embed = embed_bot

     # Callback for the select menu
     async def help_callback(interaction):


        nonlocal current_page, current_commands, embed

        if help_select.values[0] == "Bot related":
            current_commands = bot_related_commands
            embed = embed_bot
        elif help_select.values[0] == "AI":
            current_commands = ai_commands
            embed = embed_ai
        elif help_select.values[0] == "General":
            current_commands = general_commands
            embed = embed_general
        elif help_select.values[0] == "Fun":
            current_commands = fun_commands
            embed = embed_fun
        elif help_select.values[0] == "Moderation":
            current_commands = moderation_commands
            embed = embed_moderation
        elif help_select.values[0] == "Automod":
            current_commands = automod_commands
            embed = embed_automod
        elif help_select.values[0] == "Admin":
            current_commands = admin_commands
            embed = embed_admin
        elif help_select.values[0] == "Music":
            current_commands = music_commands
            embed = embed_music

        current_page = 0  # Reset to the first page
        embed = get_chunk(embed, current_commands, current_page * 5)
        await interaction.response.defer()
        await help_msg.edit(embed=embed, view=help_view)
     help_select.callback = help_callback
     # Callback for the buttons
     async def button_callback(interaction):
      nonlocal current_page, current_commands, embed


      if interaction.data["custom_id"] == "Previous":
        current_page = max(current_page - 1, 0)
      elif interaction.data["custom_id"] == "Next":
        current_page = min(current_page + 1, (len(current_commands) - 1) // 5)

      embed = get_chunk(embed, current_commands, current_page * 5)
      await interaction.response.defer()
      await help_msg.edit(embed=embed, view=help_view)

     for button in buttons:
         button.callback = button_callback

