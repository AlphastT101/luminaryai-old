import discord
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
        

        if message.content.startswith(tuple(cmd_list)):
            if not await check_blist(message, mongodb):
                await bot.process_commands(message)





        elif await getdb("ai-channels",server_id, mongodb) == "found":


            if await check_blist(message, mongodb):
                return

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