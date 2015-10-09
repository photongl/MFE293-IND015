import settings, nltk.data, datetime, math, os, urllib
from filing_iterator2 import filings_iterator2
from sklearn.feature_extraction.text import TfidfVectorizer


# some config parameters
year_start = 1997
year_end = 2015
num_features = 10

FEATURES_PATH = "E:\\slo\\"

URL = "http://www.federalreserve.gov/BoardDocs/snloansurvey/200102/default.htm"

for year in range(year_start, year_end + 1):
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



# prepare training data
docs = filings_iterator2(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'))

# train bag-of-words model
vectorizer = TfidfVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = num_features)

train_data_features = vectorizer.fit_transform(docs.get_filing_without_stopwords_from_db())
train_data_features = train_data_features.toarray()

# write out bag of words to file
f = open("E:\\BOW_SLO_FEATURES_{}.csv".format(num_features), 'w')

# Write header
f.write("Date,")
for i in range(1, num_features + 1):
    f.write("feat_{},".format(i))
f.write("year.quarter")
f.write("\n")

# Write data
i = 0
for file in os.listdir("E:\\slo\\"):
    document_features = train_data_features[i, :]
    date_str = file[0:-4]
    f.write("{},".format(date_str))
    for feature in document_features:
        f.write("{},".format(feature))
    f.write("{}-Q{}".format(date_str[0:4], math.ceil(int(date_str[4:6])/3)))
    f.write("\n")
    i = i+1
f.close()

f = open("E:\\FEATURE_SLO_NAMES.csv".format(num_features), 'w')
feature_names = vectorizer.get_feature_names()
for name in feature_names:
    f.write("{}\n".format(name))
f.close()
