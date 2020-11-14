from discord.ext import commands
import discord

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
        # Sends a DM to new members requesting that they pay attention to the rules channel and some points on how to get help with the boss
        await member.create_dm()
        rules_channel = self.bot.get_channel(RULES_CHANNEL)
        owner = self.bot.get_user(OWNER_ID)
        await member.dm_channel.send(f"Hi {member.name}! Thanks for joining us.\n"
        f"Before you do anything, make sure you head to {rules_channel.mention} to make sure you're aware of the rules and guidelines.\n"
        f"This bot is here to help you. For more details on what you can do with the bot, use: ```!help```"
        f"If you have find any issues with the bot and want to make suggestions, drop a DM to {owner.mention}\n"
        "Have fun!")

        # If spoiler mode is on, mentions them in #general and points them in the direction of the spoiler-zone channels
        if self.bot.spoiler:
            njpw_spoiler_channel = self.bot.get_channel(NJPW_SPOILER_CHANNEL)
            non_njpw_spoiler_channel = self.bot.get_channel(NON_NJPW_SPOILER_CHANNEL)
            general_channel = self.bot.get_channel(NEW_MEMBER_CHANNEL)
            await general_channel.send(f"Welcome {member.mention}! For spoilerific chat about the ongoing/last show, join us in the spoiler channels:\n"
                            f"NJPW Events: {njpw_spoiler_channel.mention}\n"
                            f"Other Events: {non_njpw_spoiler_channel.mention}\n")

    # A listener for all messages in the server
    # Most likely use case will be for temporary or "unofficial" commands that do not use the standard prefix
    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        # No message listeners are used yet
        pass

    @commands.Cog.listener("on_command_error")
    async def on_command_error(self, ctx, error):
        print(f"Failure to invoke command \"{ctx.invoked_with}\":\n- {error}")


def setup(bot):
    bot.add_cog(Listeners(bot))