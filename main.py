#!/usr/local/bin/python3

import json
import logging

from data import constants
from lootbot import Lootbot


description = '''
Cookie clicker within Discord. Do what you normally do and earn points. 
Be lucky and earn a lootbox to earn more points!
'''


def setup_logging():
    logging.getLogger('discord').setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    handler = logging.FileHandler(
        filename='log/Lootbot.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    log.addHandler(handler)
    return log


def load_auth():
    with open('data/auth.json') as data_file:
        return json.load(data_file)


def main():
    log = setup_logging()
    help_attrs = dict(hidden=True)  # Hides the !help description in !help
    bot = Lootbot(command_prefix=constants.BOT_PREFIX, description=description,
                  pm_help=None, help_attrs=help_attrs)
    auth = load_auth()
    discord_token = auth['discord_token']
    bot.client_id = auth['discord_client_id']

    for extension in constants.INITIAL_EXTENSIONS:
        try:
            bot.load_extension(extension)
        except Exception:
            log.exception(f"Failed to load {extension}")

    bot.run(discord_token)


if __name__ == "__main__":
    main()
