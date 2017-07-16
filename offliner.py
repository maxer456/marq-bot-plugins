#!/usr/bin/env pyton3

from disco.bot import Plugin
from disco.types.user import Status
from gevent import sleep, kill, GreenletExit

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
        self.current = {}
        self.counters = {}

    def unload(self, ctx):
        super().unload(ctx)

        for counter in self.counters.values():
            counter.kill()

    @Plugin.listen('PresenceUpdate')
    def member_presence_update(self, event):
        userid = str(event.user.id)

        if event.status == Status.OFFLINE:
            self.current[userid] = 0
            guild = self.ctx['guild']
            channel = next(iter(guild.channels.values()))
            
            def counter():
                while True:
                    sleep(self.DAY)
                    self.current[userid] += 1
                    points = '~~||||~~ ' * (self.current[userid] // 5) + '|' * (self.current[userid] % 5)
                    channel.send_message('{}: {}'.format(event.user.mention, points))

            self.counters[userid] = self.spawn(counter)
        elif userid in self.counters:
            self.counters[userid].kill()
            del self.counters[userid]

            # Do not save zeroes
            if self.current[userid] == 0:
                return

            # Save maximum and statistics
            try:
                if self.maximum[userid] < self.current[userid]:
                    self.maximum[userid] = self.current[userid]
            except KeyError:
                self.maximum[userid] = self.current[userid]

            try:
                self.history[userid] = self.history[userid] + [self.current[userid]]
            except KeyError:
                self.history[userid] = [self.current[userid]]
