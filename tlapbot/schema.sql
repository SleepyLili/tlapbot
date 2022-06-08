DROP TABLE IF EXISTS points;

CREATE TABLE points (
  id TEXT PRIMARY KEY,
  username TEXT NOT NULL,
  points INTEGER
);