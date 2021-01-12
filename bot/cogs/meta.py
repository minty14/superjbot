import discord
from discord.ext import commands

import utils.embeds
from database.models import (
    KennyAlarm
)

class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="gamer",
        aliases=["alarm", "kennyalarm", "kenny"],
        brief="How well are we doing at not mentioning The Gamer?"
        )
    async def gamer(self, ctx):
        embed = utils.embeds.kenny_alarm_embed(KennyAlarm.objects.first())
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Meta(bot))