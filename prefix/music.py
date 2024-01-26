import yt_dlp as youtube_dl
from discord.ext import commands
import discord
import pyshorteners
import asyncio


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
    description="Join a voice channel first",
    color=0x99ccff
)
join_first_embed.set_thumbnail(url="attachment://thumbnail.png")

already_joined = discord.Embed(
    title="LumianryAI - music",
    description="Bot is already connected to a voice channel. use `ai.leave` to leave.",
    color=0x99ccff
)
already_joined.set_thumbnail(url="attachment://thumbnail.png")


pls_wait_embed = discord.Embed(
    title="LumianryAI - music",
    description="Please wait...",
    color=0x99ccff
)
pls_wait_embed.set_thumbnail(url="attachment://thumbnail.png")

no_result_embed = discord.Embed(
    title="LumianryAI - music",
    description="No results found",
    color=0x99ccff
)
no_result_embed.set_thumbnail(url="attachment://thumbnail.png")


not_in_voice = discord.Embed(
    title="LumianryAI - music",
    description="I am not currently in a voice channel.",
    color=0x99ccff
)
not_in_voice.set_thumbnail(url="attachment://thumbnail.png")

playback_stopped = discord.Embed(
    title="LumianryAI - music",
    description="Playback stopped, and I left the voice channel.",
    color=0x99ccff
)
playback_stopped.set_thumbnail(url="attachment://thumbnail.png")

need_same_channel_to_stop = discord.Embed(
    title="LumianryAI - music",
    description="You need to be in the same voice channel as me to stop playback and disconnect.",
    color=0x99ccff
)
need_same_channel_to_stop.set_thumbnail(url="attachment://thumbnail.png")



loop_enabled = discord.Embed(
    title="LumianryAI - music",
    description="Loop enabled",
    color=0x99ccff
)
loop_enabled.set_thumbnail(url="attachment://thumbnail.png")

loop_disabled = discord.Embed(
    title="LumianryAI - music",
    description="Loop disabled",
    color=0x99ccff
)
loop_disabled.set_thumbnail(url="attachment://thumbnail.png")


