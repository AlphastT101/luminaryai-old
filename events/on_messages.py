import discord
from data import server_data_ai, ai_channels
from bot_utilities.ai_utils import generate_response_msg


def on_messages(bot, cmd_list ,blacklisted_users, member_histories_msg, blacklisted_servers):
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
            if message.guild.id not in blacklisted_servers:
                await message.channel.send("**Please use ai.help or /help!**")
            else:
                return
        elif message.content.startswith("hello im LuminaryAI. to start chatting, just tag me") and message.author == bot.user:
            await message.delete()
        elif message.content.startswith("uhh my head hurts") and message.author == bot.user:
            await message.delete()
            if message.guild.id not in blacklisted_servers:
                await message.channel.send("**Wacked successfully!**")
            else:
                return
        

        if message.author == bot.user or message.author.bot:
            return
        if message.content.startswith(tuple(cmd_list)) and message.guild.id not in blacklisted_servers and message.author.id not in blacklisted_users:
            await bot.process_commands(message)
            return



        elif server_data_ai.get(server_id, {}).get('response_enabled', False) and server_id in ai_channels and message.channel.id == ai_channels.get(server_id, 0):

            member_id = str(message.author.id)  # Using member ID as the key
            history = member_histories_msg.get(member_id, [])

            answer_embed = discord.Embed(
                title="LuminaryAI - answer generation",
                description="Generating answer...",
                color=0x99ccff
            )
            answer = await message.reply(embed=answer_embed)


            user_input = message.content
            generated_message, updated_history = await generate_response_msg(message, user_input, history)

            # Update member-specific history
            member_histories_msg[member_id] = updated_history

            answer_generated = discord.Embed(
                title="LumianryAI - answer generation",
                description=generated_message,
                color=0x99ccff
            )
            await answer.edit(embed=answer_generated)


        elif not any(message.content.startswith(prefix) for prefix in bot.command_prefix):
            return  # Message doesn't start with any command prefix, and AI responses are disabled