import discord


def pod_info_embed(pod_info, last_pod):
    embed = discord.Embed(
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

def last_pod_embed(last_pod):
    embed = discord.Embed(
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

def shows_embed(type, shows, number_of_shows):
    events = shows[:number_of_shows]
    
    if type == "schedule":
        embed = discord.Embed(
            title="Upcoming NJPW Shows",
            url="https://www.njpw1972.com/schedule",
            description=f"Here's the next {number_of_shows} shows!"
        )
        
    elif type == "result":
        embed = discord.Embed(
            title="Previous NJPW Shows",
            url="https://www.njpw1972.com/result",
            description=f"Here's the previous {number_of_shows} shows!"
        )

    embed.set_thumbnail(url=events[0]["thumb"])

    for event in events:
        embed.add_field(
            name=event["name"],
            value=f"""Date: {event["date"]}\nCity: {event["city"]}\nVenue: {event["venue"]}""",
            inline=False
        )

    return embed