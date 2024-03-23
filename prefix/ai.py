import discord
from discord.ext import commands
import io
import random
from bot_utilities.ai_utils import generate_response_cmd, poly_image_gen, generate_image_prodia, sdxl, search_photo, web_search
import aiohttp
from data import ai_channels, server_data_ai
# from openai import AsyncOpenAI
# from dotenv import load_dotenv
# from bot_utilities.config_loader import load_current_language, config
# import os
# import requests
# from urllib.parse import quote


async def embed(ctx ,title, description, color):
    embed = discord.Embed(title=title, description=description, color=color)
    await ctx.send(embed=embed)






aiml_folder = "data"

# Dictionary to store server-specific data
# server_data_aiml = {}
# aiml_channels = {}





def ai(bot, member_histories_msg):

    ############## ai ##############
    # @bot.command(name='activate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def start(ctx):
    #     # Get or create server-specific data and set AI responses as false
    #     server_id = ctx.guild.id
    #     if server_id not in server_data_ai:
    #         server_data_ai[server_id] = {'response_enabled': False}

    #     # Check if the user is a moderator, administrator, or has a specific role
    #     if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:

    #         if ctx.channel.slowmode_delay >= 10:
    #             server_data_ai[server_id]['response_enabled'] = True #set ai to true
    #             ai_channels[server_id] = ctx.channel.id  # Store the channel ID
    #             await ctx.send(f'AI enabled. AI responses will be sent in <#{ctx.channel.id}>.')
    #         else:
    #             await ctx.send("Enable 10s slow mode first.")
    #     else:
    #         await ctx.send("You don't have permission to use this command.")
    # @bot.command(name='deactivate')
    # @commands.cooldown(1, 10, commands.BucketType.user)
    # async def stop(ctx):
    #     server_id = ctx.guild.id
    #     # Check if the user is a moderator, administrator, or has a specific role
    #     if any(role.permissions.manage_messages for role in ctx.author.roles) or ctx.author.id == 1026388699203772477:
    #         server_data_ai[server_id]['response_enabled'] = False
    #         await ctx.send("AI disabled.")
    #     else:
    #         await ctx.send("You don't have permission to use this command.")







    @bot.command(name='response')
    @commands.cooldown(1, 80, commands.BucketType.user)
    async def answer_command(ctx, *, args: str = None):
        if args is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your question.", color=0x99ccff)
            return
        # Get or create member-specific history
        member_id = str(ctx.author.id)  # Using member ID as the key
        history = member_histories_msg.get(member_id, [])

        answer_embed = discord.Embed(
            title="LuminaryAI - answer generation",
            description="Generating answer...",
            color=0x99ccff
        )
        answer = await ctx.reply(embed=answer_embed)

        user_input = args
        generated_message, updated_history = await generate_response_cmd(ctx, user_input, history)

        # Update member-specific history
        member_histories_msg[member_id] = updated_history

        answer_generated = discord.Embed(
            title="LumianryAI - answer generation",
            description=generated_message,
            color=0x99ccff
        )
        await answer.edit(embed=answer_generated)



    @bot.command(name='imagine')
    @commands.cooldown(1, 50, commands.BucketType.user)
    async def imagine_command(ctx, *, prompt: str = None):
        if prompt is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your prompt", color=0x99ccff)
            return
        embed_img_generation = discord.Embed(
            title="LuminaryAI image generation",
            description="Image generating...",
            color=0x99ccff
        )
        msg = await ctx.reply(embed=embed_img_generation)  # Add await here
        try:
            image_url = await sdxl(prompt) 
            # Create an embed with the image
            embed_final = discord.Embed(
                title="LuminaryAI - Image generation",
                description=f"Requested by: {ctx.author}\nPrompt: {prompt}",
                color=0x99ccff
            )
            embed_final.set_footer(text="LuminaryAI encourages positive interactions. It disclaims responsibility for content generated based on user inputs.")
            embed_final.set_image(url=image_url)
            
            # Send the embed
            await msg.edit(embed=embed_final)

        except:
            error_embed = discord.Embed(
                title="Luminary - image generation",
                description="ERROR: 403\n\nThis error occurs when the user's request contains inappropriate content, leading to restricted access. Please ensure your input adheres to community guidelines to avoid this issue.",
                color=0xFF0000
            )
            await msg.edit(embed=error_embed)


    @bot.command(name="search")
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def search(ctx,*, query: str = None):
        if query is None:
            await embed(ctx, "LuminaryAI - answer generation", "Please enter your prompt", color=0x99ccff)
            return
        result = web_search(query)
        if result == "":
            result = "No results found"
        web_embed = discord.Embed(
            title="Luminary - web search",
            description=result,
            color=0x99ccff
        )
        file = discord.File("web_search.png", filename="web_search.png")
        web_embed.set_thumbnail(url="attachment://web_search.png")
        web_embed.set_footer(text="LumianryAI")
        await ctx.reply(embed=web_embed, file=file)

    @bot.command(name='imagine.p')
    @commands.cooldown(1, 40, commands.BucketType.user)
    async def imagine_m2_command(ctx, *, prompt: str = None):
        if prompt is None:
            await ctx.reply("**Please enter your prompt!**", delete_after=3)
            return
        generating = discord.Embed(
            title="LuminaryAI - Image generation",
            description=f"Generating image...",
            color=0x99ccff
        )
        delete_msg = await ctx.send(embed=generating)
        async with aiohttp.ClientSession() as session:
            try:
                send_embed = discord.Embed(
                    title="LuminaryAI - Image generation",
                    description=f"Requested by: {ctx.author}\nPrompt: {prompt}",
                    color=0x99ccff
                )
                image = await poly_image_gen(session, prompt)
                file=discord.File(image, 'generated_image.png')
                send_embed.set_image(url=f'attachment://generated_image.png')
                await delete_msg.delete()
                await ctx.reply(embed=send_embed, file=file)
            except Exception as e:
                print(f"An error occurred: {e}")
                await ctx.reply("An error occurred while generating the image. Please try again.")


    @bot.command(name='prodia')
    @commands.cooldown(1, 40, commands.BucketType.user)
    async def prodia_command(ctx,*,prompt: str = None):
        if prompt is None:
            await ctx.reply("**Invalid command!**", delete_after=3)
            return
        embed_prodia = discord.Embed(
            title="LuminaryAI - Image generation using prodia",
            description="Generating image...",
            color=0x99ccff
        )
        msg = await ctx.reply(embed=embed_prodia)
        try:
            models = [
                "Realistic_Vision_V2.0.safetensors [79587710]",
                "portrait+1.0.safetensors [1400e684]",
                "revAnimated_v122.safetensors [3f4fefd9]",
                "analog-diffusion-1.0.ckpt [9ca13f02]",
                "AOM3A3_orangemixs.safetensors [9600da17]",
                "dreamlike-diffusion-1.0.safetensors [5c9fd6e0]",
                "dreamlike-diffusion-2.0.safetensors [fdcf65e7]",
                "dreamshaper_5BakedVae.safetensors [a3fbf318]",
                "mechamix_v10.safetensors [ee685731]",
                "meinamix_meinaV9.safetensors [2ec66ab0]",
                "sdv1_4.ckpt [7460a6fa]",
                "v1-5-pruned-emaonly.ckpt [81761151]",
                "shoninsBeautiful_v10.safetensors [25d8c546]",
                "theallys-mix-ii-churned.safetensors [5d9225a4]",
                "timeless-1.0.ckpt [7c4971d4]",
                "elldreths-vivid-mix.safetensors [342d9d26]",
                "openjourney_V4.ckpt [ca2f377f]",
                "deliberate_v2.safetensors [10ec4b29]",
                "dreamshaper_6BakedVae.safetensors [114c8abb]",
                "lyriel_v16.safetensors [68fceea2]",
                "anything-v4.5-pruned.ckpt [65745d25]",
                "openjourney_V4.ckpt [ca2f377f]",
            ]
            model = random.choice(models)
            seed = random.randint(10000, 99999)
            sampler = "Euler"
            img_file_obj = await generate_image_prodia(prompt, model, sampler, seed, None)
            prodia_final = discord.Embed(
                title="LuminaryAI - Image generation using prodia",
                color=0x99ccff,
                description=f"Model: {model}\n Seed: {seed}\n Model and seed is randomly selected. Please use slash command `/imagine` to customize."
            )
            prodia_final.set_footer(text="LuminaryAI encourages positive interactions. It disclaims responsibility for content generated based on user inputs.")

            # Attach the image directly to the embed
            file=discord.File(img_file_obj, 'generated_image.png')
            prodia_final.set_image(url=f'attachment://generated_image.png')

            # Send the embed with the attached image
            await msg.delete()
            await ctx.send(embed=prodia_final, file=file)

        except Exception as e:
            print(e)
            error_embed = discord.Embed(
                title="Luminary - prodia Image generation",
                description="ERROR: 403\n\nThis error can occurs when the user's request contains inappropriate content, leading to restricted access. Please ensure your input adheres to community guidelines to avoid this issue.",
                color=0xFF0000
            )
            await msg.edit(embed=error_embed)


    @bot.command(name='searchimg')
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def searchimg(ctx,* , query):
        a = search_photo(query)
        if a == "Bad":
            bad_embd = discord.Embed(
                title="LuminaryAI - Image search",
                description=f"Requested by: {ctx.author}\nPrompt: {query}\n\n ⚠️ Can't search for image.",
                color="0xFF0000"
            )
            file = discord.File("web_search.png", filename="web_search.png")
            bad_embd.set_thumbnail(url="attachment://web_search.png")
            await ctx.send(bad_embd, file=file)
        else:
            embed = discord.Embed(
                title="LuminaryAI - Image search",
                description=f'Requested by: {ctx.author}\nPrompt: {query}',
                color=0x99ccff,
            )
            embed.set_image(url=a)
            await ctx.send(embed=embed)