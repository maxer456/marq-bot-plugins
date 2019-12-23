#!/usr/bin/env pyton3

from disco.bot import Plugin
from disco.types import UNSET
from disco.types.user import Status
from gevent import sleep, kill, GreenletExit

from datetime import datetime, timedelta

class Offliner(Plugin):
    """
    Plugin to count the days a person has been offline, along with
    statistics for comparison.
    """


    def load(self, ctx):
        super().load(ctx)

        self.maximum = self.storage.guild('offliner_maximum')
        self.history = self.storage.guild('offliner_history')
        self.status = self.storage.guild('offliner_status')


    def unload(self, ctx):
        super().unload(ctx)


    @Plugin.listen('PresenceUpdate')
    def member_presence_update(self, event):
        userid = str(event.user.id)
        time = datetime.now()
        timestamp = time.hour * 3600 + time.minute * 60 + time.second
        timestamp //= 10
        timestamp %= 10

        if event.status == Status.OFFLINE:
            try:
                status = self.status[timestamp]
            except KeyError:
                status = {}

            status[userid] = 0
            print(timestamp)
            self.status[timestamp] = status
        else:
            try:
                status = self.status[timestamp]
                del status[userid]
                self.status[timestamp] = status
            except KeyError:
                pass


    @Plugin.schedule(10, repeat=True, init=False)
    def offliner_schedule(self):
        time = datetime.now()
        timestamp = time.hour * 3600 + time.minute * 60 + time.second
        timestamp //= 10
        timestamp %= 10
        print(timestamp)
        for guild in self.state.guilds.values():
            self.offliner_guild_check(guild, timestamp)


    def offliner_guild_check(self, guild, stamp):
        self.ctx['guild'] = guild

        try:
            status = self.status[stamp]
            newstatus = {}

            for uid, val in status.items():
                if uid in self.state.users:
                    user = self.state.users[uid]
                    if user.presence == UNSET or user.presence == Status.OFFLINE:
                        newstatus[uid] = status[uid] + 1
                        self.send_off_line(guild, user, newstatus[uid])

            self.status[stamp] = newstatus
        except KeyError:
            pass
        finally:
            self.ctx.drop()


    def send_off_line(self, guild, user, lines):
        channel = next(iter(guild.channels.values()))
        points = '~~||||~~ ' * (lines // 5) + '|' * (lines % 5)
        channel.send_message('<@{}>: {}'.format(user.id, points))
