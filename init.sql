-- DROP DATABASE IF EXISTS api;

-- CREATE DATABASE api;

DROP TABLE IF EXISTS pf_ip_ban;
CREATE TABLE pf_ip_ban (id SERIAL PRIMARY KEY, ip CIDR UNIQUE, updated_at timestamp without time zone, source character varying);
INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('209.229.0.0/16', '2019-04-07 11:11:25-07', 'emerging');
INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('219.229.0.2', '2019-04-14 11:11:25-07', 'emerging');

ALTER TABLE pf_ip_ban OWNER TO api;

DROP TABLE IF EXISTS users
CREATE TABLE users (api_user character varying, password character varying, active INTEGER);
INSERT INTO users VALUES ('test', '8d604831', 1);
-- INSERT INTO users VALUES (test, 8d604831-623a-4e1b-b82a-618d82b18d5a, 1);

ALTER TABLE users OWNER TO api;