alread_playing = discord.Embed(
    title="LumianryAI - music",
    description="Already playing!\n\n looking for the queue system?\n help us by joining our support server.",
    color=0x99ccff
)
alread_playing.set_thumbnail(url="attachment://thumbnail.png")
def music(bot):
    @bot.command(name='join')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def join(ctx):
        if ctx.author.voice is None:
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=join_first_embed, file=file)
            return

        # Get the bot's Member object
        bot_member = ctx.guild.get_member(bot.user.id)

        if ctx.voice_client is not None and ctx.voice_client.is_connected():
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=already_joined, file=file)
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
                title="LumianryAI - music",
                description=f"\n\nJoined {channel}",
                color=0x99ccff
            )
            file = discord.File("music.png", filename="thumbnail.png")
            joined_embed.set_thumbnail(url="attachment://thumbnail.png")
            await ctx.send(embed=joined_embed, file=file)




    server_loops = {}  # Dictionary to store loop status for each server

    @bot.command(name='loop')
    async def toggle_loop(ctx):
        server_id = ctx.guild.id
        if server_id not in server_loops:
            server_loops[server_id] = True  # Initialize loop status for the server if not present
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=loop_enabled, file=file)
        elif server_loops[server_id] == True:
            server_loops[server_id] = False
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=loop_disabled,file=file)
        elif server_loops[server_id] == False:
            server_loops[server_id] = True
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=loop_enabled, file=file)

    @bot.command(name='play')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play(ctx, *, song_name):
        server_id = ctx.guild.id
        if server_id not in server_loops:
            server_loops[server_id] = False


        file = discord.File("music.png", filename="thumbnail.png")
        wait = await ctx.send(embed=pls_wait_embed, file=file)

        if ctx.author.voice is None or ctx.author.voice.channel is None:
            await wait.edit(embed=join_first_embed)
            return

        channel = ctx.author.voice.channel
        voice_channel = ctx.voice_client

        # Check if the bot is already in a voice channel
        if voice_channel is None and channel is not None:
            await wait.edit(embed=not_in_voice)
            return
        if not voice_channel.is_playing():
            # Download the song information using yt_dlp
            ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'no_warnings': True}
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
                if 'entries' in info and info['entries']:
                    # Get the first entry (song) in the search results
                    first_entry = info['entries'][0]

                    # Extract the song name and video link and duration
                    song_name = first_entry.get('title', 'Unknown Title')
                    video_link = first_entry.get('url', 'Unknown Link')
                    duration = first_entry.get('duration', 0)

                    # Shorten the video link
                    shortened_video_link = shorten_url(video_link)
                    # Format the duration in a user-friendly way
                    duration_formatted = str(round(duration / 60, 2)) + " minutes"

                    # Play the song
                    voice_channel.play(discord.FFmpegPCMAudio(video_link, **FFMPEG_OPTIONS))

                    playing_embed = discord.Embed(
                        title="LumianryAI - music",
                        description=f"Now playing: {song_name} \n\nAudio link: {shortened_video_link}\n\n Song duration: {duration_formatted}",
                        color=0x99ccff
                    )
                    file = discord.File("music.png", filename="thumbnail.png")
                    playing_embed.set_thumbnail(url="attachment://thumbnail.png")
                    await wait.edit(embed=playing_embed)
                    await asyncio.sleep(duration)  # Wait for the song to finish
                    loop = server_loops[server_id]  # Get loop status for the current server

                    while loop:
                        loop = server_loops[server_id]  # Get loop status for the current server
                        if loop:
                            voice_channel.stop()
                            voice_channel.play(discord.FFmpegPCMAudio(video_link, **FFMPEG_OPTIONS))
                            await asyncio.sleep(duration)  # Wait for the song to finish
                        elif loop == False and not voice_channel.is_playing():
                            voice_channel.stop()
                            break
                else:
                    await wait.edit(embed=no_result_embed)

        else:
            await wait.edit(embed=alread_playing)
    # queues = {}

    # @bot.command(name='play')
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # async def play(ctx, *, song_name):
    #     server_id = ctx.guild.id
    #     if server_id not in server_loops:
    #         server_loops[server_id] = False

    #     file = discord.File("music.png", filename="thumbnail.png")
    #     wait = await ctx.send(embed=pls_wait_embed, file=file)

    #     if ctx.author.voice is None or ctx.author.voice.channel is None:
    #         await wait.edit(embed=join_first_embed)
    #         return

    #     channel = ctx.author.voice.channel
    #     voice_channel = ctx.voice_client

    #     if voice_channel is None and channel is not None:
    #         await wait.edit(embed=not_in_voice)
    #         return

    #     if server_id not in queues:
    #         queues[server_id] = []

    #     # Download the song information using yt_dlp
    #     ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'no_warnings': True}
    #     with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #         info = ydl.extract_info(f"ytsearch:{song_name}", download=False)
    #         if 'entries' in info and info['entries']:
    #             first_entry = info['entries'][0]
    #             song_name = first_entry.get('title', 'Unknown Title')
    #             video_link = first_entry.get('url', 'Unknown Link')
    #             duration = first_entry.get('duration', 0)
    #             queues[server_id].append({'song_name': song_name, 'video_link': video_link, 'duration': duration})
    #             shortened_video_link = shorten_url(video_link)  # Implement your URL shortening logic
    #             duration_formatted = str(round(duration / 60, 2)) + " minutes"
    #             now_playing = discord.Embed(
    #                 title="Song added to queue",
    #                 description=f"Name: {song_name} \n\nAudio link: {shortened_video_link}\n\n Song duration: {duration_formatted}",
    #                 color=0x99ccff
    #             )
    #             now_playing.set_thumbnail(url="attachment://thumbnail.png")
    #             await wait.edit(embed=now_playing)

    #             # Check if the bot is connected to a voice channel and not playing
    #             if voice_channel and not voice_channel.is_playing() and not server_loops[server_id]:
    #                 await play_next_song(ctx)
    #         else:
    #             await wait.edit(embed=discord.Embed(title="LuminaryAI - music", description=f'No results found for: {song_name}', color=0xff0000))
    #             return

    # async def play_next_song(ctx):
    #     server_id = ctx.guild.id
    #     voice_channel = ctx.voice_client

    #     if server_id in queues and queues[server_id]:
    #         next_song = queues[server_id].pop(0)
    #         song_name = next_song['song_name']
    #         video_link = next_song['video_link']
    #         duration = next_song['duration']
    #         shortened_video_link = shorten_url(video_link)  # Implement your URL shortening logic
    #         duration_formatted = str(round(duration / 60, 2)) + " minutes"

    #         # Download the next song information using yt_dlp
    #         ydl_opts = {'format': 'bestaudio', 'noplaylist': True, 'no_warnings': True}
    #         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #             info = ydl.extract_info(video_link, download=False)
    #             if 'entries' in info and info['entries']:
    #                 next_song_info = info['entries'][0]
    #                 queues[server_id].append({'song_name': next_song_info.get('title', 'Unknown Title'),
    #                                         'video_link': video_link,
    #                                         'duration': next_song_info.get('duration', 0)})

    #                 # Define a callback function to play the next song
    #                 def play_next(e):
    #                     asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop)

    #                 # Play the next song and set the callback
    #                 voice_channel.play(discord.FFmpegPCMAudio(video_link, **FFMPEG_OPTIONS), after=play_next)
    #                 playing_embed = discord.Embed(
    #                     title="Now playing",
    #                     description=f"{song_name}\n\nAudio link: {shortened_video_link}\n\n Song duration: {duration_formatted}",
    #                     color=0x99ccff
    #                 )
    #                 file = discord.File("music.png", filename="thumbnail.png")
    #                 playing_embed.set_thumbnail(url="attachment://thumbnail.png")
    #                 await ctx.send(embed=playing_embed, file=file)
    #             else:
    #                 await ctx.send('Error: Unable to get information for the next song.')
    #     else:
    #         await ctx.send('Queue is empty.')


    @bot.command(name='leave')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):
        # Check if the bot is in a voice channel
        if ctx.voice_client is not None:
            # Check if the user is in the same voice channel as the bot
            if ctx.author.voice is not None and ctx.author.voice.channel == ctx.voice_client.channel:
                # Stop playing and disconnect from the voice channel
                ctx.voice_client.stop()
                await ctx.voice_client.disconnect()
                file = discord.File("music.png", filename="thumbnail.png")
                await ctx.send(embed=playback_stopped,file=file)
            else:
                file = discord.File("music.png", filename="thumbnail.png")
                await ctx.send(embed=need_same_channel_to_stop, file=file)
        else:
            file = discord.File("music.png", filename="thumbnail.png")
            await ctx.send(embed=not_in_voice, file=file)

