import random
import math
import settings
from data import strings

def create_level_message(db, member, server, reward_summary, level):
    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    message_settings = db.get_message_settings(member, server)

    message = ""
    if message_settings[0]:
        message += member.mention + " got: ```css\n"
    else:
        message += "```css\n" + member.name + " got:\n\n"

    message += _create_lootbox_summary(rarity_count)

    message += "\n" + strings.level_flavour[random.randint(0, len(strings.level_flavour) - 1)] + ": " + str(level)

    message += "```"

    message += _create_user_summary(db, message_settings, member, server, loots, gained_exp)

    return message

def create_random_lootbox_message(db, member, server, reward_summary):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    message_settings = db.get_message_settings(member, server)

    message = ""
    if message_settings[0]:
        message += member.mention + " got: ```css\n"
    else:
        message += "```css\n" + member.name + " got:\n\n"

    message += _create_lootbox_summary(rarity_count)

    message += "\n" + strings.message_flavour[random.randint(0, len(strings.message_flavour) - 1)]
    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp)

    return message


def create_quest_message(db, member, server, reward_summary, quest, mention=False):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    message_settings = db.get_message_settings(member, server)

    message = ""
    if message_settings[0] or mention:
        message += member.mention + " got: ```css\n"
    else:
        message += "```css\n" + member.name + " got:\n\n"

    message += _create_lootbox_summary(rarity_count)

    if quest['type'] == 'daily':
        message += "\nFor completing daily: '" + quest['name'] + "' ```"
    if quest['type'] == 'weekly':
        message += "\nFor completing weekly: '" + quest['name'] + "' ```"

    message += _create_user_summary(db, message_settings, member, server, loots, gained_exp)

    return message


def create_game_message(db, member, server, reward_summary, show_loot=False):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    message_settings = db.get_message_settings(member, server)

    message = ""
    if message_settings[0]:
        message += member.mention + " got: ```css\n"
    else:
        message += "```css\n" + member.name + " got:\n\n"

    message += _create_lootbox_summary(rarity_count)

    if strings.game_flavour.get(member.game.name) is not None:
        flavour = strings.game_flavour[member.game.name]
    else:
        flavour = strings.game_flavour['default']

    message += "\n" + \
        flavour[random.randint(
            0, len(strings.message_flavour) - 1)] + " in " + member.game.name + "."

    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp, show_loot=show_loot)

    return message


def _create_lootbox_summary(rarity_count):

    message = ""

    if rarity_count[0] > 1:
        message += str(rarity_count[0]) + " common Lootboxes\n"
    elif rarity_count[0] == 1:
        message += str(rarity_count[0]) + " common Lootbox\n"
    if rarity_count[1] > 1:
        message += str(rarity_count[1]) + " rare Lootboxes\n"
    elif rarity_count[1] == 1:
        message += str(rarity_count[1]) + " rare Lootbox\n"
    if rarity_count[2] > 1:
        message += str(rarity_count[2]) + " epic Lootboxes\n"
    elif rarity_count[2] == 1:
        message += str(rarity_count[2]) + " epic Lootbox\n"
    if rarity_count[3] > 1:
        message += str(rarity_count[3]) + " legendary Lootboxes\n"
    elif rarity_count[3] == 1:
        message += str(rarity_count[3]) + " legendary Lootbox\n"

    return message


def _create_user_summary(db, message_settings, member, server, loots, gained_exp, show_loot=False):

    message = "```js\n"

    add_multipliers = [0, 0, 0]

    if message_settings[1] or show_loot:
        message += "\n# Loot:"

    for loot in loots:
        if message_settings[1] or show_loot:
            message += "\n  " + loot['name']

        if loot['type'] == 'multiplier':
            if loot['target'] == 'message':
                add_multipliers[0] += loot['value']
            if loot['target'] == 'game':
                add_multipliers[0] += loot['value']
            if loot['target'] == 'voice':
                add_multipliers[0] += loot['value']

    if message_settings[2]:
        new_multipliers = db.get_multipliers(member, server)
        message += (
            "\n\n# Multipliers:" +
            "\n  Message:      " + str(new_multipliers[0]) + (" " * (8 - len(str(new_multipliers[0])))) + "(+" + str(add_multipliers[0]) + ")" +
            "\n  Game:         " + str(new_multipliers[1]) + (" " * (8 - len(str(new_multipliers[1])))) + "(+" + str(add_multipliers[1]) + ")" +
            "\n  Voice:        " + str(new_multipliers[2]) + (" " * (8 - len(str(new_multipliers[2])))) + "(+" + str(add_multipliers[2]) + ")")

    if message_settings[3]:
        member_progress = db.get_member_progress(member, server)
        level = member_progress[0]
        experience = member_progress[1]

        # Level % progress
        # Subtract from xp for next level to get xp for this level
        level_exp = experience - _get_exp_level(level)
        next_level = _get_exp_next_level(level)
        level_progress = math.ceil((level_exp / next_level) * 100)

        message += (
            "\n\n# Progress:" +
            "\n  Level:        " + str(level) +
            "\n  Level Exp:    " + str(level_exp) + (" " * (8 - len(str(level_exp)))) + "(" + str(level_progress) + " %)" +
            "\n  Total Exp:    " + str(experience) + (" " * (8 - len(str(experience)))) + "(+" + str(gained_exp) + ")")

    message += "```"

    return message


def _get_exp_level(level):
    level_exp = 100 * (level * level)
    return level_exp


def _get_exp_next_level(level):
    next_level = _get_exp_level(level + 1) - _get_exp_level(level)
    return next_level
