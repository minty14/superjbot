"""
A set of tools for manual interaction with the scraper
"""
import logging

from scraper import Scraper, PodScraper
from database.models import (
    PodcastEpisode
)

scraper = Scraper()
pod_scraper = PodScraper()

# The below function exists should the podcast_episode collection need to be dropped and rebuilt
def update_all_pods():
    # Scrape all pod episodes from the RSS feed
    episodes = pod_scraper.scrape_old_episodes()
    for episode in episodes:
        pod_scraper.update_old_episodes(episodes)