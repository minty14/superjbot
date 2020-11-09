# external imports
import asyncio
import discord
from discord.ext import tasks
from discord.ext.commands import Bot

# module imports
import embeds
from scraper import Scraper
from constants import (
    TOKEN, NEW_MEMBER_CHANNEL, RULES_CHANNEL, NEW_POD_CHANNEL, OWNER_ID, NJPW_SPOILER_CHANNEL, NON_NJPW_SPOILER_CHANNEL
)

# create required intents
intents = discord.Intents.default()
intents.members = True

# instantiate the bot and web scraper
bot = Bot(command_prefix="!", intents=intents)
scraper = Scraper()

# Runs when the bot succesfully logs into Discord
@bot.event
async def on_ready():
    # Sets the spoiler status to False by default
    bot.spoiler = False

    # Starts the update info event loop
    # last_pod and new_pod attributes are created for use in the loop
    bot.last_pod = []
    bot.new_pod = False
    update_info.start()

    # Starts the update profiles loop
    update_profiles.start()

    # For each guild that the bot is logged into, prints user, guild name and ID
    for i in bot.guilds:
        print(
            f"Logged in as \'{bot.user}\' in \'{i.name}\' (Guild ID: {i.id})")

###
# Background Tasks
# https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.loop
# https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.Loop
###

# Background task to periodically run the scraper and store data in variables
@tasks.loop(minutes=10)
async def update_info():
    # Establish whether there is a new pod episode by checking:
    # - bot.last_pod isn't an empty dict (ie. the bot has restarted since the last update) 
    # - the previously stored bot.last_pod is different to a new scrape of the last pod ep
    # If both are true, then the bot.new_pod attr is True
    if bot.last_pod != [] and bot.last_pod != scraper.last_pod():
        bot.new_pod = True

    # Use Scraper methods to store attrs to speed up command response by eliminating the need for the scrapes to be run every time
    try:
        bot.pod_info = scraper.pod_info()
        bot.last_pod = scraper.last_pod()
        bot.next_shows = scraper.shows("schedule")
        bot.last_shows = scraper.shows("result")
        print("Info Variables Updated")

        # If new_pod was earlier set to True, creates a message and posts it to the NEW_POD_CHANNEL (currently #general)
        # Finish by setting new_pod back to False for the next loop
        if bot.new_pod:
            embed = embeds.pod_episode_embed(bot.last_pod)
            channel = bot.get_channel(NEW_POD_CHANNEL)
            await channel.send("@here New Pod!")
            await channel.send(embed=embed)
            bot.new_pod = False

    except:
        print("Unable to Update Info Variables:\n" + Exception)

# Background task to pull wrestler profiles and store in a variable.
# More intensive than the other scraper and will change less often, so only runs once a day
@tasks.loop(hours=24)
async def update_profiles():
    bot.profiles = scraper.profiles()
    print("Profiles Updated")

###
# Event Listeners
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20listen#discord.ext.commands.Bot.listen
###

# Runs when a new member joins the server
@bot.listen("on_member_join")
async def on_member_join(member):
    # Sends a DM to new members requesting that they pay attention to the rules channel and some points on how to get help with the boss
    await member.create_dm()
    rules_channel = bot.get_channel(RULES_CHANNEL)
    owner = bot.get_user(OWNER_ID)
    await member.dm_channel.send(f"Hi {member.name}! Thanks for joining us.\n"
    f"Before you do anything, make sure you head to {rules_channel.mention} to make sure you're aware of the rules and guidelines.\n"
    f"This bot is here to help you. For more details on what you can do with the bot, use: ```!help```"
    f"If you have find any issues with the bot and want to make suggestions, drop a DM to {owner.mention}\n"
    "Have fun!")

    # If spoiler mode is on, mentions them in #general and points them in the direction of the spoiler-zone channels
    if bot.spoiler:
        njpw_spoiler_channel = bot.get_channel(NJPW_SPOILER_CHANNEL)
        non_njpw_spoiler_channel = bot.get_channel(NON_NJPW_SPOILER_CHANNEL)
        general_channel = bot.get_channel(NEW_MEMBER_CHANNEL)
        await general_channel.send(f"Welcome {member.mention}! For spoilerific chat about the ongoing/last show, join us in the spoiler channels:\n"
                           f"NJPW Events: {njpw_spoiler_channel.mention}\n"
                           f"Other Events: {non_njpw_spoiler_channel.mention}\n")

