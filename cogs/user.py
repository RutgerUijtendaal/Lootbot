import logging
import math

from cogs.utils import messages
from discord.ext import commands

log = logging.getLogger(__name__)


class User:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def ranking(self, ctx):
        """ Shows the ranking for the server """
        server = ctx.message.server

        ranking = self.bot.db.get_ranking(server)

        message = messages.create_ranking_message(ranking, body=True)

        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def summary(self, ctx):
        """ Return a summary of the user for this season """
        member = ctx.message.author
        server = ctx.message.server

        deck = self.bot.db.get_cards(member, server)
        lootboxes = self.bot.db.get_season_lootbox(member, server)
        multipliers = self.bot.db.get_multipliers(member, server)
        progress = self.bot.db.get_member_progress(member, server)

        message = "```md\n"
        message += "[" + ctx.message.author.name + \
            "](" + str(progress[0]) + ")"

        message += messages.create_deck_message(deck)

        message += "``````js\n"

        message += messages.create_lootbox_message(lootboxes)

        message += messages.create_multiplier_message(multipliers)

        message += messages.create_progress_message(progress)

        message += "```"

        await self.bot.say(message)

    @commands.command(pass_context=True)
    async def deck(self, ctx):
        """ Lists the cards in your deck """

        member = ctx.message.author
        server = ctx.message.server

        deck = self.bot.db.get_cards(member, server)
        progress = self.bot.db.get_member_progress(member, server)

        message = "```md\n"
        message += "[" + ctx.message.author.name + \
            "](" + str(progress[0]) + ")"

        message += messages.create_deck_message(deck)

        message += "```"

        await self.bot.say(message)


def setup(bot):
    bot.add_cog(User(bot))
