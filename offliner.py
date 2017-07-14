#/usr/bin/env pyton3

from disco.bot import Plugin
from disco.types.user import Status
from time import time

class Offliner(Plugin):
    """
    Plugin to count the days a person has been offline, along with
    statistics for comparison.
    """

    def load(self, ctx):
        super().load(ctx)
        self.stats = self.storage.guild('offliner_stats')
        self.current = {}

    @Plugin.command('ping')
    def command_ping(self, event):
        event.msg.reply('Pong!')

    @Plugin.listen('PresenceUpdate')
    def member_presence_update(self, event):
        if event.status == Status.OFFLINE:
            self.stats[event.user.id] = time()
            
