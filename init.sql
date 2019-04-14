-- DROP DATABASE IF EXISTS api;

-- CREATE DATABASE api;

DROP TABLE IF EXISTS pf_ip_ban
DROP TABLE IF EXISTS users

CREATE TABLE pf_ip_ban (id SERIAL PRIMARY KEY, ip INET, updated_at timestamp without time zone, source character varying);
-- INSERT INTO pf_ip_ban (ip, updated_at, source)
-- VALUES ('209.229.0.0/16', '2019-04-07 11:11:25-07', 'emerging');


CREATE TABLE users (user TEXT, password TEXT, active INTEGER);
INSERT INTO users VALUES (test, 8d604831, 1);
-- INSERT INTO users VALUES (test, 8d604831-623a-4e1b-b82a-618d82b18d5a, 1);

