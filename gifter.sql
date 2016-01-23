-- Table definitions for gifter (catalog project).

-- Uncomment lines below if needed
-- CREATE DATABASE gifter;
-- \c gifter;

-- Drop old tables
DROP TABLE IF EXISTS givers CASCADE;
DROP TABLE IF EXISTS recipients CASCADE;
DROP TABLE IF EXISTS gifts;

-- Create tables
CREATE TABLE givers ( 
  id        SERIAL PRIMARY KEY,
  name      VARCHAR(80) NOT NULL,
  email     VARCHAR(80) NOT NULL,
  picture   VARCHAR(250) 
);

CREATE TABLE recipients ( 
  id        SERIAL PRIMARY KEY,
  name      VARCHAR(80) NOT NULL,
  bday      VARCHAR(20),
  sizes     VARCHAR(30),
  giver_id  INT REFERENCES givers(id)
);

CREATE TABLE gifts ( 
  id            SERIAL PRIMARY KEY,
  name          VARCHAR(80) NOT NULL,
  description   VARCHAR(250),
  link          VARCHAR(250),
  image         VARCHAR(250),
  status        VARCHAR(10),
  date_added    DATE NOT NULL,
  date_given    DATE,
  giver_id      INT REFERENCES givers(id),
  rec_id        INT REFERENCES recipients(id)
);
