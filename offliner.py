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
