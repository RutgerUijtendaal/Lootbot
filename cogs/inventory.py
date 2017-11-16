import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class Inventory:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def inventory(self, ctx):
        """ Lists the items in your inventory """
        inventory = self.bot.db.get_items(ctx.message.author, ctx.message.server)

    @commands.command(pass_context=True)
    async def test(self, ctx):
        experience = {
            'name': "Message Base Experience",
            'type': 'experience',
            'target': 'message',
            'value': 1000
        }
        await self.bot.award_experience(ctx.message.author, ctx.message.server, experience)


def setup(bot):
    bot.add_cog(Inventory(bot))
