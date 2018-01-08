CREATE TABLE wakeups
(
    id INTEGER PRIMARY KEY AUTO_INCREMENT NOT NULL,
    name TEXT,
    day TEXT,
    hour INT,
    minute INT,
    repeat INT,
    duration INT,
    start_at INT,
    start_at_string TEXT
);
