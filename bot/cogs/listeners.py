import logging
import discord

from discord.ext import commands

import utils.tasks
from database.models import SpoilerMode
from settings.constants import (
    NEW_MEMBER_CHANNEL, RULES_CHANNEL, NEW_POD_CHANNEL, OWNER_ID, NJPW_SPOILER_CHANNEL, NON_NJPW_SPOILER_CHANNEL
)

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    ###
    # Event Listeners
    # https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=bot%20listen#discord.ext.commands.Bot.listen
    ###

    # Runs when a new member joins the server
    @commands.Cog.listener("on_member_join")
    async def on_member_join(self, member):
        logging.info(f"New member joined - {member.name}")
        # Sends a DM to new members requesting that they pay attention to the rules channel and some points on how to get help with the boss
        try:
            await member.create_dm()
            await member.dm_channel.send(f"Hi {member.name}! Thanks for joining us.\n"
            f"Before you do anything, make sure you head to {self.bot.rules_channel.mention} to make sure you're aware of the rules and guidelines.\n"
            f"This bot is here to help you. For more details on what you can do with the bot, use: ```!help```"
            f"If you have find any issues with the bot and want to make suggestions, drop a DM to {self.bot.owner.mention}\n"
            "Have fun!")

            logging.debug(f"Successfully sent welcome DM to new user {member.name}")

        except Exception as e:
            logging.error(f"Unable to create DM channel for {member.name}:" + e)

        # If spoiler mode is on, mentions them in #general and points them in the direction of the spoiler-zone channels
        spoiler_mode = SpoilerMode.objects()
        if spoiler_mode:
            await self.bot.general_channel.send(f"Welcome {member.mention}! For spoilerific chat about the ongoing/last show, join us in the spoiler channels:\n")
            for s in spoiler_mode:
                if s.mode == "njpw":
                    await self.bot.general_channel.send(f"**{s.title}**: {self.bot.njpw_spoiler_channel.mention}")
                if s.mode == "non-njpw":
                    await self.bot.general_channel.send(f"**{s.title}**: {self.bot.non_njpw_spoiler_channel.mention}")

    # A listener for all messages in the server
    # Most likely use case will be for temporary or "unofficial" commands that do not use the standard prefix
    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        # No message listeners are used yet
        pass

    @commands.Cog.listener("on_command")
    async def on_command(self, ctx):
        logging.info(f"Command [{ctx.command}] invoked with msg [{ctx.message.content}] by {ctx.author}")

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        logging.error(f"Command [{ctx.invoked_with}] failed with msg [{ctx.message.content}] by {ctx.author}: {error}")


def setup(bot):
    bot.add_cog(Listeners(bot))