import discord
# from discord import app_commands
# import os
# from PIL import Image
import datetime
import time

def bot_slash(bot, cmd_log_channel_id,start_time):

    ##### check #######
    @bot.tree.command(name="status", description="Check bot status")
    async def check(interaction: discord.Interaction):
        await interaction.response.send_message("bot is online")

        await bot.get_channel(cmd_log_channel_id).send(f"{interaction.user} used status(slash) command in {interaction.guild.name}")

    ##### help #######
    @bot.tree.command(name="help", description="Help/command list")
    async def help(interaction: discord.Interaction):
        help_ = discord.Embed(
            title='Help/command list',
            description="try using `ai.help {command}` !",
            color=0x99ccff  # Convert hex color to integer
        )
        help_.add_field(name='?start', value="Enable AI response.", inline=False)
        help_.add_field(name='?stop', value="Disable AI response.", inline=False)
        help_.add_field(name='?rps', value="Play RPS", inline=False)
        help_.add_field(name='?user', value="Shows userID, username and user avatar.", inline=False)
        help_.add_field(name='?randomfact', value="Shows userID, username and user avatar.", inline=False)
        help_.add_field(name='?meme', value="shows a random meme.", inline=False)
        help_.add_field(name='?help', value="shows a list of commands.", inline=False)
        help_.add_field(name='?about', value="about the bot", inline=False)
        help_.add_field(name='?cat', value="shows a cat.", inline=False)
        help_.add_field(name='?img', value="Generates images according to user-inputes", inline=False)
        help_.add_field(name='?ai', value="Generates answers according to user-inputes", inline=False)

        await interaction.response.send_message(embed=help_)

        await bot.get_channel(cmd_log_channel_id).send(f"{interaction.user} used help(slash) command in {interaction.guild.name}")


    ############## about ##################
    @bot.tree.command(name="about", description="about the bot")
    async def about(interaction: discord.Interaction):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        about = discord.Embed(
            title='About',
            description='[support server](<https://discord.gg/3fRkNa3HR9>)\n[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=3025808252417&response_type=code&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D1110111253256482826%26scope%3Dbot&scope=bot+guilds>)\n[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n\nLuminaryAI, a Python and AIML-powered Discord bot, adeptly replicates human-like conversation and can generate images. Through advanced technologies, it engages users in dynamic and natural dialogues. Designed to create interactive experiences, this bot transforms text-based interactions into lifelike discussions on the Discord platform.',
            color=0x99ccff  # Convert hex color to integer
        )
        about.add_field(name='Owner', value="alphast101", inline=True)
        about.add_field(name='Used languages', value="Python 3.11 | AIML 0.9.2 | discord.py 2.3.2", inline=True)
        about.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/8964c60e7cd3dd4b919811e566e5ccb7.webp?size=80")
        about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
        about.add_field(name='AI engine', value="Luminary", inline=True)
        about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
        about.add_field(name='Members', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
        about.set_image(url="attachment://ai.png")
        filename = "ai.png"
        await interaction.response.send_message(embed=about, file=discord.File(filename, filename="ai.png"))

        await bot.get_channel(cmd_log_channel_id).send(f"{interaction.user} used about(slash) command in {interaction.guild.name}")

