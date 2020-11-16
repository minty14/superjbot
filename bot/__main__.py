# external imports
import os
import asyncio
import logging
import discord
from discord.ext import tasks
from discord.ext.commands import Bot

# module imports
import utils.scraper
from settings.constants import (
    TOKEN, NEW_POD_CHANNEL
)

# Configure Logging

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('superjbot.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s#%(message)s', datefmt='%d.%m.%y-%H:%M:%S')
f_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s#%(message)s', datefmt='%d.%m.%y-%H:%M:%S')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
# Level also set here as logs weren't being output without it
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[c_handler, f_handler]
    )

# Create required intents
# Add members intent to run member events
intents = discord.Intents.default()
intents.members = True

# Instantiate the bot and web scraper
bot = Bot(command_prefix="!", intents=intents)
scraper = utils.scraper.Scraper()

# Load all of the cogs in the cogs/ folder
for filename in os.listdir("./bot/cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

# Run when the bot succesfully logs into Discord
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
        logging.info(f"Logged in as \'{bot.user}\' in \'{i.name}\' (Guild ID: {i.id})")

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
        logging.info("Info Variables Updated")

        # If new_pod was earlier set to True, creates a message and posts it to the NEW_POD_CHANNEL (currently #general)
        # Finish by setting new_pod back to False for the next loop
        if bot.new_pod:
            embed = utils.embeds.pod_episode_embed(bot.last_pod)
            channel = bot.get_channel(NEW_POD_CHANNEL)
            await channel.send("@here New Pod!")
            await channel.send(embed=embed)
            bot.new_pod = False

    except:
        logging.error("Unable to Update Info Variables:\n" + Exception)

# Background task to pull wrestler profiles and store in a variable.
# More intensive than the other scraper and will change less often, so only runs once a day
@tasks.loop(hours=24)
async def update_profiles():
    bot.profiles = scraper.profiles()
    logging.info("Profiles Updated")


# Starts the bot when the module is run
# TOKEN is defined in constants and should be set for staging or prod environments
bot.run(TOKEN)
