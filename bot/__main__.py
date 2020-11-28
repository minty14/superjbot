# external imports
import os
import asyncio
import logging
from datetime import datetime, timedelta
from mongoengine import connect, errors

# discord imports
import discord
from discord.ext import tasks
from discord.ext.commands import Bot

# module imports
import utils.tasks
from settings.constants import TOKEN
from database.models import (
    SpoilerMode, ScheduleShow, NonNjpwShow, Profile, PodcastEpisode, PodcastInfo)


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

# Instantiate the bot
bot = Bot(command_prefix="!", intents=intents)

# Load all of the cogs in the cogs/ folder
for filename in os.listdir("./bot/cogs"):
    if filename.endswith(".py") and filename != "__init__.py":
        bot.load_extension(f"cogs.{filename[:-3]}")

# Connect to the mongodb cluster
connect(host=os.environ['DBURL'])

# Run when the bot succesfully logs into Discord
@bot.event
async def on_ready():
        # For each guild that the bot is logged into, prints user, guild name and ID
    for i in bot.guilds:
        logging.info(f"Logged in as \'{bot.user}\' in \'{i.name}\' (Guild ID: {i.id})")
    
    # Start background task loops
    logging.info("Starting new_podcast_watcher")
    new_podcast_watcher.start()
    logging.info("Starting new_show_watcher")
    new_show_watcher.start()
    logging.info("Starting new_profile_watcher")
    new_profile_watcher.start()
    logging.info("Starting spoiler_mode_watcher")
    spoiler_mode_watcher.start()

    # Store guild, channel and user IDs in bot attributes
    logging.info("Creating bot attributes from IDs")
    utils.tasks.set_ids(bot)

    logging.info("Finished logging in")

###
# Background Tasks
# https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.loop
# https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.Loop
###

# Frequently look for new podcasts episodes in the DB
@tasks.loop(minutes=5)
async def new_podcast_watcher():
    logging.debug("Running new_podcast_watcher")

    # DB query to return podcast episodes tagged as new
    new_podcasts = PodcastEpisode.objects(new=True)

    if new_podcasts:
        # Loop through results on the remote chance that more than one episode was found
        for p in new_podcasts:
            logging.info("New podcast episode found: " + p.title)
            await bot.general_channel.send(content="@here New Pod!", 
                               embed=utils.embeds.pod_episode_embed(p))
            p.update(new=False)

# Alert the discord to shows added to the schedule on njpw1972.com
@tasks.loop(minutes=30)
async def new_show_watcher():
    logging.debug("Running new_show_watcher")

    # DB query to return podcast episodes tagged as new
    new_shows = ScheduleShow.objects(new=True)

    if new_shows:
        for s in new_shows:
            logging.info("New scheduled show found: " + s.name)
        try:
            await bot.general_channel.send(content="New show(s) added to the schedule:",
                            embed=utils.embeds.new_shows_embed(new_shows))
        except Exception:
            await bot.general_channel.send(content="New show(s) added to the schedule:",
                            embed=utils.embeds.new_shows_embed(new_shows[0:2]))
        new_shows.update(new=False)

# Alert the discord to wrestler profiles added to on njpw1972.com
@tasks.loop(hours=6)
async def new_profile_watcher():
    logging.debug("Running new_profile_watcher")

    # DB query to return podcast episodes tagged as new
    new_profiles = Profile.objects(new=True)

    if new_profiles:
        await bot.general_channel.send("New Profile(s) Added: ")
        for p in new_profiles:
            logging.info("New profile found: " + p.name)
            await bot.general_channel.send(embed=utils.embeds.profile_embed(p))
        new_profiles.update(new=False)

# Check for shows starting soon and set spoiler mode
# Also check for spoiler modes which have ended
@tasks.loop(minutes=3.5)
async def spoiler_mode_watcher():
    logging.debug("Running spoiler_mode_watcher")

    # DB query to return njpw shows which start in the next 5 minutes and continue if any exist
    starting_shows = ScheduleShow.objects(date__lte=datetime.now() + timedelta(minutes=5))
    if starting_shows:
        for s in starting_shows:
            # Check that spoiler mode hasn't already been triggered for that show
            if not SpoilerMode.objects(title=s.name):

                # Build spoiler_mode document
                spoiler_mode = SpoilerMode(
                    mode = "njpw",
                    title=s.name,
                    ends_at=s.date + timedelta(hours=s.spoiler_hours),
                    thumb=s.thumb
                )

                # Save the document to the DB
                spoiler_mode.save()

                # Notify @here of the starting show and include the embed which lists the end time
                await bot.general_channel.send(content=f"@here **{spoiler_mode.title}** starting soon. Head to {bot.njpw_spoiler_channel.mention} for spoiler chat.",
                        embed=utils.embeds.spoiler_mode_embed(spoiler_mode))

                await bot.njpw_spoiler_channel.edit(topic=spoiler_mode.title)
                
                logging.info(f"NJPW #spoiler-zone time started for {spoiler_mode.title}, ends in {s.spoiler_hours}")

    # DB query to return non-njpw shows which start in the next 5 minutes and continue if any exist
    non_njpw_shows = NonNjpwShow.objects(date__lte=datetime.now() + timedelta(minutes=5))
    if non_njpw_shows:
        for s in non_njpw_shows:
            # Check that spoiler mode hasn't already been triggered for that show
            if not SpoilerMode.objects(title=s.name):

                # Build spoiler_mode document
                spoiler_mode = SpoilerMode(
                    mode = "non_njpw",
                    title=s.name,
                    ends_at=s.date + timedelta(hours=s.spoiler_hours)
                )

                # Save the document to the DB
                spoiler_mode.save()

                # Notify @here, in the non-njpw chat channel of the starting show and include the embed which lists the end time
                await bot.non_njpw_channel.send(
                    content=f"@here **{spoiler_mode.title}** starting soon. Head to {bot.non_njpw_spoiler_channel.mention} for spoiler chat",
                    embed=utils.embeds.spoiler_mode_embed(spoiler_mode)
                )

                await bot.non_njpw_spoiler_channel.edit(topic=spoiler_mode.title)

                logging.info(f"Non NJPW #spoiler-zone time started for **{spoiler_mode.title}**, ends in {s.spoiler_hours} hours")

    # DB query to find spoiler_mode events which have now ended
    ending_shows = SpoilerMode.objects(ends_at__lt=datetime.now())
    if ending_shows:
        for s in ending_shows:          
            # For ended spoiler modes, send notifications to the relevant channels
            if s.mode == "njpw":
                if SpoilerMode.object(mode=s.mode).count() < 2:
                    await bot.general_channel.send(
                        content=f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away.\n\nNext show:",
                        embed=utils.embeds.schedule_shows_embed(ScheduleShow.objects(date__gt=datetime.now())[:1], 1)
                    )
                else:
                    await bot.general_channel.send(
                        content=f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away.\nOngoing spoiler embargo:",
                        embed=utils.embeds.spoiler_mode_embed(ending_shows[1])
                        )
            elif s.mode == "non_njpw":
                await bot.non_njpw_channel.send(
                    f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away."
                )

            # Remove the spoiler mode document from the DB
            s.delete()

            logging.info(f"{s.mode} spoiler-zone time ended for {s.title}")

# Starts the bot when the module is run
# TOKEN is defined in constants and should be set for staging or prod environments
bot.run(TOKEN)
