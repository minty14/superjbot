"""
A web scraper Class instantiated once the bot starts running and is logged in. 

Scrapes information from commonly used sources as part of the update_info loop.
"""
from bs4 import BeautifulSoup
import requests

class Scraper():
    def __init__(self):
        # Store some commonly used URLs
        self.pod_info_url = "https://redcircle.com/shows/super-j-cast/episodes/d7179957-bb87-4208-9117-a1c6f43b9229"
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
        soup = self.create_soup(self.pod_info_url, "lxml")

        info = {
            "title": soup.find(class_="show-title").get_text().strip(),
            "description": soup.find_all("div", class_="show-page__about")[0].p.get_text().strip(),
            # This isn't returning the right value at the moment, so using the hardcoded link
            # "img_url": soup.find_all("img", class_="show-image")[0].src,
            "img_url": "https://media.redcircle.com/images/2020/8/20/14/3b3c9e21-4329-4283-b1c4-6ab1b3be5a6a_93146d1b-2f16-477b-b6c1-c17069ef70dc_c8a8e6cf-7ba4-44bb-954c-53ec5023adc8_32630451.jpg?d=280x280",
            "url": self.pod_info_url
        }

        return info

    # Pull data on the latest podcast episode direct from the RSS feed
    def last_pod(self):
        soup = self.create_soup(self.pod_rss_feed, "xml")
        
        # .find pulls the first item in the RSS feed, which will be the latest episode
        item = soup.find("item")

        latest = {
            "title": item.title.text,
            "description": item.description.text,
            "link": item.link.text,
            # Remove some of the formatting around the date
            "published": " ".join(item.pubDate.text.split(" ")[0:4]), 
            "duration": item.duration.text,
            "file": item.enclosure.url
        }

        return latest

    # Pull info on past or future shows
    # type is either result (past) or schedule (future)
    def shows(self, type):
        soup = self.create_soup("https://www.njpw1972.com/" + type + "/", "lxml")

        all_events = soup.find_all("div", class_="event")

        events_list = []

        for event in all_events:
            event_name = event.find("h3").get_text().strip()
            dates = event.find_all("li")
            for date in dates:
                show_dict = {
                    "name": event_name,
                    "date": " ".join(date.find("p", class_="date").get_text().strip().split()),
                    "city": date.find("p", class_="city").get_text().strip(),
                    "venue": date.find("p", class_="venue").get_text().strip(),
                    "thumb": event.find("img")["src"]
                }
                events_list.append(show_dict)

        return events_list

    # TODO: create function to pull the results from past show(s)
    def results(self):
        pass

    # Build a list of the profiles on njpw1972.com
    # Loop through the profiles to pull more info from each wrestler's individual profile page
    def profiles(self):
        soup = self.create_soup(self.njpw_profiles_url, "lxml")

        profile_list = soup.find("ul", class_="wrestlerList").find_all("li")

        # Create the list of profile dicts
        profiles = []

        # For each profile on the page, we create a dict containing info which is then added to with the info in the individual profile page
        for profile in profile_list:
            profile_dict = {
                "name": profile.find("p", class_="name").get_text().strip(),
                "link": profile.find("a")["href"],
                "render": profile.find("img")["src"]
            }
            profiles.append(profile_dict)
            print(f"Found {profile_dict['name']}")

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
        for pf in profiles:
            print(f"Adding Attributes to {pf['name']}")
            pf_soup = self.create_soup(pf["link"], "lxml").find("div", class_="profileDetail")

            # Loop through the profile_attributes dict, adding the key and value to the individual dict of the wrestler
            for key in profile_attributes:
                # BeautifulSoup throws an AttributeError exception if the element is not found, so we need to catch these because the attributes listed for each wrestler is not consistent
                try:
                    pf[key] = pf_soup.find("dt", text=profile_attributes[key]).findNext("dd").get_text().strip()
                except AttributeError:
                    pf[key] = None

            # Find UNIT separately from the loop as it's stored in a p tag
            try:
                pf["unit"] = pf_soup.find("p", text="UNIT").findNext("p").get_text().strip()
            except AttributeError:
                pf["unit"] = None

            # For twitter, we're pulling the link, not the text, so this is done separately
            try:
                pf["twitter"] = pf_soup.find("dt", text="TWITTER").findNext("a")["href"]
            except AttributeError:
                pf["twitter"] = None

            # The bio is in a textBox div
            try:
                pf["bio"] = pf_soup.find("div", class_="textBox").get_text().strip()
            except AttributeError:
                pf["bio"] = None
        
        return profiles
