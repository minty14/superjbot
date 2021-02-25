"""
Cog for show related commands. 

These commands pull and display info related to previous and upcoming shows
"""

from datetime import datetime, timedelta

import discord
from discord.ext import commands

import utils.embeds
from database.models import (
    SpoilerMode, ScheduleShow, ResultShow
)

class Shows(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###
    # Bot Commands
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20command#discord.ext.commands.Bot.command
    ###

    # Displays info upcoming shows - takes the number of shows to display as an argument
    # Info is scraped from the NJPW website and stored in the bot.next_shows attribute
    @commands.command(name="nextshows",
        aliases=["next", "nextshow"],
        brief="Show details on upcoming show(s)", 
        help="""Show details on the specified number of upcoming NJPW shows.
        For each show, displays the following information:
        \tDate of the show, with door and bell times in JST.
        \tThe city in which the show takes place.
        \tThe venue at which the show takes place.""",
        usage="[number_of_shows] (defaults: \"nextshows/next\"=3 \"nextshow\"=1)"
        )
    async def next_shows(self, ctx, number_of_shows=1):
        # If "nextshow" is used to invoke the command, embrace grammatical correctness and display only one show
        if ctx.invoked_with == "nextshow":
            number_of_shows = 1

        # DB query for the requested number of shows
        next_shows = ScheduleShow.objects[:number_of_shows]
        
        # build and send the reply
        embed = utils.embeds.schedule_shows_embed(next_shows, number_of_shows)
        await ctx.send(embed=embed)

    # Displays info on previous shows - takes the number of shows to display as an argument
    # Info is scraped from the NJPW website and stored in the bot.last_shows attribute
    @commands.command(name="lastshows",
        aliases=["last", "lastshow"],
        brief="Show details on previous show(s)", 
        help="""Show details on the specified number of previous NJPW shows.
        For each show, displays the following information:
        \tDate of the show, with door and bell times in JST.
        \tThe city in which the show took place.
        \tThe venue at which the show took place.""",
        usage="[number_of_shows] (defaults: \"lastshows/last\"=3 \"lastshow\"=1)"
        )
    async def last_shows(self, ctx, number_of_shows=1):
        # grammatical correctness is for life, only display one show if "lastshow" is used to invoke
        if ctx.invoked_with == "lastshow":
            number_of_shows = 1
        
        # DB query for the requested number of shows
        last_shows = ResultShow.objects[:number_of_shows]
        
        # build and send the reply
        embed = utils.embeds.result_shows_embed(last_shows, number_of_shows)
        await ctx.send(embed=embed)

    # Displays whether spoiler mode is currently set or not
    @commands.command(name="spoiler", 
        brief="Check whether there's currently a spoiler embargo",
        help="""Shows whether spoiler-zone mode is currently ON or OFF."""
        )
    async def spoiler(self, ctx):
        njpw_spoiler = SpoilerMode.objects(mode="njpw")
        if njpw_spoiler:
            for s in njpw_spoiler:
                await ctx.send(f"NJPW _#spoiler-zone_ mode is ON for **{s.title}**, keep show chat in {self.bot.njpw_spoiler_channel.mention} (ends in {':'.join(str(s.ends_at - datetime.now()).split(':')[:2])})")
        else:
            await ctx.send("NJPW _#spoiler-zone_ mode is OFF")

        non_njpw_spoiler = SpoilerMode.objects(mode="non-njpw")
        if non_njpw_spoiler:
            for s in non_njpw_spoiler:
                await ctx.send(f"Non-NJPW _#spoiler-zone_ mode is ON for **{s.title}**, keep show chat in {self.bot.non_njpw_spoiler_channel.mention} (ends in {':'.join(str(s.ends_at - datetime.now()).split(':')[:2])})")
        else:
            await ctx.send("Non-NJPW _#spoiler-zone_ mode is OFF")


def setup(bot):
    bot.add_cog(Shows(bot))