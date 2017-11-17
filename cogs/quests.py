#!/usr/local/bin/python3

import logging
import math

import random
import settings

from data.objects import quests
from cogs.utils import messages
from discord.ext import commands

log = logging.getLogger(__name__)


class Quests:

    def __init__(self, bot):
        self.bot = bot
        self.questslist = quests.QUESTS

    @commands.command(pass_context=True)
    async def dailies(self, ctx):
        """ List daily quests"""
        message = "```md\n# Dailies:\n\n"
        for x, daily in enumerate(self.questslist['daily']):
            message += "<" + str(x + 1) + "  [" + daily['name'] + "]>\n"
            message += "    " + daily['description'] + "\n\n"
        message += "```"
        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def weeklies(self, ctx):
        """ List weekly quests """
        message = "```md\n# Weeklies:\n\n"
        for x, weekly in enumerate(self.questslist['weekly']):
            message += "<" + str(x + 1) + "  [" + weekly['name'] + "]>\n"
            message += "    " + weekly['description'] + "\n\n"
        message += "```"
        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def quests(self, ctx):
        """ List all quests """
        message = "```md\n# Dailies:\n\n"
        for x, daily in enumerate(self.questslist['daily']):
            message += "<" + str(x + 1) + "  [" + daily['name'] + "]>\n"
            message += "    " + daily['description'] + "\n\n"
        message += "# Weeklies:\n\n"
        for x, weekly in enumerate(self.questslist['weekly']):
            message += "<" + str(x + 1) + "  [" + weekly['name'] + "]>\n"
            message += "    " + weekly['description'] + "\n\n"
        message += "```"
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Quests(bot))
