-- Table: filings

-- DROP TABLE filings;

CREATE TABLE filings
(
  cik bigint NOT NULL,
  date_filed date NOT NULL,
  filing text,
  form_type text NOT NULL,
  filing_id text NOT NULL,
  CONSTRAINT filings_pkey PRIMARY KEY (filing_id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE filings
  OWNER TO postgres;
GRANT ALL ON TABLE filings TO postgres;
GRANT ALL ON TABLE filings TO mfe_citi;

-- Index: filings_cik_date_filed_form_type_idx

-- DROP INDEX filings_cik_date_filed_form_type_idx;

CREATE INDEX filings_cik_date_filed_form_type_idx
  ON filings
  USING btree
  (cik, date_filed, form_type COLLATE pg_catalog."default");

