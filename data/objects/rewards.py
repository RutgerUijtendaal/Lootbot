#!/usr/local/bin/python3

import logging
import asyncio
import random
import cogs.utils.messages as messages

log = logging.getLogger(__name__)

# Item functions


async def spam_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        spam_reward = {
            'name': "Message Base Experience",
            'type': 'experience',
            'target': 'message',
            'value': 100
        }

        total_exp = await bot.award_experience(_member, server, spam_reward)

        message = messages.create_card_use_message(
            bot.db, _member, server, card, total_exp=total_exp)

        use_message.append(message)

    return use_message


async def npc_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        npc_reward = {
            'name': "Game Base Experience",
            'type': 'experience',
            'target': 'game',
            'value': 100
        }

        total_exp = await bot.award_experience(_member, server, npc_reward)

        message = messages.create_card_use_message(
            bot.db, _member, server, card, total_exp=total_exp)

        use_message.append(message)

    return use_message


async def booming_voice_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        booming_voice_reward = {
            'name': "Voice Base Experience",
            'type': 'experience',
            'target': 'voice',
            'value': 100
        }

        total_exp = await bot.award_experience(_member, server, booming_voice_reward)

        message = messages.create_card_use_message(
            bot.db, _member, server, card, total_exp=total_exp)

        use_message.append(message)

    return use_message


async def pot_of_greed_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        lootbox_reward = [0, 0, 0, 0]

        for _ in range(2):
            rarity = bot.roll_lootbox_rarity_string()
            lootbox_reward[0] += 1 if rarity == 'common' else 0
            lootbox_reward[1] += 1 if rarity == 'rare' else 0
            lootbox_reward[2] += 1 if rarity == 'epic' else 0
            lootbox_reward[3] += 1 if rarity == 'legendary' else 0

        reward_summary = await bot.create_lootbox_reward(
            _member, server, common=lootbox_reward[0], rare=lootbox_reward[1], epic=lootbox_reward[2], legendary=lootbox_reward[3])

        message = messages.create_card_use_message(
            bot.db, _member, server, card, reward_summary=reward_summary)

        use_message.append(message)

    return use_message


async def epic_mage_ring_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        reward_summary = await bot.create_lootbox_reward(_member, server, common=0, rare=0, epic=1, legendary=0)

        message = messages.create_card_use_message(
            bot.db, _member, server, card, reward_summary=reward_summary)

        use_message.append(message)

    return use_message


async def stacked_deck_function(bot, member, server, card):
    card['user_name'] = member.name
    members = []
    cards = bot.rewards['loot']['card']
    for _member in server.members:
        if not _member.bot:
            if _member.id != member.id:
                members.append(_member)

    use_message = []
    for x in range(2):
        if x == 0:
            _member = member
        else:
            _member = members[random.randint(0, len(members) - 1)]
            members.remove(_member)

        _card = [cards[random.randint(0, len(cards) - 1)]]

        await bot.process_loot(_member, server, _card)
        card['reward_text'] = _card[0]['name']
        message = messages.create_card_use_message(
            bot.db, _member, server, card)

        use_message.append(message)

    return use_message


# Reward list

