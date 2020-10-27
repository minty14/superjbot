# external imports
import asyncio
import discord
from discord.ext import tasks
from discord.ext.commands import Bot

# module imports
import embeds
from constants import TOKEN, NEW_MEMBER_CHANNEL, RULES_CHANNEL, NEW_POD_CHANNEL, OWNER_ID
from scraper import Scraper

# create required intents
intents = discord.Intents.default()
intents.members = True

# instantiate the bot and web scraper
bot = Bot(command_prefix="!", intents=intents)
scraper = Scraper()

###
# Event Listeners
###

# Runs when the bot succesfully logs into Discord
@bot.event
async def on_ready():
    # Sets the spoiler status to False by default
    bot.spoiler = False
    # Starts the update info event loop
    bot.last_pod = []
    bot.new_pod = False
    update_info.start()
    # For each guild that the bot is logged into, prints user, guild name and ID
    for i in bot.guilds:
        print(
            f"Logged in as \'{bot.user}\' in \'{i.name}\' (Guild ID: {i.id})")


@bot.listen("on_member_join")
async def on_member_join(member):
    await member.create_dm()
    channel = bot.get_channel(RULES_CHANNEL)
    owner = bot.get_user(OWNER_ID)
    await member.dm_channel.send(f"Hi {member.name}! Thanks for joining us.\n"
    f"Before you do anything, make sure you head to {channel.mention} to make sure you're aware of the rules and guidelines.\n"
    f"This bot is here to help you. For more details on what you can do with the bot, use: ```!help```"
    f"If you have find any issues with the bot and want to make suggestions, drop a DM to {owner.mention}\n"
    "Have fun!")
    if bot.spoiler:
        channel = bot.get_channel(NEW_MEMBER_CHANNEL)
        await channel.send(f"Welcome {member.mention}! For spoilerific chat about the ongoing/last show, join us in {channel.mention}. Thanks!")

@bot.listen("on_message")
async def on_message(message):
    # No message listeners are used yet
    pass

###
# Background Tasks
###

# Background task to periodically run the scraper and store data in variables
@tasks.loop(minutes=10)
async def update_info():
    if bot.last_pod != [] and bot.last_pod != scraper.last_pod():
        bot.new_pod = True
    try:
        bot.pod_info = scraper.pod_info()
        bot.last_pod = scraper.last_pod()
        bot.next_shows = scraper.shows("schedule")
        bot.last_shows = scraper.shows("result")
        print("Info Variables Updated")
        if bot.new_pod:
            embed = discord.Embed(
                title=bot.last_pod["title"],
                url=bot.last_pod["link"],
                description=bot.last_pod["description"]
            )

            embed.add_field(
                name="Published",
                value=bot.last_pod["published"]
            )

            embed.add_field(
                name="Duration",
                value=bot.last_pod["duration"]
            )

            channel = bot.get_channel(NEW_POD_CHANNEL)
            await channel.send("@here New Pod!")
            await channel.send(embed=embed)
            bot.new_pod = False

    except:
        print("Unable to Update Info Variables:\n" + Exception)

###
# Bot Commands
###

# Simple command to confirm that the bot is online and what current latency is
@bot.command(name="ping", 
    brief="Check that the bot is alive",
    help="Checks that the bot is online and working and displays the current latency in ms."
    )
async def ping(ctx):
    await ctx.send(f"Hello, I'm here :grinning: \nBot Latency: {round(bot.latency * 1000)}ms")

# Admin only - stops the bot from running
@bot.command(name="kill",
    aliases=["killbot", "stop", "stopbot"],
    brief="Stop the bot",
    help="Stops the bot from running. Can be used if bot is having issues or causing problems in the server. Once stopped, the bot will need to be manually restarted.",
    hidden=True
    )
async def kill(ctx):
    if any(role > ctx.guild.default_role for role in ctx.author.roles):
        await bot.close()

