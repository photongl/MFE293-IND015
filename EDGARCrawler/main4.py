'''
Created on Aug 29, 2015

@author: akshaym
'''
import settings, logging, nltk.data
from filing_iterator import filings_iterator

# some config parameters
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
                    level=logging.INFO)
year_start = 2000
year_end = 2015
n_docs = 1
num_features = 50
model_name = "sec_filings_model_{}.d2v".format(num_features)


# prepare training data
filings_it = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = 9681, useDB = True, year_start = year_start, year_end = year_end)

max_len = 0
for doc in filings_it.get_filing_without_stopwords_from_db():
    if (len(doc) > max_len):
        max_len = len(doc.split(" "))

print(max_len)

