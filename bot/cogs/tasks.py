import logging
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

import utils.embeds
from database.models import (
    PodcastEpisode, ScheduleShow, ResultShow, NonNjpwShow, SpoilerMode, Profile
)


class Tasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Start background task loops
        logging.info("Starting new_podcast_watcher")
        self.new_podcast_watcher.start()
        logging.info("Starting new_show_watcher")
        self.new_show_watcher.start()
        logging.info("Starting new_profile_watcher")
        self.new_profile_watcher.start()
        logging.info("Starting spoiler_mode_watcher")
        self.spoiler_mode_watcher.start()

    ###
    # Background Tasks
    # https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.loop
    # https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html?highlight=tasks%20loop#discord.ext.tasks.Loop
    ###

    # Frequently look for new podcasts episodes in the DB
    @tasks.loop(minutes=5)
    async def new_podcast_watcher(self):

        try:
            logging.debug("Running new_podcast_watcher")

            # DB query to return podcast episodes tagged as new
            new_podcasts = PodcastEpisode.objects(new=True)

            if new_podcasts:
                # Loop through results on the remote chance that more than one episode was found
                for p in new_podcasts:
                    logging.info("New podcast episode found: " + p.title)
                    await self.bot.general_channel.send(content="@here New Pod!", 
                                    embed=utils.embeds.pod_episode_embed(p))
                    p.update(new=False)

        except Exception as e:
            logging.error("Error encountered while running new_podcast_watcher: " + str(e))

    # Alert the discord to shows added to the schedule on njpw1972.com
    @tasks.loop(minutes=30)
    async def new_show_watcher(self):

        try:
            logging.debug("Running new_show_watcher")

            # DB query to return podcast episodes tagged as new
            new_shows = ScheduleShow.objects(new=True)

            if new_shows:
                for s in new_shows:
                    logging.info("New scheduled show found: " + s.name)
                try:
                    await self.bot.general_channel.send(content="New show(s) added to the schedule:",
                                    embed=utils.embeds.new_shows_embed(new_shows))
                except Exception:
                    await self.bot.general_channel.send(content="New show(s) added to the schedule:",
                                    embed=utils.embeds.new_shows_embed(new_shows[0:2]))
                new_shows.update(new=False)

        except Exception as e:
            logging.error("Error encountered while running new_show_watcher: " + str(e))

    # Alert the discord to wrestler profiles added to on njpw1972.com
    @tasks.loop(hours=6)
    async def new_profile_watcher(self):
        try:
            logging.debug("Running new_profile_watcher")

            # DB query to return podcast episodes tagged as new
            new_profiles = Profile.objects(new=True)

            if new_profiles:
                await self.bot.general_channel.send("New Profile(s) Added: ")
                for p in new_profiles:
                    logging.info("New profile found: " + p.name)
                    await self.bot.general_channel.send(embed=utils.embeds.profile_embed(p))
                new_profiles.update(new=False)
        except Exception as e:
            logging.error("Error encountered while running new_profile_watcher: " + str(e))

    # Check for shows starting soon and set spoiler mode
    # Also check for spoiler modes which have ended
    @tasks.loop(minutes=3.5)
    async def spoiler_mode_watcher(self):
        try:
            logging.debug("Running spoiler_mode_watcher")

            # DB query to return njpw shows which start in the next 5 minutes and continue if any exist
            starting_shows = ScheduleShow.objects(time__lte=datetime.now() + timedelta(minutes=5))
            if starting_shows:
                for s in starting_shows:
                    # Check that spoiler mode hasn't already been triggered for that show and that the show is live
                    if not SpoilerMode.objects(title=s.name) and s.live_show:

                        # Build spoiler_mode document
                        spoiler_mode = SpoilerMode(
                            mode = "njpw",
                            title=s.name,
                            ends_at=s.time + timedelta(hours=s.spoiler_hours),
                            thumb=s.thumb
                        )

                        # Save the document to the DB
                        spoiler_mode.save()

                        # Notify @here of the starting show and include the embed which lists the end time
                        await self.bot.general_channel.send(
                            content=f"@here **{spoiler_mode.title}** starting soon. Head to {self.bot.njpw_spoiler_channel.mention} for spoiler chat.",
                            embed=utils.embeds.spoiler_mode_embed(spoiler_mode)
                        )

                        await self.bot.njpw_spoiler_channel.edit(topic=spoiler_mode.title)
                        
                        logging.info(f"NJPW #spoiler-zone time started for {spoiler_mode.title}, ends in {s.spoiler_hours}")

            # DB query to return non-njpw shows which start in the next 5 minutes and continue if any exist
            non_njpw_shows = NonNjpwShow.objects(time__lte=datetime.now() + timedelta(minutes=5))
            if non_njpw_shows:
                for s in non_njpw_shows:
                    # Check that spoiler mode hasn't already been triggered for that show
                    if not SpoilerMode.objects(title=s.name):

                        # Build spoiler_mode document
                        spoiler_mode = SpoilerMode(
                            mode = "non_njpw",
                            title=s.name,
                            ends_at=s.time + timedelta(hours=s.spoiler_hours)
                        )

                        # Save the document to the DB
                        spoiler_mode.save()

                        # Notify @here, in the non-njpw chat channel of the starting show and include the embed which lists the end time
                        await self.bot.non_njpw_channel.send(
                            content=f"@here **{spoiler_mode.title}** starting soon. Head to {self.bot.non_njpw_spoiler_channel.mention} for spoiler chat",
                            embed=utils.embeds.spoiler_mode_embed(spoiler_mode)
                        )

                        await self.bot.non_njpw_spoiler_channel.edit(topic=spoiler_mode.title)

                        logging.info(f"Non NJPW #spoiler-zone time started for **{spoiler_mode.title}**, ends in {s.spoiler_hours} hours")

            # DB query to find spoiler_mode events which have now ended
            ending_shows = SpoilerMode.objects(ends_at__lt=datetime.now())
            if ending_shows:
                for s in ending_shows:          
                    # For ended spoiler modes, send notifications to the relevant channels
                    if s.mode == "njpw":
                        if SpoilerMode.objects(mode=s.mode).count() < 2:
                            await self.bot.general_channel.send(
                                content=f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away.\n\nNext show:",
                                embed=utils.embeds.schedule_shows_embed(ScheduleShow.objects(time__gt=datetime.now())[:1], 1)
                            )
                        else:
                            await self.bot.general_channel.send(
                                content=f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away.\nOngoing spoiler embargo:"
                            )
                            for i in SpoilerMode.objects(title__ne=s.title):
                                await self.bot.general_channel.send(
                                    embed=utils.embeds.spoiler_mode_embed(i)
                                )
                    elif s.mode == "non_njpw":
                        await self.bot.non_njpw_channel.send(
                            f"@here **{s.title}** _#spoiler-zone_ time has ended. Spoil away."
                        )

                    # Remove the spoiler mode document from the DB
                    s.delete()

                    logging.info(f"{s.mode} spoiler-zone time ended for {s.title}")
        
        except Exception as e:
            logging.error("Error encountered while running spoiler_mode_watcher: " + str(e))

def setup(bot):
    bot.add_cog(Tasks(bot))