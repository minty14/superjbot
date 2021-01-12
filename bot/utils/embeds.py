"""
Functions to build commonly used embeds.

discord.py builds embeds using the Embed Class and Methods, as many command replies are standard
in structure, functions are defined here to make them repeatable.

https://discordpy.readthedocs.io/en/latest/api.html?highlight=discord%20embed#discord.Embed
"""
from discord import Embed

from datetime import datetime
from pytz import timezone

# Build an embed with the general info of the podcast
# All information is currently pulled from the show's RedCircle page
def pod_info_embed(pod_info, last_pod):
    embed = Embed(
        title=pod_info["title"],
        url=pod_info["url"],
        description=pod_info["description"]
    )

    embed.set_thumbnail(
        url=pod_info["img_url"]
    )

    embed.add_field(
        name="Latest Episode",
        value=last_pod["title"] + " - " +
        last_pod["published"].strftime("%a %d %b %Y") + "\n" + last_pod["link"],
        inline=False
    )

    embed.add_field(
        name="Twitter",
        value="https://twitter.com/thesuperjcast",
        inline=False
    )

    embed.add_field(
        name="Donate",
        value="https://app.redcircle.com/shows/cf1d4e82-ac3d-47e6-948d-1d299cf6744e/sponsor",
        inline=False
    )

    embed.add_field(
        name="ProWrestlingTees",
        value="https://www.prowrestlingtees.com/superjcast",
        inline=False
    )

    return embed

# Build an embed with information on the latest pod episode
# Currently uses the last_pod info, so only works for the latest episode, but could be expanded to show any episode
def pod_episode_embed(last_pod):
    embed = Embed(
        title=last_pod["title"],
        url=last_pod["link"],
        description=last_pod["description"]
    )

    embed.add_field(
        name="Download",
        value=last_pod["file"],
        inline=False
    )

    embed.add_field(
        name="Published",
        value=last_pod["published"]
    )

    embed.add_field(
        name="Duration",
        value=last_pod["duration"]
    )

    return embed

# Build an embed with info on future shows
# The number of shows to display declared in an argument
def schedule_shows_embed(shows, number_of_shows):
    # Build the title and intro section of the embed depending on the types, and number, of shows
    if number_of_shows == 1:
        show = shows[0]
        
        embed = Embed(
                title=show.name,
                description=show.card
            )

        # Some fields are blank on njpw1972.com and this causes errors when trying to add a field
        # Check whether they exist before creating the field
        
        if show.city:
            embed.add_field(
                name="City",
                value=show.city
            )

        if show.venue:
            embed.add_field(
                name="Venue",
                value=show.venue
            )

        embed.add_field(
            name="Time",
            value=zone_times_str(show.date),
            inline=False
        )
                
    
    else:
        embed = Embed(
                title="Upcoming NJPW Shows",
                url="https://www.njpw1972.com/schedule",
                description=f"Here's the next {number_of_shows} shows..."
            )

        for show in shows:

            embed.add_field(
                name=show.name,
                value=f"Card: {show.card}\nCity: {show.city}\nVenue: {show.venue}\n" + zone_times_str(show.date),
                inline=False
            )
    
    # Use the logo of the next show as the embed thumbnail
    embed.set_thumbnail(url=shows[0].thumb)

    return embed

# Build an embed with info on past shows
# The number of shows to display declared in an argument
def result_shows_embed(shows, number_of_shows):
    # Build the title and intro section of the embed depending on the types, and number, of shows
    embed = Embed(
        title="Previous NJPW Shows",
        url="https://www.njpw1972.com/result",
        description=f"Here's the previous {number_of_shows} show(s)!"
    )

    for show in shows:

        embed.add_field(
            name=show["name"],
            value=f"{show.date.strftime(datefmt)}\nCity: {show.city}\nVenue: {show.venue}",
            inline=False
        )
    
    # Use the logo of the next show as the embed thumbnail
    embed.set_thumbnail(url=shows[0]["thumb"])

    return embed

# Build an embed with info on shows added to the schedule
def new_shows_embed(shows):
    embed = Embed()

    for show in shows:

        embed.add_field(
            name=show["name"],
            value=f"City: {show.city}\nVenue: {show.venue}\n" + zone_times_str(show.date),
            inline=False
        )

    embed.set_thumbnail(
        url=shows[0]["thumb"]
    )

    return embed

