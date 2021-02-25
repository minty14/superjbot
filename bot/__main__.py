"""
Bot setup

Configuration of logging, DB connection and cog loading is done here.
"""

# external imports
import os
import logging
from mongoengine import connect

# discord imports
import discord
from discord.ext.commands import Bot

# module imports
import utils.tasks
from settings.constants import TOKEN

## Configure Logging

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('superjbot.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s# %(message)s', datefmt='%d.%m.%y-%H:%M:%S')
f_format = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s# %(message)s', datefmt='%d.%m.%y-%H:%M:%S')
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

# Instantiate the bot
bot = Bot(command_prefix="!", intents=intents)

# Connect to the mongodb cluster
connect(host=os.environ['DBURL'])

# Run when the bot succesfully logs into Discord
@bot.event
async def on_ready():
    # For each guild that the bot is logged into, prints user, guild name and ID
    for i in bot.guilds:
        logging.info(f"Logged in as \'{bot.user}\' in \'{i.name}\' (Guild ID: {i.id})")

    # Load all of the cogs in the cogs/ folder
    # Cogs are loaded on_ready in case any of the loops need to send updates to channels
    for filename in os.listdir("./bot/cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            bot.load_extension(f"cogs.{filename[:-3]}")

            logging.info(f"Loaded Cog: {filename[:-3]}")
    
    # Store guild, channel and user IDs in bot attributes
    logging.info("Creating bot attributes from IDs")
    utils.tasks.set_ids(bot)

    logging.info("Finished logging in")

# Starts the bot when the module is run
# TOKEN is defined in constants and should be set for staging or prod environments
bot.run(TOKEN)
