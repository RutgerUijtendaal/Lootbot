#!/usr/local/bin/python3

import random
import math
import settings
from data import strings
from data.objects import rewards

# Command messages


def create_deck_message(deck):

    message = "\n\n# Deck:"
    for x in range(settings.DECK_SIZE):
        if deck is not None:
            message += "\n<" + str(x + 1) + ": "
            if len(deck) > x:
                for card in rewards.REWARDS['loot']['card']:
                    if card['card_id'] == deck[x]:
                        message += "[" + card['name'] + "]>"
            else:
                message += "[Empty]>"
        else:
            message += "\n<" + str(x + 1) + ": [Empty]>"

    return message


def create_lootbox_message(lootboxes):
    message = ""
    message += ("\n\n# Lootboxes:" +
                "\n  Common:       " + str(lootboxes[0]) +
                "\n  Rare:         " + str(lootboxes[1]) +
                "\n  Epic:         " + str(lootboxes[2]) +
                "\n  Legendary:    " + str(lootboxes[2]))

    return message


def create_multiplier_message(multipliers):

    message = ""
    message += ("\n\n# Multipliers:" +
                "\n  Message:      " + str(multipliers[0]) +
                "\n  Game:         " + str(multipliers[1]) +
                "\n  Voice:        " + str(multipliers[2]))

    return message


def create_progress_message(progress):
    level = progress[0]
    experience = progress[1]
    message = ""

    level_exp = math.ceil(experience - _get_exp_level(level))
    next_level = _get_exp_next_level(level)
    level_progress = math.ceil((level_exp / next_level) * 100)

    message += (
        "\n\n# Progress:" +
        "\n  Level:        " + str(level) +
        "\n  Level Exp:    " + str(level_exp) + (" " * (8 - len(str(level_exp)))) + "(" + str(level_progress) + " %)" +
        "\n  Total Exp:    " + str(experience))

    return message


def create_ranking_message(ranking, body=False):
    if body:
        message = "```js\n"
    else:
        message = ""

    message += "# Ranking\n"
    for x, member in enumerate(ranking):
        message += "\n  " + str(1 + x) + ": " + \
            member[0] + (" " * (10 - len(str(member[0]))))
        message += "(Level:" + \
            (" " * (3 - len(str(member[1])))) + str(member[1])
        message += " | Experience: " + str(member[2]) + ")"

    if body:
        message += "```"

    return message


# Program Announcements


def create_level_message(db, member, server, reward_summary, level):
    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""
    message += _create_mention_start(member, level, message_settings)

    message += _create_lootbox_summary(rarity_count)

    message += "\n# " + strings.level_flavour[random.randint(
        0, len(strings.level_flavour) - 1)] + ": " + str(level)

    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp)

    return message


def create_random_lootbox_message(db, member, server, reward_summary):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""
    message += _create_mention_start(member, level, message_settings)

    message += _create_lootbox_summary(rarity_count)

    message += "\n# " + \
        strings.message_flavour[random.randint(
            0, len(strings.message_flavour) - 1)]
    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp)

    return message


def create_quest_message(db, member, server, reward_summary, quest, mention=False):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""

    message += _create_mention_start(member,
                                     level, message_settings, mention=mention)

    message += _create_lootbox_summary(rarity_count)

    if quest['type'] == 'daily':
        message += "\n# For completing daily: '" + quest['name'] + "'```"
    if quest['type'] == 'weekly':
        message += "\n# For completing weekly: '" + quest['name'] + "'```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp)

    return message


def create_game_message(db, member, server, reward_summary, show_loot=False):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""
    message += _create_mention_start(member, level, message_settings)

    message += _create_lootbox_summary(rarity_count)

    if strings.game_flavour.get(member.game.name) is not None:
        flavour = strings.game_flavour[member.game.name]
    else:
        flavour = strings.game_flavour['default']

    message += "\n# " + \
        flavour[random.randint(
            0, len(strings.game_flavour) - 1)] + " in " + member.game.name + "."

    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp, show_loot=show_loot)

    return message


def create_voice_message(db, member, server, reward_summary, show_loot=False):

    rarity_count = reward_summary[0]
    loots = reward_summary[1]
    gained_exp = reward_summary[2]

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""
    message += _create_mention_start(member, level, message_settings)

    message += _create_lootbox_summary(rarity_count)

    message += "\n# " + strings.voice_flavour[random.randint(
        0, len(strings.voice_flavour) - 1)] + ""

    message += "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp, show_loot=show_loot)

    return message


