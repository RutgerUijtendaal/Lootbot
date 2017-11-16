QUESTS = {
    'daily': [
        {
            'name': "Hello World",
            'type': 'daily',
            'description': "Type your first message of the day",
            'goal_value': 1,
            'reward_type': 'lootbox',
            'reward_rarity': 'common',
            'reward_count': 1,
            'database': 'daily_message'
        },

        {
            'name': "A Game A Day",
            'type': 'daily',
            'description': "Play 30 minutes of a game",
            'goal_value': 30,
            'reward_type': 'lootbox',
            'reward_rarity': 'rare',
            'reward_count': 1,
            'database': 'daily_game'
        },

        {
            'name': "We Need To Talk",
            'type': 'daily',
            'description': "Spend 15 minutes in voice chat with someone else",
            'goal_value': 15,
            'reward_type': 'lootbox',
            'reward_rarity': 'rare',
            'reward_count': 1,
            'database': 'daily_voice'
        }


    ],

    'weekly': [
        {
            'name': "World Wants You To Slow Down",
            'type': 'weekly',
            'description': "Type 200 messages",
            'goal_value': 200,
            'reward_type': 'lootbox',
            'reward_rarity': 'epic',
            'reward_count': 1,
            'database': 'weekly_message'
        },

        {
            'name': "Just One More Turn",
            'type': 'weekly',
            'description': "Play games for 6 hours",
            'goal_value': 360,
            'reward_type': 'lootbox',
            'reward_rarity': 'epic',
            'reward_count': 1,
            'database': 'weekly_game'
        },

        {
            'name': "Ok enough chit-chat",
            'type': 'weekly',
            'description': "Spend two hours in voice chat with someone else",
            'goal_value': 120,
            'reward_type': 'lootbox',
            'reward_rarity': 'legendary',
            'reward_count': 1,
            'database': 'weekly_voice'
        }
    ],

    'achievements': [
        {

        }
    ]

}
