import logging
import cogs.utils.messages as messages

log = logging.getLogger(__name__)

# Item functions


async def award_epic_server(bot, member, server, item):

    item['user'] = member.name

    for _member in server.members:
        reward_summary = await bot.create_lootbox_reward(_member, server, epic=1)

        message = messages.create_item_use_message(
            bot.db, member, server, item, reward_summary=reward_summary)

        bot.say_lootbox_channel(message, server)


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

    # Instant rewards are not stored in inventory and applied to the user right away
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

        'item': [
            {
                'item_id': 1,
                'name': "",
                'type': 'item',
                'description': "",
                'reward_text': "",
                'flavour_text': "",
                'show_user': True,
                'user_name': "",
                'function': award_epic_server
            },

            {
                'item_id': 2,
                'name': "",
                'type': 'item',
                'description': "",
                'reward_text': "",
                'flavour_text': "",
                'show_user': True,
                'user_name': "",
                'function': award_epic_server
            },


        ]

    }

}
