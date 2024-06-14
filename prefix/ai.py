import discord
from discord import Embed
from discord.ext import commands
import io
import random
from bot_utilities.ai_utils import *
import aiohttp
import datetime
import json
from bot_utilities.owner_utils import *

async def embed(ctx ,title, description, color):
    embed = discord.Embed(title=title, description=description, color=color)
    await ctx.send(embed=embed)








def ai(bot, member_histories_msg, mongodb):

    ############## ai ##############
    @bot.command(name='activate')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def start(ctx):
        server_id = ctx.guild.id

        if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
            insert_result = await insertdb("ai-channels",server_id, mongodb)
            if insert_result == "success":
                await ctx.send(embed=Embed(description="Success, now I'll respond to **all messages** in this channel.", color=discord.Colour.green()))
            elif insert_result == "already set":
                await ctx.send(embed=Embed(description=":x: **Error**, this channel is already activated.", colour=discord.Colour.red()))
        else:
            await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)


    @bot.command(name='deactivate')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def stop(ctx):

        server_id = ctx.guild.id

        if ctx.author.guild_permissions.administrator or ctx.author.id == 1026388699203772477:
            delete_result = await deletedb("ai-channels", server_id, mongodb)

            if delete_result == "success":
                await ctx.send(embed=Embed(description="**Successfully disabled this channel.**", color=discord.Color.green()),)
            elif delete_result == "not found":
                await ctx.send(embed=Embed(description=":x: **Error**, this channel isn't activated.", colour=discord.Colour.red()))
        else:
            await ctx.send(embed=Embed(description="**You don't have permission to use this comamnd.**", color=discord.Color.red()),)







    @bot.command(name='response')
    @commands.cooldown(1, 80, commands.BucketType.user)
    async def answer_command(ctx, *, args: str = None):
        if args is None:
            await embed(ctx, "LuminaryAI - Error", "Please enter your question.", color=0x99ccff)
            return
        # Get or create member-specific history
        member_id = str(ctx.author.id)  # Using member ID as the key
        history = member_histories_msg.get(member_id, [])

        answer_embed = discord.Embed(
            title="LuminaryAI - Loading",
            description="Plese wait while i process your request.",
            color=0x99ccff,
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        answer_embed.set_footer(text="This may take a few moments", icon_url=bot.user.avatar.url)
        answer = await ctx.reply(embed=answer_embed)

        user_input = args
        generated_message, updated_history = await generate_response_cmd(ctx, user_input, history)
        member_histories_msg[member_id] = updated_history
        print(generated_message)

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
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def search(ctx, *, query: str = None):
        if query is None:
            await embed(ctx, "LuminaryAI - Web search", "Please enter your prompt", color=0x99ccff)
            return

        wait = discord.Embed(
            title="LuminaryAI - loading",
            description="Please wait while i process your request.",
            timestamp=ctx.message.created_at,
            color=0x99ccff,
        )
        wait.set_footer(text=f"Thanks for using {bot.user}!", icon_url=bot.user.avatar.url)
        file_web_search = discord.File('images/web_search.png', filename='web_search.png')
        wait.set_thumbnail(url='attachment://web_search.png')
        wait = await ctx.send(embed=wait, file=file_web_search)
        result = web_search(query)
        if result == "":
            result = "No results found"

        image_urls = search_image(query)
        if not image_urls:
            await ctx.send("No results found")
            return

        file_path = create_composite_image(image_urls)
        web_embed = discord.Embed(
            title=f"Luminary - Web Search",
            description=f"{result}",
            color=0x99ccff,
            timestamp=ctx.message.created_at
        )

        file_composite = discord.File(file_path, filename="composite_image.png")
        file_web_search = discord.File('images/web_search.png', filename='web_search.png')

        web_embed.set_thumbnail(url='attachment://web_search.png')
        web_embed.set_image(url="attachment://composite_image.png")
        web_embed.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)

        await wait.delete()
        await ctx.reply(embed=web_embed, files=[file_composite, file_web_search])

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