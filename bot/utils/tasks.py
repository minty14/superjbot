import logging

from settings.constants import (
    OWNER_ID, GUILD_ID, GENERAL_CHANNEL, NON_NJPW_CHANNEL, 
    NEW_MEMBER_CHANNEL, RULES_CHANNEL, NEW_POD_CHANNEL,
    NJPW_SPOILER_CHANNEL, NON_NJPW_SPOILER_CHANNEL)

# Set some commonly used IDs as bot attributes
def set_ids(bot):
    logging.info("Setting Channel IDs")

    bot.general_channel = bot.get_channel(GENERAL_CHANNEL)
    logging.debug(
        f"general_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.new_pod_channel = bot.get_channel(NEW_POD_CHANNEL)
    logging.debug(
        f"new_pod_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")

    bot.non_njpw_channel = bot.get_channel(NON_NJPW_CHANNEL)
    logging.debug(
        f"non_njpw_spoiler_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.new_member_channel = bot.get_channel(NEW_MEMBER_CHANNEL)
    logging.debug(
        f"new_member_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.rules_channel = bot.get_channel(RULES_CHANNEL)
    logging.debug(
        f"rules_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.njpw_spoiler_channel = bot.get_channel(NJPW_SPOILER_CHANNEL)
    logging.debug(
        f"njpw_spoiler_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.non_njpw_spoiler_channel = bot.get_channel(NON_NJPW_SPOILER_CHANNEL)
    logging.debug(
        f"non_njpw_spoiler_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")

    logging.info("Setting Owner ID")
    bot.owner = bot.get_user(OWNER_ID)
    logging.debug(f"owner: {bot.owner.name}, display_name: {bot.owner.display_name}, id: {bot.owner.id}")

    logging.info("Setting Guild ID")
    bot.guild = bot.get_guild(GUILD_ID)