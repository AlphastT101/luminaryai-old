import discord
from discord import app_commands
from discord.ext import commands
from bot_utilities.ai_utils import generate_response, generate_image_prodia, search, poly_image_gen, generate_gpt4_response, dall_e_gen, sdxl
import random
from model_enum import Model
import asyncio
blacklisted_words = [
    "naked",
    "porn",
    "sexy",
    "anal",
    "boobs",
    "boob",
    "dick",
    "boobjob",
    "without clothes",
    "no clothes",
    "blowjob",
    "nsfw",
    "age restricted",
    "pornography",
    "girl without underwear",
]

def ai_slash(bot):
    @commands.guild_only()
    @bot.tree.command(name="imagine", description="Generate an image")
    @app_commands.choices(sampler=[
        app_commands.Choice(name='📏 Euler (Recommended)', value='Euler'),
        app_commands.Choice(name='📏 Euler a', value='Euler a'),
        app_commands.Choice(name='📐 Heun', value='Heun'),
        app_commands.Choice(name='💥 DPM++ 2M Karras', value='DPM++ 2M Karras'),
        app_commands.Choice(name='🔍 DDIM', value='DDIM')
    ])
    @app_commands.choices(model=[
        app_commands.Choice(name='🌌 Elldreth vivid mix', value='ELLDRETHVIVIDMIX'),
        app_commands.Choice(name='🌌 Deliberate v2', value='DELIBERATE'),
        app_commands.Choice(name='🌌 Dreamshaper', value='DREAMSHAPER_6'),
        app_commands.Choice(name='🌌 Lyriel', value='LYRIEL_V16'),
        app_commands.Choice(name='🌌 Anything diffusion', value='ANYTHING_V4'),
        app_commands.Choice(name='🌌 Openjourney (Midjourney alternative)', value='OPENJOURNEY'),
        app_commands.Choice(name='🌌 Realistic', value='REALISTICVS_V20'),
        app_commands.Choice(name='🌌 Portrait', value='PORTRAIT'),
        app_commands.Choice(name='🌌 Rev animated', value='REV_ANIMATED'),
        app_commands.Choice(name='🌌 Analog', value='ANALOG'),
        app_commands.Choice(name='🌌 AbyssOrangeMix', value='ABYSSORANGEMIX'),
        app_commands.Choice(name='🌌 Dreamlike v1', value='DREAMLIKE_V1'),
        app_commands.Choice(name='🌌 Dreamlike v2', value='DREAMLIKE_V2'),
        app_commands.Choice(name='🌌 Dreamshaper 5', value='DREAMSHAPER_5'),
        app_commands.Choice(name='🌌 MechaMix', value='MECHAMIX'),
        app_commands.Choice(name='🌌 MeinaMix', value='MEINAMIX'),
        app_commands.Choice(name='🌌 Stable Diffusion v14', value='SD_V14'),
        app_commands.Choice(name='🌌 Stable Diffusion v15', value='SD_V15'),
        app_commands.Choice(name="🌌 Shonin's Beautiful People", value='SBP'),
        app_commands.Choice(name="🌌 TheAlly's Mix II", value='THEALLYSMIX'),
        app_commands.Choice(name='🌌 Timeless', value='TIMELESS')
    ])
    @app_commands.describe(
        prompt="Prompt for the image to generate",
        model="Model to generate image",
        sampler="Sampler for denosing",
    )
    @commands.guild_only()
    async def imagine(interaction:discord.Interaction, prompt: str, model: app_commands.Choice[str], sampler: app_commands.Choice[str], seed: int = None):
        for word in prompt.split():
            is_nsfw = word in blacklisted_words
        if is_nsfw:
            await interaction.response.send_message(f"⚠️ Can't generate image", delete_after=5)
            return

        if seed is None:
            seed = random.randint(10000, 99999)
        # await ctx.response.defer()
        await interaction.response.defer(ephemeral=False)
        model_uid = Model[model.value].value[0]

        imagefileobj = await generate_image_prodia(prompt, model_uid, sampler.value, seed)

        img_file = discord.File(imagefileobj, filename="image.png", description=prompt)
        embed = discord.Embed(color=discord.Color.random())
        embed.title = f"Generated Image by LuminaryAI"
        embed.add_field(name='Prompt', value=f'- {prompt}', inline=False)
        embed.add_field(name='Model', value=f'- {model.value}', inline=False)
        embed.add_field(name='Sampler', value=f'- {sampler.value}', inline=False)
        embed.add_field(name='Seed', value=f'- {seed}', inline=False)
    
        sent_message = await interaction.followup.send(embed=embed, file=img_file)