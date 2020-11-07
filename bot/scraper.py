from bs4 import BeautifulSoup
import requests


class Scraper():
    def __init__(self):
        pass

    def create_soup(self, url, features):
        page = requests.get(url)
        soup = BeautifulSoup(page.content, features)

        return soup

    def pod_info(self):
        url = "https://redcircle.com/shows/super-j-cast/episodes/d7179957-bb87-4208-9117-a1c6f43b9229"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "lxml")

        info = {
            "title": soup.find(class_="show-title").get_text().strip(),
            "description": soup.find_all("div", class_="show-page__about")[0].p.get_text().strip(),
            # This isn't returning the right value at the moment, so using the hardcoded link
            # "img_url": soup.find_all("img", class_="show-image")[0].src,
            "img_url": "https://media.redcircle.com/images/2020/8/20/14/3b3c9e21-4329-4283-b1c4-6ab1b3be5a6a_93146d1b-2f16-477b-b6c1-c17069ef70dc_c8a8e6cf-7ba4-44bb-954c-53ec5023adc8_32630451.jpg?d=280x280",
            "url": url
        }

        return info

    def last_pod(self):
        page = requests.get(
            "https://feeds.redcircle.com/cf1d4e82-ac3d-47e6-948d-1d299cf6744e")
        soup = BeautifulSoup(page.content, "xml")
        item = soup.find("item")

        latest = {
            "title": item.title.text,
            "description": item.description.text,
            "link": item.link.text,
            "published": " ".join(item.pubDate.text.split(" ")[0:4]),
            "duration": item.duration.text,
            "file": item.enclosure.url
        }

        return latest

    def shows(self, type):
        page = requests.get("https://www.njpw1972.com/" + type + "/")
        soup = BeautifulSoup(page.content, "lxml")

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

    def results(self):
        pass

    def profiles(self):
        soup = self.create_soup("https://www.njpw1972.com/profiles/", "lxml")

        profile_list = soup.find("ul", class_="wrestlerList").find_all("li")

        profiles = []

        for profile in profile_list:
            profile_dict = {
                "name": profile.find("p", class_="name").get_text().strip(),
                "link": profile.find("a")["href"],
                "render": profile.find("img")["src"]
            }
            profiles.append(profile_dict)

        profile_attributes = {
            "height": "HEIGHT",
            "weight": "WEIGHT",
            "birthday": "YEAR OF BIRTH",
            "birthplace": "PLACE OF BIRTH",
            "blood type": "BLOOD TYPE",
            "debut": "DEBUT",
            "finisher": "FINISH HOLD",
            "theme": "THEME SONG",
            "blog": "BLOG"
        }

        for pf in profiles:
            pf_soup = self.create_soup(pf["link"], "lxml").find("div", class_="profileDetail")

            for key in profile_attributes:
                try:
                    pf[key] = pf_soup.find("dt", text=profile_attributes[key]).findNext("dd").get_text().strip()
                except AttributeError:
                    pf[key] = None
            try:
                pf["unit"] = pf_soup.find("p", text="UNIT").findNext("p").get_text().strip()
            except AttributeError:
                pf["unit"] = None

            try:
                pf["twitter"] = pf_soup.find("dt", text="TWITTER").findNext("a")["href"]
            except AttributeError:
                pf["twitter"] = None

            try:
                pf["bio"] = pf_soup.find("div", class_="textBox").get_text().strip()
            except AttributeError:
                pf["bio"] = None
        
        return profiles
