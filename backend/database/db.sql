PRAGMA foreign_keys = ON;

CREATE TABLE user (
    user_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL UNIQUE
);

CREATE TABLE history (
    history_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    ip_addr TEXT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE password (
    pass_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    pass_hash TEXT NOT NULL,
    mfg_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

-- CREATE TABLE live (
--     live_id TEXT PRIMARY KEY,
--     user_id TEXT NOT NULL,
--     live_ip TEXT NOT NULL,
--     live_token TEXT NOT NULL UNIQUE,
--     created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
--     expires_at DATETIME NOT NULL,
--     FOREIGN KEY (user_id) REFERENCES user(user_id)
-- );