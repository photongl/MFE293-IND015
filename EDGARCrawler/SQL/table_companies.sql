-- Table: companies

-- DROP TABLE companies;

CREATE TABLE companies
(
  id serial NOT NULL,
  cik bigint,
  company_name text,
  CONSTRAINT companies_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE companies
  OWNER TO postgres;
GRANT ALL ON TABLE companies TO postgres;
GRANT ALL ON TABLE companies TO mfe_citi;

-- Index: idx_cik

-- DROP INDEX idx_cik;

CREATE INDEX idx_cik
  ON companies
  USING btree
  (cik);

-- Index: idx_cmp_name

-- DROP INDEX idx_cmp_name;

CREATE INDEX idx_cmp_name
  ON companies
  USING btree
  (company_name COLLATE pg_catalog."default");

