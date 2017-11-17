import logging
import random
import math
import datetime
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
        self.season_timer = None
        self.message_timer = None
        self.game_timer = None
        self.voice_timer = None
        # Setup game/voice users
        self.message_users = []
        self.game_users = []
        self.voice_users = []

    async def on_ready(self):
        log.info("Discord client ready")
        await self.add_all_servers()
        await self.set_daily_reset()
        await self.set_season_reset()
        await self.set_message_timer()
        await self.set_game_timer()
        await self.set_voice_timer()

    async def add_all_servers(self):
        for server in self.servers:
            self.db.add_server(server)
            for member in server.members:
                if not member.bot:
                    self.db.add_member(member)
                    if member.game is not None:
                        self.add_game_user(member, server)
                    if member.voice.voice_channel is not None:
                        self.add_voice_user(member, server)

    async def close(self):
        log.info("Shutting down bot")
        self.db.close()
        self.game_timer.cancel()
        self.voice_timer.cancel()
        self.daily_timer.cancel()
        await super().close()

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

    async def on_member_join(self, member):
        if not member.bot:
            self.db.add_member(member)

    async def on_server_join(self, server):
        self.db.add_server(server)
        for member in server.members:
            if not member.bot:
                self.db.add_member(member)

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

        lootbox_reward = [0, 0, 0, 0]

        if self.calculate_level(member_progress):
            while self.calculate_level(member_progress):
                level = member_progress[0] + 1
                level_reward = self.get_level_reward(level)
                lootbox_reward[0] += 1 if level_reward == 'common' else 0
                lootbox_reward[1] += 1 if level_reward == 'rare' else 0
                lootbox_reward[2] += 1 if level_reward == 'epic' else 0
                lootbox_reward[3] += 1 if level_reward == 'legendary' else 0

                await self.award_level(member, server, level)
                member_progress = self.db.get_member_progress(member, server)

            reward_summary = await self.create_lootbox_reward(
                member, server, common=lootbox_reward[0], rare=lootbox_reward[1], epic=lootbox_reward[2], legendary=lootbox_reward[3])

            message = messages.create_level_message(
                self.db, member, server, reward_summary, level)
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

    # Message functions

    async def on_message(self, ctx):
        command = False
        # Ignore rewards if it's a command
        if ctx.content.startswith(settings.BOT_PREFIX):
            command = True
        if not ctx.author.bot and not command:
            member = ctx.author
            server = ctx.server
            blocked = False
            for user in self.message_users:
                if user[0] == member.id and user[1] == server.id:
                    blocked = True
            # If this is the first daily message from user complete daily
            if not blocked:
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
                self.add_message_user(member, server)
        else:
            await self.process_commands(ctx)

    async def process_message_users(self):
        self.message_users.clear()
        await self.set_message_timer()

    def add_message_user(self, member, server):
        """ Add a message user to the list of users that recently typed

        game_user = [member.id, server.id]
        """
        self.message_users.append([member.id, server.id])

    async def set_message_timer(self):
        message_timer_seconds = settings.MESSAGE_TIMER

        self.message_timer = Timer(
            message_timer_seconds, self.process_message_users)

    # Game functions

    async def process_game_users(self):
        """ Get the game user list and iterate through them, award lootboxes, experience, dailies and weeklies """
        for user in self.game_users:
            member = self.get_member_object(user[0], user[1])
            server = self.get_server_object(user[0], user[1])
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
            # Award experience
            experience = await self.award_experience(member, server, self.rewards['experience'][1])
            self.db.update_experience(member, server, experience)

        # Start a new timer to process game users again
        await self.set_game_timer()

    def add_game_user(self, member, server):
        """ Add a game user to the list of users

        game_user = [member.id, server.id, [common, rare, epic, legendary], tick_counts]
        """
        self.game_users.append([member.id, server.id, [0, 0, 0, 0], 0])

    async def set_game_timer(self):
        game_timer_seconds = settings.GAME_TIMER

        self.game_timer = Timer(game_timer_seconds, self.process_game_users)

    # Voice Functions

    async def on_voice_state_update(self, bmember, amember):
        """ Called whenever a member changes voice status

        Check if the user joined or left a server and add/remove them from the active voice user list.
        If a user left voice award possible reward for being in voice chat.
        """
        if bmember.voice.voice_channel is None and amember.voice.voice_channel is not None:
            self.add_voice_user(amember, amember.server)

        # When a user leaves voice chat check time and award points & lootboxes
        if bmember.voice.voice_channel is not None and amember.voice.voice_channel is None:
            box_earned = True
            for user in self.voice_users:
                if user[0] == bmember.id and user[1] == bmember.server.id:
                    # Check if any Lootboxes were earned
                    for box in user[2]:
                        if box > 0:
                            box_earned = True
                    # Award Lootboxes
                    if box_earned:
                        boxes = user[2]
                        reward_summary = await self.create_lootbox_reward(bmember, bmember.server, common=boxes[0], rare=boxes[1], epic=boxes[2], legendary=boxes[3])
                        message = messages.create_voice_message(
                            self.db, bmember, bmember.server, reward_summary, show_loot=True)
                        await self.say_lootbot_channel(bmember.server, message)
            # Filter the user out of the voice_users list
            self.voice_users = list(
                filter(lambda x: x[0] != amember.id and x[1] != amember.server.id, self.voice_users))

    async def process_voice_users(self):
        """ Get the voice user list and iterate through them, award lootboxes, experience, dailies and weeklies

        Voice rewards are only awarded when at least 2 people on a server are in voice
        """
        for user in self.voice_users:
            member = self.get_member_object(user[0], user[1])
            server = self.get_server_object(user[0], user[1])
            if self.check_voice_users(server):
                if self.roll_lootbox(member, server):
                    lootbox_rarity_int = self.roll_lootbox_rarity_int()
                    user[2][lootbox_rarity_int] += 1
                user[3] += 1
                # If the user played for more than daily req award daily
                if (user[3] * settings.VOICE_TIMER / 60) >= self.quests['daily'][2]['goal_value']:
                    if self.db.get_dailies(member, server)[2] == 0:
                        await self.complete_quest(member, server, self.quests['daily'][2])
                # Add a tick to the game counter
                self.db.set_voice_counter(member, server, 1)
                voice_counter = self.db.get_counters(member, server)[2]
                # If total play time this season is higher than weekly award weekly
                if (voice_counter * settings.VOICE_TIMER / 60) >= self.quests['weekly'][2]['goal_value']:
                    if self.db.get_weeklies(member, server)[2] == 0:
                        await self.complete_quest(member, server, self.quests['weekly'][2])
                # Award experience
                experience = await self.award_experience(
                    member, server, self.rewards['experience'][2])
                self.db.update_experience(member, server, experience)

        # Start a new timer to process voice users again
        await self.set_voice_timer()

    def check_voice_users(self, server):
        """ Returns True if at least 2 people are in voice at the same time on a server """
        voice_counter = 0
        for member in server.members:
            if member.voice.voice_channel is not None:
                voice_counter += 1

        if voice_counter >= 2:
            return True
        return False

    def add_voice_user(self, member, server):
        """ Add a game user to the list of users

        game_user = [member.id, server.id, [
            common, rare, epic, legendary], tick_counts]
        """
        self.voice_users.append([member.id, server.id, [0, 0, 0, 0], 0])

    async def set_voice_timer(self):
        voice_timer_seconds = settings.VOICE_TIMER

        self.voice_timer = Timer(voice_timer_seconds, self.process_voice_users)

    # Quests

    async def complete_quest(self, member, server, quest):
        """ Complete a quest for a member. Update quest status in database and give reward """

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
            message = messages.create_quest_message(
                self.db, member, server, reward_summary, quest, mention=False)
        elif quest['type'] == 'weekly':
            self.db.set_weekly(member, server, quest['database'], True)
            message = messages.create_quest_message(
                self.db, member, server, reward_summary, quest, mention=True)

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
            loots = loots + await self.collect_lootbox(member, server, 'epic', card=True, count=rarity_count[3])

        total_exp = await self.process_loot(member, server, loots)

        reward_summary = (rarity_count, loots, total_exp)

        return reward_summary

    async def collect_lootbox(self, member, server, rarity, card=False, count=1):
        """ Collects loot for a rarity and number of lootboxes

        rarity: 'common', 'rare', 'epic','legendary'.

        """
        loots = []

        for _ in range(count):
            for loot in self.collect_loot(rarity):
                loots.append(loot)

        if card:
            for _ in range(count):
                loots.append(self.collect_card())

        extra_card = random.randint(1, 10)
        if extra_card == 1 and card is False:
            extra_rarity = self.get_one_up_rarity(rarity)
            if extra_rarity == 'card':
                loots.append(self.collect_card())
            else:
                for loot in self.collect_loot(rarity, count=1):
                    loots.append(loot)

        self.db.add_lootbox(member, server, rarity)

        return loots

    def get_level_reward(self, level):
        """" Picks reward rarity for a set level """

        if level % 5 == 0:
            return 'legendary'
        elif level % 3 == 0:
            return 'epic'
        elif level % 2 == 0:
            return 'rare'
        return 'common'

    def get_one_up_rarity(self, rarity):
        if rarity == 'common':
            return 'rare'
        if rarity == 'rare':
            return 'epic'
        if rarity == 'epic':
            return 'card'

    def roll_lootbox(self, member, server):
        """ Roll to check if a lootbox should be awarded. Chance is 1/lootbox_chance.

        Chance takes into consideration lootboxes earned today and how many rolls you did without getting a lootbox

        """
        pity_counter = self.db.get_counters(member, server)[3]
        daily_boxes = self.db.get_dailies(member, server)[3]

        lootbox_chance = self.lb_settings['lootbox_chance']
        pity_modifer = self.lb_settings['pity_modifier']
        boxes_modifier = self.lb_settings['boxes_modifier']

        high_end = math.ceil(lootbox_chance * (pity_modifer**pity_counter))
        high_end = math.ceil(boxes_modifier ** (daily_boxes * daily_boxes))

        if high_end < 4:
            high_end = 1

        lootbox = random.randint(1, high_end)
        if lootbox == 1:
            self.db.reset_pity_counter(member, server)
            self.db.set_daily_boxes(member, server, 1)
            return True

        self.db.set_pity_counter(member, server, 1)

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

        total_exp = 0

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
            if loot['type'] == 'experience':
                total_exp += await self.award_experience(member, server, loot)
            # Add card to deck. If deck is full card is destroyed.
            if loot['type'] == 'card':
                card_added = self.db.add_card(member, server, loot['card_id'])
                if not card_added:
                    message = messages.create_card_add_error_message(
                        member, loot)
                    await self.say_lootbot_channel(server, message)

        return total_exp

    async def process_card(self, member, server, card_id):
        """ Called by a user to consume an card

        Gets the card based on ID from the dictionary and calls the card function to consume
        """
        cards = self.rewards['loot']['card']
        deck = self.db.get_cards(member, server)

        card = None
        for _card in cards:
            if _card['card_id'] == card_id:
                card = _card

        if deck is None:
            return False

        for _card_id in deck:
            if _card_id == card_id:
                await card['function'](self, member, server, card)
                self.db.remove_card(member, server, card_id)
                return True

        return False

    def collect_loot(self, rarity, count=None):
        """ Collect loot of type loot for set rarity. Yields a dictionary object of loot.

        rarity: 'common', 'rare', 'epic', 'legendary'
        """
        if count is None:
            count = self.lb_settings['loot_counter']

        for _ in range(count):
            reward_index = random.randint(
                0, len(self.rewards['loot'][rarity]) - 1)
            loot = self.rewards['loot'][rarity][reward_index]
            yield loot

    def collect_card(self):
        """ Collect loot of type card for set rarity. Yields a dictionary object of loot."""

        reward_index = random.randint(0, len(self.rewards['loot']['card']) - 1)
        loot = self.rewards['loot']['card'][reward_index]
        return loot

    # Bot functions

    def get_member_object(self, member_id, server_id):
        for server in self.servers:
            for member in server.members:
                if member.id == member_id and server.id == server_id:
                    return member

    def get_server_object(self, member_id, server_id):
        for server in self.servers:
            for member in server.members:
                if member.id == member_id and server.id == server_id:
                    return server

    # Announcements

    async def say_lootbot_channel(self, server, message):
        """ Send message to BOT_CHANNEL of specified server """
        for channel in server.channels:
            if channel.name == settings.BOT_CHANNEL:
                await self.send_message(channel, message)

    async def say_global(self, message):
        """ Send message to BOT_CHANNEL for every server in the bot """
        for server in self.servers:
            await self.say_lootbot_channel(server, message)

    # Daily Reset

    async def set_daily_reset(self):
        """ Set a timer for 4 A.M. the next day. Calls reset_dailies when timer fires """
        x = datetime.datetime.today()
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

    # Season Reset

    async def set_season_reset(self):
        """ Set a timer for 4 A.M. on wednesday. Calls reset_season when timer fires """
        x = datetime.date.today()
        if x.weekday() == 2:
            x += datetime.timedelta(7)
        else:
            while x.weekday() != 2:
                x += datetime.timedelta(1)

        y = datetime.time(hour=4, second=2)

        next_reset = datetime.datetime.combine(x, y)

        delta = next_reset - datetime.datetime.today()
        secs = delta.seconds

        self.season_timer = Timer(secs, self.reset_season)
        log.info("Season reset set for %s", next_reset)

    async def reset_season(self):
        """ Reset the dailies, announce and start timer for next day """
        for server in self.servers:
            self.db.add_season_end(server)
            ranking = self.db.get_ranking(server)
            message = messages.create_ranking_message(ranking, body=True)
            await self.say_lootbot_channel(server, message)
        self.db.reset_season()
        log.info("Reset Season")
        asyncio.sleep(1)
        await self.say_global("Season has been reset.")
        await self.set_season_reset()

        asyncio.sleep(1)
        cards = self.rewards['loot']['card']
        for server in self.servers:
            message = "```js\nSeason starter cards:\n\n"
            for member in server.members:
                if not member.bot:
                    card = [cards[random.randint(0, len(cards) - 1)]]
                    await self.process_loot(member, server, card)

                    message += member.name + " got card: \n"
                    message += "\n  [" + card[0]['name'] + "]\n\n"

            message += "```"
            await self.say_lootbot_channel(server, message)

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
