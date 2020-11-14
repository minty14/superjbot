"""
Custom commands.check functions

Defines custom checks to be passed to @commands.check()
"""

# Checks that the author of the invoked command is in a user group higher than @everyone
def is_admin(ctx):
    return any(role > ctx.guild.default_role for role in ctx.author.roles)