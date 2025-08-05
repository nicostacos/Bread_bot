
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import datetime
import asyncio

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
BOT_OWNER_ID = 993607806915706891

# Add this at the top with other variables
bot_start_time = None
default_filter_words = ["fuck", "shit", "bitch", "nigger", "nigga", "niggers", "niggas", "nigguh", "nigguhs"]
custom_filter_words = default_filter_words.copy()

# ⚡ Slash Commands
@bot.tree.command(name="test", description="A simple test command")
async def test_command(interaction: discord.Interaction):
    await interaction.response.send_message("Test command works! ✅")

@bot.tree.command(name="ping", description="Check if the bot is responsive")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! 🏓")

@bot.tree.command(name="hello", description="Say hello to the bot")
async def slash_hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}! 👋")

@bot.tree.command(name="coin_toss", description="flips a coin")
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
@app_commands.describe(user="The user to unban", reason="Reason for unbanning")
async def unban(interaction: discord.Interaction, user: discord.User, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You need mod permissions to use this command!", ephemeral=True)
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
@app_commands.describe(member="The member to mute", duration="Duration in minutes", reason="Reason for muting")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason provided"):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You need moderate members permissions to use this command!", ephemeral=True)
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
@app_commands.describe(member="The member to unmute", reason="Reason for unmuting")
async def unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You need moderate members permissions to use this command!", ephemeral=True)
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

