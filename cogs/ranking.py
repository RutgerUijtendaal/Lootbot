import logging
import discord

from discord.ext import commands

from data import rewards

log = logging.getLogger(__name__)


class Ranking:

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(pass_context=True)
    async def ranking(self, ctx):
        '''Shows the rankings for the server '''
        message = "```js\n"
        all_points = self.db.get_all_points(ctx.message.server)
        for key in all_points:
            key_length = len(key)
            message = message + key + ":" + (" " * (12 - key_length))
            message = message + str(all_points[key]) + " points \n"
        message = message + "```"
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Ranking(bot))
