from discord.ext import commands
import discord

import utils.embeds

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
    async def next_shows(self, ctx, number_of_shows=3):
        # If "nextshow" is used to invoke the command, embrace grammatical correctness and display only one show
        if ctx.invoked_with == "nextshow":
            number_of_shows = 1

        # build and send the reply
        embed = utils.embeds.shows_embed("schedule", self.bot.next_shows, number_of_shows)
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
    async def last_shows(self, ctx, number_of_shows=3):
        # grammatical correctness is for life, only display one show if "lastshow" is used to invoke
        if ctx.invoked_with == "lastshow":
            number_of_shows = 1
        
        # build and send the reply
        embed = utils.embeds.shows_embed("result", self.bot.last_shows, number_of_shows)
        await ctx.send(embed=embed)

    # Displays whether spoiler mode is currently set or not
    @commands.command(name="spoiler", 
        brief="Check whether there's currently a spoiler embargo",
        help="""Shows whether spoiler-zone mode is currently ON or OFF."""
        )
    async def spoiler(self, ctx):
        if self.bot.spoiler:
            await ctx.send("_#spoiler-zone mode is ON, keep show chat in the relevant spoiler-zone channel_")
        else:
            await ctx.send("_#spoiler-zone mode is OFF, anything goes!_")


def setup(bot):
    bot.add_cog(Shows(bot))