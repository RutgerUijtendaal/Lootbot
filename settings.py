#!/usr/local/bin/python3

# Program
LOG_LEVEL = 'INFO'

# Database
DATABASE_PATH = "data/lootbot.db"

# Bot

TRELLO_LINK = "https://trello.com/b/s52Fqf4L/lootbot"
DESIGN_LINK = "https://docs.google.com/document/d/15CvsTLqlmZnjCEmZk3KYvYLlhpGEZPiwtM23TEF6enE/edit?usp=sharing"
GITHUB_LINK = "https://github.com/RutgerUijtendaal/Lootbot"

BOT_PREFIX = "$"
BOT_CHANNEL = "lootbot"

OWNER_ID = "186546645465432065"

INITIAL_EXTENSIONS = (
    "cogs.cards",
    "cogs.user",
    "cogs.bot",
    "cogs.quests",
)


# Experience

LEVEL_BASE = 100

# Lootbox

LOOTBOX_EMOJI = [
    # TODO: Create on join server and use those instead
    ":lootbox_common:381118736914186250",
    ":lootbox_rare:381118738373541888",
    ":lootbox_epic:381118737966956544",
    ":lootbox_legendary:381118737849384961"
]

LOOTBOX_SETTINGS = {
    'loot_counter': 2,              # Instant reward count per lootbox
    'card_loot_counter': 1,         # Item reward count per card chance
    'lootbox_chance': 1,            # Chance is 1/lootbox_chance
    'pity_modifier': 0.94,          # Create a curve to inc drop chance with pity timer
    'boxes_modifier': 1.05,
    'common_chance': 10,            # Rarity chance form an array to pick from
    'rare_chance': 6,               # Chance for a rarity is rarity_chance/array_length
    'epic_chance': 3,
    'legendary_chance': 1
}

# Messages

MESSAGE_TIMER = 3

# Game

GAME_TIMER = 120                     # Time in seconds to award users for being in game

GAMES_CHECK_WHITELIST = False
GAMES_WHITELIST = [
    'Overwatch',
    'Hearthstone',
    'Warframe'
]

# Voice

VOICE_TIMER = 60

# deck

DECK_SIZE = 5
