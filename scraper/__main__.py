import asyncio
import os
from mongoengine import connect

import scraper
import db

connect(host=os.environ['DBURL'])

scraper = scraper.Scraper()

def update_profiles():
    profiles = scraper.profiles()

    for pf in profiles:
        print(f"Adding {pf['name']} to DB")
        pf_doc = db.Profile(**pf)

        pf_doc.update(upsert=True, **pf)

def update_shows():
    shows = scraper.shows("schedule")

    for i in shows:
        print(f"Adding {i['name']} to DB")
        doc = db.Show(**i)

        doc.update(upsert=True, **i)

def update_last_pod():
    last_pod = scraper.last_pod()

    print(f"Adding {last_pod['title']} to DB")
    doc = db.PodcastEpisode(**last_pod)

    doc.update(upsert=True, **last_pod)

def update_pod_info():
    pod_info = scraper.pod_info()
    
    print(f"Adding {pod_info['title']} to DB")
    doc = db.PodcastInfo(**pod_info)

    doc.update(upsert=True, **pod_info)

update_shows()