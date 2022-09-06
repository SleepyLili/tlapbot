DROP TABLE IF EXISTS points;
DROP TABLE IF EXISTS redeem_queue;

CREATE TABLE points (
  id TEXT PRIMARY KEY,
  name TEXT,
  points INTEGER
);

CREATE TABLE redeem_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  redeem TEXT,
  redeemer_id TEXT,
  FOREIGN KEY (redeemer_id) REFERENCES points (id)
);