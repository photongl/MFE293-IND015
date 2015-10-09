import settings, logging, nltk.data, math, datetime
from filing_iterator import filings_iterator
from gensim.models import doc2vec

# some config parameters
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
                    level=logging.INFO)
year_start = 2000
year_end = 2015
num_features = 100
model_name = "sec_filings_model_{}.d2v".format(num_features)


# prepare training data
sentences = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = 10000, useDB = True, year_start = year_start, year_end = year_end)

model = doc2vec.Doc2Vec(sentences, 
                        size = num_features,
                        min_count = 1,
                        seed = 5,
                        window = 20,
                        sample = 1e-3,
                        #hashfxn = analyze.hash32
                        workers = 4)

#model.init_sims(replace=True)
#model.save(model_name)

# ==============================================================
# retrieve features for each document and store them in a file
# ==============================================================
sentences = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = 26761, useDB = True, year_start = year_start, year_end = year_end)
f = open(settings.BASE_PATH + "FILING_FEATURES_{}.csv".format(num_features), 'w')

# Write header
f.write("Name,")
f.write("Date,")
for i in range(1, num_features + 1):
    f.write("feat_{},".format(i))
f.write("year.quarter")
f.write("\n")

# Write data
for document in sentences:
    rec = document.tags[0].split(sep='_')    
    document_features = model.infer_vector(document.words)
    f.write("{},".format(rec[0]))
    date_str = rec[3][:-4]
    f.write("{},".format(date_str))
    for feature in document_features:
        f.write("{},".format(feature))    
    filing_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")    
    f.write("{}-Q{}\n".format(filing_date.year, math.ceil(filing_date.month/3)))
f.close()
