from discord.ext import commands
import discord

import utils.embeds
from database.models import Profile

class Profiles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###
    # Bot Commands
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20command#discord.ext.commands.Bot.command
    ###
     
    # Display the profile that matches the searched name
    # Uses a keyword only argument so that users can search names with spaces in without ""s
    @commands.command(name="profile",
        aliases=["p"],
        brief="Provide the name of a wrestler to get their profile",
        help="""Search for, and display, a current NJPW wrestler's profile.\n
                Partial searches are fine, so for example "!profile taka" will find any wrestler with "taka" anywhere in their name."""
        )
    async def profile(self, ctx, *, name):
        # Force the searched name to be 3 or more characters - a lower limit can cause spammy replies 
        if len(name) < 3:
            await ctx.send("Please enter at least 3 characters to find a profile")
        else:
            profiles = Profile.objects(name__icontains=name).exclude("_id", "bio")
            for p in profiles:
                embed = utils.embeds.profile_embed(p)
                await ctx.send(embed=embed)

    
    # Display the bio that matches the searched name
    # Uses a keyword only argument so that users can search names with spaces in without ""s
    @commands.command(name="bio",
        aliases=["b"],
        brief="Provide the name of a wrestler to get their bio",
        help="""Search for, and display, a current NJPW wrestler's bio.\n
                Partial searches are fine, so for example "!bio taka" will find any wrestler with "taka" anywhere in their name.
                
                Bios are limited to 2048 characters due to Discord limitations."""
        )
    async def bio(self, ctx, name):
        # Force the searched name to be 3 or more characters - a lower limit can cause spammy replies 
        if len(name) < 3:
            await ctx.send("Please enter at least 3 characters to find a profile")
        else:
            bios = Profile.objects(name__icontains=name).exclude("_id")
            for b in bios:
                embed = utils.embeds.bio_embed(b)
                await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Profiles(bot))