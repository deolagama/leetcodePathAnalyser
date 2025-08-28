CREATE TABLE IF NOT EXISTS problems (
  problem_id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  difficulty INTEGER NOT NULL,
  concepts TEXT NOT NULL, -- JSON array
  url TEXT
);
CREATE TABLE IF NOT EXISTS attempts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id TEXT NOT NULL,
  problem_id TEXT NOT NULL,
  ts TEXT NOT NULL,
  outcome INTEGER NOT NULL, -- 0/1
  attempts INTEGER,
  minutes INTEGER,
  used_hint INTEGER DEFAULT 0,
  FOREIGN KEY(problem_id) REFERENCES problems(problem_id)
);