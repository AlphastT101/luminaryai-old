import discord
from discord.ext import commands
from discord.ui import Select, View
import datetime
import time

def bbot(bot, cmd_log_channel_id, developer_members, start_time):

    ############### About ########################
    @bot.command(name='about', aliases=["!about", "/about"])
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def about(ctx):
        current_time = time.time()
        difference = int(round(current_time - start_time))
        uptime_duration = datetime.timedelta(seconds=difference)

        about = discord.Embed(
            title='About',
            description='[support server](<https://discord.gg/3fRkNa3HR9>)\n[Discord bot list](<https://top.gg/bot/1110111253256482826>)\n[Invite bot](<https://discord.com/oauth2/authorize?client_id=1110111253256482826&permissions=3025808252417&response_type=code&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D1110111253256482826%26scope%3Dbot&scope=bot+guilds>)\n[Discord bot list vote](<https://top.gg/bot/1110111253256482826/vote>)\n\nLuminaryAI, a Python and AIML-powered Discord bot, adeptly replicates human-like conversation and can generate images. Through advanced technologies, it engages users in dynamic and natural dialogues. Designed to create interactive experiences, this bot transforms text-based interactions into lifelike discussions on the Discord platform.',
            color=0x99ccff  # Convert hex color to integer
        )
        about.add_field(name='Owner', value="alphast101", inline=True)
        about.add_field(name='Used languages', value="Python 3.11 | discord.py 2.3.2", inline=True)
        about.set_author(name="alphast101", icon_url="https://cdn.discordapp.com/avatars/1026388699203772477/8964c60e7cd3dd4b919811e566e5ccb7.webp?size=80")
        about.add_field(name='Uptime', value=str(uptime_duration), inline=True)
        about.add_field(name='AI engine', value="Luminary", inline=True)
        about.add_field(name='Total guilds', value=f'{len(bot.guilds)}', inline=True)
        about.add_field(name='Members', value=f'{sum(guild.member_count for guild in bot.guilds)}', inline=True)
        about.set_image(url="attachment://ai.png")
        filename = "ai.png"
        # Send the embed without the file parameter
        await ctx.send(embed=about, file=discord.File(filename, filename="ai.png"))


    ############### Help ########################
    @bot.command(name='info')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def help_command(ctx, command_info: str = None):
        rps = discord.Embed(
            title="Help: RPS",
            description="Play RPS with the bot",
            color=0x99ccff
        )
        rps.add_field(name='Syntax:', value='```ai.rps {your move}```')

        cat = discord.Embed(
            title="Help: cat",
            description="Shows a random cat picture",
            color=0x99ccff
        )
        cat.add_field(name='Syntax:', value='```ai.cat```')

        meme = discord.Embed(
            title="Help: meme",
            description="Shows a random meme",
            color=0x99ccff
        )
        meme.add_field(name='Syntax:', value='```ai.meme```')

        randomfact = discord.Embed(
            title="Help: randomfact",
            description="shows a randomfact about the world",
            color=0x99ccff
        )
        randomfact.add_field(name='Syntax:', value='```ai.randomfact```')

        user = discord.Embed(
            title="Help: user",
            description="Shows user ID, username, user avatar. \n user_mention is optional",
            color=0x99ccff
        )
        user.add_field(name='Syntax:', value='```ai.user {user_mention}```')

        start = discord.Embed(
            title="Help: start",
            description="Initiate AI responses by executing the ?start command. The bot will respond when the `?start` command is triggered. Prefix commands won't function while AI responses are active. To deactivate AI responses, use the ?stop command.",
            color=0x99ccff
        )
        start.add_field(name='Syntax:', value='```ai.start```')

        stop = discord.Embed(
            title="Help: stop",
            description="Disable AI responses",
            color=0x99ccff
        )
        stop.add_field(name='Syntax:', value='```ai.stop```')

        img = discord.Embed(
            title="Help: img",
            description="Generate images!",
            color=0x99ccff
        )
        img.add_field(name='Syntax:', value='```ai.imagine {prompt}```')
        img.add_field(name='Example:', value='```ai.imagine bmw m4```')

        ai = discord.Embed(
            title="Help: ai",
            description="Generate answers!",
            color=0x99ccff
        )
        ai.add_field(name='Syntax:', value='```ai.response {prompt}```')
        ai.add_field(name='Example:', value='```ai.response Write a complex python code.```')

        if command_info is None:
            await ctx.send("Invalid command", delete_after=3)
        elif command_info.lower() == "rps":
            await ctx.send(embed=rps)
        elif command_info.lower() == "cat":
            await ctx.send(embed=cat)
        elif command_info.lower() == "meme":
            await ctx.send(embed=meme)
        elif command_info.lower() == "randomfact":
            await ctx.send(embed=randomfact)
        elif command_info.lower() == "start":
            await ctx.send(embed=start)
        elif command_info.lower() == "stop":
            await ctx.send(embed=stop)
        elif command_info.lower() == "user":
            await ctx.send(embed=user)
        elif command_info.lower() == "imagine":
            await ctx.send(embed=img)
        elif command_info.lower() == "response":
            await ctx.send(embed=ai)
        else:
            await ctx.send("invalid command")

        await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used info command in {ctx.guild.name}")



    ####### return message ######
    @bot.command(name="m", aliases=['!m', '/m'])
    async def m(ctx, *, message):
        allowed = [1026388699203772477, 885977942776246293, 973461136680845382]
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


        await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} mp command in {ctx.guild.name}")

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


        await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used serverinv command in {ctx.guild.name}")



    @bot.command(name="server")
    async def list_servers(ctx):
        if ctx.author.id == 1026388699203772477:
            servers = bot.guilds

            if not servers:
                await ctx.send("The bot is not a member of any servers.")
                return

            server_names = [server.name for server in servers]
            server_list = "\n".join(server_names)

            embed = discord.Embed(
                title="Server List",
                description=server_list,
                color=0x99ccff
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("**This command is restricted**", delete_after=3)

        await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used server command in {ctx.guild.name}")

    @bot.command(name="servermem")
    async def list_server_members(ctx, *, server_name: str):
        if ctx.author.id == 1026388699203772477:
            server = discord.utils.get(bot.guilds, name=server_name)

            if server is None:
                await ctx.send(f"Bot is not a member of a server named {server_name}.")
                return

            members = [member.name for member in server.members]

            if not members:
                await ctx.send(f"No members found in the server named {server_name}.")
                return

            members_list = "\n".join(members)
            await ctx.send(f"Members of {server_name}:\n```{members_list}```")

        else:
            await ctx.send("**This command is restricted**", delete_after=3)


        await ctx.bot.get_channel(cmd_log_channel_id).send(f"{ctx.author} used servermem command in {ctx.guild.name}")

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
        embed_bot.add_field(name="`invite`", value="invite the bot", inline=False)
        embed_bot.add_field(name="`uptime`", value="Bot uptime", inline=False)
        embed_bot.add_field(name="`support`", value="Support server link", inline=False)
        embed_bot.add_field(name="`owner`", value="shows owner of the bot", inline=False)




        embed_ai = discord.Embed(
            title="AI commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_ai.add_field(name='`ai.imagine`', value="Generates images using SDXL according to user-inputes. We prefer to use the slash command `/imagine`", inline=False)
        embed_ai.add_field(name='`ai.imagine.p`', value="Generates images using pollinations.ai according to user-inputes. We prefer to use the slash command `/imagine`", inline=False)
        embed_ai.add_field(name='`ai.response`', value="Generates answers according to user-inputes. Message history available", inline=False)
        embed_ai.add_field(name='`ai.aiml.start`', value="Enable AIML responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.aiml.stop`', value="Disable AIML responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.activate`', value="Disable AI responses, You need a role with manage messages to run this command.", inline=False)
        embed_ai.add_field(name='`ai.deactivate`', value="Disable AI responses, You need a role with manage messages to run this command.", inline=False)



        embed_general = discord.Embed(
            title="general commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_general.add_field(name='`user {mention}`', value="Shows username & avatar. if you enable developer mode, then it also displays userID, account creation date & guild join date.", inline=False)



        embed_fun = discord.Embed(
            title="fun commands",
            color=0x99ccff  # Convert hex color to integer
        )
        embed_fun.add_field(name='`rps {your move}`', value="play RPS with the bot", inline=False)
        embed_fun.add_field(name='`meme`', value="Shows a meme", inline=False)
        embed_fun.add_field(name='`cat`', value="shows a cat", inline=False)
        embed_fun.add_field(name='`randomfact`', value="Shows a random fact", inline=False)



        embed_moderation = discord.Embed(
            title="moderation commands - under development",
            color=0x99ccff  # Convert hex color to integer
        )



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
        await ctx.send(embed=help_embbed, view=help_view)
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