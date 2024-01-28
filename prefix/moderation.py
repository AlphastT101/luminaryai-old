import discord
from discord.ext import commands




def moderation(bot):
    @bot.command(name='purge', help='Deletes a specified number of messages')
    async def purge(ctx, num_messages: str = None):
        channel = ctx.channel
        if ctx.author.guild_permissions.manage_messages:
            if channel.permissions_for(channel.guild.me).manage_messages:
                try:
                    num_messages_int = int(num_messages)  # Convert the string to an integer
                    if num_messages_int < 1:
                        await ctx.send(f"**How can i delete {num_messages_int} messages?**", delete_after=3)
                        return
                    if num_messages_int == 1:
                        await ctx.send("**If you want to delete just one message, then please do this manually.**", delete_after=3)
                        return
                    else:
                        await ctx.channel.purge(limit=num_messages_int + 1)  # +1 to include the command message
                        await ctx.send(f"**Successfully purged {num_messages_int} messages**", delete_after=3)
                        return
                except ValueError:
                    await ctx.send("**Invalid input. Please provide a valid number of messages.**", delete_after=3)
                    return
            else:
                await ctx.send("**I don't have the necessary permission in this channel to perform this action!**", delete_after=3)
                return
        else:
            await ctx.send("**You do not have the necessary permissions to perform this action!**", delete_after=3)
            return