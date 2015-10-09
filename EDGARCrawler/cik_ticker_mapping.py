import re
import urllib.request
 
URL = 'http://www.sec.gov/cgi-bin/browse-edgar?company={}&Find=Search&owner=exclude&action=getcompany'
CIK_RE = re.compile(r'.*CIK=(\d{10}).*')


def get_cik(tickers): 
    cik_dict = {}
    for ticker in tickers:
        results = CIK_RE.findall(urllib.request.urlopen(URL.format(ticker)).read().decode('utf=8'))
        if len(results):
            cik_dict[str(ticker).lower()] = str(results[0])
    return cik_dict