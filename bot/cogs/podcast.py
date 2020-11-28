from discord.ext import commands
import discord

import utils.embeds
from database.models import PodcastInfo, PodcastEpisode

class Podcast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###
    # Bot Commands
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20command#discord.ext.commands.Bot.command
    ###

    # Displays static generic infomation about the podcast
    # Info scraped from the podcast RedCircle page 
    @commands.command(name="podinfo",
        aliases=["pod"],
        brief="Show general info about the podcast", 
        help="""Shows general information about the Super J-Cast, with a link to the show's RedCircle Page.
        For the podcast, displays the following information:
        \tThe latest episode title with link to the episode on RedCircle.
        \tA link to the show's Twitter account.
        \tA link to the show's sponsor page.
        \tA link to the show's ProWrestlingTees store.
        """
        )
    async def pod_info(self, ctx):
        # build and send the reply
        pod_info = PodcastInfo.objects.first()
        last_pod = PodcastEpisode.objects.first()
        embed = utils.embeds.pod_info_embed(pod_info, last_pod)
        await ctx.send(embed=embed)
            
    # Show details on the lates podcast episode
    # Info scraped from the podcast RedCircle page 
    @commands.command(name="lastpod", 
        aliases=["latest", "latestpod"],
        brief="Show details on the latest pod episode",
        help="""Shows details on the latest episode of the Super J-Cast, with a link to listen to the show online.
        For the latest episode, displays the following information:
        \tThe episode's description.
        \tThe episode's release date.
        \tThe episode's duration."""
        )
    async def pod_episode_embed(self, ctx):
        # build and send the reply
        last_pod = PodcastEpisode.objects.first()
        embed = utils.embeds.pod_episode_embed(last_pod)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Podcast(bot))