import PopulateDB, settings

year_start = 2000
year_end = 2015

f = open(settings.BASE_PATH + settings.COMPANY_CIK_SP500)
lines = f.readlines()    
f.close()

for line in lines:
    fields = [field.strip() for field in line.split(sep = ',')]
    ticker = fields[0]
    company_cik = str(int(fields[2]))
    #PopulateDB.populate_filing_for_company(company_cik, True, '{}_{}'.format(ticker, company_cik), year_start, year_end)
    PopulateDB.populate_filing_for_company(company_cik, ticker, True, '{}_{}'.format(ticker, company_cik), year_start, year_end)