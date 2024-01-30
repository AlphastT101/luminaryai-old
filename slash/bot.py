import discord
from discord.ui import Select, View
import datetime
import time
from discord.ext import commands



def bot_slash(bot, cmd_log_channel_id,start_time):

    ##### check #######
    @bot.tree.command(name="status", description="Check bot status")
    @commands.guild_only()
    async def check(interaction: discord.Interaction):
        await interaction.response.send_message("bot is online")

        await bot.get_channel(cmd_log_channel_id).send(f"{interaction.user} used status(slash) command in {interaction.guild.name}")

    ##### help #######
    @bot.tree.command(name="help", description="Help/command list")
    @commands.guild_only()
    async def help(interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        embed_bot = discord.Embed(
            title="Bot related commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_bot.add_field(name="`developer {choice}`", value="Enable developer mode. choices - true & false", inline=False)
        embed_bot.add_field(name="`about`", value="about the bot", inline=False)
        embed_bot.add_field(name="`help`", value="command list", inline=False)
        embed_bot.add_field(name="`invite`", value="invite the bot", inline=False)
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
        embed_ai.add_field(name='`ai.activate`', value="Disable AI responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.deactivate`', value="Disable AI responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.searchimg {prompt}`', value="Disable AI responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`@luminaryai {prompt}`', value="Ping LuminaryAI to generate text and images.", inline=False)



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
        embed_moderation.add_field(name='`ai.purge`', value="Purge messages, you need proper permissions to use this command.", inline=False)



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
            description="[support server](<https://discord.gg/3fRkNa3HR9>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=3025808252417&response_type=code&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D1110111253256482826%26scope%3Dbot&scope=bot+guilds>)\n\nLuminaryAI is like a smart friend on Discord, using a powerful AI engine called 'Luminary' made by AlphasT101. It's here to help everyone in the Discord group with anything you need.",
            color=0x99ccff  # Convert hex color to integer
        )
        await interaction.followup.send(embed=help_embbed, view=help_view)
        async def help_callback(interaction):
            if help_select.values[0] == "Bot related":
                await interaction.response.send_message(embed=embed_bot)
            elif help_select.values[0] == "AI":
                await interaction.response.send_message(embed=embed_ai)
            elif help_select.values[0] == "General":
                await interaction.response.send_message(embed=embed_general)
            elif help_select.values[0] == "Fun":
                await interaction.response.send_message(embed=embed_fun)
            elif help_select.values[0] == "Moderation":
                await interaction.response.send_message(embed=embed_moderation)
            elif help_select.values[0] == "Automod":
                await interaction.response.send_message(embed=embed_automod)
            elif help_select.values[0] == "Admin":
                await interaction.response.send_message(embed=embed_admin)
            elif help_select.values[0] == "Music":
                await interaction.response.send_message(embed=embed_music)


        help_select.callback = help_callback


    ############## about ##################
    @commands.guild_only()
    @bot.tree.command(name="about", description="about the bot")
    @commands.guild_only()
    async def about(interaction: discord.Interaction):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        about = discord.Embed(
            title='About',
            description='[support server](<https://discord.gg/3fRkNa3HR9>)\n[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=3025808252417&response_type=code&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D1110111253256482826%26scope%3Dbot&scope=bot+guilds>)\n[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n\nLuminaryAI, a Python and AI-powered Discord bot, adeptly replicates human-like conversation and can generate images. Through advanced technologies, it engages users in dynamic and natural dialogues. Designed to create interactive experiences, this bot transforms text-based interactions into lifelike discussions on the Discord platform.',
            color=0x99ccff  # Convert hex color to integer
        )
        about.add_field(name='Owner', value="alphast101", inline=True)
        about.add_field(name='Used languages', value="Python 3.11 discord.py 2.3.2", inline=True)
        about.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/8964c60e7cd3dd4b919811e566e5ccb7.webp?size=80")
        about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
        about.add_field(name='AI engine', value="Luminary", inline=True)
        about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
        about.add_field(name='Members', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
        about.set_image(url="attachment://ai.png")
        filename = "ai.png"
        await interaction.response.send_message(embed=about, file=discord.File(filename, filename="ai.png"))

        await bot.get_channel(cmd_log_channel_id).send(f"{interaction.user} used about(slash) command in {interaction.guild.name}")