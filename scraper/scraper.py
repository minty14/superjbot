"""
A web scraper Class instantiated once the bot starts running and is logged in

Provides class methods to scrape information from various sources to then be stored in the DB
"""
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import pytz

from database.models import ResultShow, ScheduleShow, PodcastInfo, PodcastEpisode, Profile

class Scraper():
    # Take a url and create a Beautiful soup object
    # Features is usually lxml or xml
    def create_soup(self, url, features):
        logging.info(f"Creating soup from {url}")

        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, features)
            return soup

        except Exception as e:
            logging.error(f"Unable to create soup from {url}")

class PodScraper(Scraper):
    def __init__(self):
        logging.info("Building podcast scraper")

        self.pod_info_url = "https://redcircle.com/shows/super-j-cast/"
        self.pod_rss_feed = "https://feeds.redcircle.com/cf1d4e82-ac3d-47e6-948d-1d299cf6744e"

    def scrape_info(self):
        logging.info("Scraping podcast information")
        
        try:
            soup = self.create_soup(self.pod_info_url, "lxml")

            pod_info = {
                "title": soup.find(class_="show-title").get_text().strip(),
                "description": soup.find_all("div", class_="show-page__about")[0].p.get_text().strip(),
                # This isn't returning the right value at the moment, so using the hardcoded link
                # "img_url": soup.find_all("img", class_="show-image")[0].src,
                "img_url": "https://media.redcircle.com/images/2020/8/20/14/3b3c9e21-4329-4283-b1c4-6ab1b3be5a6a_93146d1b-2f16-477b-b6c1-c17069ef70dc_c8a8e6cf-7ba4-44bb-954c-53ec5023adc8_32630451.jpg?d=280x280",
                "url": self.pod_info_url
            }

            logging.debug("pod_info: " + str(pod_info))

            return pod_info

        # Catch exceptions during the scraper and DB update
        except Exception as e:
            logging.error("Unable to scrape pod info: " + str(e))
    
    def update_info(self, pod_info):
        logging.info("Updating podcast information")
        
        try:
            # Attempt to update the existing podcast information with the scraped data            
            update = PodcastInfo.objects(title=pod_info['title']).update(**pod_info, full_result=True)
            
            # If any changes are actually made, timestamp and log
            if update.modified_count > 0:
                PodcastInfo.objects(title=pod_info['title']).update(updated_at=datetime.now)
                logging.info("Podcast info updated")
        
        except Exception as e:
            logging.error("Unable to update pod info: " + str(e))

    def scrape_latest_episode(self):
        logging.info("Scraping latest podcast episode")

        try:
            soup = self.create_soup(self.pod_rss_feed, "xml")
            
            # .find pulls the first item in the RSS feed, which will be the latest episode
            item = soup.find("item")

            # Remove some of the formatting around the date and convert to date object
            published = datetime.strptime(
                " ".join(item.pubDate.text.split(" ")[0:4]), 
                "%a, %d %b %Y"
                ).date()

            # Put the last episode info into a dict and return it
            last_pod = {
                "title": item.title.text,
                "description": item.description.text,
                "link": item.link.text,
                "published": published, 
                "duration": item.duration.text,
                "file": item.enclosure.get("url")
            }

            logging.debug("last_pod: " + str(last_pod))

            return last_pod

        # Catch exceptions during the scraper and DB update
        except Exception as e:
            logging.error("Unable to scrape latest pod episode: " + str(e))

    def update_latest_episode(self, last_pod):
        logging.info("Updating latest podcast episode")
        
        try:    
            # Check if the latest episode is already in the DB
            if PodcastEpisode.objects(link=last_pod['link']):
                
                # If the episode already exists, update to reflect any changes to the data
                update = PodcastEpisode.objects(link=last_pod['link']).update(**last_pod, full_result=True)
                
                # If any changes are actually made, timestamp and log
                if update.modified_count > 0:
                    PodcastEpisode.objects(name=last_pod['name'], date=last_pod['date']).update(updated_at=datetime.now)
                    logging.info(f"Podcast Episode Updated: {last_pod['name']}")
            
            else:
                # If episode is not already in DB, add it
                episode = PodcastEpisode(**last_pod).save()
                logging.info(f"New Podcast Episode Added: {episode.title}")
        
        except Exception as e:
            logging.error("Unable to update latest pod episode: " + str(e))

    def scrape_old_episodes(self):
        logging.info("Scraping all podcast episodes")

        try:
            soup = self.create_soup(self.pod_rss_feed, "xml")
            items = soup.find_all("item")

            all_episodes = []

            for item in items:
                published = datetime.strptime(
                " ".join(item.pubDate.text.split(" ")[0:4]), 
                "%a, %d %b %Y"
                ).date()

            # Put the last episode info into a dict and return it
                episode = {
                    "title": item.title.text,
                    "description": item.description.text,
                    "link": item.link.text,
                    "published": published, 
                    "duration": item.duration.text,
                    "file": item.enclosure.get("url")
                }

                all_episodes.append(episode)

            logging.debug("all_episodes: " + str(all_episodes))

            return all_episodes

        except Exception as e:
            logging.error("Unable to scrape all pod episodes: " + str(e))

    def update_old_episode(self, episode):
        logging.info(f"Updating podcast episode \"{episode['name']}\"")

        try:
            # If the episode is not already in the DB, add it
            if not PodcastEpisode.objects(link=episode["link"]):
                # Overwrite the new field to prevent spamming the discord
                episode["new"] = False
                episode = PodcastEpisode(**episode).save()
                logging.info("New Podcast Episode Added: " + episode.title)
        
        except Exception as e:
            logging.error("Unable to update pod episode: " + str(e))
    
