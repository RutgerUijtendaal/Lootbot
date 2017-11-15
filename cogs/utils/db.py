import os
import time
import datetime
import logging
import sqlite3
from threading import Thread
from queue import Queue

import settings
from data.init import models

log = logging.getLogger(__name__)

# http://amir.rachum.com/blog/2012/04/26/implementing-the-singleton-pattern-in-python/
# Create a singleton class as a metaclass to only allow one instance of the database thread to be active


class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(
                SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

# http://code.activestate.com/recipes/526618/
# Run the database in a seperate thread to make sure accessing doesn't block the rest of the program


class Database(Thread, metaclass=SingletonType):

    def __init__(self):
        super().__init__(name='database')
        log.info("Starting Database")
        self.reqs = Queue()
        sqlite3.register_adapter(datetime.datetime, self.adapt_datetime)
        self.start()

    def run(self):
        try:
            conn = sqlite3.connect(settings.DATABASE_PATH)
            cursor = conn.cursor()
        except sqlite3.Error as e:
            log.error(e)

        while True:
            req, arg, res = self.reqs.get()
            if req == '--close--':
                break
            try:
                cursor.execute(req, arg)
            except Exception as e:
                print(e)
            conn.commit()
            if res:
                for rec in cursor:
                    res.put(rec)
                res.put('--no more--')
        conn.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def select(self, req, arg=None):
        res = Queue()
        self.execute(req, arg, res)
        while True:
            rec = res.get()
            if rec == '--no more--':
                break
            yield rec

    def close(self):
        self.execute('--close--')

    def create_database(self):
        if os.path.isfile(settings.DATABASE_PATH):
            pass
        else:
            for sql in models.table_creation:
                self.execute(sql)

    def adapt_datetime(self, ts):
        return time.mktime(ts.timetuple())

    # Server

    def add_server(self, server):

        sql = '''INSERT OR IGNORE INTO server(server_id, name) VALUES(?,?)'''
        self.execute(sql, (server.id, server.name))

    def get_all_servers(self):
        pass

    # Member

    def add_member(self, member):

        sql = '''INSERT OR IGNORE INTO member(member_id, name, server_id) VALUES(?,?,?)'''
        self.execute(sql, (member.id, member.name, member.server.id))
        sql = '''INSERT OR IGNORE INTO multiplier(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))
        sql = '''INSERT OR IGNORE INTO lootbox(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))
        sql = '''INSERT OR IGNORE INTO counter(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))
        sql = '''INSERT OR IGNORE INTO daily(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))
        sql = '''INSERT OR IGNORE INTO weekly(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))
        sql = '''INSERT OR IGNORE INTO settings(member_id, server_id) VALUES(?,?)'''
        self.execute(sql, (member.id, member.server.id))

    def update_experience(self, member, server, experience):
        sql_update = '''UPDATE member SET experience = experience + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (experience, member.id, server.id))

    def set_level(self, member, server, level):
        sql_update = '''UPDATE member SET level = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (level, member.id, server.id))

    def get_member_progress(self, member, server):
        sql_retrieve = '''SELECT level, experience FROM member WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            progress = res
        return progress

    # Lootboxes

    def get_season_lootbox(self, member, server):
        sql_retrieve = ('''SELECT season_common_lootbox_count,
                                  season_rare_lootbox_count,
                                  season_epic_lootbox_count,
                                  season_legendary_lootbox_count 
                           FROM lootbox 
                           WHERE member_id = ? AND server_id = ?''')
        for res in self.select(sql_retrieve, (member.id, server.id)):
            season_lootboxes = res
        return season_lootboxes

    def get_total_lootbox(self, member, server):
        sql_retrieve = ('''SELECT total_common_lootbox_count,
                                  total_rare_lootbox_count,
                                  total_epic_lootbox_count,
                                  total_legendary_lootbox_count 
                           FROM lootbox 
                           WHERE member_id = ? AND server_id = ?''')
        for res in self.select(sql_retrieve, (member.id, server.id)):
            season_lootboxes = res
        return season_lootboxes

    def add_lootbox(self, member, server, rarity):
        if rarity == 'common':
            sql_update = ('''UPDATE lootbox 
                            SET season_common_lootbox_count = season_common_lootbox_count + 1,
                                total_common_lootbox_count = total_common_lootbox_count + 1
                            WHERE member_id = ? AND server_id = ? ''')
        if rarity == 'rare':
            sql_update = ('''UPDATE lootbox 
                            SET season_rare_lootbox_count = season_rare_lootbox_count + 1,
                                total_rare_lootbox_count = total_rare_lootbox_count + 1
                            WHERE member_id = ? AND server_id = ? ''')
        if rarity == 'epic':
            sql_update = ('''UPDATE lootbox 
                            SET season_epic_lootbox_count = season_epic_lootbox_count + 1,
                                total_epic_lootbox_count = total_epic_lootbox_count + 1
                            WHERE member_id = ? AND server_id = ? ''')
        if rarity == 'legendary':
            sql_update = ('''UPDATE lootbox 
                            SET season_legendary_lootbox_count = season_legendary_lootbox_count + 1,
                                total_legendary_lootbox_count = total_legendary_lootbox_count + 1
                            WHERE member_id = ? AND server_id = ? ''')
        self.execute(sql_update, (member.id, server.id))

    # Multipliers

    def update_message_multiplier(self, member, server, multiplier):
        sql_update = '''UPDATE multiplier SET message_multiplier = message_multiplier + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (multiplier, member.id, server.id))

    def update_game_multiplier(self, member, server, multiplier):
        sql_update = '''UPDATE multiplier SET game_multiplier = game_multiplier + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (multiplier, member.id, server.id))

    def update_voice_multiplier(self, member, server, multiplier):
        sql_update = '''UPDATE multiplier SET voice_multiplier = voice_multiplier + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (multiplier, member.id, server.id))

    def get_message_multiplier(self, member, server):

        sql_retrieve = '''SELECT message_multiplier FROM multiplier WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            message_point_multiplier = res[0]
        return message_point_multiplier

    def get_game_multiplier(self, member, server):

        sql_retrieve = '''SELECT game_multiplier FROM multiplier WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            game_point_multiplier = res[0]
        return game_point_multiplier

    def get_voice_multiplier(self, member, server):

        sql_retrieve = '''SELECT voice_multiplier FROM multiplier WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            voice_point_multiplier = res[0]
        return voice_point_multiplier

    def get_multipliers(self, member, server):

        sql_retrieve = '''SELECT message_multiplier, game_multiplier, voice_multiplier FROM multiplier WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            multipliers = res
        return multipliers

    # Counters

    def get_counters(self, member, server):
        sql_retrieve = '''SELECT message_counter, game_counter, voice_counter FROM counter WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            counters = res
        return counters

    def set_message_counter(self, member, server, message_counter):

        sql_update = '''UPDATE counter SET message_counter = message_counter + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (message_counter, member.id, server.id))

    def set_game_counter(self, member, server, game_counter):

        sql_update = '''UPDATE counter SET game_counter = game_counter + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (game_counter, member.id, server.id))

    def set_voice_counter(self, member, server, voice_counter):

        sql_update = '''UPDATE counter SET voice_counter = voice_counter + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (voice_counter, member.id, server.id))

    def reset_counters(self):
        sql_update = (''' UPDATE counter
                          SET   message_counter = 0, 
                                game_counter = 0,
                                voice_counter = 0, ''')
        self.execute(sql_update)

    # Dailies

    def get_dailies(self, member, server):
        sql_retrieve = '''SELECT daily_message, daily_game, daily_voice FROM daily WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            dailies = res
        return dailies

    def set_daily(self, member, server, column, completed):

        sql_update = '''UPDATE daily SET ''' + column + \
            ''' = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (completed, member.id, server.id))

    def reset_dailies(self):
        sql_update = (''' UPDATE daily
                          SET   daily_message= 0,
                                daily_game = 0,
                                daily_voice = 0 ''')
        self.execute(sql_update)

    # Weeklies

    def get_weeklies(self, member, server):
        sql_retrieve = '''SELECT weekly_message, weekly_game, weekly_voice FROM weekly WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            weeklies = res
        return weeklies

    def set_weekly(self, member, server, column, completed):

        sql_update = '''UPDATE weekly SET ''' + column + \
            ''' = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (completed, member.id, server.id))

    def reset_weeklies(self):
        sql_update = (''' UPDATE weekly
                          SET   weekly_message = 0,
                                weekly_game = 0,
                                weekly_voice = 0 ''')
        self.execute(sql_update)

    # User Settings

    def set_message_mentions(self, member, server, mentions):

        if self.get_message_settings(member, server)[0] != mentions:
            sql_update = '''UPDATE settings SET message_mentions = ? WHERE member_id = ? AND server_id = ?'''
            self.execute(sql_update, (mentions, member.id, server.id))
        else:
            log.error("Mentions was already set to %s for user %s at %s", str(
                mentions), member.name, server.name)

    def set_message_loot(self, member, server, loot):

        if self.get_message_settings(member, server)[1] != loot:
            sql_update = '''UPDATE settings SET message_loot = ? WHERE member_id = ? AND server_id = ?'''
            self.execute(sql_update, (loot, member.id, server.id))
        else:
            log.error("loot was already set to %s for user %s at %s", str(
                loot), member.name, server.name)

    def set_message_multipliers(self, member, server, multipliers):

        if self.get_message_settings(member, server)[2] != multipliers:
            sql_update = '''UPDATE settings SET message_multipliers = ? WHERE member_id = ? AND server_id = ?'''
            self.execute(sql_update, (multipliers, member.id, server.id))
        else:
            log.error("multipliers was already set to %s for user %s at %s", str(
                multipliers), member.name, server.name)

    def set_message_score(self, member, server, score):

        if self.get_message_settings(member, server)[3] != score:
            sql_update = '''UPDATE settings SET message_score = ? WHERE member_id = ? AND server_id = ?'''
            self.execute(sql_update, (score, member.id, server.id))
        else:
            log.error("score was already set to %s for user %s at %s", str(
                score), member.name, server.name)

    def get_message_settings(self, member, server):

        sql_retrieve = '''SELECT message_mentions, message_loot, message_multipliers, message_score FROM settings WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            message_settings = res
        return message_settings
