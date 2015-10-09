import settings, nltk.data, datetime, math
from filing_iterator import filings_iterator
from sklearn.feature_extraction.text import TfidfVectorizer


# some config parameters
year_start = 2000
year_end = 2015
num_features = 100
N = 26761

# prepare training data
docs = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = N, useDB = True, year_start = year_start, year_end = year_end)

# train bag-of-words model
vectorizer = TfidfVectorizer(analyzer = "word",   \
                             tokenizer = None,    \
                             preprocessor = None, \
                             stop_words = None,   \
                             max_features = num_features)

train_data_features = vectorizer.fit_transform(docs.get_filing_without_stopwords_from_db())
train_data_features = train_data_features.toarray()

# write out bag of words to file
f = open(settings.BASE_PATH + "BOW_FEATURES_{}.csv".format(num_features), 'w')

# Write header
f.write("Name,")
f.write("Date,")
for i in range(1, num_features + 1):
    f.write("feat_{},".format(i))
f.write("year.quarter")
f.write("\n")

# Write data
for i in range(0, N):
    rec = docs.file_list[i].split(sep='_')    
    document_features = train_data_features[i, :]
    f.write("{},".format(rec[0]))
    date_str = rec[3][:-4]
    f.write("{},".format(date_str))
    for feature in document_features:
        f.write("{},".format(feature))
    filing_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")    
    f.write("{}-Q{}".format(filing_date.year, math.ceil(filing_date.month/3)))
    f.write("\n")
f.close()

f = open(settings.BASE_PATH + "FEATURE_NAMES.csv".format(num_features), 'w')
feature_names = vectorizer.get_feature_names()
for name in feature_names:
    f.write("{}\n".format(name))
f.close()
