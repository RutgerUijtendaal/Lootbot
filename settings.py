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
    ":lootboxcommon:377958608127918101",
    ":lootboxrare:377958642974064651",
    ":lootboxlegendary:377958669570146305"
]

LOOTBOX_SETTINGS = {
    'instant_loot_counter': 2,      # Instant reward count per lootbox
    'item_loot_counter': 1,         # Item reward count per item chance
    'lootbox_chance': 1,            # Chance is 1/lootbox_chance
    'common_chance': 6,             # Rarity chance form an array to pick from
    'rare_chance': 3,               # Chance for a rarity is rarity_chance/array_length
    'legendary_chance': 1
}
