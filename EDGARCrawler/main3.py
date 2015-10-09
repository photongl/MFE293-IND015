import settings, logging, nltk.data, numpy as np
from filing_iterator import filings_iterator
from gensim.models import word2vec

def get_document_features(model, words, num_features, max_words = 20000):
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((max_words, num_features),dtype="float32")    
    nwords = 0
    # 
    # Index2word is a list that contains the names of the words in 
    # the model's vocabulary. Convert it to a set, for speed 
    index2word_set = set(model.index2word)
    #
    # Loop over each word in the document and, if it is in the model's
    # vocabulary, add its feature vector to the total
    for word in words:
        if word in index2word_set:            
            featureVec[nwords,:] = model[word] 
            nwords = nwords + 1
            if (nwords >= max_words):
                break
            
    return featureVec

# some config parameters
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
                    level=logging.INFO)
year_start = 2000
year_end = 2008
n_docs = 1
num_features = 64
num_words = 20000
model_name = "sec_filings_model_{}.d2v".format(num_features)

# prepare training data
filings_it = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = 1000, useDB = True, year_start = year_start, year_end = year_end)
sentences = filings_it.get_all_filing_sentences_from_db()

# train model
model = word2vec.Word2Vec(sentences, 
                        size = num_features,
                        min_count = 5,
                        seed = 5,
                        window = 20,
                        sample = 1e-3,
                        #hashfxn = analyze.hash32
                        workers = 4)

model.init_sims(replace=True)
model.save(model_name)
print(model.most_similar('equity'))

# ==============================================================
# retrieve features for each document and store them in a file
# ==============================================================
docs = filings_iterator(tokenizer = nltk.data.load('tokenizers/punkt/english.pickle'), N = 8485, useDB = True)
# Write data
for document in docs:
    filename = settings.BASE_PATH_FEATURES + "{}".format(document.tags[0])
    
    # get features as numpy array and dump to file
    document_features = get_document_features(model, document.words, num_features, num_words)
    np.savez_compressed(filename, document_features)
