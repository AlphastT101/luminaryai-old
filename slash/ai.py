import discord
from discord import app_commands
from discord.ext import commands
from bot_utilities.ai_utils import vision, sdxl
from data import blacklisted_servers, blacklisted_users
import datetime

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
    @bot.tree.command(name="vision", description="Vision an image")
    async def vision_command(interaction: discord.Interaction, message: str, image_link: str):
        if interaction.guild.id in blacklisted_servers or interaction.user.id in blacklisted_users:
            return
        
        await interaction.response.defer(ephemeral=False)
        response = await vision(message, image_link)

        response_embed = discord.Embed(
            title="LuminaryAI - vision",
            description=response,
            color=discord.Color.green() if response != "Ouch! Something went wrong!" else discord.Color.red()
        )

        response_embed.set_footer(text="Reply from LuminaryAI Image Vision. LuminaryAI does not guarantee the accuracy of the response provided. The Vision model is currently in **beta**")
        await interaction.followup.send(embed=response_embed)


    @commands.guild_only()
    @bot.tree.command(name="imagine", description="Imagine an image using LuminaryAI")
    async def imagine_pla(interaction: discord.Interaction, prompt: str):

        if interaction.guild.id in blacklisted_servers or interaction.user.id in blacklisted_users:
            return
        
        await interaction.response.defer(ephemeral=False)

        try:
            image_url = await sdxl(prompt) 

            embed_final = discord.Embed(
                title="LuminaryAI - Image Generation",
                description=f"Requested by: `{interaction.user}`\nPrompt: `{prompt}`",
                color=0x99ccff,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed_final.set_footer(text="LuminaryAI encourages positive interactions. It disclaims responsibility for content generated based on user inputs.")
            embed_final.set_image(url=image_url)
            embed_final.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
            
            # Send the embed
            await interaction.followup.send(embed=embed_final)

        except:
            error_embed = discord.Embed(
                title="Luminary - image generation",
                description="ERROR: \n\nThis error occurs when the user's request contains inappropriate content, leading to restricted access. Please ensure your input adheres to community guidelines to avoid this issue.",
                color=0xFF0000,
                timestamp=datetime.datetime.now(datetime.timezone.utc)
            )
            embed_final.set_footer(text="Thanks for using LuminaryAI!", icon_url=bot.user.avatar.url)
            await interaction.followup.send(embed=error_embed)