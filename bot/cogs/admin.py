import os
import logging
from datetime import datetime, timedelta
from mongoengine import errors

import discord
from discord.ext import commands

from utils import checks
from utils import embeds
from database.models import SpoilerMode, ScheduleShow

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
        await ctx.send("Bot stopping/restarting")
        logging.info(f"Bot stopped with {ctx.invoked_with} by {ctx.author}")
        await self.bot.close()

    # Sets the spoiler variable to true, which does the following:
    #   - Alerts @here when spoiler-zone mode starts, and for how long
    #   - Alerts @here when the spoiler embargo is lifted
    #   - Displays a reminder to new users that spoiler chat should go in the relevant channel
    @commands.command(name="setspoiler", 
        brief="Control a custom spoiler-zone mode",
        help="""Start a customer spoiler-zone mode, or stop an existing one.
                !setspoiler takes 3 inputs, but 2 are optional:
                "Event Name" - The name of the show or event, used to identify the spoiler-mode
                [njpw|non-njpw|off] - Set the type of spoiler mode (njpw or non-njpw), or end an existing spoiler mode with "off"
                [number_of_hours] - Set the number of hours the spoiler-mode will be in effect for, starting immediately
                
                If not specified, the defaults are: mode = non-njpw, hours = 14
                To set a different number of hours, you MUST also provide the mode, even if it is the default""",
        usage="\"Event Name\" [njpw|non-njpw|off] [number_of_hours]"
        )
    @commands.check(checks.is_admin)
    async def set_spoiler(self, ctx, title, mode="non-njpw", hours: int = 14):
        
        # create show doc
        spoiler_mode = SpoilerMode(
            mode=mode,
            title=title,
            ends_at=datetime.now() + timedelta(hours=hours),
            thumb=None
        )
        
        try:
            # send to relevant channel
            if mode == "njpw":
                spoiler_mode.save()
                await self.bot.general_channel.send(
                            content=f"@here **{spoiler_mode.title}** starting. Head to {self.bot.njpw_spoiler_channel.mention} for spoiler chat.",
                            embed=embeds.spoiler_mode_embed(spoiler_mode)
                        )

            elif mode == "non-njpw":
                spoiler_mode.save()
                await self.bot.non_njpw_channel.send(
                            content=f"@here **{spoiler_mode.title}** starting. Head to {self.bot.non_njpw_spoiler_channel.mention} for spoiler chat",
                            embed=embeds.spoiler_mode_embed(spoiler_mode)
                        )

            elif mode == "off":
                spoiler_mode = SpoilerMode.objects.get(title=title)
                spoiler_mode.delete()
                if spoiler_mode.mode == "njpw":
                    await self.bot.general_channel.send(
                            content=f"@here **{title}** _#spoiler-zone_ time has ended. Spoil away.\n\nNext show:",
                            embed=embeds.schedule_shows_embed(ScheduleShow.objects(date__gt=datetime.now())[:1], 1)
                        )

                if spoiler_mode.mode == "non-njpw":
                    await self.bot.non_njpw_channel.send(
                        f"@here **{title}** _#spoiler-zone_ time has ended. Spoil away."
                    )

            else:
                await ctx.send("_mode_ must be one of: \"njpw\", \"non-njpw\", \"off\"")
                spoiler_mode.delete()
        
        except errors.NotUniqueError:
            spoiler_mode = SpoilerMode.objects.get(title=title)
            await ctx.send(content=f"Event \"{title}\" already exists",
                            embed=embeds.spoiler_mode_embed(spoiler_mode))

        except errors.DoesNotExist:
                    await ctx.send(content=f"Event \"{title}\" does not exist.")


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
                await ctx.send(f"Could not load \"{cog}\" category: " + e)
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
                await ctx.send(f"Could not unload \"{cog}\" category: " + e)
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