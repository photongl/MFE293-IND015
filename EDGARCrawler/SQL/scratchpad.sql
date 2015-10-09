insert into companies(cik, company_name)
select distinct cik, upper(company_name)
from filing_index;



select c.cik, f.date_filed, f.form_type, f.file_name from companies c, filing_index f where c.cik = f.cik and f.date_filed between (DATE '20111107' - 365) and DATE '20111107'+7 and c.company_name like upper('%Dynegy%')

select distinct c.cik, f.date_filed, f.form_type, f.file_name from companies c, filing_index f where c.cik = f.cik and c.company_name like upper('%ally financial%') order by date_filed

select * from filings where date_filed = '20030814';

select * from companies where company_name like upper('Labarge Inc%')

select * from companies where cik=806085;

select * from filings where form_type = '424B3' limit 100;

select distinct cik from filings;

select count(*) from filings;

select * from filing_index where cik = 1021010


select * from companies where company_name like upper('Vertrue%')

select distinct f.*
from filings f, companies c
where f.cik = c.cik
and c.company_name like upper('%integrated electrical%')
and f.date_filed = (select max(f2.date_filed) from filings f2 where f2.cik = f.cik and f2.form_type = f.form_type)
and f.form_type = '10-Q'
order by f.date_filed