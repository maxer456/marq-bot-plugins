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


    @Plugin.command('redditnews list', aliases=['rdnl', 'rdn list'])
    def redditnews_list(self, event):
        if len(self.searches):
            msg = 'Currently set up subreddits:'
        else:
            msg = 'There are currently no set up subreddits.'

        for k in self.searches.keys():
            msg += ' {}'.format(k)

        event.msg.reply(msg)


    @Plugin.command('redditnews add', '<subreddit:str> <search:str...>', aliases=['rdna','rdn add'])
    def redditnews_add(self, event, subreddit, search):
        try:
            msg = 'Replacing {} search \'{}\' with '.format(subreddit, self.searches[subreddit])
        except KeyError:
            msg = 'Adding {} search '.format(subreddit)

        self.searches[subreddit] = search
        msg += '\'{}\''.format(search)

        event.msg.reply(msg)


    @Plugin.command('redditnews remove', '<subreddit:str>', aliases=['rdnr', 'rdn remove'])
    def redditnews_remove(self, event, subreddit):
        try:
            del self.searches[subreddit]
            msg = 'Search {} deleted.'.format(subreddit)
        except KeyError:
            msg = 'There is no search for subreddit {}.'.format(subreddit)

        event.msg.reply(msg)
