import sys
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
import random
import datetime
import asyncio
import threading
from flask import Flask
import aiohttp
import asyncio
from pymongo import MongoClient  # ✅ MongoDB import
import discord
from discord.ext import commands
from discord import app_commands


# --- MongoDB Setup ---
MONGO_URI = "mongodb+srv://a99andres56_db_user:hlxIJzLKwPtEWayO@breadbot.aqvugjd.mongodb.net/?retryWrites=true&w=majority&appName=breadbot"

# Create a new client and connect to the server
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=False,
    tlsAllowInvalidHostnames=True,
    retryWrites=True,
    w='majority',
    appName='breadbot'
)

db = client["breadbot"]
config_collection = db["config"]


LOG_CHANNEL_ID = None
WELCOME_CHANNEL_ID = None

def save_config(guild_id, log_channel=None, welcome_channel=None):
    update_data = {}
    if log_channel is not None:
            update_data["log_channel"] = log_channel
    if welcome_channel is not None:
            update_data["welcome_channel"] = welcome_channel


    if update_data:
        config_collection.update_one(
        {"guild_id": guild_id},
        {"$set": update_data},
        upsert=True
)
def load_config(guild_id):
    data = config_collection.find_one({"guild_id": guild_id})
    if data:
        return data.get("log_channel"), data.get("welcome_channel")
    return None, None

def debug_db():
    """Debug function to print all documents in the config collection"""
    print("\n=== DEBUG: MongoDB Config Collection ===")
    for doc in config_collection.find():
        print(f"Document: {doc}")
    print("=== End of MongoDB Debug ===\n")



app = Flask(__name__)


def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


# Then start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()


@app.route('/')
def home():
    return "Bread Bot is running! 🍞"


@app.route('/health')
def health():
    return {"status": "healthy", "bot": "online"}


def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


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

TIME_ID = 1413747681163087893
PING_URL = "https://bread-bot-8rqr.onrender.com/"