def create_card_add_error_message(member, card):
    message = "```diff\n"

    message += "- # Failed to card: " + \
        card['name'] + " to user: " + member.name + "."

    message += "\n\nYour deck is probably full, use some of those cards."

    message += "```"

    return message


def create_card_use_message(db, member, server, card, total_exp=None, reward_summary=None, show_loot=False, mention=False):

    message = ""

    member_progress = db.get_member_progress(member, server)
    level = member_progress[0]

    message_settings = db.get_message_settings(member, server)

    message = ""
    message += _create_mention_start(member,
                                     level, message_settings, mention=mention)

    if reward_summary is not None:
        rarity_count = reward_summary[0]
        loots = reward_summary[1]
        gained_exp = reward_summary[2]

        message += _create_lootbox_summary(rarity_count)

        message += "\n"

    elif total_exp is not None:

        message += "<1  [" + str(total_exp) + " " + \
            card['reward_text'] + "]>\n\n"

    else:
        message += "<-  [" + card['reward_text'] + "]>\n\n"

    if card['show_user']:
        message += "# From " + card['user_name'] + \
            ' using ' + card['name'] + "\n\n"
    else:
        message += "# From using: " + card['name'] + "\n\n"

    message += "[" + card['flavour_text'] + "]()"

    message += "```"

    if reward_summary is not None:
        message += _create_user_summary(db, message_settings,
                                        member, server, loots, gained_exp, show_loot=show_loot)

    return message


def _create_mention_start(member, level, message_settings, mention=False):
    message = ""
    if message_settings[0] or mention:
        message += member.mention + " (" + str(level) + ") got: ```md\n"
    else:
        message += "```md\n[" + member.name + "](" + str(level) + ") got:\n\n"
    return message


def _create_lootbox_summary(rarity_count):

    message = ""

    if rarity_count[0] > 1:
        message += "<" + str(rarity_count[0]) + "  [Common Lootboxes]>\n"
    elif rarity_count[0] == 1:
        message += "<" + str(rarity_count[0]) + "  [Common Lootbox]>\n"
    if rarity_count[1] > 1:
        message += "<" + str(rarity_count[1]) + "  [Rare Lootboxes]>\n"
    elif rarity_count[1] == 1:
        message += "<" + str(rarity_count[1]) + "  [Rare Lootbox]>\n"
    if rarity_count[2] > 1:
        message += "<" + str(rarity_count[2]) + "  [Epic Lootboxes]>\n"
    elif rarity_count[2] == 1:
        message += "<" + str(rarity_count[2]) + "  [Epic Lootbox]>\n"
    if rarity_count[3] > 1:
        message += "<" + str(rarity_count[3]) + "  [Legendary Lootboxes]>\n"
    elif rarity_count[3] == 1:
        message += "<" + str(rarity_count[3]) + "  [Legendary Lootbox]>\n"

    return message


def _create_user_summary(db, message_settings, member, server, loots, gained_exp, show_loot=False):

    message = "```md\n"

    add_multipliers = [0, 0, 0]

    if message_settings[1] or show_loot:
        message += "\n# Loot:"

    has_card = False

    for loot in loots:
        if message_settings[1] or show_loot:
            if loot['type'] != 'card':
                message += "\n<-  [" + loot['name'] + "]>"

        if loot['type'] == 'multiplier':
            if loot['target'] == 'message':
                add_multipliers[0] += loot['value']
            if loot['target'] == 'game':
                add_multipliers[1] += loot['value']
            if loot['target'] == 'voice':
                add_multipliers[2] += loot['value']
        if loot['type'] == 'card':
            has_card = True

    if has_card:
        message += "\n\n# Cards:"
        for loot in loots:
            if loot['type'] == 'card':
                message += "\n<-  [" + loot['name'] + "]>"

    message += "```"
    message += "```js\n"

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
        level_exp = math.ceil(experience - _get_exp_level(level))
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
    level_exp = settings.LEVEL_BASE * (level ** 2.2)
    return level_exp


def _get_exp_next_level(level):
    next_level = _get_exp_level(level + 1) - _get_exp_level(level)
    return next_level
