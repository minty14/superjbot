"""
An automated scraper to pull information from various sources related to New Japan Pro Wrestling

Stores data in a mongodb cluster used as a back end for the Super J-Cast Discord bot
"""
import asyncio
import datetime
import logging
import os
from mongoengine import connect, errors

from scraper import Scraper
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

# Instantiate the Scraper
scraper = Scraper()

# Store general podcast data from the Podcast's RedCircle Page
# Info pulled: title, description, img_url, url
async def update_pod_info():
    while True:
        try:
            # Scrape the podcast information
            pod_info = scraper.pod_info()

            # Attempt to update the existing podcast information with the scraped data            
            update = PodcastInfo.objects(title=pod_info['title']).update(**pod_info, full_result=True)
            
            # If any changes are actually made, timestamp and log
            if update.modified_count > 0:
                PodcastInfo.objects(title=pod_info['title']).update(updated_at=datetime.datetime.now)
                logging.info("Podcast info updated")
        
        # Catch exceptions during the scraper and DB update
        except Exception as e:
            logging.error("Unable to update pod info: " + str(e))

        # Sleep for one day
        await asyncio.sleep(86400)

# Store data related to the latest podcast episode
# Info pulled: title, description, link, published, duration, file
async def update_pod_episode():
    while True:
        try:
            # Scrape the last pod episode from the RSS feed
            last_pod = scraper.pod_episode()

            # Check if the latest episode is already in the DB
            if PodcastEpisode.objects(link=last_pod['link']):
                
                # If the episode already exists, update to reflect any changes to the data
                update = PodcastEpisode.objects(link=last_pod['link']).update(**last_pod, full_result=True)
                
                # If any changes are actually made, timestamp and log
                if update.modified_count > 0:
                    PodcastEpisode.objects(name=last_pod['name'], date=last_pod['date']).update(updated_at=datetime.datetime.now)
                    logging.info(f"Podcast Episode Updated: {last_pod['name']}")
            
            else:
                # If episode is not already in DB, add it
                episode = PodcastEpisode(**last_pod).save()
                logging.info(f"New Podcast Episode Added: {episode.title}")

        # Catch exceptions during the scraper and DB update
        except Exception as e:
            logging.error("Unable to update pod episode: " + str(e))
        
        # Sleep for one minute
        await asyncio.sleep(60)

# Store data related to the currently scheduled shows
# Data pulled per show: name, city, venue, thumbnail url, date (in local time)
async def update_shows():
    while True:
        # Scrape the shows listed on njpw1972.com/schedule
        schedule_shows = scraper.shows("schedule")

        logging.debug(f"schedule_shows: {schedule_shows}")

        for s in schedule_shows:
            try:
                logging.debug(f"schedule_show: {s}")
                
                # For each show in the scraped date, check if it already exists in the DB
                if ScheduleShow.objects(name=s['name'], date=s['date']):

                    # If the episode already exists, update to reflect any changes to the data
                    update = ScheduleShow.objects(name=s['name'], date=s['date']).update(**s, full_result=True)
                    
                    # If any changes are actually made, timestamp and log
                    if update.modified_count > 0:
                        ScheduleShow.objects(name=s['name'], date=s['date']).update(updated_at=datetime.datetime.now)
                        logging.info(f"Show updated: {s['name']} ({str(s['date'])})")
                
                else:
                    # If episode is not already in DB, add it
                    show = ScheduleShow(**s).save()
                    logging.info(f"New scheduled show added: {show.name} ({str(show.date)})")
                
            except Exception as e:
                logging.error(f"Error adding {s['name']} ({str(s['date'])}) to DB: " + str(e))

        # Find ScheduleShow objects that are now in the past and remove them
        old_shows = ScheduleShow.objects(time__lte=datetime.datetime.now)
        for s in old_shows:
            logging.info(f"Removing past show from schedule_show collection: {s.name} ({str(s['date'])})")
            s.delete()

        # Scrape the shows listed on njpw1972.com/result
        result_shows = scraper.shows("result")
        
        for s in result_shows:
            try:
                # For each show in the scraped date, check if it already exists in the DB
                if ResultShow.objects(name=s['name'], date=s['date']):

                    # If the episode already exists, update to reflect any changes to the data
                    update = ResultShow.objects(name=s['name'], date=s['date']).update(**s, full_result=True)
                    
                    # If any changes are actually made, timestamp and log
                    if update.modified_count > 0:
                        ResultShow.objects(name=s['name'], date=s['date']).update(updated_at=datetime.datetime.now)
                        logging.info(f"Show updated: {s['name']}")
                
                else:
                    # If episode is not already in DB, add it
                    show = ResultShow(**s).save()
                    logging.info(f"New result show added: {show.name} ({str(show.date)})")
                
            except Exception as e:
                logging.error(f"Error adding {s['name']} ({str(s['date'])}) to DB: " + str(e))

        # Update shows which are live on njpwworld.com
        scraper.broadcasts()

        # Sleep for one hour
        await asyncio.sleep(3600)

# Store data related to the latest podcast episode
# Info pulled: title, description, link, published, duration, file
async def update_profiles():
    while True:
            # Scrape the profiles listed on njpw1972.com/profiles
            profiles = scraper.profiles()

            for p in profiles:
                try:
                    # For each profile in the scraped data, check if it already exists in the DB
                    if Profile.objects(name=p["name"]):

                        # If the profile already exists, update to reflect any changes to the data
                        update = Profile.objects(name=p["name"]).update(**p, full_result=True)
                        
                        # If any changes are actually made, timestamp and log
                        if update.modified_count > 0:
                            Profile.objects(name=p["name"]).update(updated_at=datetime.datetime.now, full_result=True)
                            logging.info(f"Profile updated: {p['name']}")
                    else:
                        # If profile is not already in DB, add it
                        profile = Profile(**p).save()
                        logging.info(f"New profile added: {profile.name}")
               
                except Exception as e:
                    logging.error(f"Error adding updating profile {p.name}: " + str(e))
                
            # Mark removed profiles as such - they will be deleted by the bot after notifying @here
            for p in Profile.objects.all():
                if not [x for x in profiles if x['name'] == p.name]:
                    p.update(removed=True)
                    logging.info(f"Profile no longer exists: {p.name}")

            # Sleep for 45 minutes
            await asyncio.sleep(2700)

# Add the scraper functions to the main event loop
async def main():
    await asyncio.gather(
        update_pod_info(),
        update_pod_episode(),
        update_shows(),
        update_profiles()
    )

# Run the main event loop
asyncio.run(main())
