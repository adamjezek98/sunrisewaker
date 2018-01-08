import sqlite3
import config

db = sqlite3.connect(config.db_file)
c = db.cursor()
c.execute("""SELECT name FROM sqlite_master WHERE type='table';""")
print(c.fetchall())


db.commit()
c.execute("""CREATE TABLE wakeups
(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT,
    day TEXT,
    hour INT,
    minute INT,
    repeat INT,
    duration INT,
    start_at INT,
    start_at_string TEXT
);
""")
db.commit()
c.execute("""SELECT name FROM sqlite_master WHERE type='table';""")
print(c.fetchall())
