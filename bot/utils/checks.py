"""
Custom commands.check functions

Defines custom checks to be passed to @commands.check()
"""
from settings.constants import GUILD_ID

# Checks that the author of the invoked command is in a user group higher than @everyone
def is_admin(ctx):
    guild = ctx.bot.get_guild(GUILD_ID)
    author = guild.get_member(ctx.author.id)
    return any(role > guild.default_role for role in author.roles)