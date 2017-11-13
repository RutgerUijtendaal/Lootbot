import random
import settings
import math
from data import strings


def create_random_lootbox_message(db, member, server, reward_summary, mention=False):

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

    message += "\n" + \
        strings.message_flavour[random.randint(
            0, len(strings.message_flavour) - 1)] + "```"

    message += _create_user_summary(db, message_settings,
                                    member, server, loots, gained_exp)

    return message


def create_daily_message(db, member, server, reward_summary, daily, mention=False):

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

    message += "\nFor completing daily: '" + daily['name'] + "' ```"

    message += _create_user_summary(db,
                                    message_settings, member, server, loots, gained_exp)

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


def _create_user_summary(db, message_settings, member, server, loots, gained_exp):

    message = "```js\n"

    add_multipliers = [0, 0, 0]

    if message_settings[1]:
        message += "\nLoot:"

    for loot in loots:
        if message_settings[1]:
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
            "\n\nMultipliers:" +
            "\n  Message:     " + str(new_multipliers[0]) + (" " * (7 - len(str(new_multipliers[0])))) + "(+" + str(add_multipliers[0]) + ")" +
            "\n  Game:        " + str(new_multipliers[1]) + (" " * (7 - len(str(new_multipliers[1])))) + "(+" + str(add_multipliers[1]) + ")" +
            "\n  Voice:       " + str(new_multipliers[2]) + (" " * (7 - len(str(new_multipliers[2])))) + "(+" + str(add_multipliers[2]) + ")")

    if message_settings[3]:
        member_progress = db.get_member_progress(member, server)
        level = member_progress[0]   
        experience = member_progress[1]       
                                     
        # Level % progress
        level_exp = experience - _get_exp_level(level)                          # Subtract from xp for next level to get xp for this level
        next_level = _get_exp_next_level(level)                                 # Get the experience required for the next level
        level_progress = math.ceil((level_exp/next_level) * 100)     # (current_xp/next_level_xp) * 100
        
        message += (
            "\n\nProgress:" +
            "\n  Level:       " + str(level) + 
            "\n  Next Level:  " + str(level_exp) + (" " * (7 - len(str(level_exp)))) + "(" + str(level_progress) +  " %)" +
            "\n  Total Exp:   " + str(experience) + (" " * (7 - len(str(experience)))) + "(+" + str(gained_exp) + ")")

    message += "```"

    return message

def _get_exp_level(level):
    level_exp = 100 * ((level*level)-level)
    return level_exp

def _get_exp_next_level(level):
    next_level = _get_exp_level(level+1) - _get_exp_level(level) 
    return next_level 