# ___________________________________________________________________________________________________________________________________________________________________
# ___________________________________________________________________________________________________________________________________________________________________
# ___________________________________________________________________________________________________________________________________________________________________
@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = discord.utils.utcnow()  # Record when bot came online
    
    print(f"We are ready to go in, {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} global commands: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

 # new members
@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server {member.name}")

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return
    
    # Check if message is in DMs and contains commands
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith('bread ') or message.content.startswith('/'):
            await message.channel.send("Hello! You cannot use prefix commands in DMs, use slash commands instead.")
            return
    
    # Check for filtered words (only in guilds)
    if message.guild:
        message_lower = message.content.lower()
        for word in custom_filter_words:
            if word in message_lower:
                try:
                    await message.delete()
                    
                    embed = discord.Embed(
                        title="🚫 Message Filtered",
                        description=f"{message.author.mention} Bad boy don't use that word!",
                        color=0xff0000
                    )
                    embed.set_footer(text="Message deleted by chat filter")
                    
                    await message.channel.send(embed=embed, delete_after=5)
                    break
                except discord.Forbidden:
                    print(f"❌ No permission to delete message from {message.author}")
                except Exception as e:
                    print(f"❌ Error deleting message: {e}")

    await bot.process_commands(message)

@bot.tree.command(name="filter", description="Manage the chat filter")
@app_commands.describe(
    action="Action to perform",
    word="Word to add or remove from filter"
)
@app_commands.choices(action=[
    app_commands.Choice(name="add", value="add"),
    app_commands.Choice(name="remove", value="remove"),
    app_commands.Choice(name="list", value="list"),
    app_commands.Choice(name="reset", value="reset")
])
async def filter_command(interaction: discord.Interaction, action: str, word: str = None):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!", ephemeral=True)
        return
    
    global custom_filter_words
    
    if action == "add":
        if not word:
            await interaction.response.send_message("❌ Please provide a word to add!", ephemeral=True)
            return
        
        word = word.lower()
        if word in custom_filter_words:
            await interaction.response.send_message(f"❌ `{word}` is already in the filter!", ephemeral=True)
            return
        
        custom_filter_words.append(word)
        embed = discord.Embed(
            title="✅ Word Added to Filter",
            description=f"Added `{word}` to the chat filter", ephemeral=True,
            color=0x00ff00
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Modified by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    
    elif action == "remove":
        if not word:
            await interaction.response.send_message("❌ Please provide a word to remove!", ephemeral=True)
            return
        
        word = word.lower()
        if word not in custom_filter_words:
            await interaction.response.send_message(f"❌ `{word}` is not in the filter!", ephemeral=True)
            return
        
        custom_filter_words.remove(word)
        embed = discord.Embed(
            title="✅ Word Removed from Filter",
            description=f"Removed `{word}` from the chat filter",
            color=0xff9900
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Modified by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)
    
    elif action == "list":
        if not custom_filter_words:
            embed = discord.Embed(
                title="📝 Chat Filter List",
                description="No words are currently being filtered.",
                color=0x808080
            )
        else:
            # Show uncensored words for moderators
            word_list = ", ".join([f"`{word}`" for word in custom_filter_words])
            
            embed = discord.Embed(
                title="📝 Chat Filter List",
                description=f"Currently filtering {len(custom_filter_words)} words:",
                color=0x0099ff
            )
            embed.add_field(name="Filtered Words", value=word_list, inline=False)
        
        embed.set_footer(text=f"Requested by {interaction.user.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    elif action == "reset":
        custom_filter_words = default_filter_words.copy()
        embed = discord.Embed(
            title="🔄 Filter Reset",
            description="Chat filter has been reset to default settings",
            color=0xff0000
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Reset by {interaction.user.name}")
        await interaction.response.send_message(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def filter(ctx, action=None, *, word=None):
    global custom_filter_words
    
    if not action:
        await ctx.send("❌ Please specify an action: `add`, `remove`, `list`, or `reset`")
        return
    
    action = action.lower()
    
    if action == "add":
        if not word:
            await ctx.send("❌ Please provide a word to add!")
            return
        
        word = word.lower()
        if word in custom_filter_words:
            await ctx.send(f"❌ `{word}` is already in the filter!")
            return
        
        custom_filter_words.append(word)
        embed = discord.Embed(
            title="✅ Word Added to Filter",
            description=f"Added `{word}` to the chat filter",ephemeral=True,
            color=0x00ff00
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Modified by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    elif action == "remove":
        if not word:
            await ctx.send("❌ Please provide a word to remove!")
            return
        
        word = word.lower()
        if word not in custom_filter_words:
            await ctx.send(f"❌ `{word}` is not in the filter!",ephemeral=True)
            return
        
        custom_filter_words.remove(word)
        embed = discord.Embed(
            title="✅ Word Removed from Filter",
            description=f"Removed `{word}` from the chat filter",ephemeral=True,
            color=0xff9900
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Modified by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    elif action == "list":
        if not custom_filter_words:
            embed = discord.Embed(
                title="📝 Chat Filter List",
                description="No words are currently being filtered.",
                color=0x808080
            )
        else:
            # Show uncensored words for moderators
            word_list = ", ".join([f"`{word}`" for word in custom_filter_words])
            
            embed = discord.Embed(
                title="📝 Chat Filter List",
                description=f"Currently filtering {len(custom_filter_words)} words:",
                color=0x0099ff
            )
            embed.add_field(name="Filtered Words", value=word_list, inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        try:
            await ctx.author.send(embed=embed)
            await ctx.send("📝 Filter list sent to your DMs!", delete_after=3)
        except discord.Forbidden:
            await ctx.send("❌ I can't send you a DM! Please enable DMs from server members.", delete_after=5)
    
    elif action == "reset":
        custom_filter_words = default_filter_words.copy()
        embed = discord.Embed(
            title="🔄 Filter Reset",
            description="Chat filter has been reset to default settings",
            color=0xff0000
        )
        embed.add_field(name="Total Filtered Words", value=str(len(custom_filter_words)), inline=True)
        embed.set_footer(text=f"Reset by {ctx.author.name}")
        await ctx.send(embed=embed)
    
    else:
        await ctx.send("❌ Invalid action! Use: `add`, `remove`, `list`, or `reset`")

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
        admin_commands = ["broadcast", "kick", "ban", "mute", "unmute", "purge", "lock", "unlock", "filter"]
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
            "lock": {
                "description": "Lock a channel to prevent members from sending messages (Admin only)",
                "usage": "`bread lock [#channel] [reason]`\n`/lock channel:<channel> reason:<text>`",
                "example": "`bread lock #general Maintenance`"
            },
            "unlock": {
                "description": "Unlock a channel to allow members to send messages (Admin only)",
                "usage": "`bread unlock [#channel] [reason]`\n`/unlock channel:<channel> reason:<text>`",
                "example": "`bread unlock #general All done!`"
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
            },
            "filter": {
                "description": "Manage the chat filter (Admin only)",
                "usage": "`bread filter <action> [word]`\n`/filter action:<add/remove/list/reset> word:<text>`",
                "example": "`bread filter add badword`\n`bread filter list`\n`bread filter reset`"
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
        value="`/test` - Test command\n`/ping` - Check bot response\n`/hello` - Say hello\n`/coin_toss` - Flip a coin\n`/help` - Show commands\n`/me` - Your info",
        inline=False
    )
    
    # Prefix Commands
    embed.add_field(
        name="🍞 Prefix Commands (bread)",
        value="`bread hello` - Say hello\n`bread assign` - Get bot test role\n`bread remove` - Remove bot test role\n`bread dm` - Send yourself a DM\n`bread reply` - Reply to message\n`bread poll` - Create a poll\n`bread secret` - Secret command\n`bread me` - Your info\n`bread help` - Show commands",
        inline=False
    )
    
    # Only show moderation commands if user has administrator permissions
    if ctx.author.guild_permissions.moderate_members:
        embed.add_field(
            name="⚡ Moderation Slash Commands",
            value="`/kick` - Kick a member\n`/ban` - Ban a member\n`/mute` - Mute a member\n`/unmute` - Unmute a member\n`/broadcast` - Broadcast message\n`/purge` - Delete messages\n`/lock` - Lock channel\n`/unlock` - Unlock channel\n`/filter` - Manage chat filter",
            inline=False
        )
        
        embed.add_field(
            name="🔨 Moderation Prefix Commands (bread)",
            value="`bread kick` - Kick member\n`bread ban` - Ban member\n`bread mute` - Mute member\n`bread unmute` - Unmute member\n`bread broadcast` - Broadcast message\n`bread purge` - Delete messages\n`bread lock` - Lock channel\n`bread unlock` - Unlock channel",
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

    embed = discord.Embed(
        title="🤖 Bot Status Report",
        color=0x00ff00,
        timestamp=discord.utils.utcnow()
    )
    
    # Bot basic info with actual uptime
    uptime_text = discord.utils.format_dt(bot_start_time, 'R') if bot_start_time else "Unknown"
    embed.add_field(
        name="🔧 Bot Info",
        value=f"**Status:** Online ✅\n**Latency:** {round(bot.latency * 1000)}ms\n**Online Since:** {uptime_text}",
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

@bot.tree.command(name="lock", description="Lock a channel to prevent members from sending messages")
@app_commands.describe(channel="Channel to lock (current channel if not specified)", reason="Reason for locking")
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You need Manage Channels permissions to use this command!", ephemeral=True)
        return
    
    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ I don't have permission to manage channels!", ephemeral=True)
        return
    
    # Use current channel if none specified
    target_channel = channel or interaction.channel
    
    try:
        # Get @everyone role
        everyone_role = interaction.guild.default_role
        
        # Remove send messages permission for @everyone
        await target_channel.set_permissions(everyone_role, send_messages=False, reason=reason)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{target_channel.mention} has been locked!",
            color=0xff0000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Locked by", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to modify this channel!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.tree.command(name="unlock", description="Unlock a channel to allow members to send messages")
@app_commands.describe(channel="Channel to unlock (current channel if not specified)", reason="Reason for unlocking")
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You need Manage Channels permissions to use this command!", ephemeral=True)
        return
    
    if not interaction.guild.me.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ I don't have permission to manage channels!", ephemeral=True)
        return
    
    # Use current channel if none specified
    target_channel = channel or interaction.channel
    
    try:
        # Get @everyone role
        everyone_role = interaction.guild.default_role
        
        # Restore send messages permission for @everyone (set to None = inherit)
        await target_channel.set_permissions(everyone_role, send_messages=None, reason=reason)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{target_channel.mention} has been unlocked!",
            color=0x00ff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Unlocked by", value=interaction.user.mention, inline=True)
        
        await interaction.response.send_message(embed=embed)
        
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to modify this channel!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)

@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ I don't have permission to manage channels!")
        return
    
    target_channel = channel or ctx.channel
    
    try:
        everyone_role = ctx.guild.default_role
        await target_channel.set_permissions(everyone_role, send_messages=False, reason=reason)
        
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{target_channel.mention} has been locked!",
            color=0xff0000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Locked by", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify this channel!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ I don't have permission to manage channels!")
        return
    
    target_channel = channel or ctx.channel
    
    try:
        everyone_role = ctx.guild.default_role
        await target_channel.set_permissions(everyone_role, send_messages=None, reason=reason)
        
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{target_channel.mention} has been unlocked!",
            color=0x00ff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Unlocked by", value=ctx.author.mention, inline=True)
        
        await ctx.send(embed=embed)
        
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify this channel!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")

@bot.command()
async def restart(ctx):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("❌ Only the bot owner can use this command!")
        return
    if ctx.author.id == BOT_OWNER_ID:
        await ctx.send("Are you sure you want to restart?")
        await asyncio.sleep(5)
        if not message.content == "yes" or "y" or "Yes" or "Y":
            await ctx.send("Restart cancelled.")
            return
        else:
            await ctx.send("Restarting...")
            await bot.close()
# ▶️ Start the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


