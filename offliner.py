#/usr/bin/env pyton3

from disco.bot import Plugin

class Offliner(Plugin):
    """
    Plugin to count the days a person has been offline, along with
    statistics for comparison.
    """

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
