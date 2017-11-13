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
    'instant_loot_counter': 2,      # Instant reward count per lootbox
    'item_loot_counter': 1,         # Item reward count per item chance
    'lootbox_chance': 1,            # Chance is 1/lootbox_chance
    'common_chance': 11,             # Rarity chance form an array to pick from
    'rare_chance': 6,               # Chance for a rarity is rarity_chance/array_length
    'epic_chance': 2,
    'legendary_chance': 1
}