# Build an embed with show title and end times for the start of a spoiler mode
def spoiler_mode_embed(spoiler_mode):

    embed = Embed(
        title=spoiler_mode.title
    )

    embed.add_field(
        name="Spoiler mode ends at:",
        value=zone_times_str(spoiler_mode.ends_at)
    )

    if spoiler_mode.thumb:
        embed.set_thumbnail(
            url=spoiler_mode.thumb
        )
    
    return embed

# Build an embed with a wrestler's profile using a provided dict
# Profile info is pulled from njpw1972.com/profile
def profile_embed(profile):
    
    if profile["attributes"]["unit"] in colours:
        colour = colours[profile["attributes"]["unit"]]
    else:
        colour = 8359053

    embed = Embed(
        title=profile["name"],
        url=profile["link"],
        color=colour
    )

    embed.set_thumbnail(
        url=profile["render"]
    )

    for a in profile["attributes"]:
        embed.add_field(
                name=a.title(),
                value=profile["attributes"][a]
            )

    return embed

# Build an embed with a wrestler's bio using a provided dict
# Bio info is pulled from njpw1972.com/profile
def bio_embed(profile):

    if profile["attributes"]["unit"] in colours:
        colour = colours[profile["attributes"]["unit"]]
    else:
        colour = 8359053

    embed = Embed(
        title=profile["name"],
        url=profile["link"],
        color=colour,
        description=profile["bio"][:2040] + "..."
    )

    embed.set_thumbnail(
        url=profile["render"]
    )

    if len(profile["bio"]) > 2048:
        embed.set_footer(
            text="Bio truncated due to Discord Embed limits, see the full profile by visiting njpw1972.com"
        )

    return embed

# Faction specific Discord colour codes
colours = {
        "Suzuki gun": 12745742,
        "Los Ingobernables de Japón": 15158332,
        "CHAOS": 16302848,
        "BULLET CLUB": 12370112,
        "NJPW main unit": 2123412,
        "The Empire": 3066993
    }

# Variables and functions to make managing time formatting easier
timefmt = "%H:%M %Z"
datefmt = "%a %d %b %Y"
dtfmt = "%a %d %b %Y %H:%M %Z"
zone_PST = timezone("America/Los_Angeles")
zone_EST = timezone("America/New_York")
zone_GMT = timezone("Europe/London")
zone_JST = timezone("Asia/Tokyo")

def zone_time(time, zone, fmt):
    tz_time = time.astimezone(zone)
    return tz_time.strftime(fmt)

def zone_times_str(date):
    return f"{zone_time(date, zone_PST, dtfmt)}\n{zone_time(date, zone_EST, dtfmt)}\n{zone_time(date, zone_GMT, dtfmt)}\n{zone_time(date, zone_JST, dtfmt)}"


def kenny_alarm_embed(kenny_alarm):
    embed = Embed(
        title=":rotating_light: Gamer Alarm Status :rotating_light:"
    )

    embed.add_field(
        name="Days Since Last Mention:",
        value=number_to_emojis((datetime.now()-kenny_alarm.last_mention_time).days),
        inline=False
    )

    embed.add_field(
        name="Guilty user:",
        value=kenny_alarm.last_mention_user,
        inline=False
    )

    embed.add_field(
        name="Offending message:",
        value=kenny_alarm.last_mention_message + "\n" + kenny_alarm.last_mention_link,
        inline=False
    )

    embed.add_field(
        name="Record number of days without a gamer mention:",
        value=kenny_alarm.record_days,
        inline=False
    )

    embed.set_thumbnail(
        url="https://www.njpw1972.com/wp-content/uploads/2017/02/kenny_20180611_2-352x528.png"
    )

    return embed

def number_to_emojis(number):
    
    num_emojis = {
        "1":":one:",
        "2":":two:",
        "3":":three:",
        "4":":four:",
        "5":":five:",
        "6":":six:",
        "7":":seven:",
        "8":":eight:",
        "9":":nine:",
        "0":":zero:"
    }

    for k, v in num_emojis.items():
        number = (str(number)).replace(k, v)
    
    return number
