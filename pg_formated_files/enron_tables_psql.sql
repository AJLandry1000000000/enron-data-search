-- Dumping structure for table enron.employeelist
CREATE TABLE IF NOT EXISTS employeelist (
  eid SERIAL PRIMARY KEY,
  firstName VARCHAR(31) NOT NULL DEFAULT '',
  lastName VARCHAR(31) NOT NULL DEFAULT '',
  Email_id VARCHAR(31) NOT NULL UNIQUE,
  Email2 VARCHAR(31),
  Email3 VARCHAR(31),
  EMail4 VARCHAR(31),
  folder VARCHAR(31) NOT NULL DEFAULT '',
  status VARCHAR(50)
);

-- Dumping structure for table enron.referenceinfo
CREATE TABLE IF NOT EXISTS referenceinfo (
  rfid INT NOT NULL DEFAULT 0 PRIMARY KEY,
  mid INT NOT NULL DEFAULT 0,
  reference TEXT
);

-- Dumping structure for table enron.recipientinfo
CREATE TABLE IF NOT EXISTS recipientinfo (
  rid INT NOT NULL DEFAULT 0 PRIMARY KEY,
  mid INT NOT NULL DEFAULT 0,
  rtype VARCHAR(3) CHECK (rtype IN ('TO', 'CC', 'BCC')),
  rvalue VARCHAR(127),
  dater TIMESTAMP
);

CREATE INDEX idx_rvalue ON recipientinfo (rvalue);

-- Dumping structure for table enron.message
CREATE TABLE IF NOT EXISTS message (
  mid INT NOT NULL DEFAULT 0 PRIMARY KEY,
  sender VARCHAR(127) NOT NULL DEFAULT '',
  date TIMESTAMP,
  message_id VARCHAR(127),
  subject TEXT,
  body TEXT,
  folder VARCHAR(127) NOT NULL DEFAULT ''
);

CREATE INDEX idx_sender ON message (sender);