sql_create_server_table = """ CREATE TABLE IF NOT EXISTS server (
                                    server_id TEXT PRIMARY KEY,
                                    name TEXT NOT NULL
                                    )"""

sql_create_member_table = """ CREATE TABLE IF NOT EXISTS member (
                                    member_id TEXT NOT NULL,
                                    name TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    experience INTEGER DEFAULT 0,
                                    level INTEGER DEFAULT 1,
                                    rested INTEGER DEFAULT 0,
                                    FOREIGN KEY (server_id) REFERENCES servers(server_id),
                                    PRIMARY KEY (member_id, server_id)
                                    )"""

sql_create_multiplier_table = """ CREATE TABLE IF NOT EXISTS multiplier (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    message_multiplier INTEGER DEFAULT 1,
                                    game_multiplier INTEGER DEFAULT 1,
                                    voice_multiplier INTEGER DEFAULT 1,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""

sql_create_lootbox_table = """ CREATE TABLE IF NOT EXISTS lootbox (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    total_common_lootbox_count INT DEFAULT 0,
                                    total_rare_lootbox_count INT DEFAULT 0,
                                    total_leg_lootbox_count INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                  
                                    )"""

sql_create_time_table = """ CREATE TABLE IF NOT EXISTS time (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    game_time INT DEFAULT 0,
                                    voice_time INT DEFAULT 0,
                                    message_time INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""

sql_create_daily_table = """ CREATE TABLE IF NOT EXISTS daily (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    first_random_lootbox INT DEFAULT 0,
                                    first_game INT DEFAULT 0,
                                    first_voice INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""

sql_create_settings_table = """ CREATE TABLE IF NOT EXISTS settings (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    message_mentions INT DEFAULT 0,
                                    message_loot INT DEFAULT 0,
                                    message_multipliers INT DEFAULT 1,
                                    message_score INT DEFAULT 1,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                               
                                    )"""

table_creation = [
    sql_create_server_table,
    sql_create_member_table,
    sql_create_multiplier_table,
    sql_create_lootbox_table,
    sql_create_time_table,
    sql_create_daily_table,
    sql_create_settings_table
]
