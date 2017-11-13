import logging
import random
from datetime import datetime
from threading import Timer

import asyncio
from discord.ext import commands

import settings
from data.objects import rewards, quests
import cogs.utils.messages as messages
from cogs.utils.db import Database
from cogs.utils.timer import Timer

log = logging.getLogger(__name__)


class Lootbot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Setup database
        self.db = Database()
        self.db.create_database()
        # Setup dictionaries
        self.lb_settings = settings.LOOTBOX_SETTINGS
        self.rewards = rewards.REWARDS
        self.quests = quests.QUESTS
        # Setup Rewards
        self.lootbox_rarity = []
        self.init_lootbox_rarity()
        # Setup daily/weekly resets
        self.daily_timer = None
        self.weekly_timer = None

    async def on_ready(self):
        log.info("Discord client ready")
        await self.add_all_servers()
        await self.set_daily_reset()

    async def add_all_servers(self):
        for server in self.servers:
            self.db.add_server(server)
            for member in server.members:
                if not member.bot:
                    self.db.add_member(member)

    async def close(self):
        self.db.close()
        await super().close()

    async def on_message(self, ctx):
        command = False
        # Ignore rewards if it's a command
        if ctx.content.startswith(settings.BOT_PREFIX):
            command = True
        if not ctx.author.bot and not command:
            member = ctx.author
            server = ctx.server
            # If this is the first daily message from user complete daily
            if self.db.get_first_random_lootbox(member, server) is False:
                await self.complete_daily(ctx.author, ctx.server, self.quests['daily'][0])

            # Roll for a random lootbox
            if self.roll_lootbox():
                reward_summary = await self.create_lootbox_reward(member, server)
                message = messages.create_random_lootbox_message(
                    self.db, member, server, reward_summary)
                # Add a reaction for the right rarity to the message
                for x, rarity in enumerate(reward_summary[0]):
                    if rarity > 0:
                        await self.add_reaction(ctx, settings.LOOTBOX_EMOJI[x])
                await self.say_lootbot_channel(server, message)

            # Award experience points for message
            await self.award_experience(member, server, self.rewards['experience'][0])

    async def on_member_update(self, bmember, amember):
        pass

    async def on_voice_state_update(self, bmember, amember):
        pass

    async def on_member_join(self, member):
        if not member.bot:
            self.db.add_member(member)

    async def on_server_join(self, server):
        self.db.add_server(server)
        for member in server.members:
            if not member.bot:
                self.db.add_member(member)

    # Experience functions

    async def award_experience(self, member, server, experience):
        """ Award experience of a type to user. Uses multipliers to calculate total experience gained """

        multipliers = self.db.get_multipliers(member, server)
        total_exp = 0

        if experience['type'] == 'experience':
            if experience['target'] == 'message':
                exp = multipliers[0] * experience['value']
                total_exp += exp
            if experience['target'] == 'game':
                exp = multipliers[1] * experience['value']
                total_exp += exp
            if experience['target'] == 'voice':
                exp = multipliers[2] * experience['value']
                total_exp += exp

        self.db.update_experience(member, server, total_exp)

        return total_exp

    # Lootbox functions

    async def create_lootbox_reward(self, member, server, common=0, rare=0, legendary=0):
        """ Collect lootboxes and create lootbox package. If no lootboxes are set a random rarity is rewarded

        returns list: [[common, rare, legendary], [loots]]

        """
        rarity_count = [common, rare, legendary]
        loots = []

        if common + rare + legendary == 0:
            rarity_count[self.roll_lootbox_rarity_int()] += 1

        if rarity_count[0] > 0:
            loots = loots + await self.collect_lootbox('common', rarity_count[0])
        if rarity_count[1] > 0:
            loots = loots + await self.collect_lootbox('rare', rarity_count[1])
        if rarity_count[2] > 0:
            loots = loots + await self.collect_lootbox('legendary', rarity_count[2])

        total_exp = await self.process_loot(member, server, loots)

        reward_summary = [rarity_count, loots, total_exp]

        return reward_summary

    async def complete_daily(self, member, server, daily):
        """ Complete a daily for a member. Update daily status and give reward """

        self.db.set_daily(member, server, daily['database'], True)

        # Determine reward
        if daily['reward_type'] == 'lootbox':
            common = daily['reward_count'] if daily['reward_rarity'] == 'common' else 0
            rare = daily['reward_count'] if daily['reward_rarity'] == 'rare' else 0
            legendary = daily['reward_count'] if daily['reward_rarity'] == 'legendary' else 0

            reward_summary = await self.create_lootbox_reward(
                member, server, common=common, rare=rare, legendary=legendary)

            message = messages.create_daily_message(
                self.db, member, server, reward_summary, daily)

            await self.say_lootbot_channel(server, message)

    async def process_loot(self, member, server, loots):
        """ Cycle through the loots and add rewards to the user """

        for loot in loots:
            if loot['type'] == 'multiplier':
                if loot['target'] == 'message':
                    self.db.update_message_multiplier(
                        member, server, loot['value'])
                elif loot['target'] == 'game':
                    self.db.update_game_multiplier(
                        member, server, loot['value'])
                elif loot['target'] == 'voice':
                    self.db.update_voice_multiplier(
                        member, server, loot['value'])

        # Update experience after multipliers to benefit from them
        total_exp = 0

        for loot in loots:
            if loot['type'] == 'experience':
                total_exp += await self.award_experience(member, server, loot)

        return total_exp

    async def collect_lootbox(self, rarity=None, count=1):
        """ Collects loot for a rarity and number of lootboxes

        rarity: 'common', 'rare', 'legendary'. None defaults to a random rarity

        """
        loots = []

        if rarity is None:
            rarity = self.roll_lootbox_rarity()

        for _ in range(count):
            for loot in self.collect_instant_set_rarity(rarity):
                loots.append(loot)

        return loots

    def collect_instant_set_rarity(self, rarity):
        """ Collect loot of type instant for set rarity. Yields a dictionary object of loot.

        rarity: 'common', 'rare', 'legendary'

        """
        for _ in range(self.lb_settings['instant_loot_counter']):
            reward_index = random.randint(
                0, len(self.rewards['instant'][rarity]) - 1)
            loot = self.rewards['instant'][rarity][reward_index]
            yield loot

    def collect_item(self):
        """ Collect loot of type item for set rarity. Yields a dictionary object of loot."""

        for _ in range(self.lb_settings['item_loot_counter']):
            reward_index = random.randint(0, len(self.rewards['item'] - 1))
            loot = self.rewards['item'][reward_index]
            yield loot

    def roll_lootbox(self):
        """ Roll to check if a lootbox should be awarded. Chance is 1/lootbox_chance. """
        lootbox = random.randint(1, self.lb_settings['lootbox_chance'])
        if lootbox == 1:
            return True
        return False

    def roll_lootbox_rarity_int(self):
        """ Roll for rarity. Returns '0', '1' or '2'. """
        length = len(self.lootbox_rarity)
        rarity_index = random.randint(0, length - 1)
        return self.lootbox_rarity[rarity_index]

    def roll_lootbox_rarity_string(self):
        """ Roll for rarity. Returns 'common', 'rare' or 'legendary'. """
        rarity_strings = ('common', 'rare', 'legendary')
        rarity = self.roll_lootbox_rarity_int()
        return rarity_strings[rarity]

    # Bot functions

    async def say_lootbot_channel(self, server, message):
        for channel in server.channels:
            if channel.name == settings.BOT_CHANNEL:
                await self.send_message(channel, message)

    async def say_global(self, message):
        for server in self.servers:
            for channel in server.channels:
                if channel.name == settings.BOT_CHANNEL:
                    await self.send_message(channel, message)

    async def set_daily_reset(self):
        x = datetime.today()
        # Get seconds till tomorrow 4 A.M.
        y = x.replace(day=x.day + 1, hour=4, minute=0, second=0, microsecond=0)
        delta = y - x
        secs = delta.seconds
        self.daily_timer = Timer(secs, self.reset_dailies)
        log.info("Daily reset set for %s", y)

    async def reset_dailies(self):
        self.db.reset_dailies()
        log.info("Reset dailies")
        await self.say_global("Dailies have been reset")
        await self.set_daily_reset()

    def init_lootbox_rarity(self):
        """ Initialize the rarity list. Chances are based on (rarity chance)/(total length). """
        for _ in range(self.lb_settings['common_chance']):
            self.lootbox_rarity.append(0)
        for _ in range(self.lb_settings['rare_chance']):
            self.lootbox_rarity.append(1)
        for _ in range(self.lb_settings['legendary_chance']):
            self.lootbox_rarity.append(2)
        log.info("Created lootbox rarity array of length %s",
                 str(len(self.lootbox_rarity)))
