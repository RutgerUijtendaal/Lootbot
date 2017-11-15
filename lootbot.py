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
        # Setup timers
        self.daily_timer = None
        self.weekly_timer = None
        self.game_timer = None
        # Setup game/voice users
        self.game_users = []
        self.voice_users = []

    async def on_ready(self):
        log.info("Discord client ready")
        await self.add_all_servers()
        await self.set_daily_reset()
        await self.set_game_timer()

    async def add_all_servers(self):
        for server in self.servers:
            self.db.add_server(server)
            for member in server.members:
                if not member.bot:
                    self.db.add_member(member)
                    if member.game is not None:
                        self.add_game_user(member, server)

    async def close(self):
        log.info("Shutting down bot")
        self.db.close()
        self.game_timer.cancel()
        self.daily_timer.cancel()
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
            if self.db.get_dailies(member, server)[0] == 0:
                await self.complete_quest(member, server, self.quests['daily'][0])

            # Roll for a random lootbox
            if self.roll_lootbox(member, server):
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
        # If member launches a game
        if bmember.game is None and amember.game is not None:
            if settings.GAMES_CHECK_WHITELIST:
                # If whitelist is check if game is on whitelist
                for game in settings.GAMES_WHITELIST:
                    if game == amember.game.name:
                        self.add_game_user(amember, amember.server)
            else:
                self.add_game_user(amember, amember.server)

        # If member exits a game
        if bmember.game is not None and amember.game is None:
            box_earned = False
            for user in self.game_users:
                if user[0] == bmember.id and user[1] == bmember.server.id:
                    # Check if any Lootboxes were earned
                    for box in user[2]:
                        if box > 0:
                            box_earned = True
                    # Award Lootboxes
                    if box_earned:
                        boxes = user[2]
                        reward_summary = await self.create_lootbox_reward(bmember, bmember.server, common=boxes[0], rare=boxes[1], epic=boxes[2], legendary=boxes[3])
                        message = messages.create_game_message(
                            self.db, bmember, bmember.server, reward_summary, show_loot=True)
                        await self.say_lootbot_channel(bmember.server, message)

            # Filter the user out of the game_users list
            self.game_users = list(
                filter(lambda x: x[0] != amember.id and x[1] != amember.server.id, self.game_users))

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

    # Voice and Game Timers

    async def set_game_timer(self):
        game_timer_seconds = settings.GAME_TIMER

        self.game_timer = Timer(game_timer_seconds, self.process_game_users)

    async def set_voice_timer(self):
        game_timer_seconds = settings.GAME_TIMER

        self.game_timer = Timer(game_timer_seconds, self.process_game_users)
    
    # Progress functions

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

        member_progress = self.db.get_member_progress(member, server)

        if self.calculate_level(member_progress):
            level = member_progress[0] + 1
            level_reward = self.get_level_reward(level)
            common = 1 if level_reward == 'common' else 0
            rare = 1 if level_reward == 'rare' else 0
            epic = 1 if level_reward == 'epic' else 0
            legendary = 1 if level_reward == 'legendary' else 0

            await self.award_level(member, server, level)

            reward_summary = await self.create_lootbox_reward(
                member, server, common=common, rare=rare, epic=epic, legendary=legendary)
            
            message = messages.create_level_message(self.db, member, server, reward_summary, level)
            await self.say_lootbot_channel(server, message)

        return total_exp

    async def award_level(self, member, server, level):
        """ Increment member level and give level award """
        self.db.set_level(member, server, level)


    def calculate_level(self, member_progress):
        """ Calculate if a level should be awarded if total experience is bigger than xp for next level """
        level = member_progress[0] + 1
        experience = member_progress[1]
        if experience >= settings.LEVEL_BASE * (level * level):
            return True
        return False

    # Game functions

    async def process_game_users(self):

        for user in self.game_users:
            member = self.get_member(user[0], user[1])
            server = self.get_server(user[0], user[1])
            if self.roll_lootbox(member, server):
                lootbox_rarity_int = self.roll_lootbox_rarity_int()
                user[2][lootbox_rarity_int] += 1
            user[3] += 1
            # If the user played for more than daily req award daily
            if (user[3] * settings.GAME_TIMER / 60) >= self.quests['daily'][1]['goal_value']:
                if self.db.get_dailies(member, server)[1] == 0:
                    await self.complete_quest(member, server, self.quests['daily'][1])
            # Add a tick to the game counter
            self.db.set_game_counter(member, server, 1)
            game_counter = self.db.get_counters(member, server)[1]
            # If total play time this season is higher than weekly award weekly
            if (game_counter * settings.GAME_TIMER / 60) >= self.quests['weekly'][1]['goal_value']:
                if self.db.get_weeklies(member, server)[1] == 0:
                    await self.complete_quest(member, server, self.quests['weekly'][1])

        # Start a new timer to process game users again
        await self.set_game_timer()

    # Voice Functions

    async def process_voice_users(self):
        pass

    # Dailies

    async def complete_quest(self, member, server, quest):
        """ Complete a daily for a member. Update daily status and give reward """

        # Determine reward
        if quest['reward_type'] == 'lootbox':
            common = quest['reward_count'] if quest['reward_rarity'] == 'common' else 0
            rare = quest['reward_count'] if quest['reward_rarity'] == 'rare' else 0
            epic = quest['reward_count'] if quest['reward_rarity'] == 'epic' else 0
            legendary = quest['reward_count'] if quest['reward_rarity'] == 'legendary' else 0

            reward_summary = await self.create_lootbox_reward(
                member, server, common=common, rare=rare, epic=epic, legendary=legendary)

        if quest['type'] == 'daily':
            self.db.set_daily(member, server, quest['database'], True)
            message = messages.create_quest_message(self.db, member, server, reward_summary, quest, mention=False)
        elif quest['type'] == 'weekly':
            self.db.set_weekly(member, server, quest['database'], True)
            message = messages.create_quest_message(self.db, member, server, reward_summary, quest, mention=True)

        await self.say_lootbot_channel(server, message)

    # Lootbox

    async def create_lootbox_reward(self, member, server, common=0, rare=0, epic=0, legendary=0):
        """ Collect lootboxes and create lootbox package. If no lootboxes are set a random rarity is rewarded

        returns list: [[common, rare, epic, legendary], [loots], total_exp]

        """
        rarity_count = [common, rare, epic, legendary]
        loots = []

        if common + rare + epic + legendary == 0:
            rarity_count[self.roll_lootbox_rarity_int()] += 1

        if rarity_count[0] > 0:
            loots = loots + await self.collect_lootbox(member, server, 'common', count=rarity_count[0])
        if rarity_count[1] > 0:
            loots = loots + await self.collect_lootbox(member, server, 'rare', count=rarity_count[1])
        if rarity_count[2] > 0:
            loots = loots + await self.collect_lootbox(member, server, 'epic', count=rarity_count[2])
        if rarity_count[3] > 0:
            loots = loots + await self.collect_lootbox(member, server, 'epic', item=True, count=rarity_count[3])

        total_exp = await self.process_loot(member, server, loots)

        reward_summary = (rarity_count, loots, total_exp)

        return reward_summary

    async def collect_lootbox(self, member, server, rarity, item=False, count=1):
        """ Collects loot for a rarity and number of lootboxes

        rarity: 'common', 'rare', 'epic','legendary'.

        """
        loots = []

        for _ in range(count):
            for loot in self.collect_loot(rarity):
                loots.append(loot)

        if item:
            loots.append(self.collect_item())

        self.db.add_lootbox(member, server, rarity)

        return loots

    def get_level_reward(self, level):
        if level%10 == 0:
            return 'legendary'
        elif level%5 == 0:
            return 'epic'
        elif level%3 == 0:
            return 'rare'
        return 'common'

    def roll_lootbox(self, member, server):
        """ Roll to check if a lootbox should be awarded. Chance is 1/lootbox_chance. """
        lootbox = random.randint(1, self.lb_settings['lootbox_chance'])
        if lootbox == 1:
            return True
        return False

    def roll_lootbox_rarity_int(self):
        """ Roll for rarity. Returns '0', '1', '2', '3'. """
        length = len(self.lootbox_rarity)
        rarity_index = random.randint(0, length - 1)
        return self.lootbox_rarity[rarity_index]

    def roll_lootbox_rarity_string(self):
        """ Roll for rarity. Returns 'common', 'rare', 'epic' or 'legendary'. """
        rarity_strings = ('common', 'rare', 'epic', 'legendary')
        rarity = self.roll_lootbox_rarity_int()
        return rarity_strings[rarity]

    # Loot

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

    def collect_loot(self, rarity):
        """ Collect loot of type loot for set rarity. Yields a dictionary object of loot.

        rarity: 'common', 'rare', 'epic', 'legendary'

        """
        for _ in range(self.lb_settings['loot_counter']):
            reward_index = random.randint(
                0, len(self.rewards['loot'][rarity]) - 1)
            loot = self.rewards['loot'][rarity][reward_index]
            yield loot

    def collect_item(self):
        """ Collect loot of type item for set rarity. Yields a dictionary object of loot."""

        reward_index = random.randint(0, len(self.rewards['loot']['item']) - 1)
        loot = self.rewards['loot']['item'][reward_index]
        return loot

    # Bot functions

    def add_game_user(self, member, server):
        """ Add a game user to the list of users

        game_user = [member.id, server.id, [common, rare, epic, legendary], tick_counts]
        """
        self.game_users.append([member.id, server.id, [0, 0, 0, 0], 0])

    def get_member(self, member_id, server_id):
        for server in self.servers:
            for member in server.members:
                if member.id == member_id and server.id == server_id:
                    return member

    def get_server(self, member_id, server_id):
        for server in self.servers:
            for member in server.members:
                if member.id == member_id and server.id == server_id:
                    return server

    async def say_lootbot_channel(self, server, message):
        """ Send message to BOT_CHANNEL of specified server """
        for channel in server.channels:
            if channel.name == settings.BOT_CHANNEL:
                await self.send_message(channel, message)

    async def say_global(self, message):
        """ Send message to BOT_CHANNEL for every server in the bot """
        for server in self.servers:
            await self.say_lootbot_channel(server, message)

    async def set_daily_reset(self):
        """ Set a timer for 4 A.M. the next day. Calls reset_dailies when timer fires """
        x = datetime.today()
        # Get seconds till tomorrow 4 A.M.
        y = x.replace(day=x.day + 1, hour=4, minute=0, second=0, microsecond=0)
        delta = y - x
        secs = delta.seconds
        self.daily_timer = Timer(secs, self.reset_dailies)
        log.info("Daily reset set for %s", y)

    async def reset_dailies(self):
        """ Reset the dailies, announce and start timer for next day """
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
        for _ in range(self.lb_settings['epic_chance']):
            self.lootbox_rarity.append(2)
        for _ in range(self.lb_settings['legendary_chance']):
            self.lootbox_rarity.append(3)
        log.info("Created lootbox rarity array of length %s",
                 str(len(self.lootbox_rarity)))
