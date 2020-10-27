import os

# Discord Bot Token - https://discord.com/developers/applications
TOKEN = os.environ["DISCORD_TOKEN"]

# ID of the text channel to display messages to new users. Typically the default channel
NEW_MEMBER_CHANNEL = int(os.environ["NEW_MEMBER_CHANNEL"])

# ID of the text channel which lists the guild's rules
RULES_CHANNEL = int(os.environ["RULES_CHANNEL"])

# ID of the text channel where new podcast episode announcements will be made
NEW_POD_CHANNEL = int(os.environ["NEW_POD_CHANNEL"])

# ID of the bot owner user - currently in use as bot.owner_id was returning None
OWNER_ID = int(os.environ["OWNER_ID"])