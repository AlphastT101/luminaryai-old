import yt_dlp as youtube_dl
from discord.ext import commands
import discord
import pyshorteners
import asyncio
# Assign Task
import time
import random
from datetime import datetime
import traceback
import logging

# Discord Import
import discord
from discord.ext import commands

# Youtube Import
from yt_dlp import YoutubeDL


# Music Class
class Music(commands.Cog):

  def __init__(self, bot):
    self.bot = bot
    self.music_queue = []
    self.current_song = None
    self.current_song_index = -1
    self.repeat = False

    self.voice_client = None

  @commands.Cog.listener()
  async def on_ready(self):
    await self.bot.change_presence(status=discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.listening, name=",help"))
    print("Music.py is ready!")

  def search(self, query: str, ctx):
   
    ydl_opts = {
     'format': 'bestaudio/best',
     'restrictfilenames': True,
     'noplaylist': True,
     'nocheckcertificate': True,
     'ignoreerrors': False,
     'logtostderr': False,
     'no_warnings': True,
     'default_search': 'auto',
     'source_address': '0.0.0.0',
     'quiet': True,
     'extract_flat': True,
     'audioquality': '4',  # Best audio quality
     'max_downloads': 100,  # Adjust as needed

    }


    if query.startswith("https://"):  # check if the query is a link
      with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)

        if 'entries' in info:  # if the link is a playlist link, it'll have entries
          entries = info['entries']
          return [{
              'thumbnail_url': entry['thumbnails'][0]['url'],
              'title': entry['title'],
              'source': entry['url'],
              'user_req': ctx.author
          } for entry in entries if entry['title'] != "[Deleted video]"]

        else:
          return [{
              'thumbnail_url': info['thumbnail'],
              'title': info['title'],
              'source': info['url'],
              'user_req': ctx.author
          }]

    else:  # if not then search
      with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch{4}:{query}", download=False)
        entries = info['entries']
        return [{
            'thumbnail_url': entry['thumbnails'][0]['url'],
            'title': entry['title'],
            'source': entry['url'],
            'user_req': ctx.author
        } for entry in entries]

  
  async def play(self, ctx, *, args):
    """Plays a song from youtube"""
    await ctx.send('## Ctx:', ctx)
    if not ctx.author.voice:
      await ctx.send("You are not in a voice channel!")


    if self.voice_client is None:
      self.voice_client = await ctx.author.voice.channel.connect()


    # Search the song
    query = " ".join(args)

    message = await ctx.send("> `Searching...` 🔎")
    result = self.search(query, ctx)
    await message.delete()

    if not result:
      await ctx.send("> `No results found ?` ❌")
      return

    if query.startswith("https://") and len(result) > 1:  # Playlist
      await ctx.send("> `Found playlist, add songs to queue` ✅")
      for entry in result:
        self.music_queue.append(entry)

    if query.startswith("https://") and len(result) == 1:  # Single Link
      await ctx.send(f"> `Found {result[0]['title']}, adding to queue` ✅")
      self.music_queue.append(result[0])

    if not query.startswith("https://"):  # Search and Choose | By Number
      embed = discord.Embed(
          title="Song Selection",
          color=discord.Color.blue(
          )  # ctx.guild.get_member(self.bot.user.id).color
      )

      embed.set_thumbnail(url=self.bot.user.avatar.url)
      embed.set_footer(text="Choose a song: 1-4",
                       icon_url=self.bot.user.avatar)

      for i, entry in enumerate(result):
        embed.add_field(name=f"> `{i+1}`. `{entry['title']}`",
                        value=f"- Source: {entry['source']}",
                        inline=False)

      message = await ctx.send(embed=embed)

      def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel

      try:
        response = await self.bot.wait_for("message", check=check, timeout=15)

        if response.content.lower() == "c":
          await message.delete()
          await ctx.send("> `Canceled Search`")
          await response.delete()  # Move this line inside the try block
          return  # Cancel the operation
        
        
        picked = 1 if not response.content else int(response.content)
        choice = int(picked) - 1
        if 0 <= choice < len(result):
          await message.delete()
          await ctx.channel.purge(limit=1)
          await ctx.send(
              f"> `{ctx.author.name}` picked `{result[choice]['title']}`")
          self.music_queue.append(result[choice])
          await self.play_music(ctx)
        
          await self.nowplaying(ctx)

          await self.bot.change_presence(status=discord.Status.idle, activity=discord.Game(name=f"{result[choice]['title']}"))



        else:
          await ctx.send(
              "> Choice must be from options: `1 - 4`. Type 'c' to cancel.")
          return  # Cancel the operation

      except ValueError:
        await ctx.send(
            "> Choice must be from options: `1 - 4`, Type **Number**. Type 'c' to cancel."
        )

      except TimeoutError:
        await ctx.send("> `It seems you took too long to respond. Choosing the first result.`")

        # Choose the first result as a default
        choice = 0

        await message.delete()

        await ctx.send(
            f"> `{ctx.author.name}` picked `{result[choice]['title']}`"
        )
    
        self.music_queue.append(result[choice])
        await self.play_music(ctx)
        await self.nowplaying(ctx)

        await self.bot.change_presence(
          status=discord.Status.idle,
          activity=discord.Game(name=f"{result[choice]['title']}"),
        )
        try:
          await self.play_music(ctx)
        except Exception as e:
          print(e)

  async def play_music(self, ctx):
    # loop function to check for entry in que and play
    if self.voice_client.is_playing():
      return

    if self.current_song_index + 2 <= len(self.music_queue):
      self.current_song_index = self.current_song_index + 1
      self.current_song = self.music_queue[self.current_song_index]

      ydl_opts = {
          'format': 'bestaudio',
          'quiet': True,
          'source_address': '0.0.0.0',  # Set the source address
          'extract_flat': False,
      }
      ffmpeg_opts = {
       'options': '-vn',
       # Disable video processing, use Opus codec for audio, set bitrate to 128k, compression level 10, and optimize for audio
       'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'}
        # Reconnect options


      with YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(url=self.current_song['source'],
                                  download=False)
      source = discord.FFmpegPCMAudio(result['url'], **ffmpeg_opts)

     
      self.voice_client.play(
          source,
          after=lambda e: self.bot.loop.create_task(self.play_music(ctx)))



    else:
      if self.repeat:
        self.current_song_index = -1
        await self.play_music(ctx)

      else:
        self.current_song_index = -1
        self.music_queue = []
        await self.bot.change_presence(status=discord.Status.idle,activity=discord.Activity(type=discord.ActivityType.listening, name=";help"))

        self.voice_client = await self.voice_client.disconnect()
  
  def get_next_song(self):
        if len(self.music_queue) > 1:
            # Return the second song in the queue (index 1)
            return self.music_queue[1]
        else:
            return None

  # Embed  | Current song title playing with the youtube image set
  async def nowplaying(self, ctx: commands.Context):
    try:
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Get information about the next song
        next_song = self.get_next_song()
        next_song_title = next_song['title'] if next_song else "No upcoming songs"

        # Design your embed here
        embed = discord.Embed(
            title=f"Now Playing:",
            description=f"```{self.current_song['title']}```",
            color=discord.Color.from_rgb(255, 192, 203)  # Light Pink color

        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        # Add information about the next song
        embed.add_field(name="Next Song:", value=f"```{next_song_title}```", inline=False)

    
        await ctx.send(embed=embed, view=MusicButton(self, ctx))
    except Exception as e:
        print(f"An error occurred: {e}")
 
  @commands.command(name='nowplaying', aliases=['np'])
  async def nowplaying_command(self, ctx: commands.Context):
    if not ctx.author.voice:
        await ctx.reply("You are not in a `voice channel`.")
        return
    
    try:
        # Check if there is a currently playing song
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Get information about the currently playing song
        current_song_title = self.current_song['title']

        # Get information about the next song
        next_song = self.get_next_song()
        if next_song:
            next_song_title = next_song['title']
        else:
            next_song_title = "No upcoming songs"

        # Design your "now playing" embed here
        embed = discord.Embed(
            title="Now Playing",
            description=f"```{current_song_title}```",
            color=discord.Color.green()  # Adjust color to match your bot theme
        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.add_field(name="Next Song", value=f"```{next_song_title}```", inline=False)
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        # Send the embed
        message = await ctx.send(embed=embed,view=MusicButton(self, ctx))

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")


  # Pauses currrent song
  async def toggle_pause(self):
    if self.voice_client.is_playing():
      self.voice_client.pause()
    else:
      self.voice_client.resume()

  async def toggle_repeat(self):
    self.repeat = not self.repeat

  async def skip(self):
    self.voice_client.stop()

  # Stops current song playing  
  async def stop(self):
    self.music_queue = []
    await self.voice_client.stop()

  async def shuffle(self):
    if self.music_queue:
      random.shuffle(self.music_queue)
    
  """
  @commands.command(name='playall', aliases=['pa'])
  async def playall_command(self,ctx: commands.Context):
    # Check if there are items in the search result list
    if not self.search_results:
        await ctx.send("There are no search results to play.")
        return

    # Clear the existing music queue
    self.music_queue = []

    # Add all search results to the queue
    self.music_queue.extend(self.search_results)

    # Clear the search result list
    self.search_results = []

    # Play the first item in the queue
    await self.play_music(ctx)

    # Display the now playing message
    await self.nowplaying(ctx)
  """
    
    
    
  def get_queue_songs(self):
        if len(self.music_queue) > 1:
            # Return all songs in the queue starting from index 1
            return self.music_queue[1:]
        else:
            return []  
    
  @commands.command(name='queue', aliases=['q'])
  async def queue_command(self, ctx: commands.Context):
    try:
        print("Working Queue :3")
        # Check if there are items in the queue
        if not self.music_queue:
            await ctx.send("The queue is empty.")
            return

        # Get all upcoming songs in the queue
        next_songs = self.get_queue_songs()

        # Check if there are no upcoming songs
        if not next_songs:
            await ctx.send("There are no upcoming songs in the queue.")
            return

        # Design your queue list embed here
        embed = discord.Embed(
            title="Music Queue",
            color=discord.Color.blue()  # Adjust color to match your bot theme
        )

        # Add fields for each upcoming song
        for index, song in enumerate(next_songs, start=1):
            embed.add_field(name=" ",value=f"```{index}. {song['title']}```", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")









class MusicButton(discord.ui.View):
  def __init__(self, music_class: Music, ctx: commands.Context, timeout=None):
    super().__init__(timeout=timeout)

    self.music_class = music_class
    self.ctx = ctx

    # Initiate Button Pause Label
    # self.children[0].label = "Pause" if self.music_class.voice_client.is_playing() else "Resume"

    # Initiate Button Repeat Label
    # self.children[1].label = "Repeat On" if self.music_class.repeat else "Repeat Off"
    # self.children[1].style =  you can change style if you want
  
  #design your buttons

  # Embed  | Current song title playing with the youtube image set
  async def nowplaying(self, ctx: commands.Context):
    try:
        if self.current_song is None:
            await ctx.send("No song is currently playing.")
            return

        # Check if there are upcoming songs in the queue
        if len(self.music_queue) > 1:
            next_song = self.music_queue[1]
            next_song_title = next_song['title']
        else:
            next_song_title = "No upcoming songs"

        # Design your embed here
        embed = discord.Embed(
            title="Now Playing",
            description=f"```{self.current_song['title']}```",
            color=discord.Color.green()  # Adjust color to match your bot theme
        )

        embed.set_image(url=self.current_song['thumbnail_url'])
        embed.add_field(name="Next Song", value=f"```{next_song_title}```", inline=False)
        embed.set_footer(icon_url=ctx.message.author.avatar, text=f"Playing for {ctx.message.author.name}")

        await ctx.send(embed=embed)

    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")


    except Exception as e:
        # Handle exceptions and inform the user
        await ctx.send(f"An error occurred: {e}")

 
  @discord.ui.button(
    label= "Pause",
    style=discord.ButtonStyle.primary,
  )
  async def toggle_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return
    await self.music_class.toggle_pause()
    button.emoji = "<:pause2:1176772089764651009>" if self.music_class.voice_client.is_playing() else "<:resume:1176772087059316858>"

    await interaction.response.edit_message(view=self)

  
  @discord.ui.button(
    label= "Repeat",
    style=discord.ButtonStyle.primary,
  )
  async def toggle_repeat(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return
    await self.music_class.toggle_repeat()
    self.children[1].style = discord.ButtonStyle.green if self.music_class.repeat else discord.ButtonStyle.primary
    await interaction.response.edit_message(view=self)
  
  @discord.ui.button(
    label= "Skip",
    style=discord.ButtonStyle.primary,
   )
  async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
    if not interaction.user.voice:
      await interaction.response.send_message("My apologises, but your are not in a voice channel.", ephemeral=True)
      return
    try:
        # Get information about the user who skipped
        skipper_name = interaction.user.name
        skipper_avatar_url = interaction.user.avatar

        # Skip the current song
        await self.music_class.skip()

        # Send an embed indicating who skipped and include the now playing information
        await interaction.response.send_message(
            embed=discord.Embed(
                title=f"{skipper_name} skipped the song!",
                color=discord.Color.red(),  # Adjust color to match your bot theme
            ).set_thumbnail(url=skipper_avatar_url)
        )

        # Wait for a moment to ensure the skip operation is complete
        await asyncio.sleep(1)

        # Update the now playing information
        await Music.nowplaying(ctx)

        await self.music_class.nowplaying(self.ctx)
        

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}")

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}")
  
  @discord.ui.button(
    label="Stop",
    style=discord.ButtonStyle.danger,
  )
  async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
    try:
        # Check if the user is in a voice channel
        if not interaction.user.voice:
            await interaction.response.send_message("You are not in a voice channel bro?", ephemeral=True)
            return

        # Get the name and avatar of the user who stopped the music
        stopper_name = interaction.user.name
        stopper_avatar_url = interaction.user.avatar

        # Stop the music
        await self.music_class.stop()

        # Create an ephemeral embed indicating the music has been stopped
        stop_embed = discord.Embed(
            title="Music Stopped",
            description=f"Music has been stopped by {stopper_name}!",
            color=discord.Color.red(),  # Adjust color to match your bot theme
        )
        stop_embed.set_thumbnail(url=stopper_avatar_url)  # Set user's avatar as thumbnail

        # Send the ephemeral embed
        await interaction.response.send_message(embed=stop_embed, ephemeral=True)

    except Exception as e:
        # Handle exceptions and inform the user
        await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
    

# Define the FFMPEG options
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}

# Function to shorten a URL using TinyURL
def shorten_url(original_url):
    s = pyshorteners.Shortener()
    return s.tinyurl.short(original_url)






join_first_embed = discord.Embed(
    title="LumianryAI - music",
    description="Please join a voice channel first.",
    color=0xFF0000
)
join_first_embed.set_thumbnail(url="attachment://thumbnail.png")

already_joined = discord.Embed(
    title="LumianryAI - music",
    description="Bot is already connected to a voice channel. use `ai.leave` to leave.",
    color=0xFF0000
)
already_joined.set_thumbnail(url="attachment://thumbnail.png")


pls_wait_embed = discord.Embed(
    title="LumianryAI - music",
    description="Please wait...",
    color=0xFF0000
)
pls_wait_embed.set_thumbnail(url="attachment://thumbnail.png")

no_result_embed = discord.Embed(
    title="LumianryAI - music",
    description="No results found",
    color=0xFF0000
)
no_result_embed.set_thumbnail(url="attachment://thumbnail.png")


not_in_voice = discord.Embed(
    title="LumianryAI - music",
    description="I am not currently in a voice channel.",
    color=0xFF0000
)
not_in_voice.set_thumbnail(url="attachment://thumbnail.png")

playback_stopped_left = discord.Embed(
    title="LumianryAI - music",
    description="Playback stopped, and I left the voice channel.",
    color=0x99ccff
)
playback_stopped_left.set_thumbnail(url="attachment://thumbnail.png")



playback_stopped = discord.Embed(
    description="Playback stopped.",
    color=0x99ccff
)
playback_paused = discord.Embed(
    description="Playback paused.",
    color=0x99ccff
)
playback_resumed = discord.Embed(
    description="Playback resumed.",
    color=0x99ccff
)



need_same_channel_to_stop = discord.Embed(
    title="LumianryAI - music",
    description="You need to be in the same voice channel as me to perform this action.",
    color=0xFF0000
)
need_same_channel_to_stop.set_thumbnail(url="attachment://thumbnail.png")



loop_enabled = discord.Embed(
    description="Loop enabled",
    color=0x99ccff
)
loop_disabled = discord.Embed(
    description="Loop disabled",
    color=0x99ccff
)



alread_playing = discord.Embed(
    title="LumianryAI - music",
    description="Already playing!\n\n looking for the queue system?\n help us by joining our support server.",
    color=0x99ccff
)
alread_playing.set_thumbnail(url="attachment://thumbnail.png")
def music(bot):
    @bot.command(name='join')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def join(ctx):
        if ctx.author.voice is None:

            await ctx.send(embed=join_first_embed)
            return

        # Get the bot's Member object
        bot_member = ctx.guild.get_member(bot.user.id)

        if ctx.voice_client is not None and ctx.voice_client.is_connected():

            await ctx.send(embed=already_joined)
            return
        else:
            channel = ctx.author.voice.channel

            # Check if the bot has necessary permissions in the voice channel
            required_permissions = ["connect", "speak", "send_messages"]
            missing_permissions = [perm for perm in required_permissions if not getattr(channel.permissions_for(bot_member), perm)]

            if missing_permissions:
                perms_embed = discord.Embed(
                    title="LumianryAI - missing perms",
                    description=f"I don't have the following permissions in the voice channel:\n{', '.join(missing_permissions)}",
                    color=0xFF0000
                )
                file = discord.File("music.png", filename="thumbnail.png")
                perms_embed.set_thumbnail(url="attachment://thumbnail.png")
                await ctx.send(embed=perms_embed, file=file)
                return

            if ctx.voice_client is None:
                voice_channel = await channel.connect()
                await ctx.guild.change_voice_state(channel=channel, self_mute=False, self_deaf=True)
            else:
                voice_channel = ctx.voice_client.channel

            joined_embed = discord.Embed(
                description=f"**Joined {channel}**",
                color=0x99ccff
            )
            await ctx.send(embed=joined_embed)




    server_loops = {}  # Dictionary to store loop status for each server

    @bot.command(name='loop')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def toggle_loop(ctx):
        server_id = ctx.guild.id
        if server_id not in server_loops:
            server_loops[server_id] = True  # Initialize loop status for the server if not present

            await ctx.send(embed=loop_enabled)
        elif server_loops[server_id] == True:
            server_loops[server_id] = False

            await ctx.send(embed=loop_disabled)
        elif server_loops[server_id] == False:
            server_loops[server_id] = True

            await ctx.send(embed=loop_enabled)

    @bot.command(name='play')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def play(ctx, *, args = 'chill step coding music'):
     print('working')
     try:
         music_instance = Music(bot)  # Assuming Music is the name of your Music class
         await music_instance.play(ctx=ctx, args=args)
         print("Song Name: ", args)

     except Exception as e:
        await error_embed(ctx, e)

    async def error_embed(ctx, e):
     # Create an error embed after catching the exception
     error_embed = discord.Embed(
        description=f'```bash\n{e}```',
        color=discord.Color.red(),
        timestamp=datetime.now()
     )
     error_embed.set_author(name=f'{bot.user.display_name.title()} - Error', icon_url='https://thumbs.dreamstime.com/b/warning-sign-line-icon-linear-style-mobile-concept-web-design-exclamation-mark-outline-vector-alert-danger-hazard-163698246.jpg')
    
    
     # Extract traceback information
     traceback_info = traceback.format_exception(type(e), e, e.__traceback__)
     traceback_str = ''.join(traceback_info)
    
     # Add traceback information to the embed
     error_embed.add_field(
        name="Traceback",
        value=f'```{traceback_str}```',
        inline=False
     )
    
     # Get the last traceback frame from the exception
     tb_frame = traceback.extract_tb(e.__traceback__)[-1]
     file_location = tb_frame.filename  # File location
     line_number = tb_frame.lineno  # Line number

     error_embed.add_field(
        name=" ",
        value=f":warning: **Potential issue found:**\n- **File:** `{file_location}`\n- **Line:** `{line_number}`",
        inline=False
     )
     error_embed.set_footer(icon_url=bot.user.avatar, text='Error Found')

     # Send the error embed to the channel
     await ctx.send(embed=error_embed)

    @bot.command(name='leave')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def leave(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.stop()
                await ctx.voice_client.disconnect()

                await ctx.send(embed=playback_stopped_left)
            else:

                await ctx.send(embed=need_same_channel_to_stop)
        else:

            await ctx.send(embed=not_in_voice)


    @bot.command(name='stop')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.stop()

                await ctx.send(embed=playback_stopped)
            else:

                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='pause')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.pause()

                await ctx.send(embed=playback_paused)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='resume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.resume()

                await ctx.send(embed=playback_resumed)
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)


    @bot.command(name='volume')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def volume(ctx, volume_str: str):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                try:
                    # Convert the volume from a percentage to a float (0.0 to 1.0)
                    volume_percentage = int(volume_str)
                    volume = volume_percentage / 100.0
                    # Set the volume; ensure it's within the valid range (0.0 to 1.0)
                    # if 0.0 <= volume <= 1.0:
                    ctx.voice_client.source.volume = volume
                    await ctx.send(embed=discord.Embed(description=f"**Volume has been successfully set to {volume_percentage}%**", color=0x99ccff))
                    # else:
                    #     await ctx.send(embed=discord.Embed(description="**Please provide an integer between 0 and 100 for the volume.**"))
                except ValueError:
                    await ctx.send(embed=discord.Embed(description="**Please provide a valid integer to set the volume.**\n\nExample:\n```ai.volume 70```", color=0x99ccff))
            else:
                await ctx.send(embed=need_same_channel_to_stop)
        else:
            await ctx.send(embed=not_in_voice)