import discord
from discord.ext import commands
import asyncio
from datetime import timedelta, datetime
import re



def parse_duration(duration_str):
    match = re.match(r"(\d+)([dhm])", duration_str)
    if not match:
        return None
    duration, unit = match.groups()
    duration = int(duration)
    if unit == 'd':
        return timedelta(days=duration)
    elif unit == 'h':
        return timedelta(hours=duration)
    elif unit == 'm':
        return timedelta(minutes=duration)



def moderation(bot):
    @bot.command(name='purge', help='Deletes a specified number of messages')
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def purge(ctx, num_messages: str = None):
        channel = ctx.channel
        if num_messages is None:
            await ctx.send("**Please provide a number of messages to purge!**")
            return
        if ctx.author.guild_permissions.manage_messages:
            if channel.permissions_for(channel.guild.me).manage_messages:
                try:
                    num_messages_int = int(num_messages)  # Convert the string to an integer
                    if num_messages_int < 1:
                        await ctx.send(f"**How can i delete {num_messages_int} messages?**", delete_after=3)
                    if num_messages_int == 1:
                        await ctx.send("**If you want to delete just one message, then please do this manually.**", delete_after=3)
                    else:
                        await ctx.channel.purge(limit=num_messages_int + 1)  # +1 to include the command message
                        await ctx.send(embed=discord.Embed(title=f"**Successfully purged {num_messages_int} messages**"), delete_after=3)
                except ValueError:
                    await ctx.send("**Invalid input. Please provide a valid number of messages.**", delete_after=3)
            else:
                await ctx.send("**I don't have the necessary permission in this channel to perform this action!**", delete_after=3)
        else:
            await ctx.send("**You do not have the necessary permissions to perform this action!**", delete_after=3)
        


    @bot.command(name='kick')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            await ctx.send(embed=discord.Embed(title="Please provide a valid Discord member to kick.",colour=0xc8dc6c), delete_after=10)
            return

        # Protect the bot from kicking itself or the server owner
        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(title="I cannot kick the server owner.",colour=0xc8dc6c), delete_after=10)
            return
        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(title="I can't kick myself!",colour=0xc8dc6c), delete_after=10)
            return
        
        # Check if the command caller has the required permission
        if not ctx.author.guild_permissions.kick_members:
            await ctx.send(embed=discord.Embed(title="You do not have the necessary permissions to perform this action.",colour=0xc8dc6c), delete_after=10)
            return

        # Check if the bot itself has the permission to kick members
        if not ctx.guild.me.guild_permissions.kick_members:
            await ctx.send(embed=discord.Embed(title="I don't have the necessary permission in this channel to perform this action!",colour=0xc8dc6c), delete_after=10)
            return


            
        try:
            # Send a confirmation message to the moderator
            confirm_msg = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description="Are you sure you want to kick this member?\nMember: `{member}`\nReason: `{reason}`",colour=0xc8dc6c))
            # Add reactions for confirmation
            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            # Check for the moderator's reaction
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.kick(reason=reason)
                await confirm_msg.delete()


                await ctx.send(embed=discord.Embed(title=f"Member {member} has been kicked.\nReason: {reason}",colour=0xc8dc6c), delete_after=10)
            else:
                await confirm_msg.delete()
                await ctx.send(embed=discord.Embed(title=f"Action cancelled.", description="`{member}` has not been kicked.",colour=0xc8dc6c), delete_after=10)

        except asyncio.TimeoutError:
            await confirm_msg.delete()
            await ctx.send(embed=discord.Embed(title="No reaction received. Kick action cancelled."), delete_after=10)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(title="Kick failed. I don't have enough permissions to kick this user.",colour=0xc8dc6c), delete_after=10)







    @bot.command(name='ban')
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def kick(ctx, member: discord.Member = None, *, reason: str = "No reason provided"):
        if member is None:
            await ctx.send(embed=discord.Embed(title="Please provide a valid Discord member to ban.",colour=0xc8dc6c), delete_after=10)
            return

        # Protect the bot from kicking itself or the server owner
        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(title="I cannot ban the server owner.",colour=0xc8dc6c), delete_after=10)
            return
        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(title="I can't ban myself!",colour=0xc8dc6c), delete_after=10)
            return
        
        # Check if the command caller has the required permission
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(title="You do not have the necessary permissions to perform this action.",colour=0xc8dc6c), delete_after=10)
            return

        # Check if the bot itself has the permission to kick members
        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(title="I don't have the necessary permission in this channel to perform this action!",colour=0xc8dc6c), delete_after=10)
            return


            
        try:
            # Send a confirmation message to the moderator
            confirm_msg = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"Are you sure you want to ban this member?\nMember: `{member}`\nReason: `{reason}`",colour=0xc8dc6c))
            # Add reactions for confirmation
            await confirm_msg.add_reaction('✅')
            await confirm_msg.add_reaction('❌')

            # Check for the moderator's reaction
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌']

            reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            
            if str(reaction.emoji) == '✅':
                await member.ban(reason=reason)


                await confirm_msg.edit(embed=discord.Embed(title=f"Member {member} has been banned.\nReason: {reason}",colour=0xc8dc6c), delete_after=10)
            else:
                await confirm_msg.edit(embed=discord.Embed(title=f"Action cancelled.", description="`{member}` has not been banned.",colour=0xc8dc6c), delete_after=10)

        except asyncio.TimeoutError:
            await confirm_msg.edit(embed=discord.Embed(title="No reaction received. ban action cancelled.", color=0x99ccff), delete_after=10)
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(title="Kick failed. I don't have enough permissions to ban this user.",colour=0xc8dc6c), delete_after=10)



    @bot.command(name='unban', help='Unban a previously banned user.')
    async def unban(ctx, user: discord.User, *, reason="No reason provided"):

        # Check if the command caller has the required permission
        if not ctx.author.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(title="You do not have the necessary permissions to perform this action.",colour=0xc8dc6c), delete_after=10)
            return

        # Check if the bot itself has the permission to ban members
        if not ctx.guild.me.guild_permissions.ban_members:
            await ctx.send(embed=discord.Embed(title="I don't have the ban members permission to perform this action.",colour=0xc8dc6c), delete_after=10)
            return

        # Retrieve the ban entries to check if the user is banned
        banned_users = [ban_entry async for ban_entry in ctx.guild.bans()]
        for ban_entry in banned_users:
            if ban_entry.user == user:
                try:
                    # Ask for confirmation
                    confirm_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation", description=f"{user.mention}, are you sure you want to unban this user? React with ✅ to confirm.", color=0x99ccff))
                    await confirm_message.add_reaction("✅")
                    await confirm_message.add_reaction('❌')

                    def check(reaction, user_check):
                        return user_check == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

                    try:
                        # Waiting for the reaction to be added
                        reaction, user_check = await bot.wait_for('reaction_add', timeout=20.0, check=check)
                    except asyncio.TimeoutError:
                        await ctx.send(embed=discord.Embed(title="Unban confirmation failed. Command cancelled.", color=0x99ccff))
                        return

                    if str(reaction.emoji) == '✅':
                        # Perform the unban
                        await ctx.guild.unban(user, reason=reason)
                        await confirm_message.edit(embed=discord.Embed(title="Member unbanned", description=f"Unbanned member: {user.mention}\n Reason: {reason}", color=0x99ccff))
                    else:
                        await confirm_message.edit(embed=discord.Embed(title=f"Action cancelled.", description="`{member}` has not been unbanned.",colour=0xc8dc6c, color=0x99ccff), delete_after=10)
                except discord.Forbidden:
                    await confirm_message.edit(embed=discord.Embed(title="I do not have permission to unban this user.", color=0x99ccff))
                    return
                except discord.HTTPException as e:
                    await confirm_message.edit(embed=discord.Embed(title="Failed to unban due to an HTTP error.", color=0x99ccff))
                    return
                break
        else:
            # User is not in the ban entries
            await ctx.send(embed=discord.Embed(title=f"{user.mention} is not banned.", color=0x99ccff))






    @bot.command(name='timeout', help='Timeout a user for a specified duration.')
    async def timeout(ctx, member: discord.Member = None, duration: str = None, *, reason: str = "No reason provided"):
        if member == ctx.guild.owner:
            await ctx.send(embed=discord.Embed(title="I cannot timeout the server owner.", color=0x99ccff))
            return

        if member == ctx.bot.user:
            await ctx.send(embed=discord.Embed(title="I cannot timeout myself.", color=0x99ccff))
            return

        if member == ctx.author:
            await ctx.send(embed=discord.Embed(title="You cannot timeout yourself.", color=0x99ccff))
            return
        
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send(embed=discord.Embed(title="I don't have the `manage roles` permission to perform this commad!",colour=0xc8dc6c), delete_after=10)
            return
        

        if member is None:
            await ctx.send(embed=discord.Embed(title="Please provide a member", color=0x99ccff))
            return

        if duration is None:
            await ctx.send(embed=discord.Embed(title="Please provide a duration.", color=0x99ccff))
            return
        time_delta = parse_duration(duration)
        if time_delta is None:
            await ctx.send(embed=discord.Embed(title="Invalid duration. Use 'd' for days, 'h' for hours, 'm' for minutes.", color=0x99ccff))
            return

        time_now = discord.utils.utcnow()
        timeout_until = time_now + time_delta

        try:
            # Ask for confirmation
            confirm_message = await ctx.send(embed=discord.Embed(title="LuminaryAI - confirmation",description=f"{member.mention}, are you sure you want to apply this timeout?\nReact with ✅ to confirm.", color=0x99ccff))
            await confirm_message.add_reaction("✅")
            await confirm_message.add_reaction('❌')

            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirm_message.id

            try:

                reaction, user = await ctx.bot.wait_for('reaction_add', timeout=20.0, check=check)
            except asyncio.TimeoutError:
                await confirm_message.edit(embed=discord.Embed(title="Timeout confirmation failed. Command cancelled.", color=0x99ccff))
                return

            if str(reaction.emoji) == '✅':
                # Apply timeout
                await member.edit(timed_out_until=timeout_until)
                await confirm_message.edit(embed=discord.Embed(title="Member timed out",description=f"{member.mention} has been timed out for `{duration}`.\nReason: `{reason}`", color=0x99ccff))
            else:
                await confirm_message.edit(embed=discord.Embed(title=f"Action cancelled.", description=f"{member} has not been timed out.", color=0x99ccff), delete_after=10)
            
        except discord.Forbidden:
            await ctx.send(embed=discord.Embed(title="I do not have permission to timeout this user.", color=0x99ccff))
        except discord.HTTPException as e:
            await ctx.send(embed=discord.Embed(title=f"Failed to timeout due to an HTTP error.", color=0x99ccff))
            print(e)