async def keep_alive_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(TIME_ID)

    if channel is None:
        print(f"❌ Could not find channel with ID {TIME_ID}")
        return

    while not bot.is_closed():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(PING_URL) as resp:
                    status = resp.status
            embed = discord.Embed(
                title="🌐 Keep Alive Ping",
                description=f"Pinged `{PING_URL}`",
                color=discord.Color.green(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Status", value=f"{status}", inline=True)
            await channel.send(embed=embed)
            print(f"[KeepAlive] Sent ping with status {status}")
        except Exception as e:
            embed = discord.Embed(
                title="⚠️ Keep Alive Error",
                description=f"Failed to ping `{PING_URL}`",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
            embed.add_field(name="Error", value=str(e), inline=False)
            await channel.send(embed=embed)
            print(f"[KeepAlive] Error: {e}")

        await asyncio.sleep(300)  # every 5 minutes


# ✅ attach setup_hook to bot before bot.run()
async def setup_hook():
    bot.add_bg_task = asyncio.create_task(keep_alive_task())


bot.setup_hook = setup_hook


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user} (ID: {bot.user.id})')
    print('------')
    try:
        synced = await bot.tree.sync()  # global sync
        print(f"🌍 Synced {len(synced)} global command(s)")

        if len(synced) == 0:
            print("⚠️ No global commands were synced. "
                  "Remember: global slash commands may take up to 1 hour to appear for everyone.")
        else:
            print("✅ Global commands registered. "
                  "It may take up to 1 hour before all users see them.")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


# Name of the secret role this is test
secret_role = "bot test"
GUILD_ID = 1247215187799572643
BOT_OWNER_ID = 993607806915706891


# Add this at the top with other variables
bot_start_time = None
default_filter_words = ["fuck", "shit", "bitch", "nigger", "nigga", "niggers", "niggas", "nigguh", "nigguhs", "dick",
                        "gay"]
global custom_filter_words
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


@bot.command()
async def hello(ctx):
    """Say hello to the bot (prefix command)"""
    await ctx.send(f"Hello, {ctx.author.mention}! 👋")


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


@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    """Kick a member from the server (prefix command)"""
    if not ctx.guild.me.guild_permissions.kick_members:
        await ctx.send("❌ I don't have permission to kick members!")
        return

    # Check if the target user is the command invoker
    if member == ctx.author:
        await ctx.send("❌ You can't kick yourself!")
        return

    # Check if the target user is the server owner
    if member == ctx.guild.owner:
        await ctx.send("❌ You can't kick the server owner!")
        return

    # Check if the target user has a higher role than the bot
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I can't kick someone with a role higher or equal to mine!")
        return

    # Check if the target user has a higher role than the command invoker
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't kick someone with a role higher or equal to yours!")
        return

    try:
        # Send DM to the user before kicking
        try:
            await member.send(f"You have been kicked from **{ctx.guild.name}**\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Kick the user
        await member.kick(reason=f"{reason} (kicked by {ctx.author})")

        # Send confirmation message
        await ctx.send(f"✅ {member.mention} has been kicked!\nReason: {reason}")

        # Log the kick
        await send_mod_log(
            guild=ctx.guild,
            title="👢 Member Kicked",
            description=f"{member.mention} has been kicked from the server.",
            color=0xff9900,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", ctx.author.mention, True),
                ("Reason", reason, True),
                ("Account Created", discord.utils.format_dt(member.created_at, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Kick Failed",
            description=f"Failed to kick {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ]
        )


@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="The member to kick", reason="Reason for kicking")
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!",
                                                ephemeral=True)
        return

    # Check if bot has kick permissions
    if not interaction.guild.me.guild_permissions.kick_members:
        await interaction.response.send_message("❌ I don't have permission to kick members!", ephemeral=True)
        return

    # Prevent kicking self
    if member == interaction.user:
        await interaction.response.send_message("❌ You can't kick yourself!", ephemeral=True)
        return

    # Prevent kicking the bot
    if member == interaction.guild.me:
        await interaction.response.send_message("❌ You can't kick me!", ephemeral=True)
        return

    # Prevent kicking someone with equal or higher roles
    if member.top_role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
        await interaction.response.send_message("❌ You can't kick someone with equal or higher roles!", ephemeral=True)
        return

    try:
        # Send DM to the user before kicking
        try:
            await member.send(f"You have been kicked from **{interaction.guild.name}**\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Kick the user
        await member.kick(reason=f"{reason} (kicked by {interaction.user})")

        # Send confirmation message
        await interaction.response.send_message(f"✅ {member.mention} has been kicked!\nReason: {reason}")

        # Log the kick
        await send_mod_log(
            guild=interaction.guild,
            title="👢 Member Kicked",
            description=f"{member.mention} has been kicked from the server.",
            color=0xff9900,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", interaction.user.mention, True),
                ("Reason", reason, True),
                ("Account Created", discord.utils.format_dt(member.created_at, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )

    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)
        # Log the error
        await send_mod_log(
            guild=interaction.guild,
            title="❌ Kick Failed",
            description=f"Failed to kick {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", interaction.user.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ]
        )


@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="The member to ban", reason="Reason for banning")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!",
                                                ephemeral=True)
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

        # After successfully banning the member, log it
        if BAN_LOG_CHANNEL_ID:
            log_channel = interaction.guild.get_channel(BAN_LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🚫 Member Banned",
                    description=f"{member.mention} was banned by {interaction.user.mention}",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                embed.add_field(name="User ID", value=str(member.id), inline=True)
                embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

                try:
                    await log_channel.send(embed=embed)
                except Exception as e:
                    print(f"Failed to send ban log: {e}")

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
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 10,
               reason: str = "No reason provided"):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You need moderate members permissions to use this command!",
                                                ephemeral=True)
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
        timeout_duration = discord.utils.utcnow() + datetime.timedelta(minutes=duration)

        await member.timeout(timeout_duration, reason=reason)
        await interaction.response.send_message(
            f"✅ {member.mention} has been muted for {duration} minutes!\nReason: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to timeout this member!", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)


@bot.command()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, duration: int = 10, *, reason="No reason provided"):
    """Mute a member for a specified duration (in minutes)"""
    # Check if bot has timeout permissions
    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("❌ I don't have permission to timeout members!")
        return

    # Prevent muting self
    if member == ctx.author:
        await ctx.send("❌ You can't mute yourself!")
        return

    # Prevent muting someone with equal or higher roles
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't mute someone with equal or higher roles!")
        return

    # Prevent muting the bot
    if member == ctx.guild.me:
        await ctx.send("❌ You can't mute me!")
        return

    try:
        # Calculate timeout duration
        timeout_until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)

        # Send DM to the user before muting
        try:
            await member.send(f"You have been muted in **{ctx.guild.name}** for {duration} minutes.\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Apply the timeout
        await member.timeout(timeout_until, reason=f"{reason} (by {ctx.author})")

        # Send confirmation message
        await ctx.send(f"✅ {member.mention} has been muted for {duration} minutes!\nReason: {reason}")

        # Log the mute
        await send_mod_log(
            guild=ctx.guild,
            title="🔇 Member Muted",
            description=f"{member.mention} has been muted for {duration} minutes.",
            color=0xffa500,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", ctx.author.mention, True),
                ("Duration", f"{duration} minutes", True),
                ("Reason", reason, True),
                ("Muted Until", discord.utils.format_dt(timeout_until, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to timeout this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Mute Failed",
            description=f"Failed to mute {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ])
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("❌ You need moderate members permissions to use this command!",
                                                ephemeral=True)
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
        await interaction.response.send_message("❌ You can't unmute someone with equal or higher roles!",
                                                ephemeral=True)
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
        await interaction.response.send_message(f"✅ Broadcasted message to {channel_count} channels {ping_status}!",
                                                ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)


@bot.tree.command(name="setwelcome", description="Set the welcome channel for new members")
@app_commands.describe(channel="The channel to send welcome messages in")
@commands.has_permissions(administrator=True)
async def set_welcome_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    """Set the welcome channel for new members (slash command)"""
    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await interaction.response.send_message(f"✅ Welcome channel set to {channel.mention}", ephemeral=True)


async def send_mod_log(guild: discord.Guild, title: str, description: str, color: int, fields: list = None,
                       thumbnail: str = None):
    """Helper function to send mod logs to the log channel"""
    global LOG_CHANNEL_ID
    if not LOG_CHANNEL_ID:
        return False

    try:
        log_channel = guild.get_channel(LOG_CHANNEL_ID)
        if not log_channel:
            return False

        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=discord.utils.utcnow()
        )

        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

        if thumbnail:
            embed.set_thumbnail(url=thumbnail)

        await log_channel.send(embed=embed)
        return True
    except Exception as e:
        print(f"Failed to send mod log: {e}")
        return False


# Removed duplicate setlogchannel command - using the setlog command instead
# The slash command is now handled by the main setlog command with app_commands


@bot.event
async def on_ready():
    global bot_start_time
    bot_start_time = discord.utils.utcnow()  # Record when bot came online

    print(f"We are ready to go in, {bot.user.name}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} global commands: {[cmd.name for cmd in synced]}")
        # Print debug info on startup
        debug_db()
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


# new members
@bot.event
async def on_member_join(member):
    """Handle new member joining the server"""
    # Send DM
    try:
        await member.send(f"Welcome to the server {member.name}")
    except Exception as e:
        print(f"Failed to send DM to {member.name}: {e}")

    # Get welcome channel from database
    _, welcome_channel_id = load_config(member.guild.id)
    
    # Send embed to welcome channel if set
    if welcome_channel_id:
        channel = member.guild.get_channel(welcome_channel_id)
        if channel:
            embed = discord.Embed(
                title="Welcome!",
                description=f"{member.mention} has joined the server!",
                color=discord.Color.green()
            )
            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)
            await channel.send(embed=embed)


@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return

    # Handle DM messages
    if isinstance(message.channel, discord.DMChannel):
        if message.content.startswith('bread '):
            await message.channel.send("Hello! You cannot use prefix commands in DMs, use slash commands instead.")
        return

    # Check for filtered words (only in guilds, and only if it's not a command)
    if message.guild and not message.content.startswith('bread '):
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
                    return
                except discord.Forbidden:
                    print(f"❌ No permission to delete message from {message.author}")
                except Exception as e:
                    print(f"❌ Error deleting message: {e}")

    # Let the bot process commands naturally
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
        await interaction.response.send_message("❌ You need Administrator permissions to use this command!",
                                                ephemeral=True)
        return

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
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action == "list":
        # Show uncensored words for moderators
        word_list = ", ".join([f"`{word}`" for word in custom_filter_words])

        embed = discord.Embed(
            title="📝 Chat Filter List",
            description=f"Currently filtering {len(custom_filter_words)} words:",
            color=0x0099ff
        )
        embed.add_field(name="Filtered Words", value=word_list or "No words in filter", inline=False)
        embed.set_footer(text=f"Requested by {interaction.user.name}")

        try:
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("📝 Filter list sent to your DMs!", ephemeral=True, delete_after=5)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I can't send you a DM! Please enable DMs from server members.",
                ephemeral=True,
                delete_after=10
            )

    else:
        await interaction.response.send_message(
            "❌ Invalid action! Use: `add`, `remove`, `list`, or `reset`",
            ephemeral=True
        )


@bot.command()
@commands.has_permissions(administrator=True)
async def filter(ctx, action=None, *, word=None):
    """Manage the chat filter (prefix command)

    Actions:
    - add <word>: Add a word to the filter
    - remove <word>: Remove a word from the filter
    - list: List all filtered words
    - reset: Reset filter to default words
    """
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
        await ctx.send(f"✅ Added `{word}` to the filter!")

        # Log the filter addition
        await send_mod_log(
            guild=ctx.guild,
            title="🚫 Filter Word Added",
            description=f"`{word}` was added to the chat filter.",
            color=0xff0000,
            fields=[
                ("Word", f"`{word}`", True),
                ("Moderator", ctx.author.mention, True),
                ("Total Words", str(len(custom_filter_words)), True)
            ]
        )

    elif action == "remove":
        if not word:
            await ctx.send("❌ Please provide a word to remove!")
            return

        word = word.lower()
        if word not in custom_filter_words:
            await ctx.send(f"❌ `{word}` is not in the filter!")
            return

        custom_filter_words.remove(word)
        await ctx.send(f"✅ Removed `{word}` from the filter!")

        # Log the filter removal
        await send_mod_log(
            guild=ctx.guild,
            title="✅ Filter Word Removed",
            description=f"`{word}` was removed from the chat filter.",
            color=0x00ff00,
            fields=[
                ("Word", f"`{word}`", True),
                ("Moderator", ctx.author.mention, True),
                ("Total Words", str(len(custom_filter_words)), True)
            ]
        )

    elif action == "list":
        if not custom_filter_words:
            await ctx.send("The filter is currently empty!")
            return

        # Split the list into chunks to avoid hitting embed field value limits
        chunk_size = 20
        chunks = [custom_filter_words[i:i + chunk_size] for i in range(0, len(custom_filter_words), chunk_size)]

        embed = discord.Embed(
            title=f"🚫 Filtered Words ({len(custom_filter_words)} total)",
            color=0xff0000
        )

        for i, chunk in enumerate(chunks, 1):
            filter_list = "\n".join([f"• `{w}`" for w in chunk])
            embed.add_field(
                name=f"Words {((i - 1) * chunk_size) + 1}-{min(i * chunk_size, len(custom_filter_words))}",
                value=filter_list,
                inline=False
            )

        embed.set_footer(text=f"Requested by {ctx.author}")

        try:
            await ctx.author.send(embed=embed)
            await ctx.send("📝 Filter list sent to your DMs!", delete_after=3)
        except discord.Forbidden:
            await ctx.send("❌ I can't send you a DM! Please enable DMs from server members.", delete_after=5)

        # Log the filter list view
        await send_mod_log(
            guild=ctx.guild,
            title="📋 Filter List Viewed",
            description=f"{ctx.author.mention} viewed the filter list.",
            color=0x3498db,
            fields=[
                ("Total Words", str(len(custom_filter_words)), True),
                ("Moderator", ctx.author.mention, True)
            ]
        )

    elif action == "reset":
        # Log the reset with before/after counts
        old_count = len(custom_filter_words)
        custom_filter_words = default_filter_words.copy()
        new_count = len(custom_filter_words)

        embed = discord.Embed(
            title="🔄 Filter Reset",
            description="Chat filter has been reset to default settings",
            color=0xff0000
        )
        embed.add_field(name="Previous Word Count", value=str(old_count), inline=True)
        embed.add_field(name="New Word Count", value=str(new_count), inline=True)
        embed.set_footer(text=f"Reset by {ctx.author}")

        await ctx.send(embed=embed)

        # Log the filter reset
        await send_mod_log(
            guild=ctx.guild,
            title="🔄 Filter Reset",
            description="Chat filter was reset to default words.",
            color=0xff0000,
            fields=[
                ("Previous Words", str(old_count), True),
                ("New Words", str(new_count), True),
                ("Moderator", ctx.author.mention, True)
            ]
        )

    else:
        await ctx.send("❌ Invalid action! Use: `add`, `remove`, `list`, or `reset`")
        return


@bot.command()
@commands.has_permissions(administrator=True)
async def broadcast(ctx, *, message):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("No one wants to hear you talking")
        return

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


@bot.tree.command(name="setchannel", description="Set up log and welcome channels")
async def set_channel(
    interaction: discord.Interaction,
    log_channel: discord.TextChannel = None,
    welcome_channel: discord.TextChannel = None
):
    """Set up log and welcome channels for the server"""
    try:
        if not any([log_channel, welcome_channel]):
            return await interaction.response.send_message(
                "Please specify at least one channel (log_channel or welcome_channel).",
                ephemeral=True
            )
        
        # Get current config
        current_log, current_welcome = load_config(interaction.guild_id)
        
        # Update config with new values
        new_log = log_channel.id if log_channel else current_log
        new_welcome = welcome_channel.id if welcome_channel else current_welcome
        
        # Save to MongoDB
        save_config(
            guild_id=interaction.guild_id,
            log_channel=new_log,
            welcome_channel=new_welcome
        )
        
        # Prepare response
        response = "✅ Channel configuration updated!\n"
        if log_channel:
            response += f"- Log Channel: {log_channel.mention}\n"
        if welcome_channel:
            response += f"- Welcome Channel: {welcome_channel.mention}"
            
        await interaction.response.send_message(response, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}",
            ephemeral=True
        )

