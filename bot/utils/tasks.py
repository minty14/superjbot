"""
Generic tasks which need to be run ad-hoc

Includes tasks which are run once, ie at login, or on demand rather than on loops
"""

import logging

from settings.constants import (
    OWNER_ID, GUILD_ID, GENERAL_CHANNEL, NON_NJPW_CHANNEL, 
    NEW_MEMBER_CHANNEL, RULES_CHANNEL, NEW_POD_CHANNEL,
    NJPW_SPOILER_CHANNEL, NON_NJPW_SPOILER_CHANNEL, AEW_CHANNEL)

# Set some commonly used IDs as bot attributes
def set_ids(bot):
    logging.info("Setting Channel IDs")

    bot.general_channel = bot.get_channel(GENERAL_CHANNEL)
    logging.info(
        f"general_channel: {bot.general_channel.name}, id: {bot.general_channel.id}, category: {bot.general_channel.category}")
    
    bot.new_pod_channel = bot.get_channel(NEW_POD_CHANNEL)
    logging.info(
        f"new_pod_channel: {bot.new_pod_channel.name}, id: {bot.new_pod_channel.id}, category: {bot.new_pod_channel.category}")

    bot.non_njpw_channel = bot.get_channel(NON_NJPW_CHANNEL)
    logging.info(
        f"non_njpw_spoiler_channel: {bot.non_njpw_channel.name}, id: {bot.non_njpw_channel.id}, category: {bot.non_njpw_channel.category}")
    
    bot.new_member_channel = bot.get_channel(NEW_MEMBER_CHANNEL)
    logging.info(
        f"new_member_channel: {bot.new_member_channel.name}, id: {bot.new_member_channel.id}, category: {bot.new_member_channel.category}")
    
    bot.rules_channel = bot.get_channel(RULES_CHANNEL)
    logging.info(
        f"rules_channel: {bot.rules_channel.name}, id: {bot.rules_channel.id}, category: {bot.rules_channel.category}")
    
    bot.njpw_spoiler_channel = bot.get_channel(NJPW_SPOILER_CHANNEL)
    logging.info(
        f"njpw_spoiler_channel: {bot.njpw_spoiler_channel.name}, id: {bot.njpw_spoiler_channel.id}, category: {bot.njpw_spoiler_channel.category}")
    
    bot.non_njpw_spoiler_channel = bot.get_channel(NON_NJPW_SPOILER_CHANNEL)
    logging.info(
        f"non_njpw_spoiler_channel: {bot.non_njpw_spoiler_channel.name}, id: {bot.non_njpw_spoiler_channel.id}, category: {bot.non_njpw_spoiler_channel.category}")

    bot.aew_channel = bot.get_channel(AEW_CHANNEL)
    logging.info(
        f"aew_channel: {bot.aew_channel.name}, id: {bot.aew_channel.id}, category: {bot.aew_channel.category}")

    logging.info("Setting Owner ID")
    bot.owner = bot.get_user(OWNER_ID)
    logging.info(f"owner: {bot.owner.name}, display_name: {bot.owner.display_name}, id: {bot.owner.id}")

    logging.info("Setting Guild ID")
    bot.guild = bot.get_guild(GUILD_ID)