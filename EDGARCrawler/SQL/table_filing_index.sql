-- Table: filing_index

-- DROP TABLE filing_index;

CREATE TABLE filing_index
(
  cik bigint NOT NULL,
  company_name text NOT NULL,
  date_filed date NOT NULL,
  form_type text NOT NULL,
  file_name text NOT NULL,
  CONSTRAINT filing_index_pkey PRIMARY KEY (cik, date_filed, form_type, file_name)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE filing_index
  OWNER TO postgres;
GRANT ALL ON TABLE filing_index TO postgres;
GRANT ALL ON TABLE filing_index TO mfe_citi;

-- Index: "company_idx_CompanyName_idx"

-- DROP INDEX "company_idx_CompanyName_idx";

CREATE INDEX "company_idx_CompanyName_idx"
  ON filing_index
  USING btree
  (company_name COLLATE pg_catalog."default");