class ShowScraper(Scraper):
    def __init__(self):
        logging.info("Building show scraper")

    def scrape_shows(self, type):
        logging.info("Scraping " + type + " shows")

        shows = []
        
        for x in range(1, 3):
            soup = self.create_soup("https://www.njpw1972.com/" + type + "?pageNum=" + str(x), "lxml")
            all_events = soup.find_all("div", class_="event")

            for event in all_events:
                # Each "event" can actually be one show, or a whole tour, with multiple dates
                # event_name can be consistent across multiple dates, so is set here, outside of the next for loop
                event_name = event.find("h3").get_text().strip()
                dates = event.find_all("li")

                for date in dates:
                    try:
                        show_dict = {
                            "name": event_name,
                            "city": date.find("p", class_="city").get_text().strip(),
                            "venue": date.find("p", class_="venue").get_text().strip(),
                            "thumb": event.find("img")["src"],
                            "card": date.find("a")["href"]
                        }

                        # The url of their placeholder logo needs to be replaced with the full path
                        if show_dict['thumb'] == "/wp-content/themes/njpw-en/images/common/noimage_poster.jpg":
                            show_dict['thumb'] = "https://www.njpw1972.com/wp-content/themes/njpw-en/images/common/noimage_poster.jpg"

                        #Scrape the scheduled time of the show and split our the date and time
                        date_time = " ".join(date.find("p", class_="date").get_text().strip().split())
                        date = " ".join(date_time.split(" ")[:4])
                        time = date_time.split("BELL")[1].strip()

                        # The 'date' dict values here are a duplicate of 'time'. It is added to the DB as a DateField
                        # 'date' is then used to update show DB entries without duplicating when the show time has changed
                        if "EST" in time:
                            # If the timezone is EST (eg Strong), set the correct timezone and localise the time to UTC
                            tz = pytz.timezone("US/Eastern")
                            time = time[:7] # Removes the timezone from the time text contents
                            show_dict['time'] = tz.localize(datetime.strptime(date + " " + time, "%a. %B. %d. %Y %I:%M%p"))
                            show_dict['date'] = show_dict['time']
                        else:
                            # Default timezone is JST so start times are localised to UTC based on that
                            tz = pytz.timezone("Asia/Tokyo")
                            show_dict['time'] = tz.localize(datetime.strptime(date + " " + time, "%a. %B. %d. %Y %H:%M"))
                            show_dict['date'] = show_dict['time']
                        
                        logging.debug("show_dict: " + str(show_dict))

                        shows.append(show_dict)

                        return shows
                                        
                    except Exception as e:
                        logging.error(f"Unable to scrape show {event_name}: " + str(e))

    def update_show(self, show, type):
        logging.info(f"Updating show {show['name']}")
        
        try:
            if type == "schedule":
                model = ScheduleShow
            if type == "result":
                model = ResultShow

            # For each show in the scraped date, check if it already exists in the DB
            if model.objects(name=show['name'], date=show['date']):

                # If the episode already exists, update to reflect any changes to the data
                update = model.objects(name=show['name'], date=show['date']).update(**show, full_result=True)
                
                # If any changes are actually made, timestamp and log
                if update.modified_count > 0:
                    model.objects(name=show['name'], date=show['date']).update(updated_at=datetime.now)
                    logging.info(f"Show updated: {show['name']} ({str(show['date'])})")
            
            else:
                # If episode is not already in DB, add it
                show = model(**show).save()
                logging.info(f"New {type} show added: {show.name} ({str(show.date)})")

        except Exception as e:
            logging.error(f"Unable to update show {show['name']}: " + str(e))

    def scrape_broadcasts(self):
        logging.info("Scraping broadcasted shows")

        try:
            # Custom headers are needed otherwise njpwworld gives an unsupported browser error
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
            session = requests.get("https://njpwworld.com/feature/schedule", headers=headers)
            soup = BeautifulSoup(session.text, "html.parser")

            # Tab1 contains the schedule, tab2 is past events
            schedule = soup.find("div", id="tab1")
            # Each month's shows is listed in a seperate table
            months = schedule.find_all("table")
            # The year isn't in individual dates, so pull it from the table headers
            years = soup.find_all("h1", class_="ttl-schedule menu-ja")

            # In the source text, both the english and japanese calendars are there - even indices are japanese tables, odds are english
            # Ignore tr[0] as it's the table header. The year is spliced from the text header (ie "2021年2月配信予定一覧")
            
            # Update current month's shows
            self.update_broadcasts(months[0].find_all('tr')[1:], years[0].text[:4])
            
            # Update next month's shows if the schedule exists
            if len(months) > 2:
                self.update_broadcasts(months[2].find_all('tr')[1:], years[1].text[:4])
        
        except Exception as e:
            logging.error("Error trying to scrape broadcast shows: " + str(e))

    def update_broadcasts(self, broadcasts, year):
        logging.info("Updating broadcasted shows")

        for broadcast in broadcasts:
            try:
                # Pull the date and time from the first 2 columns
                show_details = [s.text for s in (broadcast.find_all('td'))][:2]
                # Create a datetime object for the show by building a string and formatting it (Japanese time)
                time = pytz.timezone("Asia/Tokyo").localize(datetime.strptime(show_details[1][:5] + " " + show_details[0].split("(")[0] + " " + year, "%H:%M %m/%d %Y"))
                # Find a show with a matching datetime
                # If live_show is already True, we don't need to update it, so filter those out
                show = ScheduleShow.objects(time=time, live_show=False).first()

                # If there's a match, update the DB
                if show:
                    show.update(live_show=True)
                    logging.info(f"New broadcast found: {show.name} ({show.date})")
            
            except Exception as e:
                logging.error("Error trying to update broadcast shows: " + str(e))

    def remove_old_shows(self):
        old_shows = ScheduleShow.objects(time__lte=datetime.now)
        
        for s in old_shows:
            logging.info(f"Removing past show from schedule_show collection: {s.name} ({str(s['date'])})")
            s.delete()

