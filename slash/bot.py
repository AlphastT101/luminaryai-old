import discord
from discord.ui import Select, View
import datetime
import time
from discord.ext import commands
import psutil
from data import blacklisted_servers

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


def bot_slash(bot,start_time):

    ##### check #######
    @bot.tree.command(name="status", description="Check bot status")
    @commands.guild_only()
    async def check(interaction: discord.Interaction):
        if interaction.guild.id in blacklisted_servers:
            return
        await interaction.response.send_message("bot is online")

    ##### help #######
    @bot.tree.command(name="help", description="Help/command list")
    @commands.guild_only()
    async def help(interaction: discord.Interaction):
        if interaction.guild.id in blacklisted_servers:
            return
        await interaction.response.defer(ephemeral=False)
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
        help_msg = await interaction.followup.send(embed=help_embbed, view=help_view)
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


    ############## about ##################
    @bot.tree.command(name="about", description="about the bot")
    @commands.guild_only()
    async def about(interaction: discord.Interaction):
        if interaction.guild.id in blacklisted_servers:
            return
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        about = discord.Embed(
            title='About',
            description="[support server](<https://discord.com/invite/hmMBe8YyJ4>)\n[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=8&scope=bot>)\n[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n[Site](<https://luminaryai.netlify.app>)\n[Terms of Service](<https://luminaryai.netlify.app/tos>)\n\nLuminaryAI is your Discord bot powered by artificial intelligence. It utilizes cutting-edge AI features to enrich your server's experience, providing automated moderation, text filtering, image generation, and more!",
            color=0x99ccff  # Convert hex color to integer
        )
        about.add_field(name='Owner', value="alphast101", inline=True)
        about.add_field(name='Used languages', value="Python 3.11 discord.py 2.3.2", inline=True)
        about.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/49e0b0b97f57bba4181cb759aef7ebcc.webp?size=80")
        about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
        about.add_field(name='AI engine', value="Luminary", inline=True)
        about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
        about.add_field(name='Members', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
        about.add_field(name='RAM usage', value=f"{ram_text}", inline=True)
        about.add_field(name='CPU usage', value=f"{cpu_text}", inline=True)
        about.set_image(url="attachment://ai.png")
        filename = "ai.png"
        await interaction.response.send_message(embed=about, file=discord.File(filename, filename="ai.png"))