-- Role: mfe_citi_rw

-- DROP ROLE mfe_citi_rw;

CREATE ROLE mfe_citi_rw LOGIN
  ENCRYPTED PASSWORD 'md5e10733dfd041b66830398993480b58b2'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
GRANT mfe_citi TO mfe_citi_rw;
