'''
Created on Jul 14, 2015

@author: akshaym
'''
import numpy as np
import os
import urllib
from matplotlib import pyplot as plt
from scipy import ndimage
from matplotlib.image import imsave

FEATURES_PATH = "E:\\slo\\"
start_year = 1997
end_year = 2015

URL = "http://www.federalreserve.gov/BoardDocs/snloansurvey/200102/default.htm"

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        date_str = str(year)+str(month).zfill(2)
        final_url = "http://www.federalreserve.gov/BoardDocs/snloansurvey/{}/default.htm".format(date_str)
        print(final_url)

        try:
            filing_text = urllib.request.urlopen(final_url).read().decode('utf-8')
            print(filing_text)
            if (filing_text != ""):
                f = open(FEATURES_PATH + ("{}.txt".format(date_str)), 'w')
                f.write(filing_text)
                f.close()
        except:
            print("EOFError. Retry attempt")

        