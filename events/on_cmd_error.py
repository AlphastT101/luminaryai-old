import discord
from discord.ext import commands
import inspect

error_log_channel_id = 1191754729592717383


def on_cmd_error(bot):
    @bot.event
    async def on_command_error(ctx, error):
        # Check if the error is CommandNotFound
        if isinstance(error, commands.CommandNotFound):
            return  # Return without sending an error message
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f'This command is on cooldown, you can use it in {round(error.retry_after, 2)}s')
            return  # Return without sending an error message

        if isinstance(error, commands.MissingPermissions):
            await ctx.send(embed=discord.Embed(title="You do not have the necessary permissions to perform this action"))
            return # Return without sending an error message
        command_name = ctx.command.name if ctx.command else "Unknown"
        
        # Handle other errors with enhanced information
        try:
            raise error  # Raise the error to capture details
        
        # Member not found
        except discord.ext.commands.errors.MemberNotFound:
            await ctx.send(embed=discord.Embed(title="Member not found", colour=0xc8dc6c), delete_after=10)
        except Exception as e:
                
            # Get the line number where the exception occurred
            line_number = inspect.currentframe().f_back.f_lineno

            # Log the error to a designated channel
            await ctx.bot.get_channel(error_log_channel_id).send(embed=discord.Embed(title="Ouch! Error!", description=f"`{ctx.author} used '{command_name}' command in {ctx.guild.name} at line {line_number}!`\n\n**Error:** ```bash\n{e}```"))

            # Send a user-friendly error message
            error_embed = discord.Embed(
                title="LuminaryAI - Error!",
                description=f"An error occurred while executing the '{command_name}' command. Please try again a few moments later.",
                color=0xFF0000
            )
            
            await ctx.send(embed=error_embed)