# Sets the spoiler variable to true, which does the following:
#   - Alerts @here when spoiler-zone mode starts, and for how long
#   - Alerts @here when the spoiler embargo is lifted
#   - Displays a reminder to new users that spoiler chat should go in the relevant channel
@bot.command(name="spoiler", 
    brief="Check whether there's currently a spoiler embargo",
    help="""* number_of_time and unit_of_time only needed when run by admins & deputies
    
    For admins/deputies:
    \tSets spoiler-zone mode to ON, for the specified number of hours.
    \tSets spoiler-zone mode to OFF if already running.
    For other users:
    \tShows whether spoiler-zone mode is currently ON or OFF.""",
    usage="[number_of_time] (default=12, valid=WHOLE NUMBERS) [unit_of_time] (default=h, valid=s,m,h,d)\neg. \"!spoiler 24 h\""
    )
async def spoiler(ctx, time: int = 12, unit="h"):
    if any(role > ctx.guild.default_role for role in ctx.author.roles):
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
        if not bot.spoiler:
            bot.spoiler = True
            await ctx.send(f"@here _We're now in the spoiler-zone, keep show chat in the relevant spoiler-zone channel\n\nSpoiler embargo will lift in {str(time)}{unit}_")
            await asyncio.sleep(time * units[unit])
        bot.spoiler = False
        await ctx.send("@here _Spoiler embargo lifted, chat away!_")
        await next_shows(ctx)
        

    else:
        if bot.spoiler:
            await ctx.send("_#spoiler-zone mode is ON, keep show chat in the relevant spoiler-zone channel_")
        else:
            await ctx.send("_#spoiler-zone mode is OFF, anything goes!_")

# Displays info upcoming shows - takes the number of shows to display as an argument
# Info is scraped from the NJPW website and stored in the bot.next_shows attribute
@bot.command(name="nextshows",
    aliases=["next", "nextshow"],
    brief="Show details on upcoming show(s)", 
    help="""Show details on the specified number of upcoming NJPW shows.
    For each show, displays the following information:
    \tDate of the show, with door and bell times in JST.
    \tThe city in which the show takes place.
    \tThe venue at which the show takes place.""",
    usage="[number_of_shows] (defaults: \"nextshows/next\"=3 \"nextshow\"=1)"
    )
async def next_shows(ctx, number_of_shows=3):
    if ctx.invoked_with == "nextshow":
        number_of_shows = 1
    embed = embeds.shows_embed("schedule", bot.next_shows, number_of_shows)
    await ctx.send(embed=embed)

# Displays info on previous shows - takes the number of shows to display as an argument
# Info is scraped from the NJPW website and stored in the bot.last_shows attribute
@bot.command(name="lastshows",
    aliases=["last", "lastshow"],
    brief="Show details on previous show(s)", 
    help="""Show details on the specified number of previous NJPW shows.
    For each show, displays the following information:
    \tDate of the show, with door and bell times in JST.
    \tThe city in which the show took place.
    \tThe venue at which the show took place.""",
    usage="[number_of_shows] (defaults: \"lastshows/last\"=3 \"lastshow\"=1)"
    )
async def last_shows(ctx, number_of_shows=3):
    if ctx.invoked_with == "lastshow":
        number_of_shows = 1
    embed = embeds.shows_embed("result", bot.last_shows, number_of_shows)
    await ctx.send(embed=embed)

# Show details on the lates podcast episode
# Info scraped from the podcast RedCircle page 
@bot.command(name="lastpod", 
    aliases=["latest", "latestpod"],
    brief="Show details on the latest pod episode",
    help="""Shows details on the latest episode of the Super J-Cast, with a link to listen to the show online.
    For the latest episode, displays the following information:
    \tThe episode's description.
    \tThe episode's release date.
    \tThe episode's duration."""
    )
async def last_pod(ctx):
    embed = embeds.last_pod_embed(bot.last_pod)
    await ctx.send(embed=embed)

# Displays static generic infomation about the podcast
@bot.command(name="podinfo",
    aliases=["pod"],
    brief="Show general info about the podcast", 
    help="""Shows general information about the Super J-Cast, with a link to the show's RedCircle Page.
    For the podcast, displays the following information:
    \tThe latest episode title with link to the episode on RedCircle.
    \tA link to the show's Twitter account.
    \tA link to the show's sponsor page.
    \tA link to the show's ProWrestlingTees store.
    """
    )
async def pod_info(ctx):
    embed = embeds.pod_info_embed(bot.pod_info, bot.last_pod)
    await ctx.send(embed=embed)

bot.run(TOKEN)
