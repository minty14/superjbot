"""
Sensitive data is passed in through environment variables and stored in constants.

IDs are treated as ints by discord.py, so are explicitly converted here.
"""
import os

###
# Bot Related
###

# Discord Bot Token - https://discord.com/developers/applications
TOKEN = os.environ["DISCORD_TOKEN"]

# ID of the bot owner user - currently in use as bot.owner_id was returning None
OWNER_ID = int(os.environ["OWNER_ID"])

# Explicit ID of the Super J-Cast Discord Guild/Server
GUILD_ID = int(os.environ["GUILD_ID"])

###
# Channel IDs
###

# ID of the general text-chat channel
GENERAL_CHANNEL = int(os.environ["GENERAL_CHANNEL"])

# ID of the non-njpw chat channel
NON_NJPW_CHANNEL = int(os.environ["NON_NJPW_CHANNEL"])

# ID of the text channel to display messages to new users. Typically the default channel
NEW_MEMBER_CHANNEL = int(os.environ["NEW_MEMBER_CHANNEL"])

# ID of the text channel which lists the guild's rules
RULES_CHANNEL = int(os.environ["RULES_CHANNEL"])

# ID of the text channel where new podcast episode announcements will be made
NEW_POD_CHANNEL = int(os.environ["NEW_POD_CHANNEL"])

# IDs of the spoiler channels
NJPW_SPOILER_CHANNEL = int(os.environ["NJPW_SPOILER_CHANNEL"])
NON_NJPW_SPOILER_CHANNEL = int(os.environ["NON_NJPW_SPOILER_CHANNEL"])