# A listener for all messages in the server
# Most likely use case will be for temporary or "unofficial" commands that do not use the standard prefix
@bot.listen("on_message")
async def on_message(message):
    # No message listeners are used yet
    pass

###
# Bot Commands
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20command#discord.ext.commands.Bot.command
###

# Simple command to confirm that the bot is online and what current latency is
# Currently hidden to stop spam. Will later be made admin/deputy only
@bot.command(name="ping", 
    brief="Check that the bot is alive",
    help="Checks that the bot is online and working and displays the current latency in ms.",
    hidden=True
    )
async def ping(ctx):
    await ctx.send(f"Hello, I'm here :grinning: \nBot Latency: {round(bot.latency * 1000)}ms")

# Admin only - stops the bot from running
# In production, the container will restart, rendering this a "restart" function
@bot.command(name="kill",
    aliases=["killbot", "stop", "stopbot"],
    brief="Stop the bot",
    help="Stops the bot from running. Can be used if bot is having issues or causing problems in the server. Once stopped, the bot will need to be manually restarted.",
    hidden=True
    )
async def kill(ctx):
    if any(role > ctx.guild.default_role for role in ctx.author.roles):
        await bot.close()

# Admins - Sets the spoiler variable to true, which does the following:
#   - Alerts @here when spoiler-zone mode starts, and for how long
#   - Alerts @here when the spoiler embargo is lifted
#   - Displays a reminder to new users that spoiler chat should go in the relevant channel
#
# Non-admins - this displays whether spoiler mode is currently set
# TODO: add the ability for admins to check spoiler status
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
    # Check whether the command author is admin
    if any(role > ctx.guild.default_role for role in ctx.author.roles):
        # sleep time is set in seconds, so create a multiplier depending on the time unit set
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}

        # spoiler mode is not currently active - set mode to on, display an @here message in the channel it was invoked in, and sleep for the specified time
        if not bot.spoiler:
            bot.spoiler = True
            await ctx.send(f"@here _We're now in the spoiler-zone, keep show chat in the relevant spoiler-zone channel\n\nSpoiler embargo will lift in {str(time)}{unit}_")
            await asyncio.sleep(time * units[unit])

        # spoiler mode is currently active - set mode off and inform @here
        bot.spoiler = False
        await ctx.send("@here _Spoiler embargo lifted, chat away!_")
        await next_shows(ctx)
        
    # if the author isn't an admin, just display whether or not spoiler mode is currently on
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
    # If "nextshow" is used to invoke the command, embrace grammatical correctness and display only one show
    if ctx.invoked_with == "nextshow":
        number_of_shows = 1

    # build and send the reply
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
    # grammatical correctness is for life, only display one show if "lastshow" is used to invoke
    if ctx.invoked_with == "lastshow":
        number_of_shows = 1
    
    # build and send the reply
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
async def pod_episode_embed(ctx):
    # build and send the reply
    embed = embeds.pod_episode_embed(bot.last_pod)
    await ctx.send(embed=embed)

# Displays static generic infomation about the podcast
# Info scraped from the podcast RedCircle page 
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
    # build and send the reply
    embed = embeds.pod_info_embed(bot.pod_info, bot.last_pod)
    await ctx.send(embed=embed)

# Display the profile that matches the searched name
# Uses a keyword only argument so that users can search names with spaces in without ""s
@bot.command(name="profile",
    brief="Provide the name of a wrestler to get their profile",
    help="""Search for, and display, a current NJPW wrestler's profile.\n
            Partial searches are fine, so for example "!profile taka" will find any wrestler with "taka" anywhere in their name."""
    )
async def profile(ctx, *, name):
    # Force the searched name to be 3 or more characters - a lower limit can cause spammy replies 
    if len(name) < 3:
        await ctx.send("Please enter at least 3 characters to find a profile")
    else:
        # loop through the stored profiles and display any profiles that match
        for pf in bot.profiles:
            if name.lower() in pf["name"].lower():
                embed = embeds.profile_embed(pf)
                await ctx.send(embed=embed)

# Starts the bot when the module is run
# TOKEN is defined in constants and should be set for staging or prod environments
bot.run(TOKEN)
