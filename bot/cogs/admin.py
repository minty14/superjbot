import asyncio
import os
import logging

from discord.ext import commands
import discord

from utils import checks

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###
    # Bot Commands
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20command#discord.ext.commands.Bot.command
    ###

    # Simple command to confirm that the bot is online and what current latency is
    # Currently hidden to stop spam. Will later be made admin/deputy only
    @commands.command(name="ping", 
        brief="Check that the bot is alive",
        help="Checks that the bot is online and working and displays the current latency in ms."
        )
    @commands.check(checks.is_admin)
    async def ping(self, ctx):
        await ctx.send(f"Hello, I'm here :grinning: \nBot Latency: {round(self.bot.latency * 1000)}ms")

    # Admin only - stops the bot from running
    # In production, the container will restart, rendering this a "restart" function
    @commands.command(name="kill",
        aliases=["killbot", "stop", "stopbot"],
        brief="Stop the bot",
        help="""Stops the bot from running. Can be used if bot is having issues or causing problems in the server. Once stopped, the bot will restart.
                Should only be used """,
        hidden=True
        )
    @commands.check(checks.is_admin)
    async def kill(self, ctx):
        await self.bot.close()

    # Sets the spoiler variable to true, which does the following:
    #   - Alerts @here when spoiler-zone mode starts, and for how long
    #   - Alerts @here when the spoiler embargo is lifted
    #   - Displays a reminder to new users that spoiler chat should go in the relevant channel
    @commands.command(name="setspoiler", 
        brief="Check whether there's currently a spoiler embargo",
        help="""Sets spoiler-zone mode to ON, for the specified number of hours.
                Sets spoiler-zone mode to OFF if already running.""",
        usage="[number_of_time] (default=12, valid=WHOLE NUMBERS) [unit_of_time] (default=h, valid=s,m,h,d)\neg. \"!spoiler 24 h\""
        )
    @commands.check(checks.is_admin)
    async def set_spoiler(self, ctx, time: int = 12, unit="h"):
        # sleep time is set in seconds, so create a multiplier depending on the time unit set
        units = {"s": 1, "m": 60, "h": 3600, "d": 86400}

        # spoiler mode is not currently active - set mode to on, display an @here message in the channel it was invoked in, and sleep for the specified time
        if not self.bot.spoiler:
            self.bot.spoiler = True
            await ctx.send(f"@here We're now in the _spoiler-zone_, keep show chat in the relevant spoiler-zone channel\n\nSpoiler embargo will lift in {str(time)}{unit}")
            logging.info(f"Spoiler mode set by {ctx.author} for {str(time)}{unit}")
            await asyncio.sleep(time * units[unit])

        # spoiler mode is currently active - set mode off and inform @here
        self.bot.spoiler = False
        await ctx.send("@here _Spoiler embargo lifted, chat away!_")
        await ctx.invoke(self.bot.get_command("nextshows"))
        logging.info(f"Spoiler mode lifted")

    ###
    # Cog Controls
    ###

    # Load the extension(s) with the given cog name(s)
    # Can take multiple cog names as arguments
    @commands.command(name="load", 
        brief="Load/enable the category with the given name",
        help="""Load/enable the category with the given name. Only works if the category name given is not already loaded/enabled.
                
                More than one name can be given, separated by spaces, to load multiple categories.
                
                Use this to enable previously disabled categories.""",
        usage="[category_name(s)]"
        )
    @commands.check(checks.is_admin)
    async def load(self, ctx, *cogs: str):
        for cog in cogs:
            try:
                self.bot.load_extension("cogs." + cog)
                await ctx.send(f"\"{cog}\" category loaded")
                logging.debug(f"{cog} loaded by {ctx.author}")
            except Exception as e:
                await ctx.send(f"Could not load \"{cog}\" category")
                logging.error(f"Error loading {cog}: " + e)
        
    # Unload the extension(s) with the given cog name(s)
    # Can take multiple cog names as arguments
    @commands.command(name="unload", 
        brief="Unload/disable the category with the given name",
        help="""Unload/disable the category with the given name. Only works if the category name given is not already unloaded/disabled.
                
                More than one name can be given, separated by spaces, to load multiple categories.
                
                This command is useful if you want to indefinitely disable a set of commands. (You can see which command falls under which category with !help""",
        usage="[category_name(s)]"
        )
    @commands.check(checks.is_admin)
    async def unload(self, ctx, *cogs: str):
        for cog in cogs:
            try:
                self.bot.unload_extension("cogs." + cog)
                await ctx.send(f"\"{cog}\" category unloaded")
                logging.debug(f"{cog} unloaded by {ctx.author}")
            except Exception as e:
                await ctx.send(f"Could not unload \"{cog}\" category")
                logging.error(f"Error unloading {cog}: " + e)
        
    # Reload the extension(s) with the given cog name(s)
    # Can take multiple cog names as arguments
    @commands.command(name="reload", 
        brief="Reload/disable & enable the category with the given name",
        help="""Reload/disable & enable the category with the given name. If the category(s)' not loaded, it will try to load it.
                
                More than one name can be given, separated by spaces, to reload multiple categories.
                
                Used to update categories when changes have been made, without restarting the whole bot.""",
        usage="[category_name(s)]"
        )
    @commands.check(checks.is_admin)
    async def reload(self, ctx, *cogs: str):
        for cog in cogs:    
            try:
                self.bot.reload_extension("cogs." + cog)
                await ctx.send(f"\"{cog}\" category reloaded")
                logging.debug(f"{cog} reloaded by {ctx.author}")
            except Exception as e:
                await ctx.send(f"Could not reload \"{cog}\" category, trying to load")
                logging.error(f"Error reloading {cog}: " + e)
                # If the cog isn't currently loaded, it will raise an exception, so try to load the cog
                await ctx.invoke(self.bot.get_command("load"), cog)
        
    # Reload all the cogs in the cogs folder
    @commands.command(name="reloadall", 
        brief="Reload/disable & enable all categories.",
        help="""Reload/disable & enable enable all categories. If the category(s)' not loaded, it will try to load it.
                
                Used to update categories when changes have been made, without restarting the whole bot."""
        )
    @commands.check(checks.is_admin)
    async def reloadall(self, ctx):
        for filename in os.listdir("./bot/cogs"):
            if filename.endswith(".py") and filename != "__init__.py":
                cog = filename[:-3]
                await ctx.invoke(self.bot.get_command("reload"), cog)


def setup(bot):
    bot.add_cog(Admin(bot))