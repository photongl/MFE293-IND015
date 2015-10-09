import settings, re, math, logging, psycopg2, nltk.data, os
import numpy as np
from gensim.models import word2vec, doc2vec
from bs4 import BeautifulSoup

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',\
                    level=logging.INFO)    


def clean_filing(filing_text):    
    """Cleans the filing text by stripping HTML"""    
    return BeautifulSoup(filing_text).get_text().lower()


def filing_to_wordlist(filing_text):
    words = filing_text.split()
    return words

def filing_to_sentences(filing_text):    
    clean_text = clean_filing(filing_text)
    raw_sentences = tokenizer.tokenize(clean_text.strip())    
    sentences = []
    
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(filing_to_wordlist(raw_sentence))
                
    return sentences

def filing_to_labeled_sentences(filing_text):
    clean_text = clean_filing(filing_text)
    raw_sentences = tokenizer.tokenize(clean_text.strip())    
    sentences = []
    
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(doc2vec.LabeledLineSentence(filing_to_wordlist(raw_sentence)))
                
    return sentences

def get_clean_filing_text(cik, ticker = '', year_start = 2000, year_end = 2015):
    conn = psycopg2.connect(settings.CONN_STRING)
    cur = conn.cursor()
    cur.execute('select f.cik, f.date_filed, f.form_type, f.file_name from filing_index f where f.cik = %s;',  (cik, ))
    
    for record in cur:
            date_filed = record[1]
            form_type = record[2]
            file_name = record[3]

            if (form_type in settings.FORM_TYPES and 
                (date_filed.year >= year_start and date_filed.year <= year_end)):
                
                # figure out filename
                filename = '{}_{}_{}_{}.txt'.format(ticker, cik, form_type, str(date_filed))
                filename_clean = '{}_{}_{}_{}_clean.txt'.format(ticker, cik, form_type, str(date_filed))

                # check if clean file exists - if not create it
                if os.path.isfile(settings.BASE_PATH_FILINGS + filename_clean):
                    print('Filing {} already exists. Skipping.'.format(filename_clean))
                else:
                    # read file and clean it
                    f_clean = open(settings.BASE_PATH_FILINGS + filename_clean, 'w')
                    try:
                        print('Cleaning file {} and writing to {}'.format(filename, filename_clean))
                        f = open(settings.BASE_PATH_FILINGS + filename, 'r')
                        filing_text = f.read()
                        f.close()
                        clean_text = clean_filing(filing_text)                        
                        f_clean.write(clean_text)
                        f_clean.close()                
                    except:
                        print('Character mapping error. Skipping...')
                        f_clean.close()
                        continue

                # train model
                print("Training model with {} filing for {} for date {}...".format(form_type, ticker, date_filed))
                sentences = doc2vec.LabeledLineSentence(settings.BASE_PATH_FILINGS + filename_clean)
                model.build_vocab(sentences)
                
                model.train(sentences)                
    cur.close()
    conn.close()

def hash32(value):
     return hash(value) & 0xffffffff


def deeplearn_filing(sentences, model_name, num_features):    
    #
    # Create a word-vector feature-set from a group of
    # tokenized sentences
    #

    # Set values for various parameters
    num_features = num_features     # Word vector dimensionality                      
    min_word_count = 1              # Minimum word count                        
    num_workers = 4                 # Number of threads to run in parallel
    context = 20                    # Context window size                                                                                    
    downsampling = 1e-3             # Downsample setting for frequent words
    
    # Initialize and train the model (this will take some time)    
    print("Training model...")
    model = word2vec.Word2Vec(sentences, workers=num_workers, \
                size=num_features, min_count = min_word_count, \
                window = context, sample = downsampling, hashfxn = hash32)
    
    # If you don't plan to train the model any further, calling 
    # init_sims will make the model much more memory-efficient.
    model.init_sims(replace=True)
    
    # save the model for later use
    model.save(model_name)
    return model

def train_model(model, cik, ticker = '', year_start = 2000, year_end = 2015):
    conn = psycopg2.connect(settings.CONN_STRING)
    cur = conn.cursor()
    cur.execute('select f.cik, f.date_filed, f.form_type, f.file_name from filing_index f where f.cik = %s;',  (cik, ))
    
    for record in cur:
            date_filed = record[1]
            form_type = record[2]
            file_name = record[3]

            if (form_type in settings.FORM_TYPES and 
                (date_filed.year >= year_start and date_filed.year <= year_end)):
                
                # figure out filename
                filename = '{}_{}_{}_{}.txt'.format(ticker, cik, form_type, str(date_filed))
                filename_clean = '{}_{}_{}_{}_clean.txt'.format(ticker, cik, form_type, str(date_filed))

                # check if clean file exists - if not create it
                if os.path.isfile(settings.BASE_PATH_FILINGS + filename_clean):
                    print('Filing {} already exists. Skipping.'.format(filename_clean))
                else:
                    # read file and clean it
                    f_clean = open(settings.BASE_PATH_FILINGS + filename_clean, 'w')
                    try:
                        print('Cleaning file {} and writing to {}'.format(filename, filename_clean))
                        f = open(settings.BASE_PATH_FILINGS + filename, 'r')
                        filing_text = f.read()
                        f.close()
                        clean_text = clean_filing(filing_text)                        
                        f_clean.write(clean_text)
                        f_clean.close()                
                    except:
                        print('Character mapping error. Skipping...')
                        f_clean.close()
                        continue

                # train model
                print("Training model with {} filing for {} for date {}...".format(form_type, ticker, date_filed))
                sentences = doc2vec.LabeledLineSentence(settings.BASE_PATH_FILINGS + filename_clean)
                model.build_vocab(sentences)
                
                model.train(sentences)                
    cur.close()
    conn.close()

def get_document_features(model, words, num_features):
    # Function to average all of the word vectors in a given
    # paragraph
    #
    # Pre-initialize an empty numpy array (for speed)
    featureVec = np.zeros((num_features,),dtype="float32")
    #
    nwords = 0.
    # 
    # Index2word is a list that contains the names of the words in 
    # the model's vocabulary. Convert it to a set, for speed 
    index2word_set = set(model.index2word)
    #
    # Loop over each word in the document and, if it is in the model's
    # vocabulary, add its feature vector to the total
    for word in words:
        if word in index2word_set: 
            nwords = nwords + 1.
            featureVec = np.add(featureVec,model[word])
    # 
    # Divide the result by the number of words to get the average
    featureVec = np.divide(featureVec, nwords)
    return featureVec