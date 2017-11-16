# Program
LOG_LEVEL = 'INFO'

# Database
DATABASE_PATH = "data/lootbot.db"

# Bot
BOT_PREFIX = "$"
BOT_CHANNEL = "lootbot"

# Experience

LEVEL_BASE = 100

# Lootbox

LOOTBOX_EMOJI = [
    # TODO: Create on join server and use those instead
    ":lootbox_common:379684019564183552",
    ":lootbox_rare:379684022751723541",
    ":lootbox_epic:379684022093217793",
    ":lootbox_legendary:379684021820456960"
]

LOOTBOX_SETTINGS = {
    'loot_counter': 2,              # Instant reward count per lootbox
    'item_loot_counter': 1,         # Item reward count per item chance
    'lootbox_chance': 1,            # Chance is 1/lootbox_chance
    'pity_modifier': 0.94,          # Create a curve to inc drop chance with pity timer
    'boxes_modifier': 1.05,
    'common_chance': 0, #12,            # Rarity chance form an array to pick from
    'rare_chance': 0, #7,               # Chance for a rarity is rarity_chance/array_length
    'epic_chance': 0, #2,
    'legendary_chance': 1
}

# Game

GAME_TIMER = 60                     # Time in seconds to award users for being in game

GAMES_CHECK_WHITELIST = False
GAMES_WHITELIST = [
    'Overwatch',
    'Hearthstone',
    'Warframe'
]

# Voice

VOICE_TIMER = 60

# Inventory

INVENTORY_SIZE = 5
