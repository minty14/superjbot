"""
discord.py builds embeds using the Embed Class and Methods, as many command replies are standard
in structure, functions are defined here to make them repeatable.

https://discordpy.readthedocs.io/en/latest/api.html?highlight=discord%20embed#discord.Embed
"""
from discord import Embed

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
        last_pod["published"] + "\n" + last_pod["link"],
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
        name="Published",
        value=last_pod["published"]
    )

    embed.add_field(
        name="Duration",
        value=last_pod["duration"]
    )

    return embed

# Build an embed with info on past or future shows
# The number of shows to display declared in an argument
def shows_embed(type, shows, number_of_shows):
    # Splice the requested number of shows from the shows dict
    events = shows[:number_of_shows]
    
    # Build the title and intro section of the embed depending on the types, and number, of shows
    if type == "schedule":
        embed = Embed(
            title="Upcoming NJPW Shows",
            url="https://www.njpw1972.com/schedule",
            description=f"Here's the next {number_of_shows} shows!"
        )
        
    elif type == "result":
        embed = Embed(
            title="Previous NJPW Shows",
            url="https://www.njpw1972.com/result",
            description=f"Here's the previous {number_of_shows} shows!"
        )
    
    # Use the logo of the next show as the embed thumbnail
    embed.set_thumbnail(url=events[0]["thumb"])

    # Create an entry for each of the requested shows
    for event in events:
        embed.add_field(
            name=event["name"],
            value=f"""Date: {event["date"]}\nCity: {event["city"]}\nVenue: {event["venue"]}""",
            inline=False
        )

    return embed

# Build an embed with a wrestler's profile using a provided dict
# Profile info is pulled from njpw1972.com/profile
def profile_embed(profile):
    embed = Embed(
        title=profile["name"],
        url=profile["link"]
    )

    embed.set_thumbnail(
        url=profile["render"]
    )

    # Profile attributes aren't consistent across all profiles on njpw1972.com, so build a list of all possible attributes
    optional_attributes = [
        "unit", "height", "weight", "finisher", "theme", "debut", "birthplace", "birthday", "blood type", "blog", "twitter"
    ]

    # For each of the possible attributes, check if they exist in the current profile dict and create an embed field if they are
    for attr in optional_attributes:
        if profile[attr]:
            embed.add_field(
                name=attr.title(),
                value=profile[attr]
            )

    return embed
