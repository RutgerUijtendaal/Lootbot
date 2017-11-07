sql_create_servers_table = """ CREATE TABLE IF NOT EXISTS servers (
                                    server_id TEXT PRIMARY KEY,
                                    name TEXT NOT NULL
                                    )"""

sql_create_members_table = """ CREATE TABLE IF NOT EXISTS members (
                                    member_id TEXT NOT NULL,
                                    name TEXT NOT NULL,
                                    server_id TEXT NOT NULL,
                                    points INTEGER DEFAULT 0,
                                    message_point_multiplier INTEGER DEFAULT 1,
                                    game_point_multiplier INTEGER DEFAULT 1,
                                    voice_point_multiplier INTEGER DEFAULT 1,
                                    common_lootbox_count INT DEFAULT 0,
                                    rare_lootbox_count INT DEFAULT 0,
                                    leg_lootbox_count INT DEFAULT 0,
                                    total_common_lootbox_count INT DEFAULT 0,
                                    total_rare_lootbox_count INT DEFAULT 0,
                                    total_leg_lootbox_count INT DEFAULT 0,
                                    game_time INT DEFAULT 0,
                                    voice_time INT DEFAULT 0,
                                    auto_open INTEGER DEFAULT 1,
                                    FOREIGN KEY (server_id) REFERENCES servers(server_id),
                                    PRIMARY KEY (member_id, server_id)
                                    )"""
