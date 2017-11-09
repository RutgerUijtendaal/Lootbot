import logging

from discord.ext import commands

from data import constants

log = logging.getLogger(__name__)


class Lootbot:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def links(self, ctx):
        ''' Opens all the lootboxes for your account '''
        message = ("```\n" +
                   constants.DESIGN_LINK + "\n" +
                   constants.TRELLO_LINK + "\n" +
                   constants.GITHUB_LINK + "```"
                   )
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Lootbot(bot))