@bot.command(name='setlog', aliases=['setlogchannel'], help='Set the log channel for moderation logs')
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel = None):
    """Set the log channel for moderation logs (prefix command)"""
    if not channel:
        channel = ctx.channel
        
    try:
        # Get current config
        _, current_welcome = load_config(ctx.guild.id)
        
        # Save to MongoDB
        save_config(
            guild_id=ctx.guild.id,
            log_channel=channel.id,
            welcome_channel=current_welcome  # Keep existing welcome channel
        )
        
        # Update global variable
        global LOG_CHANNEL_ID
        LOG_CHANNEL_ID = channel.id
        
        # Send confirmation
        await ctx.send(f"✅ Log channel set to {channel.mention}")
        
        # Send a test log
        await send_mod_log(
            guild=ctx.guild,
            title="🔧 Log Channel Set",
            description="Moderation logs will now be sent to this channel.",
            color=0x00ff00,
            fields=[
                ("Set by", ctx.author.mention, True),
                ("Channel", channel.mention, True)
            ]
        )
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# Removed duplicate setwelcome command - using the one at line 1792 instead

@bot.command(name='getchannels', aliases=['channels'], help='Show current channel configuration')
async def getchannels(ctx):
    """Show the current channel configuration (prefix command)"""
    try:
        # Get current config
        log_channel_id, welcome_channel_id = load_config(ctx.guild.id)
        
        # Create embed
        embed = discord.Embed(
            title="Channel Configuration",
            description=f"Current channel settings for {ctx.guild.name}",
            color=discord.Color.blue()
        )
        
        # Add fields
        embed.add_field(
            name="Log Channel",
            value=f"<#{log_channel_id}>" if log_channel_id else "Not set",
            inline=False
        )
        
        embed.add_field(
            name="Welcome Channel",
            value=f"<#{welcome_channel_id}>" if welcome_channel_id else "Not set",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.tree.command(name="getchannels", description="Show current channel configuration")
async def get_channels(interaction: discord.Interaction):
    """Show the current channel configuration for this server"""
    try:
        # Get current config
        log_channel_id, welcome_channel_id = load_config(interaction.guild_id)
        
        # Create embed
        embed = discord.Embed(
            title="Channel Configuration",
            description=f"Current channel settings for {interaction.guild.name}",
            color=discord.Color.blue()
        )
        
        # Add fields
        embed.add_field(
            name="Log Channel",
            value=f"<#{log_channel_id}>" if log_channel_id else "Not set",
            inline=False
        )
        
        embed.add_field(
            name="Welcome Channel",
            value=f"<#{welcome_channel_id}>" if welcome_channel_id else "Not set",
            inline=False
        )
        
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    except Exception as e:
        await interaction.response.send_message(
            f"❌ An error occurred: {str(e)}",
            ephemeral=True
        )


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int = 10, *, reason="No reason provided"):
    """Purge messages from the current channel (prefix command)"""
    if not ctx.guild.me.guild_permissions.manage_messages:
        await ctx.send("❌ I don't have permission to manage messages!")
        return

    if limit > 100:
        await ctx.send("❌ Maximum purge limit is 100 messages!")
        return

    try:
        # Purge messages (limit + 1 to include the command message)
        deleted = await ctx.channel.purge(limit=limit + 1, before=ctx.message)
        deleted_count = len(deleted) - 1  # Exclude the command message

        # Send confirmation message
        message = await ctx.send(f"✅ Purged {deleted_count} messages!", delete_after=5)

        # Log the purge
        await send_mod_log(
            guild=ctx.guild,
            title="🗑️ Messages Purged",
            description=f"{deleted_count} messages were purged in {ctx.channel.mention}.",
            color=0x3498db,
            fields=[
                ("Channel", ctx.channel.mention, True),
                ("Moderator", ctx.author.mention, True),
                ("Message Count", str(deleted_count), True),
                ("Reason", reason, False)
            ]
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to manage messages in this channel!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Purge Failed",
            description=f"Failed to purge messages in {ctx.channel.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Channel", ctx.channel.mention, True)
            ]
        )


