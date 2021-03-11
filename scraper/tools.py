"""
A set of tools for manual interaction with the scraper
"""
import logging

from scraper import Scraper
from database.models import (
    PodcastEpisode
)

scraper = Scraper()

# The below function exists should the podcast_episode collection need to be dropped and rebuilt
def update_all_pods():
    # Scrape all pod episodes from the RSS feed
    episodes = scraper.all_episodes()

    for e in episodes:
        # If the episode is not already in the DB, add it
        if not PodcastEpisode.objects(link=e["link"]):
            # Overwrite the new field to prevent spamming the discord
            e["new"] = False
            episode = PodcastEpisode(**e).save()
            logging.info("New Podcast Episode Added: " + episode.title)