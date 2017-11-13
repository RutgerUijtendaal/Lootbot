import random
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
        message += str(rarity_count[2]) + " legendary Lootboxes\n"
    elif rarity_count[2] == 1:
        message += str(rarity_count[2]) + " legendary Lootbox\n"

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
        progress = db.get_member_progress(member, server)
        message += (
            "\n\nProgress:" +
            "\n  Level:       " + str(progress[0]) +
            "\n  Experience:  " + str(progress[1]) + (" " * (7 - len(str(progress[1])))) + "(+" + str(gained_exp) + ")")

    message += "```"

    return message
