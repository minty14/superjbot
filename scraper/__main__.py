"""
An automated scraper to pull information from various sources related to New Japan Pro Wrestling

Stores data in a mongodb cluster used as a back end for the Super J-Cast Discord bot
"""
import asyncio
import logging
import os
from mongoengine import connect

from scraper import PodScraper, ShowScraper, ProfileScraper
from database.models import (NonNJPWShow, PodcastEpisode, PodcastInfo, Profile,
                             ResultShow, ScheduleShow)

# Configure Logging

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('scraper.log')
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

# Establish connection to the mongodb cluster
# http://docs.mongoengine.org/apireference.html?highlight=connect#mongoengine.connect
connect(host=os.environ['DBURL'])

# Instantiate the Scrapers
pod_scraper = PodScraper()
show_scraper = ShowScraper()
profile_scraper = ProfileScraper()

# Store general podcast data from the Podcast's RedCircle Page
# Info pulled: title, description, img_url, url
async def update_pod_info():
    while True:
        try:
            pod_info = pod_scraper.scrape_info()
            pod_scraper.update_info(pod_info)
            # Sleep for one day
            await asyncio.sleep(86400)

        except Exception as e:
            logging.error("Error running update_pod_info task: " + str(e))
            await asyncio.sleep(60)
        

# Store data related to the latest podcast episode
# Info pulled: title, description, link, published, duration, file
async def update_pod_episode():
    while True:
        try:
            latest_episode = pod_scraper.scrape_latest_episode()
            pod_scraper.update_latest_episode(latest_episode)
            
        except Exception as e:
            logging.error("Error running update_pod_episode task: " + str(e))

        # Sleep for one minute
        await asyncio.sleep(60)

# Store data related to the currently scheduled shows
# Data pulled per show: name, city, venue, thumbnail url, date (in local time)
async def update_shows():
    while True:
        try:
            # Update schedule shows
            schedule_shows = show_scraper.scrape_shows("schedule")
            for show in schedule_shows:
                show_scraper.update_show(show, "schedule")

            # Update result shows
            result_shows = show_scraper.scrape_shows("result")
            for show in result_shows:
                show_scraper.update_show(show, "result")

            # Update shows which are live on njpwworld.com
            show_scraper.scrape_broadcasts()

            # Remove old shows
            show_scraper.remove_old_shows()

            # Sleep for one hour
            await asyncio.sleep(3600)

        except Exception as e:
            logging.error("Error running update_shows task: " + str(e))
            await asyncio.sleep(60)

# Store data related to the latest podcast episode
# Info pulled: title, description, link, published, duration, file
async def update_profiles():
    while True:
        try:
            profiles = profile_scraper.scrape_profiles()
            for profile in profiles:
                profile_scraper.update_profile(profile)
            # Sleep for 45 minutes
            await asyncio.sleep(2700)

        except Exception as e:
            logging.error("Error running update_profiles task: " + str(e))
            await asyncio.sleep(60)

# Add the scraper functions to the main event loop
async def main():
    logging.info("Creating main event loop")
    await asyncio.gather(
        update_pod_info(),
        update_pod_episode(),
        update_shows(),
        update_profiles()
    )

# Run the main event loop
logging.info("Starting main event loop")
asyncio.run(main())
