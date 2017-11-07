import logging
import discord

from discord.ext import commands

from data import rewards

log = logging.getLogger(__name__)


class User:

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(pass_context=True)
    async def score(self, ctx):
        ''' Display your personal score '''
        points = self.db.get_points(
            ctx.message.author, ctx.message.server)
        await self.bot.say("```" + ctx.message.author.name + ": " + str(points) + " points```")

    @commands.command(pass_context=True)
    async def summary(self, ctx):
        res = self.db.get_user(ctx.message.author, ctx.message.server)
        message = ("```js\nUser: " + res[1] +
                   "\n  Points:   " + str(res[3]) +
                   "\n\nMultipliers:\n  Message:  " + str(res[4]) +
                   "\n  Game:     " + str(res[5]) + "\n  Voice:    " + str(res[6]) +
                   "\n\nCurrent Boxes:\n  Common:   " + str(res[7]) + "\n  Rare:     " + str(res[8]) +
                   "\n  Leg:      " + str(res[9]) +
                   "\n\nTotal Boxes:\n  Common:   " + str(res[10]) + "\n  Rare:     " + str(res[11]) +
                   "\n  Leg:      " + str(res[12]) +
                   "\n\nSettings\n  Auto_open:" + str(res[15]) +
                   '```')
        await self.bot.say(message)


def setup(bot):
    bot.add_cog(User(bot))
