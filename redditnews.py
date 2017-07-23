#!/usr/bin/env pyton3

from datetime import datetime, timezone
from disco.bot import Plugin, Config
from disco.types.message import MessageEmbed
from praw import Reddit

class RedditNewsConfig(Config):
    site_name = ''
    user_agent = ''
    history_size = 20
    thumbnails = True

@Plugin.with_config(RedditNewsConfig)
class RedditNews(Plugin):
    """
    Plugin which periodically performs a search on the specified subreddits and posts
    the results which are new to the specified channel.
    """


    def load(self, ctx):
        super().load(ctx)

        self.settings = self.storage.guild('redditnews_settings')
        self.searches = self.storage.guild('redditnews_searches')
        self.history = self.storage.guild('redditnews_history')
        self.reddit = Reddit(self.config.site_name, user_agent=self.config.user_agent)


    @Plugin.command('redditnews here', aliases=['rdnh', 'rdn here'])
    def command_channel(self, event):
        self.settings['channel'] = event.channel.id
        event.channel.send_message('I will now post my Reddit news here.')


    @Plugin.command('redditnews list', aliases=['rdnl', 'rdn list'])
    def command_list(self, event):
        if len(self.searches):
            msg = 'Currently set up subreddits:'
        else:
            msg = 'There are currently no set up subreddits.'

        for k in self.searches.keys():
            msg += ' {}'.format(k)

        event.msg.reply(msg)


    @Plugin.command('redditnews add', '<subreddit:str> <search:str...>', aliases=['rdna','rdn add'])
    def command_add(self, event, subreddit, search):
        try:
            msg = 'Replacing {} search \'{}\' with '.format(subreddit, self.searches[subreddit])
        except KeyError:
            msg = 'Adding {} search '.format(subreddit)

        self.searches[subreddit] = search
        msg += '\'{}\''.format(search)

        event.msg.reply(msg)


    @Plugin.command('redditnews remove', '<subreddit:str>', aliases=['rdnr', 'rdn remove'])
    def command_remove(self, event, subreddit):
        try:
            del self.searches[subreddit]
            msg = 'Search {} deleted.'.format(subreddit)
        except KeyError:
            msg = 'There is no search for subreddit {}.'.format(subreddit)

        event.msg.reply(msg)

    @Plugin.schedule(1800, repeat=True, init=False)
    def shedule_search(self):
        for _, guild in self.state.guilds.items():
            self.ctx['guild'] = guild
            try:
                chan = guild.channels[self.settings['channel']]
                self.perform_search(chan)
            except Exception as e:
                raise e
            finally:
                self.ctx.drop()


    def perform_search(self, chan):
        for sub, search in self.searches.items():
            subreddit = self.reddit.subreddit(sub)
            if sub not in self.history:
                self.history[sub] = []

            for post in subreddit.search(search, sort='new', time_filter='day'):
                if post.id not in self.history[sub]:
                    self.send_post(chan, post)
                    self.history[sub] = self.history[sub] + [post.id]

            if len(self.history[sub]) > self.config.history_size:
                self.history[sub] = self.history[sub][-self.config.history_size:]


    def send_post(self, chan, post):
        embed = MessageEmbed()
        embed.title, embed.url = post.title, post.url

        if post.link_flair_text:
            embed.description = '{} [{}] ([comments]({}))'
        else:
            embed.description = '{}{}([comments]({}))'
        embed.description = embed.description.format(
                post.subreddit.title,
                post.link_flair_text or ' ',
                post.shortlink
                )

        embed.color = 0x4587FF
        embed.set_author(
                name=post.author.name,
                url='{}/u/{}'.format(self.reddit.config.reddit_url, post.author.name)
                )
        embed.timestamp = datetime.fromtimestamp(post.created_utc, timezone.utc).isoformat()

        if self.config.thumbnails:
            try:
                embed.set_thumbnail(url=post.preview['images'][0]['source']['url'])
            except:
                pass

        chan.send_message('', embed=embed)
