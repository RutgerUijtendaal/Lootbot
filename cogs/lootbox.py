import logging
import discord

from discord.ext import commands

log = logging.getLogger(__name__)


class Lootbox:

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.command(pass_context=True)
    async def openall(self, ctx):
        ''' Opens all the lootboxes for your account '''
        all_lootboxes = self.db.get_all_lootboxes(
            ctx.message.author, ctx.message.server)
        # Loop through lootboxes, open them and delete from database
        for i in range(3):
            if all_lootboxes[i] > 0:
                for j in range(all_lootboxes[i]):
                    await self.bot.open_lootbox(i, ctx.message.author, ctx.message.server)
                    self.db.remove_lootbox(
                        i, ctx.message.author, ctx.message.server)

    @commands.command(pass_context=True)
    async def auto_open(self, ctx):
        ''' "$auto_open [on/off]" Set lootbox to auto open on receiving. '''
        setting = ctx.message.content[11:]
        if(setting == "on"):
            self.db.set_auto_open(ctx.message.author, ctx.message.server, True)
        elif(setting == "off"):
            self.db.set_auto_open(ctx.message.author,
                                  ctx.message.server, False)
        else:
            await self.bot.say("Unknown setting in auto_open")


def setup(bot):
    bot.add_cog(Lootbox(bot))
