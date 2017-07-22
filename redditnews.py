#!/usr/bin/env pyton3

from disco import Plugin

class RedditNews(Plugin):
    """
    Plugin which periodically performs a search on the specified subreddits and posts
    the results which are new to the specified channel.
    """

