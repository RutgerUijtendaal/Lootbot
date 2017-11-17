#!/usr/local/bin/python3

import logging
import math

import random
import settings

from cogs.utils import messages
from discord.ext import commands

log = logging.getLogger(__name__)


class Bot:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def links(self, ctx):
        ''' Opens all the lootboxes for your account '''
        message = ("```md\n" +
                   "#[Google Docs for how things work]:\n" + settings.DESIGN_LINK + "\n\n" +
                   "#[Trello for what is being worked on]:\n" + settings.TRELLO_LINK + "\n\n" +
                   "#[Github for what has been done]:\n" + settings.GITHUB_LINK + "\n" +
                   "```"
                   )
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Bot(bot))
