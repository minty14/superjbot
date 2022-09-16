"""
A web scraper Class instantiated once the bot starts running and is logged in

Provides class methods to scrape information from various sources to then be stored in the DB
"""
from bs4 import BeautifulSoup
from datetime import datetime
import logging
import requests
import pytz
import re

from database.models import ScheduleShow

class Scraper():
    def __init__(self):
        # Store some commonly used URLs
        self.pod_info_url = "https://redcircle.com/shows/super-j-cast/"
        self.pod_rss_feed = "https://feeds.redcircle.com/cf1d4e82-ac3d-47e6-948d-1d299cf6744e"
        self.njpw_profiles_url = "https://www.njpw1972.com/profiles/"

    # Take a url and create a Beautiful soup object
    # Features is usually lxml or xml
    def create_soup(self, url, features):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, features)

        return soup

    # Pull general info about the podcast and create a dict
    def pod_info(self):
        logging.info("Updating podcast information")
        
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

    # Pull data on the latest podcast episode direct from the RSS feed
    def pod_episode(self):
        logging.info("Updating latest podcast episode")

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
    
    # Pull data from all podcast episodes in the RSS feed
    def all_episodes(self):
        logging.info("Updating all podcast episodes")

        soup = self.create_soup(self.pod_rss_feed, "xml")
        items = soup.find_all("item")

        all_pods = []

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

            all_pods.append(episode)

        logging.debug("all_pods: " + str(all_pods))
        
        return all_pods


    # Pull info on past or future shows
    # type is either result (past) or schedule (future)
    def shows(self, type):
        logging.info("Updating " + type + " shows")
        
        shows = []
        
        for x in range(1, 3):
            url = "https://www.njpw1972.com/" + type + "?pageNum=" + str(x)
            soup = self.create_soup(url, "lxml")
            all_events = soup.find_all("div", class_="event")
            logging.info(f"Scraping {url} for shows.")

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

                            logging.info(f"Found show {show_dict['name']}")

                            # The url of their placeholder logo needs to be replaced with the full path
                            if show_dict['thumb'] == "/wp-content/themes/njpw-en/images/common/noimage_poster.jpg":
                                show_dict['thumb'] = "https://www.njpw1972.com/wp-content/themes/njpw-en/images/common/noimage_poster.jpg"

                            # Scrape the scheduled time of the show and split our the date and time
                            date_time = " ".join(date.find("p", class_="date").get_text().strip().split())

                            show_date = " ".join(date_time.split(" ")[:4])
                            show_time = " ".join(date_time.split(" ")[5:])

                            logging.info(f"Found time for {show_dict['name']}: {date_time}")
                            
                            # Check for the format of date time
                            # Match datetimes like: SUN. MAY. 15. 2022 | DOOR 15:30 | BELL 17:00 (Standard JPN shows)
                            if re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| DOOR \d\d:\d\d \| BELL \d\d:\d\d$", date_time, re.IGNORECASE):
                                logging.info(f"Date time for {show_dict['name']} matches format 'DAY. MONTH. 00. YEAR | DOOR 00:00 | BELL 00:00'")
                                
                                # Parse date and time from text
                                # Time is text after "bell"
                                show_time = date_time.split("BELL")[1].strip()
                                
                                # Convert the text into a datetime object
                                fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %H:%M")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")
                                
                                # Timezone for shows in this format is JST so start times are localised to UTC based on that
                                tz = pytz.timezone("Asia/Tokyo")
                                
                                # Add full datetime to dict. These are duplicated here and "date" is then added to DB as date only for generic day matching 
                                show_dict['time'] = tz.localize(fmt_datetime)
                                show_dict['date'] = show_dict['time']
                                show_dict['source_tz'] = "utc"

                            # Match datetimes like: SAT. MAY. 7. 2022
                            elif re.match(r"^\w{3}\. \w{3,9}\. [0-9]{1,2}\. [0-9]{4}$", date_time, re.IGNORECASE):
                                logging.info(f"Date time for {show_dict['name']} matches RE format 'DAY. MONTH. 00. YEAR'")
                                
                                # This format provides date only, so it is parsed directly.
                                fmt_datetime = datetime.strptime(show_date, "%a. %B. %d. %Y")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")
                                
                                # No time available, so don't add it to the dict
                                show_dict['date'] = fmt_datetime
                                show_dict['source_tz'] = "none"

                                show_dict['time'] = show_dict['date']

                            # Match datetimes like: SAT. MAY. 14. 2022 | DOOR 6PM | BELL 7PM
                            elif re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| DOOR \d(\:\d\d)?[A|P]M( \(.+?\))? \| BELL \d(\:\d\d)?[A|P]M( \(.+?\))?$", date_time, re.IGNORECASE):
                                logging.info(f"Date time for {show_dict['name']} matches format 'DAY. MONTH. 00. YEAR | DOOR 0PM | BELL 0PM'")
                                
                                # Time is text after "bell"
                                show_time = date_time.split("BELL")[1].strip()

                                if len(show_time) == 3:
                                    show_time = "0" + show_time

                                # Convert the text into a datetime object
                                if ":" in show_time:
                                    fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %I:%M%p")
                                else:
                                    fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %I%p")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")
                                
                                # Times in this format usually indicates USA shows, but no TZ is indicated, so it is not localised
                                show_dict['time'] = fmt_datetime
                                show_dict['date'] = show_dict['time']
                                show_dict['source_tz'] = "local"

                            # Match datetimes like: SUN. MAY. 15. 2022 | DOOR 4PM ET | BELL 5 PM ET or TUE. AUGUST. 16. 2022 | BELL 6PM JST
                            elif (re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| DOOR \d[A|P]M \w{2,4} \| BELL \d[A|P]M \w{2,4}$", date_time, re.IGNORECASE) or
                                  re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| DOOR \d[A|P]M \w{2,4} \| BELL \d [A|P]M \w{2,4}$", date_time, re.IGNORECASE) or
                                  re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| BELL \d[A|P]M \w{2,4}$", date_time, re.IGNORECASE)):
                                
                                logging.info(f"Date time for {show_dict['name']} matches format 'DAY. MONTH. 00. YEAR (| DOOR 0PM TZ) | BELL 0PM TZ'")
                                
                                # Parse date and time from text
                                # Date is the text up to the 4th space
                                show_date = " ".join(date_time.split(" ")[:4])
                                
                                # Time is text after "bell" - convert it to eg 7PM
                                show_time = date_time.split("BELL")[1].replace(" ", "")[:3]
                                
                                # Convert the text into a datetime object
                                fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %I%p")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")
                                
                                # Timezone is at the end of the string
                                show_tz = date_time.rsplit(" ", 1)[-1]
                                logging.info(f"Timezone found for {show_dict['name']}: {show_tz}")
                                
                                # Match timezones from text into pytz format
                                if show_tz == "JST":
                                    tz = pytz.timezone("Asia/Tokyo")
                                    show_dict['time'] = tz.localize(fmt_datetime)
                                    show_dict['source_tz'] = "utc"

                                elif show_tz == "ET":
                                    tz = pytz.timezone("US/Eastern")
                                    show_dict['time'] = tz.localize(fmt_datetime)
                                    show_dict['source_tz'] = "utc"
                                # If TZ is unrecognised, stick to local time
                                else:
                                    show_dict['time'] = fmt_datetime

                                show_dict['date'] = show_dict['time']

                            # Match datetimes like: WED. AUGUST. 10. 2022 | BELL 6:30PM JST
                            elif re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| BELL \d:\d\d[A|P]M \w{2,4}$", date_time, re.IGNORECASE):
                                logging.info(f"Date time for {show_dict['name']} matches format 'DAY. MONTH. 00. YEAR | BELL 0:00PM TZ'")
                                
                                # Parse date and time from text
                                # Date is the text up to the 4th space
                                show_date = " ".join(date_time.split(" ")[:4])

                                # Time is text after "bell" up to the last space
                                show_time = date_time.split("BELL")[1].rsplit(" ", 1)[0].replace(" ", "")

                                if len(show_time) == 6:
                                    show_time = "0" + show_time

                                # Timezone is at the end of the string
                                show_tz = date_time.rsplit(" ", 1)[-1]
                                logging.info(f"Timezone found for {show_dict['name']}: {show_tz}")

                                # Convert the text into a datetime object
                                fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %I:%M%p")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")

                                # Match timezones from text into pytz format
                                if show_tz == "JST":
                                    tz = pytz.timezone("Asia/Tokyo")
                                    show_dict['time'] = tz.localize(fmt_datetime)
                                    show_dict['source_tz'] = "utc"

                                elif show_tz == "ET":
                                    tz = pytz.timezone("US/Eastern")
                                    show_dict['time'] = tz.localize(fmt_datetime)
                                    show_dict['source_tz'] = "utc"
                                # If TZ is unrecognised, stick to local time
                                else:
                                    show_dict['time'] = fmt_datetime

                                show_dict['date'] = show_dict['time']

                            # Match datetimes like: SAT. AUGUST. 13. 2022 | BELL 8/7c
                            elif re.match(r"^\w{3}\. \w{3,9}\. \d{1,2}\. \d{4} \| \w{4} \d/\dc$", date_time, re.IGNORECASE):
                                # Parse date and time from text
                                # Date is the text up to the 4th space
                                show_date = " ".join(date_time.split(" ")[:4])

                                # Time is text after "/", central time - 
                                show_time = "0" + date_time.split("/")[1][0] + "PM"

                                # Convert the text into a datetime object
                                fmt_datetime = datetime.strptime(show_date + " " + show_time, "%a. %B. %d. %Y %I%p")
                                logging.info(f"Formatted datetime for {show_dict['name']}: {fmt_datetime}")

                                # Shows in this format are always central time as far as I can tell
                                tz = pytz.timezone("US/Central")
                                show_dict['time'] = tz.localize(fmt_datetime)
                                show_dict['source_tz'] = "local"

                                show_dict['date'] = show_dict['time']

                            else:
                                logging.warn(f"Cannot match format of {show_dict['name']}")
                            
                            logging.debug("show_dict: " + str(show_dict))

                            shows.append(show_dict)
                            logging.info(f"Finished with {show_dict['name']}, moving to next show.")
                        
                        except Exception as e:
                            logging.error(f"Unable to scrape show {event_name}: " + str(e))

        return shows

    def broadcasts(self):
        logging.info("Updating broadcasted shows")

        def update_live_broadcasts(broadcasts, year):
            for broadcast in broadcasts:
                try:
                    # Pull the date and time from the first 2 columns
                    show_details = [s.text for s in (broadcast.find_all('td'))][:2]
                    # Create a datetime object for the show by building a string and formatting it (Japanese time)

                    # If 後日配信 is in the show details, the time has not yet been confirmed
                    if "後日配信" in show_details:
                        logging.info(f"No time set for {show_details}, skipping...")
                    
                    else: 
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
        
        try:
            # Custom headers are needed otherwise njpwworld gives an unsupported browser error
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
            session = requests.get("https://njpwworld.com/feature/schedule#googtrans(en)", headers=headers)
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
            update_live_broadcasts(months[0].find_all('tr')[1:], years[0].text[:4])
            
            # Update next month's shows if the schedule exists
            if len(months) > 2:
                update_live_broadcasts(months[2].find_all('tr')[1:], years[1].text[:4])
        
        except Exception as e:
            logging.error("Error trying to scrape broadcast shows: " + str(e))


    # TODO: create function to pull the results from past show(s)
    def results(self):
        pass

    # Build a list of the profiles on njpw1972.com
    # Loop through the profiles to pull more info from each wrestler's individual profile page
    def profiles(self):
        logging.info("Updating profiles")

        soup = self.create_soup(self.njpw_profiles_url, "lxml")
        profile_list = soup.find("ul", class_="wrestlerList").find_all("li")

        # Create the list of profile dicts
        profiles = []

        # For each profile on the page, we create a dict containing info which is then added to with the info in the individual profile page
        for profile in profile_list:
            profile_dict = {
                "name": profile.find("p", class_="name").get_text().strip(),
                "link": profile.find("a")["href"],
                "render": profile.find("img")["src"],
                "attributes": {}
            }
            profiles.append(profile_dict)

            logging.debug("Found profile: " + profile_dict['name'])

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

        # For each profile found on the profiles page and pull all of their attributes into a dict
        for profile in profiles:
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
