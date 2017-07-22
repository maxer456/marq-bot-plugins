#!/usr/bin/env pyton3

from disco.bot import Plugin

class RedditNews(Plugin):
    """
    Plugin which periodically performs a search on the specified subreddits and posts
    the results which are new to the specified channel.
    """

    def load(self, ctx):
        super().load(ctx)

        self.settings = self.storage.guild('redditnews_settings')
        self.searches = self.storage.guild('redditnews_searches')

    @Plugin.command('redditnews here', aliases=['rdnh', 'rdn here'])
    def redditnews_channel(self, event):
        self.settings['channel'] = event.channel.id
        event.channel.send_message('I will now post my Reddit news here.')
