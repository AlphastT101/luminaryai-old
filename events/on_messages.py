import discord
from data import server_data_ai, ai_channels
from bot_utilities.ai_utils import generate_response_msg, sdxl
import datetime
import json
from bot_utilities.owner_utils import *

def on_messages(bot, cmd_list , member_histories_msg, mongodb):
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
        elif message.content.startswith("hello im LuminaryAI. to start chatting, just tag me") and message.author == bot.user:
            await message.delete()
        elif message.content.startswith("uhh my head hurts") and message.author == bot.user:
            await message.delete()
        

        if message.author == bot.user or message.author.bot:
            return
        
        is_blist_server = await getdb('blist-servers', message.guild.id, mongodb)
        is_blist_user = await getdb('blist-users', message.author.id, mongodb)
        if message.content.startswith(tuple(cmd_list)) and is_blist_server == "not blacklisted" and is_blist_user == "not blacklisted":
            await bot.process_commands(message)
            return



        elif server_data_ai.get(server_id, {}).get('response_enabled', False) and server_id in ai_channels and message.channel.id == ai_channels.get(server_id, 0):

            is_blist_server = await getdb('blist-servers', message.guild.id, mongodb)
            is_blist_user = await getdb('blist-users', message.author.id, mongodb)
            if is_blist_server == "not blacklisted" and is_blist_user == "not blacklisted":

                member_id = str(message.author.id)
                history = member_histories_msg.get(member_id, [])

                answer_embed = discord.Embed(
                    title="LuminaryAI - Loading",
                    description="Please wait while I process your request.",
                    color=0x99ccff,
                    timestamp=datetime.datetime.now(datetime.timezone.utc)
                )
                answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
                answer = await message.reply(embed=answer_embed)

                user_input = message.content
                generated_message, updated_history = await generate_response_msg(message, user_input, history)
                member_histories_msg[member_id] = updated_history


                try:
                    dicto = json.loads(generated_message)

                    answer_generated = discord.Embed(
                        title="LuminaryAI - Response",
                        description=dicto["answer"],
                        color=0x99ccff,
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    answer_generated.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)

                    if dicto["image_gen"] == "False":
                        await answer.edit(embed=answer_generated)

                    elif dicto["image_gen"] == "True":
                        image_url = await sdxl(dicto["image_gen_prompt"])
                        answer_generated.set_image(url=image_url)
                        await answer.edit(embed=answer_generated)

                except json.decoder.JSONDecodeError:
                    error_embed = discord.Embed(
                        title="LuminaryAI - Reponse",
                        description=generated_message,
                        color=0x99ccff,
                        timestamp=datetime.datetime.now(datetime.timezone.utc)
                    )
                    error_embed.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
                    await answer.edit(embed=error_embed)




        elif not any(message.content.startswith(prefix) for prefix in bot.command_prefix):
            return