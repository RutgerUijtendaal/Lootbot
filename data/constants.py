

# Bot config

INITIAL_EXTENSIONS = (
    "cogs.lootbot",
    "cogs.lootbox",
    "cogs.ranking",
    "cogs.user",
)

BOT_PREFIX = '$'
BOT_CHANNEL = "lootbot"

TRELLO_LINK = "https://trello.com/b/s52Fqf4L/lootbot"
DESIGN_LINK = "https://docs.google.com/document/d/15CvsTLqlmZnjCEmZk3KYvYLlhpGEZPiwtM23TEF6enE/edit?usp=sharing"
GITHUB_LINK = "https://github.com/RutgerUijtendaal/Lootbot"

# Database

DATABASE_PATH = 'lootbot.db'

# Base point rewards for different actions

BASE_MESSAGE_POINTS = 1
BASE_GAME_POINTS = 2
BASE_VOICE_POINTS = 2

# Time in seconds for how often a points can be award

VOICE_POINT_TIME = 300
GAME_POINT_TIME = 300

# Lootbox rarity columns for DB (Common, Rare, Legendary)

LOOTBOX_DB_RARITY_SELECTION = ("common_lootbox_count",
                               "rare_lootbox_count",
                               "leg_lootbox_count")

LOOTBOX_DB_RARITY_SELECTION_TOTAL = ("total_common_lootbox_count",
                                     "total_rare_lootbox_count",
                                     "total_leg_lootbox_count")

LOOTBOX_DB_LOOT_SELECTION = ("message_point_multiplier",
                             "game_point_multiplier",
                             "voice_point_multiplier",
                             "points")

LOOTBOX_STRING_RARITY = ("common", "rare", "legendary")

# Lootbox emoji tuple (Common, Rare, Legendary)


LOOTBOX_EMOJI = ("\U0001F949", "\U0001F948", "\U0001F947")


# Time in seconds for how often a lootbox can be award

VOICE_LOOTBOX_TIME = 60
GAME_LOOTBOX_TIME = 60

# Lootbox chance is ( loot_chance / loottable_max_length)

LOOTTABLE_MAX_LENGTH = 1000

COMMON_LOOTBOX_CHANCE = 10
RARE_LOOTBOX_CHANCE = 5
LEG_LOOTBOX_CHANCE = 2
