import urllib.request, settings

url_template = "ftp://ftp.sec.gov/edgar/full-index/"

def get_EDGAR_index_files():
    for year in range(settings.START_YEAR, settings.END_YEAR + 1):
        for i in range(1,5):
            full_url = url_template + str(year) + '/QTR'+ str(i) + '/company.zip'
            print('Downloading ' + full_url + '...')
            filename = 'company_index_' + str(year) + 'Q' + str(i) + '.zip'
            urllib.request.urlretrieve(full_url, settings.BASE_PATH + filename)
            print('Downloaded ' + filename)
