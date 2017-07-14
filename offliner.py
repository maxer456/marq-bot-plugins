#/usr/bin/env pyton3

from disco.bot import Plugin
from time import time

class Offliner(Plugin):
    """
    Plugin to count the days a person has been offline, along with
    statistics for comparison.
    """

    def load(self, ctx):
        super().load(ctx)
        self.offline_times = self.storage.guild('offline_times')

    @Plugin.command('ping')
    def command_ping(self, event):
        event.msg.reply('Pong!')

    @Plugin.listen('PresenceUpdate')
    def member_presence_update(self, event):
        state = self.state
        user = state.users[event.user.id]
        channels = state.guilds[event.guild_id].channels.values()
        channel = next(iter(channels))
        channel.send_message('{} just went {}!'.format(user.username, event.status))

        if state == 'offline':
            self.offline_times[event.user.id] = time()
