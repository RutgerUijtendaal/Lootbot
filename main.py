#!/usr/local/bin/python3

import json
import logging

import settings
from lootbot import Lootbot


description = '''
Cookie clicker within Discord. Do what you normally do and earn points. 
Be lucky and earn a lootbox to earn more points!
'''

initial_extensions = {

}


def setup_logging():
    # Set up discord logging levels
    logging.getLogger('discord').setLevel(logging.INFO)
    logging.getLogger('discord.http').setLevel(logging.WARNING)
    # Set program logging level
    log = logging.getLogger()
    level = logging.getLevelName(settings.LOG_LEVEL)
    log.setLevel(level)
    # Set file location and formatting
    handler = logging.FileHandler(
        filename='log/lootbot.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    log.addHandler(handler)
    return log


def load_auth():
    with open('data/init/auth.json') as data_file:
        return json.load(data_file)


def main():
    log = setup_logging()
    help_attrs = dict(hidden=True)  # Hides the !help description in !help
    bot = Lootbot(command_prefix=settings.BOT_PREFIX, description=description,
                  pm_help=None, help_attrs=help_attrs)
    auth = load_auth()
    discord_token = auth['debug_token']
    bot.client_id = auth['debug_client_id']

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception:
            log.exception(f"Failed to load {extension}")

    bot.run(discord_token)


if __name__ == "__main__":
    main()