@bot.command()
async def help(ctx, *, command_name=None):
    """Show help for bot commands"""
    if command_name:
        # Show detailed help for specific command
        command = bot.get_command(command_name.lower())
        if not command:
            await ctx.send(f"❌ Command `{command_name}` not found! Use `bread help` to see all commands.")
            return

        embed = discord.Embed(
            title=f"🍞 Help: bread {command.name}",
            description=command.help or "No description available.",
            color=0x00ff00
        )

        # Add usage examples based on command
        usage = f"`bread {command.name}`"
        if command.clean_params:
            params = []
            for name, param in command.clean_params.items():
                if param.default == param.empty:
                    params.append(f"<{name}>")
                else:
                    params.append(f"[{name}]")
            usage = f"`bread {command.name} {' '.join(params)}`"

        embed.add_field(name="Usage", value=usage, inline=False)

        # Add common examples
        examples = {
            "ban": "`bread ban @user Breaking rules`\n`bread ban @user 7d Spamming (bans for 7 days)`",
            "mute": "`bread mute @user 30 Spamming`\n`bread mute @user 1h Being rude`",
            "unmute": "`bread unmute @user`\n`bread unmute @user Time served`",
            "kick": "`bread kick @user Breaking rules`\n`bread kick @user Repeated warnings`",
            "purge": "`bread purge 50`\n`bread purge 10 Cleaning up`",
            "lock": "`bread lock #general`\n`bread lock #general Under maintenance`",
            "unlock": "`bread unlock #general`\n`bread unlock #general Maintenance complete`",
            "filter": "`bread filter add badword`\n`bread filter remove badword`\n`bread filter list`\n`bread filter reset`",
            "setlog": "`bread setlog #mod-logs`\n`bread setlog` (uses current channel)\nAlias: `setlogchannel`",
            "setwelcome": "`bread setwelcome #welcome`\n`bread setwelcome` (uses current channel)",
            "getchannels": "`bread getchannels`\n`bread channels` (alternative)",
            "setchannel": "`bread setchannel #log-channel #welcome-channel`\n`bread setchannel #log-channel` (set only log)\n`bread setchannel` (use current channel for both)",
            "setlogchannel": "Alias for `setlog`",
            "broadcast": "`bread broadcast Hello everyone!`\n`bread broadcast ping Important announcement!`"
        }

        if command.name in examples:
            embed.add_field(name="Examples", value=examples[command.name], inline=False)

        # Add required permissions if any
        if command.checks:
            perms = []
            if commands.has_permissions(administrator=True) in command.checks:
                perms.append("Administrator")
            if commands.has_permissions(manage_messages=True) in command.checks:
                perms.append("Manage Messages")
            if commands.has_permissions(manage_channels=True) in command.checks:
                perms.append("Manage Channels")
            if commands.has_permissions(ban_members=True) in command.checks:
                perms.append("Ban Members")
            if commands.has_permissions(kick_members=True) in command.checks:
                perms.append("Kick Members")
            if commands.has_permissions(moderate_members=True) in command.checks:
                perms.append("Moderate Members")

            if perms:
                embed.add_field(name="Required Permissions", value=", ".join(perms), inline=False)

        await ctx.send(embed=embed)
        return

    # Create main help embed
    embed = discord.Embed(
        title="🍞 Bread Bot - Command Reference",
        description="**Available Commands** • Use `bread help <command>` for detailed info",
        color=0x00ff00
    )

    # Add bot avatar
    embed.set_thumbnail(url=ctx.bot.user.avatar.url if ctx.bot.user.avatar else None)

    # 🔹 GENERAL COMMANDS (always visible)
    general_commands = [
        ("hello", "Say hello to the bot"),
        ("me", "Show your Discord and server information"),
        ("status", "Display bot status and statistics"),
        ("help [command]", "Show this help or get help for a specific command"),
        ("dm <message>", "Send yourself a DM with the specified message"),
        ("getchannels", "Show current log and welcome channel settings"),
        ("channels", "Alias for getchannels")
    ]

    general_text = "\n".join([f"`bread {cmd}` - {desc}" for cmd, desc in general_commands])
    embed.add_field(
        name="🔹 General Commands",
        value=general_text,
        inline=False
    )

    # Check user permissions
    has_mod_perms = any([
        ctx.author.guild_permissions.moderate_members,
        ctx.author.guild_permissions.manage_roles,
        ctx.author.guild_permissions.manage_messages,
        ctx.author.guild_permissions.administrator
    ])

    # 🔨 MODERATION COMMANDS (for users with mod permissions)
    mod_commands = [
        ("ban @user [reason]", "Ban a user from the server"),
        ("unban user#1234 [reason]", "Unban a user"),
        ("kick @user [reason]", "Kick a user from the server"),
        ("mute @user [duration] [reason]", "Mute a user (default: 10m)"),
        ("unmute @user [reason]", "Unmute a user"),
        ("purge [amount] [reason]", "Delete messages (default: 10, max: 2000)"),
        ("filter <add|remove|list|reset> [word]", "Manage filtered words"),
        ("lock [#channel] [reason]", "Lock a channel (default: current)"),
        ("unlock [#channel] [reason]", "Unlock a channel"),
        ("setlog [#channel]", "Set log channel (default: current)"),
        ("setwelcome [#channel]", "Set welcome channel (default: current)"),
        ("setchannel [#log] [#welcome]", "Set both channels at once")
    ]

    mod_text = "\n".join([f"`bread {cmd}` - {desc}" for cmd, desc in mod_commands])
    embed.add_field(
        name="🔨 Moderation Commands",
        value=mod_text,
        inline=False
    )

    # ⚙️ ADMIN COMMANDS (for administrators only)
    if ctx.author.guild_permissions.administrator:
        admin_commands = [
            ("filter <add/remove/list/reset> [word]", "Manage the automatic chat filter"),
            ("setwelcome [#channel]", "Set welcome channel for new members"),
            ("setlogchannel [#channel]", "Set channel for moderation logs"),
            ("broadcast <message>", "Send a message to all text channels")
        ]

        admin_text = "\n".join([f"`bread {cmd}` - {desc}" for cmd, desc in admin_commands])
        embed.add_field(
            name="⚙️ Administrator Commands",
            value=admin_text,
            inline=False
        )

    # ⚡ SLASH COMMANDS INFO
    slash_info = (
        "**💡 Tip:** Most commands also work as slash commands!\n"
        "• Type `/` to see available slash commands\n"
        "• Example: `bread hello` = `/hello`"
    )
    embed.add_field(
        name="⚡ Slash Commands",
        value=slash_info,
        inline=False
    )

    # Footer with usage instructions
    permissions_note = ""
    if not has_mod_perms:
        permissions_note = " • 🔒 Some commands hidden (need permissions)"

    embed.set_footer(
        text=f"Use 'bread help <command>' for detailed info{permissions_note}"
    )

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
            roles_text = ", ".join(roles) if len(
                roles) <= 10 else f"{', '.join(roles[:10])}... (+{len(roles) - 10} more)"
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
    admin_commands = [
        "broadcast", "kick", "ban", "mute", "unmute", "purge", "lock", "unlock", "filter", "setwelcome", "setbanlog"
    ]

    if command:
        command = command.lower()

        # Permission check
        if command in admin_commands and not (
                interaction.user.guild_permissions.moderate_members or
                interaction.user.guild_permissions.manage_channels or
                interaction.user.guild_permissions.manage_roles or
                interaction.user.guild_permissions.manage_messages or
                interaction.user.guild_permissions.administrator
        ):
            await interaction.response.send_message(
                "❌ You don't have permission to view this command!",
                ephemeral=True
            )
            return

        # Command examples and descriptions
        command_info = {
            "hello": {
                "description": "Say hello to the bot",
                "usage": "`/hello` or `bread hello`",
                "example": "`/hello`\n`bread hello`"
            },
            "me": {
                "description": "Show your Discord and server information",
                "usage": "`/me` or `bread me`",
                "example": "`/me`"
            },
            "status": {
                "description": "Show bot status and statistics",
                "usage": "`/status` or `bread status`",
                "example": "`/status`"
            },
            "kick": {
                "description": "Kick a member from the server",
                "usage": "`/kick member:<@user> [reason:<text>]` or `bread kick @user [reason]`",
                "example": "`/kick member:@user reason:Breaking rules`\n`bread kick @user Breaking rules`"
            },
            "ban": {
                "description": "Ban a member from the server",
                "usage": "`/ban member:<@user> [duration:<time>] [reason:<text>]` or `bread ban @user [duration] [reason]`",
                "example": "`/ban member:@user duration:7d reason:Breaking rules`\n`bread ban @user 7d Breaking rules`"
            },
            "unban": {
                "description": "Unban a user from the server",
                "usage": "`/unban user:<user_id> [reason:<text>]` or `bread unban userid [reason]`",
                "example": "`/unban user:1234567890 reason:Appealed ban`\n`bread unban 1234567890 Appealed ban`"
            },
            "mute": {
                "description": "Mute a member for a specified duration",
                "usage": "`/mute member:<@user> [duration:<minutes>] [reason:<text>]` or `bread mute @user [duration] [reason]`",
                "example": "`/mute member:@user duration:30 reason:Spamming`\n`bread mute @user 30 Spamming`"
            },
            "unmute": {
                "description": "Unmute a member",
                "usage": "`/unmute member:<@user> [reason:<text>]` or `bread unmute @user [reason]`",
                "example": "`/unmute member:@user reason:Time served`\n`bread unmute @user Time served`"
            },
            "purge": {
                "description": "Delete messages from the current channel",
                "usage": "`/purge [amount:<1-100>] [reason:<text>]` or `bread purge [amount] [reason]`",
                "example": "`/purge amount:50 reason:Cleaning up`\n`bread purge 50 Cleaning up`"
            },
            "lock": {
                "description": "Lock a channel to prevent members from sending messages",
                "usage": "`/lock [channel:<#channel>] [reason:<text>]` or `bread lock [#channel] [reason]`",
                "example": "`/lock channel:#general reason:Under maintenance`\n`bread lock #general Under maintenance`"
            },
            "unlock": {
                "description": "Unlock a previously locked channel",
                "usage": "`/unlock [channel:<#channel>] [reason:<text>]` or `bread unlock [#channel] [reason]`",
                "example": "`/unlock channel:#general reason:Maintenance complete`\n`bread unlock #general Maintenance complete`"
            },
            "filter": {
                "description": "Manage the chat filter (add/remove/list/reset words)",
                "usage": "`/filter action:<add/remove/list/reset> [word:<text>]` or `bread filter <action> [word]`",
                "example": "`/filter action:add word:badword`\n`bread filter add badword`"
            },
            "setwelcome": {
                "description": "Set the welcome channel for new members",
                "usage": "`/setwelcome [channel:<#channel>]` or `bread setwelcome [#channel]`",
                "example": "`/setwelcome channel:#welcome`\n`bread setwelcome #welcome`"
            },
            "setlogchannel": {
                "description": "Set the channel for moderation logs",
                "usage": "`/setlogchannel [channel:<#channel>]` or `bread setlogchannel [#channel]`",
                "example": "`/setlogchannel channel:#mod-logs`\n`bread setlogchannel #mod-logs`"
            },
            "broadcast": {
                "description": "Send a message to all channels in the server",
                "usage": "`/broadcast message:<text> [ping:<true/false>]` or `bread broadcast [message]`",
                "example": "`/broadcast message:Server restart in 5 minutes ping:true`\n`bread broadcast ping Server restart in 5 minutes`"
            }
        }.get(command.lower())

        if not command_info:
            await interaction.response.send_message("❌ Command not found!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"ℹ️ Help: /{command.lower()}",
            description=command_info["description"],
            color=0x00ff00
        )

        # Add command usage and examples
        embed.add_field(name="Usage", value=command_info["usage"], inline=False)
        embed.add_field(name="Examples", value=command_info["example"], inline=False)

        # Add required permissions if any
        if command.lower() in ["filter", "setwelcome", "setlogchannel", "broadcast"]:
            embed.add_field(name="Required Permissions", value="Administrator", inline=False)
        elif command.lower() in ["kick", "ban", "mute", "unmute", "purge", "lock", "unlock"]:
            embed.add_field(
                name="Required Permissions",
                value="Moderate Members, Manage Roles, or Manage Messages",
                inline=False
            )

        await interaction.response.send_message(embed=embed)
        return

    # Main help command (no specific command requested)
    embed = discord.Embed(
        title="🍞 Bread Bot Commands",
        description="Here are all available commands. Use `/help <command>` for more info on a specific command.",
        color=0x00ff00
    )

    # Add bot avatar
    if interaction.guild and interaction.guild.me.avatar:
        embed.set_thumbnail(url=interaction.guild.me.avatar.url)
    elif interaction.client.user.avatar:
        embed.set_thumbnail(url=interaction.client.user.avatar.url)

    # General Commands (always visible)
    general_commands = [
        ("/hello | bread hello", "Say hello to the bot"),
        ("/me | bread me", "Show your Discord and server info"),
        ("/status | bread status", "Show bot status and statistics"),
        ("/help [command] | bread help [command]", "Show this help or get help for a specific command")
    ]

    # Format general commands
    general_text = "\n".join([f"`{cmd}` - {desc}" for cmd, desc in general_commands])

    # Add general commands section
    embed.add_field(
        name="🔹 General Commands",
        value=general_text,
        inline=False
    )

    # Check for mod permissions
    has_mod_perms = any([
        interaction.user.guild_permissions.moderate_members,
        interaction.user.guild_permissions.manage_roles,
        interaction.user.guild_permissions.manage_messages,
        interaction.user.guild_permissions.administrator
    ])

    if has_mod_perms:
        # Moderation Commands
        mod_commands = [
            ("/kick @user [reason] | bread kick @user [reason]", "Kick a member from the server"),
            ("/ban @user [duration] [reason] | bread ban @user [reason]", "Ban a member from the server"),
            ("/unban userid [reason] | bread unban userid [reason]", "Unban a user by their ID"),
            ("/mute @user [duration] [reason] | bread mute @user [duration] [reason]",
             "Mute a member for a specified duration"),
            ("/unmute @user [reason] | bread unmute @user [reason]", "Unmute a member"),
            ("/purge [amount] [reason] | bread purge [amount] [reason]", "Delete messages (default: 10, max: 100)"),
            ("/lock [#channel] [reason] | bread lock [#channel] [reason]",
             "Lock a channel (current channel if none specified)"),
            ("/unlock [#channel] [reason] | bread unlock [#channel] [reason]",
             "Unlock a channel (current channel if none specified)")
        ]

        # Format moderation commands
        mod_text = "\n".join([f"`{cmd}` - {desc}" for cmd, desc in mod_commands])

        # Add moderation commands section
        embed.add_field(
            name="🔨 Moderation Commands",
            value=mod_text,
            inline=False
        )

    # Admin Commands (for users with admin permissions)
    if interaction.user.guild_permissions.administrator:
        admin_commands = [
            ("/filter <action> [word] | bread filter <action> [word]",
             "Manage the chat filter (add/remove/list/reset)"),
            ("/setwelcome [#channel] | bread setwelcome [#channel]",
             "Set the welcome channel (current channel if none specified)"),
            ("/setlogchannel [#channel] | bread setlogchannel [#channel]",
             "Set the log channel (current channel if none specified)"),
            ("/broadcast [message] | bread broadcast [message]", "Send a message to all channels")
        ]

        # Format admin commands
        admin_text = "\n".join([f"`{cmd}` - {desc}" for cmd, desc in admin_commands])

        # Add admin commands section
        embed.add_field(
            name="⚙️ Admin Commands",
            value=admin_text,
            inline=False
        )

    # Add footer with usage instructions
    permissions_note = ""
    if not has_mod_perms:
        permissions_note = "\n🔒 Some commands are hidden. Ask a moderator for access."

    embed.set_footer(
        text=f"Use '/help <command>' or 'bread help <command>' for detailed help about a command.{permissions_note}"
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.command(name='setwelcome', help='Set the welcome channel')
@commands.has_permissions(administrator=True)
async def setwelcome(ctx, channel: discord.TextChannel = None):
    """Set the welcome channel for new members (prefix command)"""
    if not channel:
        channel = ctx.channel
        
    try:
        # Get current config
        current_log, _ = load_config(ctx.guild.id)
        
        # Save to MongoDB
        save_config(
            guild_id=ctx.guild.id,
            log_channel=current_log,  # Keep existing log channel
            welcome_channel=channel.id
        )
        
        await ctx.send(f"✅ Welcome channel set to {channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

    global WELCOME_CHANNEL_ID
    WELCOME_CHANNEL_ID = channel.id
    await ctx.send(f"✅ Welcome channel set to {channel.mention}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    """Ban a member from the server (prefix command)"""
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ I don't have permission to ban members!")
        return

    # Check if the target user is the command invoker
    if member == ctx.author:
        await ctx.send("❌ You can't ban yourself!")
        return

    # Check if the target user is the server owner
    if member == ctx.guild.owner:
        await ctx.send("❌ You can't ban the server owner!")
        return

    # Check if the target user has a higher role than the bot
    if member.top_role >= ctx.guild.me.top_role:
        await ctx.send("❌ I can't ban someone with a role higher or equal to mine!")
        return

    # Check if the target user has a higher role than the command invoker
    if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("❌ You can't ban someone with a role higher or equal to yours!")
        return

    try:
        # Send DM to the user before banning
        try:
            await member.send(f"You have been banned from **{ctx.guild.name}**\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Ban the user
        await member.ban(reason=f"{reason} (banned by {ctx.author})", delete_message_days=7)

        # Send confirmation message
        await ctx.send(f"✅ {member.mention} has been banned!\nReason: {reason}")

        # Log the ban
        await send_mod_log(
            guild=ctx.guild,
            title="🔨 Member Banned",
            description=f"{member.mention} has been banned from the server.",
            color=0xff0000,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", ctx.author.mention, True),
                ("Reason", reason, True),
                ("Account Created", discord.utils.format_dt(member.created_at, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Ban Failed",
            description=f"Failed to ban {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ]
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")


@bot.tree.command(name="status", description="Show bot status and statistics")
async def slash_status(interaction: discord.Interaction):
    """Show bot status and statistics (slash command)"""
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
    user_count = sum(guild.member_count for guild in bot.guilds)
    embed.add_field(
        name="📊 Server Stats",
        value=f"**Servers:** {guild_count}\n**Total Users:** {user_count:,}\n**Current Server:** {interaction.guild.name}",
        inline=True
    )

    # Permissions check
    perms = interaction.guild.me.guild_permissions
    perm_status = "✅" if all([perms.kick_members, perms.ban_members, perms.manage_messages]) else "⚠️"
    embed.add_field(
        name="🔑 Bot Permissions",
        value=f"**Kick Members:** {'✅' if perms.kick_members else '❌'}\n**Ban Members:** {'✅' if perms.ban_members else '❌'}\n**Manage Messages:** {'✅' if perms.manage_messages else '❌'}\n**Status:** {perm_status}",
        inline=False
    )

    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unmute", description="Unmute a member")
@app_commands.describe(member="The member to unmute", reason="Reason for unmuting")
async def slash_unmute(interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
    """Unmute a member (slash command)"""
    # Check if user has moderate members permissions
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "❌ You need moderate members permissions to use this command!",
            ephemeral=True
        )
        return

    # Check if bot has moderate members permissions
    if not interaction.guild.me.guild_permissions.moderate_members:
        await interaction.response.send_message(
            "❌ I don't have permission to unmute members!",
            ephemeral=True
        )
        return

    # Check if member is actually muted
    if not member.is_timed_out():
        await interaction.response.send_message(
            f"❌ {member.mention} is not muted!",
            ephemeral=True
        )
        return

    try:
        # Send DM to the user before unmuting
        try:
            await member.send(f"You have been unmuted in **{interaction.guild.name}**.\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Remove the timeout
        await member.timeout(None, reason=f"{reason} (unmuted by {interaction.user})")

        # Send confirmation message
        await interaction.response.send_message(
            f"✅ {member.mention} has been unmuted!\nReason: {reason}"
        )

        # Log the unmute
        await send_mod_log(
            guild=interaction.guild,
            title="🔊 Member Unmuted",
            description=f"{member.mention} has been unmuted.",
            color=0x00ff00,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", interaction.user.mention, True),
                ("Reason", reason, True),
                ("Account Created", discord.utils.format_dt(member.created_at, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I don't have permission to unmute this member!",
            ephemeral=True
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ An error occurred: {e}", ephemeral=True)
        # Log the error
        await send_mod_log(
            guild=interaction.guild,
            title="❌ Unmute Failed",
            description=f"Failed to unmute {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", interaction.user.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ]
        )


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
            roles_text = ", ".join(roles) if len(
                roles) <= 10 else f"{', '.join(roles[:10])}... (+{len(roles) - 10} more)"
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
async def lock(interaction: discord.Interaction, channel: discord.TextChannel = None,
               reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You need Manage Channels permissions to use this command!",
                                                ephemeral=True)
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
async def unlock(interaction: discord.Interaction, channel: discord.TextChannel = None,
                 reason: str = "No reason provided"):
    if not interaction.user.guild_permissions.manage_channels:
        await interaction.response.send_message("❌ You need Manage Channels permissions to use this command!",
                                                ephemeral=True)
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
        return


@bot.command()
async def dm(ctx, *, message: str = None):
    if not message:
        await ctx.send("❌ Please provide a message to DM yourself!")
        return
    try:
        await ctx.author.send(message)
        await ctx.send("✅ DM sent!", delete_after=3)
    except discord.Forbidden:
        await ctx.send("❌ I can't send you a DM! Please enable DMs from server members.", delete_after=5)
        return


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User, *, reason="No reason provided"):
    if not ctx.guild.me.guild_permissions.ban_members:
        await ctx.send("❌ I don't have permission to unban members!")
        return

    try:
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f"✅ {user.mention} has been unbanned!\nReason: {reason}")
    except discord.NotFound:
        await ctx.send("❌ This user is not banned!")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unban this user!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
    return


@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member, *, reason="No reason provided"):
    """Unmute a member (prefix command)"""
    if not ctx.guild.me.guild_permissions.moderate_members:
        await ctx.send("❌ I don't have permission to unmute members!")
        return

    # Check if member is actually muted
    if not member.is_timed_out():
        await ctx.send(f"❌ {member.mention} is not muted!")
        return

    try:
        # Send DM to the user before unmuting
        try:
            await member.send(f"You have been unmuted in **{ctx.guild.name}**.\nReason: {reason}")
        except:
            pass  # User has DMs disabled or blocked the bot

        # Remove the timeout
        await member.timeout(None, reason=f"{reason} (unmuted by {ctx.author})")

        # Send confirmation message
        await ctx.send(f"✅ {member.mention} has been unmuted!\nReason: {reason}")

        # Log the unmute
        await send_mod_log(
            guild=ctx.guild,
            title="🔊 Member Unmuted",
            description=f"{member.mention} has been unmuted.",
            color=0x00ff00,
            fields=[
                ("User", f"{member} ({member.id})", False),
                ("Moderator", ctx.author.mention, True),
                ("Reason", reason, True),
                ("Account Created", discord.utils.format_dt(member.created_at, "R"), True)
            ],
            thumbnail=member.avatar.url if member.avatar else None
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to unmute this member!")
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Unmute Failed",
            description=f"Failed to unmute {member.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Target", f"{member} ({member.id})", True)
            ]
        )


@bot.command()
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
    """Lock a channel to prevent members from sending messages (prefix command)"""
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ I don't have permission to manage channels!")
        return

    target_channel = channel or ctx.channel

    try:
        # Get the everyone role and current permissions
        everyone_role = ctx.guild.default_role
        current_perms = target_channel.overwrites_for(everyone_role)

        # Check if channel is already locked
        if current_perms.send_messages is False:
            await ctx.send(f"❌ {target_channel.mention} is already locked!")
            return

        # Save the previous send_messages permission to restore it later
        previous_send_messages = current_perms.send_messages

        # Lock the channel
        await target_channel.set_permissions(
            everyone_role,
            send_messages=False,
            reason=f"{reason} (locked by {ctx.author})"
        )

        # Send confirmation message
        embed = discord.Embed(
            title="🔒 Channel Locked",
            description=f"{target_channel.mention} has been locked!",
            color=0xff0000
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Locked by", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

        # Log the channel lock
        await send_mod_log(
            guild=ctx.guild,
            title="🔒 Channel Locked",
            description=f"{target_channel.mention} has been locked.",
            color=0xff0000,
            fields=[
                ("Channel", target_channel.mention, True),
                ("Moderator", ctx.author.mention, True),
                ("Reason", reason, False),
                ("Previous Setting", "Allowed" if previous_send_messages is None else str(previous_send_messages), True)
            ]
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify this channel!")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Channel Lock Failed",
            description=f"Failed to lock {target_channel.mention}",
            color=0xff0000,
            fields=[
                ("Error", "Insufficient permissions", False),
                ("Moderator", ctx.author.mention, True),
                ("Channel", target_channel.mention, True)
            ]
        )
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Channel Lock Failed",
            description=f"Failed to lock {target_channel.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Channel", target_channel.mention, True)
            ]
        )


@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None, *, reason="No reason provided"):
    """Unlock a previously locked channel (prefix command)"""
    if not ctx.guild.me.guild_permissions.manage_channels:
        await ctx.send("❌ I don't have permission to manage channels!")
        return

    target_channel = channel or ctx.channel

    try:
        # Get the everyone role and current permissions
        everyone_role = ctx.guild.default_role
        current_perms = target_channel.overwrites_for(everyone_role)

        # Check if channel is already unlocked
        if current_perms.send_messages is None or current_perms.send_messages is True:
            await ctx.send(f"ℹ️ {target_channel.mention} is already unlocked!")
            return

        # Save the previous send_messages permission for logging
        previous_send_messages = current_perms.send_messages

        # Unlock the channel by resetting the send_messages permission
        if current_perms.is_empty():
            # If no other permissions are set, remove the entire override
            await target_channel.set_permissions(everyone_role, overwrite=None,
                                                 reason=f"{reason} (unlocked by {ctx.author})")
        else:
            # Otherwise, just reset the send_messages permission
            await target_channel.set_permissions(
                everyone_role,
                send_messages=None,
                reason=f"{reason} (unlocked by {ctx.author})"
            )

        # Send confirmation message
        embed = discord.Embed(
            title="🔓 Channel Unlocked",
            description=f"{target_channel.mention} has been unlocked!",
            color=0x00ff00
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Unlocked by", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)

        # Log the channel unlock
        await send_mod_log(
            guild=ctx.guild,
            title="🔓 Channel Unlocked",
            description=f"{target_channel.mention} has been unlocked.",
            color=0x00ff00,
            fields=[
                ("Channel", target_channel.mention, True),
                ("Moderator", ctx.author.mention, True),
                ("Reason", reason, False),
                ("Previous Setting", "Locked" if previous_send_messages is False else str(previous_send_messages), True)
            ]
        )

    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to modify this channel!")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Channel Unlock Failed",
            description=f"Failed to unlock {target_channel.mention}",
            color=0xff0000,
            fields=[
                ("Error", "Insufficient permissions", False),
                ("Moderator", ctx.author.mention, True),
                ("Channel", target_channel.mention, True)
            ]
        )
    except Exception as e:
        await ctx.send(f"❌ An error occurred: {e}")
        # Log the error
        await send_mod_log(
            guild=ctx.guild,
            title="❌ Channel Unlock Failed",
            description=f"Failed to unlock {target_channel.mention}",
            color=0xff0000,
            fields=[
                ("Error", str(e), False),
                ("Moderator", ctx.author.mention, True),
                ("Channel", target_channel.mention, True)
            ]
        )


@bot.command()
async def lalala(ctx):
    if ctx.author.id != BOT_OWNER_ID:
        await ctx.send("❌ Only the bot owner can use this command!")
        return

    await ctx.send("Are you sure you want to Shutdown? Reply with `yes` or `y` within 15 seconds.")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "y"]

    try:
        msg = await bot.wait_for("message", timeout=15.0, check=check)
        await ctx.send("Shuting down...")
        await bot.close()
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except asyncio.TimeoutError:
        await ctx.send("Shutdown cancelled (no confirmation received).")


# ▶️ Start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# ▶️ Start the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
