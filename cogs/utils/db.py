import os
import time
import datetime
import logging
import sqlite3
from threading import Thread
from queue import Queue

from data import models, constants

log = logging.getLogger(__name__)

# http://amir.rachum.com/blog/2012/04/26/implementing-the-singleton-pattern-in-python/


class SingletonType(type):
    def __call__(cls, *args, **kwargs):
        try:
            return cls.__instance
        except AttributeError:
            cls.__instance = super(
                SingletonType, cls).__call__(*args, **kwargs)
            return cls.__instance

# http://code.activestate.com/recipes/526618/


class Database(Thread, metaclass=SingletonType):

    def __init__(self):
        super().__init__(name='tdatabase')
        log.info("Starting Database")
        self.reqs = Queue()
        sqlite3.register_adapter(datetime.datetime, self.adapt_datetime)
        self.start()

    def run(self):
        try:
            conn = sqlite3.connect(constants.DATABASE_PATH)
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
        if os.path.isfile(constants.DATABASE_PATH):
            pass
        else:
            self.execute(models.sql_create_servers_table)
            self.execute(models.sql_create_members_table)

    def adapt_datetime(self, ts):
        return time.mktime(ts.timetuple())

    # Basic server functions

    def add_server(self, server):

        sql = '''INSERT OR IGNORE INTO servers(server_id, name) VALUES(?,?)'''
        self.execute(sql, (server.id, server.name))

    def add_member(self, member):

        sql = '''INSERT OR IGNORE INTO members(member_id, name, server_id) VALUES(?,?,?)'''
        self.execute(sql, (member.id, member.name, member.server.id))

    # Points functions

    def add_points(self, points, member, server):

        sql_update = '''UPDATE members SET points = points + ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (points, member.id, server.id))

    def get_points(self, member, server):

        sql_retrieve = '''SELECT points FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            points = res
        return points[0]

    def get_all_points(self, server):
        # Returns a dictionary of {name: points} for all users in the server
        ranking = {}
        sql_retrieve = '''SELECT name, points FROM members WHERE server_id = ? ORDER BY points DESC'''
        for res in self.select(sql_retrieve, (server.id,)):
            ranking[res[0]] = res[1]
        return ranking

    # Loot rewards

    def add_consumable_loot(self, column, value, member, server):

        sql_update = ('''UPDATE members SET ''' + column + ''' = ''' +
                      column + ''' + ? WHERE member_id = ? AND server_id = ?''')
        self.execute(sql_update, (value, member.id, server.id))
        log.info("Added %s from %s at %s. Value: %s",
                 column, member.name, server.name, value)

    # General get functions

    def get_message_point_multiplier(self, member, server):

        sql_retrieve = '''SELECT message_point_multiplier FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            message_point_multiplier = res[0]
        return message_point_multiplier

    def get_game_point_multiplier(self, member, server):

        sql_retrieve = '''SELECT game_point_multiplier FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            game_point_multiplier = res[0]
        return game_point_multiplier

    def get_voice_point_multiplier(self, member, server):

        sql_retrieve = '''SELECT voice_point_multiplier FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            voice_point_multiplier = res[0]
        return voice_point_multiplier

    def get_user(self, member, server):
        sql_retrieve = '''SELECT * FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            user = res
        return user

    # Time functions

    def set_game_time(self, member, server):

        now = datetime.datetime.now()
        sql_update = '''UPDATE members SET game_time = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (now, member.id, server.id))

    def get_game_time(self, member, server):

        now = self.adapt_datetime(datetime.datetime.now())
        sql_retrieve = '''SELECT game_time FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            start_time = res[0]
        if start_time != 0:
            return (now - start_time)
        else:
            log.error("Failed to get start time for get_game_time, member: %s, server: %s",
                      member.name, server.name)
            return 0

    def set_voice_time(self, member, server):

        now = datetime.datetime.now()
        sql_update = '''UPDATE members SET voice_time = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (now, member.id, server.id))

    def get_voice_time(self, member, server):

        now = self.adapt_datetime(datetime.datetime.now())
        sql_retrieve = '''SELECT voice_time FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            start_time = res[0]
        if start_time != 0:
            return (now - start_time)
        else:
            log.error("Failed to get start time for get_voice_time, member: %s, server: %s",
                      member.name, server.name)
            return 0

    def set_status_time(self, member, server):

        now = datetime.datetime.now()
        sql_update = '''UPDATE members SET status_time = ? WHERE member_id = ? AND server_id = ?'''
        self.execute(sql_update, (now, member.id, server.id))

    def get_status_time(self, member, server):

        now = self.adapt_datetime(datetime.datetime.now())
        sql_retrieve = '''SELECT status_time FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            start_time = res[0]
        return (now - start_time)

    # Lootbox functions

    def add_lootbox(self, rarity, member, server):

        if 0 <= rarity <= 2:
            # Update current lootbox count
            column = constants.LOOTBOX_DB_RARITY_SELECTION[rarity]
            sql_update = ('''UPDATE members SET ''' + column + ''' = ''' +
                          column + ''' + 1 WHERE member_id = ? AND server_id = ?''')
            self.execute(
                sql_update, (member.id, server.id))
            # Update total lootbox count
            column_total = constants.LOOTBOX_DB_RARITY_SELECTION_TOTAL[rarity]
            sql_update = ('''UPDATE members SET ''' + column_total + ''' = ''' +
                          column_total + ''' + 1 WHERE member_id = ? AND server_id = ?''')
            self.execute(
                sql_update, (member.id, server.id))

            log.info("Added lootbox to %s at %s. Rarity: %s",
                     member.name, server.name, constants.LOOTBOX_STRING_RARITY[rarity])
        else:
            log.error("Failed to add lootbox, rarity: %s, member: %s, server: %s", str(
                rarity), member.name, server.name)

    def add_total_lootbox(self, rarity, member, server):
        if 0 <= rarity <= 2:
            column_total = constants.LOOTBOX_DB_RARITY_SELECTION_TOTAL[rarity]
            sql_update = ('''UPDATE members SET ''' + column_total + ''' = ''' +
                          column_total + ''' + 1 WHERE member_id = ? AND server_id = ?''')
            self.execute(
                sql_update, (member.id, server.id))
        else:
            log.error("Failed to add total lootbox, rarity: %s, member: %s, server: %s", str(
                rarity), member.name, server.name)

    def remove_lootbox(self, rarity, member, server):

        all_lootboxes = self.get_all_lootboxes(member, server)
        # Make sure rarity is valid and there's a box to remove from the user
        if 0 <= rarity <= 2 and all_lootboxes[rarity] > 0:
            column = constants.LOOTBOX_DB_RARITY_SELECTION[rarity]
            sql_update = ('''UPDATE members SET ''' + column + ''' = ''' +
                          column + ''' - 1 WHERE member_id = ? AND server_id = ?''')
            self.execute(
                sql_update, (member.id, server.id))

            log.info("Removed lootbox from %s at %s. Rarity: %s",
                     member.name, server.name, constants.LOOTBOX_STRING_RARITY[rarity])
        else:
            log.error("Failed to remove lootbox, rarity: %s, member: %s, server: %s", str(
                rarity), member.name, server.name)

    def get_all_lootboxes(self, member, server):
        # Returns a tuple (x, y, z) of lootbox counts for the user
        sql_retrieve = '''SELECT common_lootbox_count, rare_lootbox_count, leg_lootbox_count FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            all_lootboxes = res
        return all_lootboxes

    # User Settings

    def set_auto_open(self, member, server, auto_open):

        if self.get_auto_open(member, server) != auto_open:
            sql_update = '''UPDATE members SET auto_open = ? WHERE member_id = ? AND server_id = ?'''
            self.execute(sql_update, (auto_open, member.id, server.id))
        else:
            log.error("Auto_open was already set to %s for user %s at %s", str(
                auto_open), member.name, server.name)

    def get_auto_open(self, member, server):

        sql_retrieve = '''SELECT auto_open FROM members WHERE member_id = ? AND server_id = ?'''
        for res in self.select(sql_retrieve, (member.id, server.id)):
            auto_open = res[0]
        if auto_open:
            return True
        return False
