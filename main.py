#thynico creation guys...
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import datetime

#  Load token from .env file
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

#  Logging setup
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create the bot instance
bot = commands.Bot(command_prefix='bread ', intents=intents, help_command=None)

# Name of the secret role
secret_role = "bot test"
GUILD_ID = 1247215187799572643
BOT_OWNER_ID = 993607806915706891  # Replace with your actual Discord user ID

# ⚡ Slash Commands
@bot.tree.command(name="test", description="A simple test command")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("Test command works! ✅")

@bot.tree.command(name="ping", description="Check if the bot is responsive")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

@bot.tree.command(name="hello", description="Say hello to the bot")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}! 👋")

@bot.tree.command(name="coin_toss", description="flips a coin")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def coin_toss(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    emoji = "👑" if result == "Heads" else "🔢"
    
    embed = discord.Embed(
        title="🪙 Coin Toss",
        description=f"{emoji} **{result}**!",
        color=0x00ff00 if result == "Heads" else 0xff0000
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return
    
    # Check if bot has kick permissions
    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.response.send_message("❌ I don't have permission to kick members!", ephemeral=True)
        return
    
    # Can't kick yourself
    if member == interaction.user:
        await interaction.response.send_message("❌ You can't kick yourself!", ephemeral=True)
        return
    
    # Can't kick the bot
    if member == interaction.guild.me:
        await interaction.response.send_message("❌ I can't kick myself!", ephemeral=True)
        return
    
    # Check role hierarchy
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You can't kick someone with equal or higher roles!", ephemeral=True)
        return
    
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been kicked!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to ban", reason="Reason for banning")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return

    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to ban members!", ephemeral=True)
        return

    if member == interaction.user:
        await interaction.response.send_message("❌ You can't ban yourself!", ephemeral=True)
        return

    if member == interaction.guild.me:
        await interaction.response.send_message("❌ I can't ban myself!", ephemeral=True)
        return

    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You can't ban someone with equal or higher roles!", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been banned!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to ban this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="unban", description="Unban a member from the server")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(user="The user to unban", reason="Reason for unbanning")
async def unban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return

    if not interaction.guild.me.guild_permissions.ban_members:
        await interaction.response.send_message("❌ I don't have permission to unban members!", ephemeral=True)
        return

    try:
        await interaction.guild.unban(user, reason=reason)
        await interaction.response.send_message(f"✅ {user.name} has been unbanned!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unban this user!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="mute", description="Mute a member for a specified duration")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to mute", duration="Duration in minutes", reason="Reason for muting")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason provided"):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return
    
    # Check if bot has timeout permissions
    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ I don't have permission to timeout members!", ephemeral=True)
        return
    
    # Can't mute yourself
    if member == interaction.user:
        await interaction.response.send_message("❌ You can't mute yourself!", ephemeral=True)
        return
    
    # Can't mute the bot
    if member == interaction.guild.me:
        await interaction.response.send_message("❌ I can't mute myself!", ephemeral=True)
        return
    
    # Check role hierarchy
    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You can't mute someone with equal or higher roles!", ephemeral=True)
        return
    
    # Duration limits (Discord max is 28 days)
    if duration > 40320:  # 28 days in minutes
        await interaction.response.send_message("❌ Maximum mute duration is 28 days (40320 minutes)!", ephemeral=True)
        return
    
    try:
        # Calculate timeout duration
        timeout_duration = discord.utils.utcnow() + datetime.timedelta (minutes=duration)
        
        await member.timeout(timeout_duration, reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been muted for {duration} minutes!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(member="The member to unmute", reason="Reason for unmuting")
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return

    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ I don't have permission to unmute members!", ephemeral=True)
        return

    if member == interaction.user:
        await interaction.response.send_message("❌ You can't unmute yourself!", ephemeral=True)
        return

    if member == interaction.guild.me:
        await interaction.response.send_message("❌ I can't unmute myself!", ephemeral=True)
        return

    if member.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ You can't unmute someone with equal or higher roles!", ephemeral=True)
        return

    try:
        await member.timeout(None, reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been unmuted!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to unmute this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="purge", description="Purge messages from a channel")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(limit="Number of messages to purge")
async def purge(interaction: discord.Interaction, limit: int = 2000):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Boy why u even try to purge messages?", ephemeral=False)
        return

    if not interaction.guild.me.guild_permissions.administrator:
        await interaction.response.send_message("❌ I don't have permission to manage messages!", ephemeral=True)
        return

    if limit > 2000:
        await interaction.response.send_message("❌ Maximum purge limit is 2000 messages!", ephemeral=True)
        return

    try:
        await interaction.channel.purge(limit=limit)
        await interaction.response.send_message(f"✅ Purged {limit} messages!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to manage messages!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="broadcast", description="Broadcast a message to all channels")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(message="The message to broadcast", ping_everyone="Whether to ping @everyone")
async def broadcast(interaction: discord.Interaction, message: str, ping_everyone: bool = False):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("No one wants to hear you talking", ephemeral=False)
        return
    
    if not interaction.guild.me.guild_permissions.send_messages:
        await interaction.response.send_message("❌ I don't have permission to send messages!", ephemeral=True)
        return
    
    try:
        channel_count = 0
        broadcast_message = f"@everyone {message}" if ping_everyone else message
        
        for channel in interaction.guild.text_channels:
            try:
                await channel.send(broadcast_message)
                channel_count += 1
            except discord.Forbidden:
                continue
        
        ping_status = "with @everyone ping" if ping_everyone else "without ping"
        await interaction.response.send_message(f"✅ Broadcasted message to {channel_count} channels {ping_status}!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)


# 🎉 When bot is ready
@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")
    
    try:
        guild = discord.Object(id=GUILD_ID)
        synced = await bot.tree.sync(guild=guild)
        print(f"✅ Synced {len(synced)} guild commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

 # new members
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

# filter
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    #  filter
    if "fuck" in message.content.lower() or "shit" in message.content.lower() or "bitch" in message.content.lower() or "nigger" in message.content.lower() or "nigga" in message.content.lower() or "niggers" in message.content.lower() or "niggas" in message.content.lower() or "nigguh" in message.content.lower() or "nigguhs" in message.content.lower() or "nazi" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} Bad boy don't use that word!")

    await bot.process_commands(message)

# 📦 Prefix Command: bb hello
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}!")

# bb assign
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} is now assigned to {secret_role}!")
    else:
        await ctx.send("Role doesn't exist!")

#  bb remove
@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secret_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{ctx.author.mention} has had the {secret_role} removed")
    else:
        await ctx.send("Role doesn't exist!")

#  bb dm
@bot.command()
async def dm(ctx, *, msg):
    try:
        await ctx.author.send(f"You said: {msg}")
        await ctx.send("✅ DM sent!", delete_after=3)
    except discord.Forbidden:
        await ctx.send("❌ I can't send you a DM! Please check your privacy settings.")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

#  bb reply
@bot.command()
async def reply(ctx):
    await ctx.reply("This is a reply to your message.")

# bb poll
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="📊 New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("🫣")

# 🔐 Prefix Command: bb secret (role protected)
@bot.command()
@commands.has_role(secret_role)
async def secret(ctx):
    await ctx.send("I dont know.")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You do not have permission to do that.")

# 📦 Prefix Commands for Moderation
@bot.command()
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("❌ I don't have permission to kick members!")
        return
    
    if member == ctx.author:
        await ctx.send("❌ You can't kick yourself!")
        return
    
    if member == ctx.guild.me:
        await ctx.send("❌ I can't kick myself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You can't kick someone with equal or higher roles!")
        return
    
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ {member.mention} has been kicked!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ I don't have permission to ban members!")
        return
    
    if member == ctx.author:
        await ctx.send("❌ You can't ban yourself!")
        return
    
    if member == ctx.guild.me:
        await ctx.send("❌ I can't ban myself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You can't ban someone with equal or higher roles!")
        return
    
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ {member.mention} has been banned!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, duration: int = 10, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("❌ I don't have permission to timeout members!")
        return
    
    if member == ctx.author:
        await ctx.send("❌ You can't mute yourself!")
        return
    
    if member == ctx.guild.me:
        await ctx.send("❌ I can't mute myself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You can't mute someone with equal or higher roles!")
        return
    
    if duration > 40320:
        await ctx.send("❌ Maximum mute duration is 28 days (40320 minutes)!")
        return
    
    try:
        timeout_duration = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
        await member.timeout(timeout_duration, reason=reason)
        await ctx.send(f"✅ {member.mention} has been muted for {duration} minutes!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to timeout this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("❌ I don't have permission to unmute members!")
        return
    
    if member == ctx.author:
        await ctx.send("❌ You can't unmute yourself!")
        return
    
    if member == ctx.guild.me:
        await ctx.send("❌ I can't unmute myself!")
        return
    
    if member.top_role >= ctx.author.top_role:
        await ctx.send("❌ You can't unmute someone with equal or higher roles!")
        return
    
    try:
        await member.timeout(None, reason=reason)
        await ctx.send(f"✅ {member.mention} has been unmuted!\nReason: {reason}")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unmute this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def broadcast(ctx, *, message):
    if not ctx.guild.me.guild_permissions.send_messages:
        await ctx.send("❌ I don't have permission to send messages!")
        return
    
    try:
        await ctx.message.delete()
        
        # Check if message starts with "ping" to enable @everyone
        if message.lower().startswith("ping "):
            ping_everyone = True
            message = message[5:]  # Remove "ping" from the start
        else:
            ping_everyone = False
        
        channel_count = 0
        broadcast_message = f"@everyone {message}" if ping_everyone else message
        
        for channel in ctx.guild.text_channels:
            try:
                await channel.send(broadcast_message)
                channel_count += 1
            except discord.Forbidden:
                continue
        
        ping_status = "with @everyone ping" if ping_everyone else "without ping"
        await ctx.send(f"✅ Broadcasted message to {channel_count} channels {ping_status}!", delete_after=5)
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(administrator=True)
async def purge(ctx, limit: int = 10):
    if not ctx.guild.me.guild_permissions.manage_messages:
        await ctx.send("❌ I don't have permission to manage messages!")
        return

    if limit > 100:
        await ctx.send("❌ Maximum purge limit is 100 messages!")
        return

    try:
        deleted = await ctx.channel.purge(limit=limit + 1)  # +1 to include the command message
        await ctx.send(f"✅ Purged {len(deleted) - 1} messages!", delete_after=5)
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to manage messages!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
async def help(ctx, *, command_name=None):
    if command_name:
        # Show detailed help for specific command
        command_name = command_name.lower()
        
        # Check permissions for admin commands
        admin_commands = ["broadcast", "kick", "ban", "mute", "unmute", "purge"]
        if command_name in admin_commands and not ctx.author.guild_permissions.administrator:
            await ctx.send(f"❌ You don't have permission to use the `{command_name}` command!")
            return
        
        # Check for the secret command role
        if command_name == "secret":
            role = discord.utils.get(ctx.guild.roles, name=secret_role)
            if not role or role not in ctx.author.roles:
                await ctx.send(f"❌ You don't have the required role to use the `{command_name}` command!")
                return
        
        command_details = {
            "hello": {
                "description": "Say hello to the bot",
                "usage": "`bread hello`",
                "example": "`bread hello`"
            },
            "assign": {
                "description": "Get the bot test role",
                "usage": "`bread assign`",
                "example": "`bread assign`"
            },
            "remove": {
                "description": "Remove the bot test role",
                "usage": "`bread remove`",
                "example": "`bread remove`"
            },
            "dm": {
                "description": "Send yourself a DM with your message",
                "usage": "`bread dm <message>`",
                "example": "`bread dm Hello this is a test!`"
            },
            "reply": {
                "description": "Reply to your message",
                "usage": "`bread reply`",
                "example": "`bread reply`"
            },
            "poll": {
                "description": "Create a poll with thumbs up and thinking reactions",
                "usage": "`bread poll <question>`",
                "example": "`bread poll Should we add more commands?`"
            },
            "secret": {
                "description": "Secret command (requires bot test role)",
                "usage": "`bread secret`",
                "example": "`bread secret`"
            },
            "broadcast": {
                "description": "Broadcast a message to all channels (Admin only)",
                "usage": "`bread broadcast [ping] <message>`\n`/broadcast message:<text> ping_everyone:<true/false>`",
                "example": "`bread broadcast Hello everyone!`\n`bread broadcast ping Important announcement!`"
            },
            "kick": {
                "description": "Kick a member from the server (Admin only)",
                "usage": "`bread kick <@member> [reason]`\n`/kick member:<user> reason:<text>`",
                "example": "`bread kick @user spam`"
            },
            "ban": {
                "description": "Ban a member from the server (Admin only)",
                "usage": "`bread ban <@member> [reason]`\n`/ban member:<user> reason:<text>`",
                "example": "`bread ban @user breaking rules`"
            },
            "mute": {
                "description": "Mute a member for specified duration (Admin only)",
                "usage": "`bread mute <@member> [duration] [reason]`\n`/mute member:<user> duration:<minutes> reason:<text>`",
                "example": "`bread mute @user 30 being annoying`"
            },
            "unmute": {
                "description": "Unmute a member (Admin only)",
                "usage": "`bread unmute <@member> [reason]`\n`/unmute member:<user> reason:<text>`",
                "example": "`bread unmute @user`"
            },
            "purge": {
                "description": "Delete messages from current channel (Admin only)",
                "usage": "`bread purge [amount]`\n`/purge limit:<number>`",
                "example": "`bread purge 50`"
            },
            "me": {
                "description": "Show your Discord and server information",
                "usage": "`bread me`\n`/me`",
                "example": "`bread me`"
            },
            "help": {
                "description": "Show bot commands and get help",
                "usage": "`bread help [command]`\n`/help command:<name>`",
                "example": "`bread help broadcast`"
            }
        }
        
        if command_name in command_details:
            cmd = command_details[command_name]
            embed = discord.Embed(
                title=f"🍞 Help: {command_name}",
                description=cmd["description"],
                color=0x00ff00
            )
            embed.add_field(name="Usage", value=cmd["usage"], inline=False)
            embed.add_field(name="Example", value=cmd["example"], inline=False)
            
            # Check if it's admin only
            if command_name in admin_commands:
                embed.add_field(name="⚠️ Requirements", value="Administrator permissions required", inline=False)
            elif command_name == "secret":
                embed.add_field(name="⚠️ Requirements", value="Bot test role required", inline=False)
                
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"❌ Command `{command_name}` not found! Use `bread help` to see all commands.")
        return
    
    # Show general help
    embed = discord.Embed(
        title="🍞 Bread Bot Commands",
        description="Here are all available commands:\n\n**💡 Tip:** Use `bread help <command>` for detailed info!",
        color=0x00ff00
    )
    
    # Slash Commands
    embed.add_field(
        name="⚡ Slash Commands",
        value="`/test` - Test command\n`/ping` - Check bot response\n`/hello` - Say hello\n`/cointoss` - Flip a coin\n`/help` - Show commands\n`/me` - Your info",
        inline=False
    )
    
    # Prefix Commands
    embed.add_field(
        name="🍞 Prefix Commands (bread)",
        value="`bread hello` - Say hello\n`bread assign` - Get bot test role\n`bread remove` - Remove bot test role\n`bread dm` - Send yourself a DM\n`bread reply` - Reply to message\n`bread poll` - Create a poll\n`bread secret` - Secret command\n`bread me` - Your info\n`bread help` - Show commands",
        inline=False
    )
    
    # Only show moderation commands if user has administrator permissions
    if ctx.author.guild_permissions.administrator:
        embed.add_field(
            name="⚡ Moderation Slash Commands",
            value="`/kick` - Kick a member\n`/ban` - Ban a member\n`/mute` - Mute a member\n`/unmute` - Unmute a member\n`/broadcast` - Broadcast message\n`/purge` - Delete messages",
            inline=False
        )
        
        embed.add_field(
            name="🔨 Moderation Prefix Commands (bread)",
            value="`bread kick` - Kick member\n`bread ban` - Ban member\n`bread mute` - Mute member\n`bread unmute` - Unmute member\n`bread broadcast` - Broadcast message\n`bread purge` - Delete messages",
            inline=False
        )
    
    embed.set_footer(text="Use bread <command> or /<command> | bread help <command> for details")
    embed.set_thumbnail(url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None)
    
    await ctx.send(embed=embed)

@bot.command()
async def me(ctx):
    user = ctx.author
    member = ctx.guild.get_member(user.id)
    
    embed = discord.Embed(
        title=f"👤 {user.display_name}'s Info",
        color=0x00ff00
    )
    
    # User avatar
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    # Basic info
    embed.add_field(
        name="📋 Basic Info",
        value=f"**Username:** {user.name}\n**Display Name:** {user.display_name}\n**ID:** {user.id}",
        inline=False
    )
    
    # Discord join date
    discord_join = user.created_at.strftime("%B %d, %Y at %I:%M %p")
    embed.add_field(
        name="📅 Discord Account Created",
        value=discord_join,
        inline=True
    )
    
    # Server join date
    if member and member.joined_at:
        server_join = member.joined_at.strftime("%B %d, %Y at %I:%M %p")
        embed.add_field(
            name="🏠 Joined This Server",
            value=server_join,
            inline=True
        )
    
    # Roles
    if member and member.roles:
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            roles_text = ", ".join(roles) if len(roles) <= 10 else f"{', '.join(roles[:10])}... (+{len(roles)-10} more)"
            embed.add_field(
                name=f"🎭 Roles ({len(roles)})",
                value=roles_text,
                inline=False
            )
        else:
            embed.add_field(
                name="🎭 Roles",
                value="No roles",
                inline=False
            )
    
    # Server permissions
    if member:
        perms = []
        if member.guild_permissions.administrator:
            perms.append("Administrator")
        if member.guild_permissions.kick_members:
            perms.append("Kick Members")
        if member.guild_permissions.ban_members:
            perms.append("Ban Members")
        if member.guild_permissions.manage_messages:
            perms.append("Manage Messages")
        
        if perms:
            embed.add_field(
                name="🔑 Key Permissions",
                value=", ".join(perms),
                inline=False
            )
    
    embed.set_footer(text=f"Requested by {user.name}")
    embed.timestamp = discord.utils.utcnow()
    
    await ctx.send(embed=embed)

@bot.tree.command(name="help", description="Show bot commands and usage")
@app_commands.guilds(discord.Object(id=GUILD_ID))
@app_commands.describe(command="Specific command to get help for")
async def slash_help(interaction: discord.Interaction, command: str = None):
    if command:
        command = command.lower()
        
        admin_commands = ["broadcast", "kick", "ban", "mute", "unmute", "purge"]
        if command in admin_commands and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(f"❌ You don't have permission to use the `{command}` command!", ephemeral=True)
            return
        
        if command == "secret":
            role = discord.utils.get(interaction.guild.roles, name=secret_role)
            if not role or role not in interaction.user.roles:
                await interaction.response.send_message(f"❌ You don't have the required role to use the `{command}` command!", ephemeral=True)
                return
        
        command_details = {
            "hello": {
                "description": "Say hello to the bot",
                "usage": "`bread hello`",
                "example": "`bread hello`"
            },
            "assign": {
                "description": "Get the bot test role",
                "usage": "`bread assign`",
                "example": "`bread assign`"
            },
            "remove": {
                "description": "Remove the bot test role",
                "usage": "`bread remove`",
                "example": "`bread remove`"
            },
            "dm": {
                "description": "Send yourself a DM with your message",
                "usage": "`bread dm <message>`",
                "example": "`bread dm Hello this is a test!`"
            },
            "reply": {
                "description": "Reply to your message",
                "usage": "`bread reply`",
                "example": "`bread reply`"
            },
            "poll": {
                "description": "Create a poll with thumbs up and thinking reactions",
                "usage": "`bread poll <question>`",
                "example": "`bread poll Should we add more commands?`"
            },
            "secret": {
                "description": "Secret command (requires bot test role)",
                "usage": "`bread secret`",
                "example": "`bread secret`"
            },
            "broadcast": {
                "description": "Broadcast a message to all channels (Admin only)",
                "usage": "`bread broadcast [ping] <message>`\n`/broadcast message:<text> ping_everyone:<true/false>`",
                "example": "`bread broadcast Hello everyone!`\n`bread broadcast ping Important announcement!`"
            },
            "kick": {
                "description": "Kick a member from the server (Admin only)",
                "usage": "`bread kick <@member> [reason]`\n`/kick member:<user> reason:<text>`",
                "example": "`bread kick @user spam`"
            },
            "ban": {
                "description": "Ban a member from the server (Admin only)",
                "usage": "`bread ban <@member> [reason]`\n`/ban member:<user> reason:<text>`",
                "example": "`bread ban @user breaking rules`"
            },
            "mute": {
                "description": "Mute a member for specified duration (Admin only)",
                "usage": "`bread mute <@member> [duration] [reason]`\n`/mute member:<user> duration:<minutes> reason:<text>`",
                "example": "`bread mute @user 30 being annoying`"
            },
            "unmute": {
                "description": "Unmute a member (Admin only)",
                "usage": "`bread unmute <@member> [reason]`\n`/unmute member:<user> reason:<text>`",
                "example": "`bread unmute @user`"
            },
            "purge": {
                "description": "Delete messages from current channel (Admin only)",
                "usage": "`bread purge [amount]`\n`/purge limit:<number>`",
                "example": "`bread purge 50`"
            }
        }
        
        if command in command_details:
            cmd = command_details[command]
            embed = discord.Embed(
                title=f"🍞 Help: {command}",
                description=cmd["description"],
                color=0x00ff00
            )
            embed.add_field(name="Usage", value=cmd["usage"], inline=False)
            embed.add_field(name="Example", value=cmd["example"], inline=False)
            
            # Check if it's admin only
            if command in admin_commands:
                embed.add_field(name="⚠️ Requirements", value="Administrator permissions required", inline=False)
            elif command == "secret":
                embed.add_field(name="⚠️ Requirements", value="Bot test role required", inline=False)
                
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"❌ Command `{command}` not found! Use `/help` to see all commands.")
        return
    
    # Show general help
    embed = discord.Embed(
        title="🍞 Bread Bot Commands",
        description="Here are all available commands:\n\n**💡 Tip:** Use `/help <command>` for detailed info!",
        color=0x00ff00
    )
    
    # Slash Commands
    embed.add_field(
        name="⚡ Slash Commands",
        value="`/test` - Test command\n`/ping` - Check bot response\n`/hello` - Say hello\n`/cointoss` - Flip a coin",
        inline=False
    )
    
    # Prefix Commands
    embed.add_field(
        name="🍞 Prefix Commands (bread)",
        value="`bread hello` - Say hello\n`bread assign` - Get bot test role\n`bread remove` - Remove bot test role\n`bread dm` - Send yourself a DM\n`bread reply` - Reply to message\n`bread poll` - Create a poll\n`bread secret` - Secret command (role required)",
        inline=False
    )
    
    # Only show moderation commands if user has administrator permissions
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="⚡ Moderation Slash Commands",
            value="`/kick` - Kick a member\n`/ban` - Ban a member\n`/mute` - Mute a member\n`/unmute` - Unmute a member\n`/broadcast` - Broadcast message\n`/purge` - Delete messages",
            inline=False
        )
        
        embed.add_field(
            name="🔨 Moderation Prefix Commands (bread)",
            value="`bread kick` - Kick member\n`bread ban` - Ban member\n`bread mute` - Mute member\n`bread unmute` - Unmute member\n`bread broadcast` - Broadcast message\n`bread purge` - Delete messages",
            inline=False
        )
    
    embed.set_footer(text="Use bread <command> or /<command> | /help <command> for details")
    embed.set_thumbnail(url=interaction.client.user.avatar.url if interaction.client.user.avatar else None)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="me", description="Show your Discord and server information")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def slash_me(interaction: discord.Interaction):
    user = interaction.user
    member = interaction.guild.get_member(user.id)
    
    embed = discord.Embed(
        title=f"👤 {user.display_name}'s Info",
        color=0x00ff00
    )
    
    # User avatar
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    
    # Basic info
    embed.add_field(
        name="📋 Basic Info",
        value=f"**Username:** {user.name}\n**Display Name:** {user.display_name}\n**ID:** {user.id}",
        inline=False
    )
    
    # Discord join date
    discord_join = user.created_at.strftime("%B %d, %Y at %I:%M %p")
    embed.add_field(
        name="📅 Discord Account Created",
        value=discord_join,
        inline=True
    )
    
    # Server join date
    if member and member.joined_at:
        server_join = member.joined_at.strftime("%B %d, %Y at %I:%M %p")
        embed.add_field(
            name="🏠 Joined This Server",
            value=server_join,
            inline=True
        )
    
    # Roles
    if member and member.roles:
        roles = [role.mention for role in member.roles if role.name != "@everyone"]
        if roles:
            roles_text = ", ".join(roles) if len(roles) <= 10 else f"{', '.join(roles[:10])}... (+{len(roles)-10} more)"
            embed.add_field(
                name=f"🎭 Roles ({len(roles)})",
                value=roles_text,
                inline=False
            )
        else:
            embed.add_field(
                name="🎭 Roles",
                value="No roles",
                inline=False
            )
    
    # Server permissions
    if member:
        perms = []
        if member.guild_permissions.administrator:
            perms.append("Administrator")
        if member.guild_permissions.kick_members:
            perms.append("Kick Members")
        if member.guild_permissions.ban_members:
            perms.append("Ban Members")
        if member.guild_permissions.manage_messages:
            perms.append("Manage Messages")
        
        if perms:
            embed.add_field(
                name="🔑 Key Permissions",
                value=", ".join(perms),
                inline=False
            )
    
    embed.set_footer(text=f"Requested by {user.name}")
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.response.send_message(embed=embed)

