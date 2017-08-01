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
    DAY = 24 * 3600


    def load(self, ctx):
        super().load(ctx)

        self.maximum = self.storage.guild('offliner_maximum')
        self.history = self.storage.guild('offliner_history')
        self.status = self.storage.guild('offliner_status')

        self.current = {}
        self.counters = {}


    def unload(self, ctx):
        super().unload(ctx)

        for counter in self.counters.values():
            counter.kill()


    @Plugin.listen('GuildCreate')
    def guild_create(self, event):
        self.current[event.guild.id] = {}
        self.counters[event.guild.id] = {}

        for userid, val in self.status.items():
            at, points = val
            delay = self.DAY - (datetime.now() - datetime.fromtimestamp(at)).seconds
            self.start_counter(userid, delay, points)


    @Plugin.listen('GuildMembersChunk')
    def members_chunk(self, event):
        counters = self.counters[event.guild_id]
        for member in event.members:
            userid = str(member.user.id)

            if (userid in counters and
                    member.user.presence != UNSET and
                    member.user.presence != Status.OFFLINE):
                self.stop_counter(userid)


    @Plugin.listen('PresenceUpdate')
    def member_presence_update(self, event):
        userid = str(event.user.id)
        counters = self.counters[event.guild_id]

        if event.status == Status.OFFLINE:
            if userid in counters:
                # Should not happen
                counters[userid].kill()
                del counters[userid]

            self.status[userid] = datetime.now().timestamp(), 0
            self.start_counter(userid)

        elif userid in counters:
            self.stop_counter(userid)


    def start_counter(self, userid, presleep=None, points=0):
        guild = self.ctx['guild']
        channel = next(iter(guild.channels.values()))
        current = self.current[guild.id]
        counters = self.counters[guild.id]

        current[userid] = points

        def counter():
            preslept = False
            while True:
                if presleep and not preslept:
                    sleep(presleep)
                    preslept = True
                else:
                    sleep(self.DAY)

                current[userid] += 1
                points = '~~||||~~ ' * (current[userid] // 5) + '|' * (current[userid] % 5)
                channel.send_message('<@{}>: {}'.format(userid, points))

                # Save current points in case of a sudden shutdown
                self.ctx['guild'] = guild
                try:
                    at, _ = self.status[userid]
                    self.status[userid] = at, current[userid]
                finally:
                    self.ctx.drop()

        counters[userid] = self.spawn(counter)


    def stop_counter(self, userid):
        guildid = self.ctx['guild'].id
        current = self.current[guildid]
        counters = self.counters[guildid]

        counters[userid].kill()
        del counters[userid]
        del self.status[userid]

        # Do not save zeroes
        if current[userid] == 0:
            del current[userid]
            return

        # Save maximum and statistics
        try:
            if self.maximum[userid] < current[userid]:
                self.maximum[userid] = current[userid]
        except KeyError:
            self.maximum[userid] = current[userid]

        try:
            self.history[userid] = self.history[userid] + [current[userid]]
        except KeyError:
            self.history[userid] = [current[userid]]

        del current[userid]
