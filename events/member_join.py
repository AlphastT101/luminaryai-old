import discord
from discord.ext import commands
from data import blacklisted_users

def member_join(bot):
    @bot.event
    async def on_member_join(member):
        if member.id in blacklisted_users:
            role = member.guild.get_role(1221422849684672532)
            await member.add_roles(role)
            return

        if member.guild.id != 1144903052717985806:
            return

        channel = member.guild.get_channel(1144914850280116254)
        embed = discord.Embed(title=f"Welcome, {member.display_name}! We're glad to have you here.", color=discord.Color.green())
        await channel.send(embed=embed)
        role = member.guild.get_role(1154607279975448636)
        await member.add_roles(role)