-- DROP DATABASE IF EXISTS api;

-- CREATE DATABASE api;

DROP TABLE IF EXISTS pf_ip_ban;
CREATE TABLE pf_ip_ban (id SERIAL PRIMARY KEY, ip CIDR UNIQUE, updated_at timestamp without time zone, source character varying);
INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('209.229.0.0/16', '2019-04-07 11:11:25-07', 'emerging');
INSERT INTO pf_ip_ban (ip, updated_at, source) VALUES ('219.229.0.2', '2019-04-14 11:11:25-07', 'emerging');

ALTER TABLE pf_ip_ban OWNER TO api;

DROP TABLE IF EXISTS users;
CREATE TABLE users (api_user character varying UNIQUE, password character varying, active INTEGER);
INSERT INTO users VALUES ('test', '8d604831', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('virtie.chown.me', 'e6f2a131-9b00-4735-90c7-e0f4f4e561f1', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('db0.chown.me', '9a4be1ec-04e0-4f15-95e8-92138767216a', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('web0.chown.me', '8356154e-18e9-4569-98d9-84e2b3eb11d4', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('ns3.chown.me', '86022c19-f9e1-4108-ac67-e70f191ab219', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('manicouagan.chown.me', '72010c86-18ab-46a5-8517-07c1027928e1', 1);
INSERT INTO USERS (api_user, password, active) VALUES ('pancake.chown.me', 'fa2a12b2-b51f-4782-ba52-da3056aebb72', 1);

ALTER TABLE users OWNER TO api;
