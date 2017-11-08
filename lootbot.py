import logging
import random
import math

from discord.ext import commands

from data import constants, rewards
from cogs.utils.db import Database

log = logging.getLogger(__name__)


class Lootbot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()
        self.db.create_database()
        self.loottable = []
        self.init_lootbox_chance()

    async def on_ready(self):
        log.info("Discord client ready")
        await self.add_all_servers()

    async def close(self):
        self.db.close()
        await super().close()

    async def add_all_servers(self):
        for server in self.servers:
            self.db.add_server(server)
            for member in server.members:
                if not member.bot:
                    self.db.add_member(member)
                    if member.game is not None:
                        self.db.set_game_time(member, server)
                    if member.voice.voice_channel is not None:
                        self.db.set_voice_time(member, server)

    async def on_message(self, msg):
        command = False
        # Ignore rewards if it's a command
        if msg.content.startswith('$'):
            command = True
        # Process message if the user is not a bot
        if not msg.author.bot and not command:
            # Roll to see if a lootbox is earned
            lootbox = self.roll_lootbox()
            # Read and write new points using message_point_modifier to calculate total points earned
            message_points_modifier = self.db.get_message_point_multiplier(
                msg.author, msg.server)
            # Always round to a full number for points
            points = math.ceil(
                constants.BASE_MESSAGE_POINTS * message_points_modifier)
            self.db.add_points(points, msg.author, msg.server)
            # If a lootbox was earned update database, add reaction to message
            if lootbox != -1:
                # Announce lootbox to server channel
                message = (
                    "```css\n" +
                    msg.author.name +
                    " awarded a " +
                    constants.LOOTBOX_STRING_RARITY[lootbox] +
                    " lootbox```"
                )
                await self.say_lootbot_channel(msg.server, message)
                await self.award_lootbox(lootbox, msg.author, msg.server)
                await self.add_reaction(msg, constants.LOOTBOX_EMOJI[lootbox])
        else:
            await self.process_commands(msg)

    async def on_member_update(self, bmember, amember):
        # If a game is launched set launch time
        if bmember.game is None and amember.game is not None:
            self.db.set_game_time(amember, amember.server)

        # When user stops playing game check time and award points & lootboxes
        if bmember.game is not None and amember.game is None:
            lootbox_earned = False
            lootboxes = [0, 0, 0]
            seconds = self.db.get_game_time(amember, amember.server)
            # For every GAME_LOOTBOX_TIME seconds played there's a chance for a lootbox
            for x in range(math.floor(seconds / constants.GAME_LOOTBOX_TIME)):
                lootbox = self.roll_lootbox()
                if lootbox != -1:
                    lootbox_earned = True
                    lootboxes[lootbox] = lootboxes[lootbox] + 1
                    await self.award_lootbox(lootbox, amember, amember.server)
            if lootbox_earned:
                message = (amember.mention + " got: ""```js\n")
                for i, x in enumerate(lootboxes):
                    if x != 0:
                        message += (str(x) + " " +
                                    constants.LOOTBOX_STRING_RARITY[i] + " lootboxes\n")
                message += "\nWhile being ingame.```"
                await self.say_lootbot_channel(amember.server, message)

            # For every GAME_POINT_TIME seconds played the user is awarded points
            game_point_multiplier = self.db.get_game_point_multiplier(
                amember, amember.server)
            _points = math.floor(seconds / constants.GAME_POINT_TIME)
            points = math.ceil(constants.BASE_GAME_POINTS *
                               game_point_multiplier * _points)
            self.db.add_points(points, amember, amember.server)

    async def on_voice_state_update(self, bmember, amember):
        # If voice is joined set voice join time
        if bmember.voice.voice_channel is None and amember.voice.voice_channel is not None:
            self.db.set_voice_time(amember, amember.server)

        # When a user leaves voice chat check time and award points & lootboxes
        if bmember.voice.voice_channel is not None and amember.voice.voice_channel is None:
            lootbox_earned = False
            lootboxes = [0, 0, 0]
            seconds = self.db.get_voice_time(amember, amember.server)
            # For every VOICE_LOOTBOX_TIME seconds on voice there's a chance for a lootbox
            for x in range(math.floor(seconds / constants.VOICE_LOOTBOX_TIME)):
                lootbox = self.roll_lootbox()
                if lootbox != -1:
                    lootbox_earned = True
                    lootboxes[lootbox] = lootboxes[lootbox] + 1
                    await self.award_lootbox(lootbox, amember, amember.server)
            if lootbox_earned:
                message = (amember.mention + " got: ""```js\n")
                for i, x in enumerate(lootboxes):
                    if x != 0:
                        message += (str(x) + " " +
                                    constants.LOOTBOX_STRING_RARITY[i] + " lootboxes\n")
                message += "While being in voice.```"
                await self.say_lootbot_channel(amember.server, message)

            # For every VOICE_POINT_TIME second on voice the user is awarded points
            voice_points_modifier = self.db.get_voice_point_multiplier(
                amember, amember.server)
            _points = math.floor(seconds / constants.VOICE_POINT_TIME)
            points = math.ceil(constants.BASE_VOICE_POINTS *
                               voice_points_modifier * _points)
            self.db.add_points(points, amember, amember.server)

    async def on_member_join(self, member):
        if not member.bot:
            self.db.add_member(member)

    async def on_server_join(self, server):
        self.db.add_server(server)
        for member in server.members:
            if not member.bot:
                self.db.add_member(member)
                if member.game is not None:
                    self.db.set_game_time(member, server)
                if member.voice.voice_channel is not None:
                    self.db.set_voice_time(member, server)

    async def say_lootbot_channel(self, server, message):
        for channel in server.channels:
            if channel.name == constants.BOT_CHANNEL:
                await self.send_message(channel, message)

    async def award_lootbox(self, rarity, member, server):
        # If auto open is set to true open the lootbox right away
        if self.db.get_auto_open(member, server):
            await self.open_lootbox(rarity, member, server)
            self.db.add_total_lootbox(rarity, member, server)
        # Else save the lootbox in the database
        else:
            self.db.add_lootbox(rarity, member, server)

    async def open_lootbox(self, rarity, member, server):
        loots = []
        for x in range(2):
            reward_index = random.randint(
                0, len(rewards.LOOT_CONSUMABLE[rarity]) - 1)
            loots.append(rewards.LOOT_CONSUMABLE[rarity][reward_index])

        message = "```js\n"
        for loot in loots:
            message += (
                member.name + " got " + loot[2] + "\n"
            )
            self.db.add_consumable_loot(
                constants.LOOTBOX_DB_LOOT_SELECTION[loot[0]], loot[1], member, server)
        message += "```"
        await self.say_lootbot_channel(server, message)

    def init_lootbox_chance(self):
        for x in range(constants.COMMON_LOOTBOX_CHANCE):
            self.loottable.append(0)
        for x in range(constants.RARE_LOOTBOX_CHANCE):
            self.loottable.append(1)
        for x in range(constants.LEG_LOOTBOX_CHANCE):
            self.loottable.append(2)
        for x in range(constants.LOOTTABLE_MAX_LENGTH - len(self.loottable)):
            self.loottable.append(-1)
        assert len(self.loottable) == constants.LOOTTABLE_MAX_LENGTH

    def roll_lootbox(self):
        # Returns -1 for no lootbox, 0 for common, 1 for rare and 2 for legendary
        return self.loottable[random.randint(0, constants.LOOTTABLE_MAX_LENGTH - 1)]