REWARDS = {

    # Base Experience rewards

    'experience': [
        {
            'name': "Message Base Experience",
            'type': 'experience',
            'target': 'message',
            'value': 1
        },

        {
            'name': "Game Base Experience",
            'type': 'experience',
            'target': 'game',
            'value': 1
        },

        {
            'name': "Voice Base Experience",
            'type': 'experience',
            'target': 'voice',
            'value': 2
        }

    ],

    # Instant rewards are not stored in deck and applied to the user right away
    'loot': {

        'common': [

            {
                'name': "Message Experience 2",
                'type': 'experience',
                'target': 'message',
                'value': 2
            },


            {
                'name': "Message Experience 3",
                'type': 'experience',
                'target': 'message',
                'value': 3
            },

            {
                'name': "Message Experience 4",
                'type': 'experience',
                'target': 'message',
                'value': 4
            },

            {
                'name': "Game Experience 2",
                'type': 'experience',
                'target': 'game',
                'value': 2
            },


            {
                'name': "Game Experience 3",
                'type': 'experience',
                'target': 'game',
                'value': 3
            },


            {
                'name': "Game Experience 4",
                'type': 'experience',
                'target': 'game',
                'value': 4
            },

            {
                'name': "Voice Experience 2",
                'type': 'experience',
                'target': 'voice',
                'value': 2
            },


            {
                'name': "Voice Experience 3",
                'type': 'experience',
                'target': 'voice',
                'value': 3
            },

            {
                'name': "Voice Experience 4",
                'type': 'experience',
                'target': 'voice',
                'value': 4
            },

            {
                'name': "Message Multiplier x 2",
                'type': 'multiplier',
                'target': 'message',
                'value': 2
            },

            {
                'name': "Message Multiplier x 3",
                'type': 'multiplier',
                'target': 'message',
                'value': 3
            },

            {
                'name': "Message Multiplier x 4",
                'type': 'multiplier',
                'target': 'message',
                'value': 4
            },

            {
                'name': "Game Multiplier x 2",
                'type': 'multiplier',
                'target': 'game',
                'value': 2
            },

            {
                'name': "Game Multiplier x 3",
                'type': 'multiplier',
                'target': 'game',
                'value': 3
            },

            {
                'name': "Game Multiplier x 4",
                'type': 'multiplier',
                'target': 'game',
                'value': 4
            },

            {
                'name': "Voice Multiplier x 2",
                'type': 'multiplier',
                'target': 'voice',
                'value': 2
            },

            {
                'name': "Voice Multiplier x 3",
                'type': 'multiplier',
                'target': 'voice',
                'value': 3
            },

            {
                'name': "Voice Multiplier x 4",
                'type': 'multiplier',
                'target': 'voice',
                'value': 4
            }

        ],

        'rare': [

            {
                'name': "Message Experience 5",
                'type': 'experience',
                'target': 'message',
                'value': 5
            },


            {
                'name': "Message Experience 6",
                'type': 'experience',
                'target': 'message',
                'value': 6
            },


            {
                'name': "Message Experience 7",
                'type': 'experience',
                'target': 'message',
                'value': 7
            },

            {
                'name': "Game Experience 5",
                'type': 'experience',
                'target': 'game',
                'value': 5
            },


            {
                'name': "Game Experience 6",
                'type': 'experience',
                'target': 'game',
                'value': 6
            },


            {
                'name': "Game Experience 7",
                'type': 'experience',
                'target': 'game',
                'value': 7
            },

            {
                'name': "Voice Experience 5",
                'type': 'experience',
                'target': 'voice',
                'value': 5
            },


            {
                'name': "Voice Experience 6",
                'type': 'experience',
                'target': 'voice',
                'value': 6
            },

            {
                'name': "Voice Experience 7",
                'type': 'experience',
                'target': 'voice',
                'value': 7
            },

            {
                'name': "Message Multiplier x 5",
                'type': 'multiplier',
                'target': 'message',
                'value': 5
            },

            {
                'name': "Message Multiplier x 6",
                'type': 'multiplier',
                'target': 'message',
                'value': 6
            },

            {
                'name': "Message Multiplier x 7",
                'type': 'multiplier',
                'target': 'message',
                'value': 7
            },

            {
                'name': "Game Multiplier x 5",
                'type': 'multiplier',
                'target': 'game',
                'value': 5
            },

            {
                'name': "Game Multiplier x 6",
                'type': 'multiplier',
                'target': 'game',
                'value': 6
            },

            {
                'name': "Game Multiplier x 7",
                'type': 'multiplier',
                'target': 'game',
                'value': 7
            },

            {
                'name': "Voice Multiplier x 5",
                'type': 'multiplier',
                'target': 'voice',
                'value': 5
            },

            {
                'name': "Voice Multiplier x 6",
                'type': 'multiplier',
                'target': 'voice',
                'value': 6
            },

            {
                'name': "Voice Multiplier x 7",
                'type': 'multiplier',
                'target': 'voice',
                'value': 7
            }

        ],

        'epic': [

            {
                'name': "Message Experience 8",
                'type': 'experience',
                'target': 'message',
                'value': 8
            },


            {
                'name': "Message Experience 9",
                'type': 'experience',
                'target': 'message',
                'value': 9
            },


            {
                'name': "Message Experience 10",
                'type': 'experience',
                'target': 'message',
                'value': 10
            },

            {
                'name': "Game Experience 8",
                'type': 'experience',
                'target': 'game',
                'value': 8
            },


            {
                'name': "Game Experience 9",
                'type': 'experience',
                'target': 'game',
                'value': 9
            },


            {
                'name': "Game Experience 10",
                'type': 'experience',
                'target': 'game',
                'value': 10
            },

            {
                'name': "Voice Experience 8",
                'type': 'experience',
                'target': 'voice',
                'value': 8
            },


            {
                'name': "Voice Experience 9",
                'type': 'experience',
                'target': 'voice',
                'value': 9
            },

            {
                'name': "Voice Experience 10",
                'type': 'experience',
                'target': 'voice',
                'value': 10
            },

            {
                'name': "Message Multiplier x 8",
                'type': 'multiplier',
                'target': 'message',
                'value': 8
            },

            {
                'name': "Message Multiplier x 9",
                'type': 'multiplier',
                'target': 'message',
                'value': 9
            },

            {
                'name': "Message Multiplier x 10",
                'type': 'multiplier',
                'target': 'message',
                'value': 10
            },

            {
                'name': "Game Multiplier x 8",
                'type': 'multiplier',
                'target': 'game',
                'value': 8
            },

            {
                'name': "Game Multiplier x 9",
                'type': 'multiplier',
                'target': 'game',
                'value': 9
            },

            {
                'name': "Game Multiplier x 10",
                'type': 'multiplier',
                'target': 'game',
                'value': 10
            },

            {
                'name': "Voice Multiplier x 8",
                'type': 'multiplier',
                'target': 'voice',
                'value': 8
            },

            {
                'name': "Voice Multiplier x 9",
                'type': 'multiplier',
                'target': 'voice',
                'value': 9
            },

            {
                'name': "Voice Multiplier x 10",
                'type': 'multiplier',
                'target': 'voice',
                'value': 10
            }
        ],

        'card': [
            {
                'card_id': 1,
                'name': "Spam",
                'type': 'card',
                'description': "Award 100 Message Experience points to the user and one random member",
                'reward_text': "Message Experience Points",
                'flavour_text': "~ Eggs, Bacon, Sausage and Spam... ~",
                'show_user': True,
                'user_name': "",
                'function': spam_function
            },

            {
                'card_id': 2,
                'name': "Squire",
                'type': 'card',
                'description': "Award 100 Game Experience points to the user and one random member",
                'reward_text': "Game Experience Points",
                'flavour_text': "~ Squire, attend me! ~",
                'show_user': True,
                'user_name': "",
                'function': npc_function
            },

            {
                'card_id': 3,
                'name': "Booming Voice",
                'type': 'card',
                'description': "Award 100 Voice Experience points to the user and one random member",
                'reward_text': "Voice Experience Points",
                'flavour_text': "~ Winner of every shouting contest. ~",
                'show_user': True,
                'user_name': "",
                'function': booming_voice_function
            },

            {
                'card_id': 4,
                'name': "Pot of Greed",
                'type': 'card',
                'description': "Give the user and one random member 2 random lootboxes",
                'reward_text': "",
                'flavour_text': "~ It's been tournament illegal since 2005. ~",
                'show_user': True,
                'user_name': "",
                'function': pot_of_greed_function
            },

            {
                'card_id': 5,
                'name': "Epic Mage Ring",
                'type': 'card',
                'description': "Give the user and one random member an Epic Lootbox",
                'reward_text': "",
                'flavour_text': "~ Screw the blue staff Jimmy, we're going for the epics. ~",
                'show_user': True,
                'user_name': "",
                'function': epic_mage_ring_function
            },

            {
                'card_id': 6,
                'name': "Stacked Deck",
                'type': 'card',
                'description': "Give the user and one random member a card",
                'reward_text': "A random card.",
                'flavour_text': "~ A great Magician never reveals his trick. ~",
                'show_user': True,
                'user_name': "",
                'function': stacked_deck_function
            }



        ]

    }

}