class ProfileScraper(Scraper):
    def __init__(self):
        logging.info("Building profile scraper")
        self.njpw_profiles_url = "https://www.njpw1972.com/profiles/"

    def scrape_profiles(self):
        logging.info("Scraping profiles")

        soup = self.create_soup(self.njpw_profiles_url, "lxml")

        try:
            profile_list = soup.find("ul", class_="wrestlerList").find_all("li")

            # Create the list of profile dicts
            profiles = []

            # For each profile on the page, we create a dict containing info which is then added to with the info in the individual profile page
            for profile in profile_list:
                try:
                    profile_dict = {
                        "name": profile.find("p", class_="name").get_text().strip(),
                        "link": profile.find("a")["href"],
                        "render": profile.find("img")["src"],
                        "attributes": {}
                    }

                    profiles.append(profile_dict)

                    logging.debug("Found profile: " + profile_dict['name'])

                except Exception as e:
                    profile_dict = {}
                    logging.error("Error scraping profile: " + e)

            # Create a dict of possible attributes so that we can loop through try/except statements
            # [name of key in wrestler's dict]: [text used to identify this data in the soup]
            profile_attributes = {
                "height": "HEIGHT",
                "weight": "WEIGHT",
                "birthday": "YEAR OF BIRTH",
                "birthplace": "PLACE OF BIRTH",
                "bloodtype": "BLOOD TYPE",
                "debut": "DEBUT",
                "finisher": "FINISH HOLD",
                "theme": "THEME SONG",
                "blog": "BLOG"
            }

        except Exception as e:
            logging.error("Unable to scrape profiles")

        # For each profile found on the profiles page and pull all of their attributes into a dict
        for profile in profiles:
            logging.info(f"Scraping attributes for {profile['name']}")
            profile_soup = self.create_soup(profile["link"], "lxml").find("div", class_="profileDetail")

            # Loop through the profile_attributes dict, adding the key and value to the individual dict of the wrestler
            for key in profile_attributes:
                # BeautifulSoup throws an AttributeError exception if the element is not found, so we need to catch these because the attributes listed for each wrestler is not consistent
                try:
                    profile["attributes"][key] = profile_soup.find("dt", text=profile_attributes[key]).findNext("dd").get_text().strip()
                except AttributeError:
                    pass

            # Find UNIT separately from the loop as it's stored in a p tag
            try:
                profile["attributes"]["unit"] = profile_soup.find("p", text="UNIT").findNext("p").get_text().strip()
            except AttributeError:
                pass

            # For twitter, we're pulling the link, not the text, so this is done separately
            try:
                profile["attributes"]["twitter"] = profile_soup.find("dt", text="TWITTER").findNext("a")["href"]
            except AttributeError:
               pass

            # The bio is in a textBox div
            try:
                profile["bio"] = profile_soup.find("div", class_="textBox").get_text().strip()
            except AttributeError:
                pass

            logging.debug("profile: " + str(profile))

        return profiles

    def update_profile(self, profile):
        logging.info(f"Updating profile {profile['name']}")

        try:
            # For each profile in the scraped data, check if it already exists in the DB
            if Profile.objects(name=profile["name"]):

                # If the profile already exists, update to reflect any changes to the data
                update = Profile.objects(name=profile["name"]).update(**profile, full_result=True)
                
                # If any changes are actually made, timestamp and log
                if update.modified_count > 0:
                    Profile.objects(name=profile["name"]).update(updated_at=datetime.now, full_result=True)
                    logging.info(f"Profile updated: {profile['name']}")
            else:
                # If profile is not already in DB, add it
                profile_doc = Profile(**profile).save()
                logging.info(f"New profile added: {profile_doc.name}")
            
        except Exception as e:
            logging.error(f"Error adding or updating profile {profile['name']}: " + str(e))

    def update_removed_profiles(self, profiles):
        logging.info("Updating removed profiles")
        # Mark removed profiles as such - they will be deleted by the bot after notifying @here
        try:
            for p in Profile.objects.all():
                if not [x for x in profiles if x['name'] == p.name]:
                    p.update(removed=True)
                    logging.info(f"Profile no longer exists: {p.name}")
        
        except Exception as e:
            logging.error("Error updating removed profiles: " + e)