@bot.command()
async def status(ctx):
    # Check if user is the bot owner
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("❌ Only the bot owner can use this command!")
        return
    
    embed = discord.Embed(
        title="🤖 Bot Status Report",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    
    # Bot basic info
    embed.add_field(
        name="🔧 Bot Info",
        value=f"**Status:** Online ✅\n**Latency:** {round(bot.latency * 1000)}ms\n**Uptime:** {discord.utils.format_dt(bot.user.created_at, 'R')}",
        inline=False
    )
    
    # Server info
    guild_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)
    embed.add_field(
        name="📊 Server Stats",
        value=f"**Servers:** {guild_count}\n**Total Members:** {member_count}\n**Current Server:** {ctx.guild.name}",
        inline=True
    )
    
    # Commands status
    slash_commands = len(bot.tree.get_commands())
    prefix_commands = len([cmd for cmd in bot.commands if not cmd.hidden])
    embed.add_field(
        name="⚡ Commands",
        value=f"**Slash Commands:** {slash_commands}\n**Prefix Commands:** {prefix_commands}\n**All Working:** ✅",
        inline=True
    )
    
    # Permissions check
    perms = ctx.guild.me.guild_permissions
    perm_status = "✅" if all([perms.kick_members, perms.ban_members, perms.manage_messages]) else "⚠️"
    embed.add_field(
        name="🔑 Bot Permissions",
        value=f"**Kick Members:** {'✅' if perms.kick_members else '❌'}\n**Ban Members:** {'✅' if perms.ban_members else '❌'}\n**Manage Messages:** {'✅' if perms.manage_messages else '❌'}\n**Status:** {perm_status}",
        inline=False
    )
    
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=embed)

# ▶️ Start the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

# ▶️ Start the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)

