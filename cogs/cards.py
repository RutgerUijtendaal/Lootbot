import logging

from cogs.utils import messages
from discord.ext import commands

log = logging.getLogger(__name__)


class Items:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def play(self, ctx):
        """ $use [card_name]. Use a card in your deck. """

        message = ctx.message.content[6:]
        card_name = message

        card_id = None
        for _card in self.bot.rewards['loot']['card']:
            if _card['name'] == card_name:
                card_id = _card['card_id']

        card_used = False
        if card_id is not None:
            card_used = await self.bot.process_card(ctx.message.author, ctx.message.server, int(card_id))
            if not card_used:
                await self.bot.say("Can't find that card in your deck. Stop trying to cheat!")
        else:
            await self.bot.say("That doesn't sound like an card to me, did you typo?")

    @commands.command(pass_context=True)
    async def card(self, ctx):
        """ $card [card_name]. Gives the description of an card """

        message = ctx.message.content[6:]
        card_name = message

        message = "```md\n"

        card = None
        for _card in self.bot.rewards['loot']['card']:
            if _card['name'] == card_name:
                card = _card

        if card is not None:
            message += "<-  [" + card['name'] + "]>\n"
            message += "    " + card['description'] + "\n"
            message += "```"
            await self.bot.say(message)
        else:
            await self.bot.say("That doesn't sound like an card to me, did you typo?")

    @commands.command(pass_context=True)
    async def cardlist(self, ctx):
        """ Lists all available cards in the game """

        cards = self.bot.rewards['loot']['card']

        message = "```md\n"

        for card in cards:
            message += "<" + str(card['card_id']) + \
                ": [" + card['name'] + "]>\n"
            message += "    " + card['description'] + "\n\n"

        message += "```"

        await self.bot.say(message)


def setup(bot):
    bot.add_cog(Items(bot))
