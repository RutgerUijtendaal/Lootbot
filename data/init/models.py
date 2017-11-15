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
                                    season_common_lootbox_count INT DEFAULT 0,
                                    season_rare_lootbox_count INT DEFAULT 0,
                                    season_epic_lootbox_count INT DEFAULT 0,
                                    season_legendary_lootbox_count INT DEFAULT 0,
                                    total_common_lootbox_count INT DEFAULT 0,
                                    total_rare_lootbox_count INT DEFAULT 0,
                                    total_epic_lootbox_count INT DEFAULT 0,
                                    total_legendary_lootbox_count INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                  
                                    )"""

sql_create_counter_table = """ CREATE TABLE IF NOT EXISTS counter (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    message_counter INT DEFAULT 0,
                                    game_counter INT DEFAULT 0,
                                    voice_counter INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""

sql_create_daily_table = """ CREATE TABLE IF NOT EXISTS daily (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    daily_message INT DEFAULT 0,
                                    daily_game INT DEFAULT 0,
                                    daily_voice INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""

sql_create_weekly_table = """ CREATE TABLE IF NOT EXISTS weekly (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    weekly_message INT DEFAULT 0,
                                    weekly_game INT DEFAULT 0,
                                    weekly_voice INT DEFAULT 0,
                                    FOREIGN KEY (member_id, server_id) REFERENCES members(member_id, server_id),
                                    PRIMARY KEY (member_id, server_id)                                   
                                    )"""                                    

sql_create_settings_table = """ CREATE TABLE IF NOT EXISTS settings (
                                    member_id TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    message_mentions INT DEFAULT 0,
                                    message_loot INT DEFAULT 1,
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
    sql_create_counter_table,
    sql_create_daily_table,
    sql_create_weekly_table,
    sql_create_settings_table
]
