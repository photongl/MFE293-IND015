import settings, psycopg2, pickle, os, re
from bs4 import BeautifulSoup
from gensim.models import doc2vec
from nltk.corpus import stopwords

def clean_filing(filing_text):    
    """Cleans the filing text by stripping HTML"""    
    start = 0      
    doc_start_indices = [m.start() for m in re.finditer("<DOCUMENT>", filing_text)]
    
    for index in doc_start_indices:
        start = index
        break
    
    end = len(filing_text)
    doc_end_indices = [m.start() for m in re.finditer("</DOCUMENT>", filing_text)]    
    for index in doc_end_indices:
        end = index
        break
    
    return BeautifulSoup(filing_text[start:end]).get_text().lower().encode().decode("ascii", "ignore")

def filing_to_wordlist(filing_text):
    words = filing_text.split()
    return words

def filing_to_sentences(filing_text, tokenizer):    
    clean_text = clean_filing(filing_text)
    raw_sentences = tokenizer.tokenize(clean_text.strip())    
    sentences = []
    
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            sentences.append(filing_to_wordlist(raw_sentence))                
    return sentences

def get_filing_id(file_name, cik):
    txt_file_name = file_name.split(sep='/')[3].split(sep='.')[0]
    return str(cik) + '/' + txt_file_name

def get_words_from_doc(filing_text, tokenizer):
    clean_text = clean_filing(filing_text)
    raw_sentences = tokenizer.tokenize(clean_text.strip())            
    words = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            words += filing_to_wordlist(raw_sentence)
    
    return words

class filings_iterator(object):
    """Iterates through filings"""
    def __init__(self, tokenizer, year_start = 2000, year_end=2015,
                  file_sp500 = settings.BASE_PATH + settings.COMPANY_CIK_SP500,
                  useDB = False, N = 1):
        self.max_docs = N
        self.year_start = year_start
        self.year_end = year_end
        self.file_sp500 = file_sp500
        self.tokenizer = tokenizer
        self.useDB = useDB
        self.stops = set(stopwords.words("english"))
        self.file_list = []
        self.filing_id_list = []

        # check if we already have the list of files we want to process
        file_list_fname = settings.BASE_PATH_CLEAN_FILINGS+ '{}.pickle'.format("file_list")
        filing_id_list_fname = settings.BASE_PATH_CLEAN_FILINGS+ '{}.pickle'.format("filing_id_list")
        if (os.path.isfile(file_list_fname) and os.path.isfile(filing_id_list_fname)):
            with open(file_list_fname, 'rb') as f:
                self.file_list = pickle.load(f)
            with open(filing_id_list_fname, 'rb') as f:
                self.filing_id_list = pickle.load(f)
            print('Found pickle file {}, skipping DB check...'.format(file_list_fname))
            print('Found pickle file {}, skipping DB check...'.format(filing_id_list_fname))
        else:
            # read list of S&P 500 companies
            f_sp500 = open(self.file_sp500)
            lines = f_sp500.readlines()    
            f_sp500.close()
            
            conn = psycopg2.connect(settings.CONN_STRING)
            for line in lines:            
                fields = [field.strip() for field in line.split(sep = ',')]
                ticker = fields[0]
                company_cik = str(int(fields[2]))
                
                cur = conn.cursor()
                cur.execute('select f.cik, f.date_filed, f.form_type, f.file_name from filing_index f where f.form_type in(%s, %s) and f.cik = %s order by f.date_filed;',
                            ('10-K', '10-Q', company_cik, ))
        
                for record in cur:
                        date_filed = record[1]
                        form_type = record[2]
                        file_name = record[3]
                        
                        if (form_type in settings.FORM_TYPES and 
                            (date_filed.year >= self.year_start and date_filed.year <= self.year_end)):
                                            
                            # figure out filename
                            filename = '{}_{}_{}_{}.txt'.format(ticker, company_cik, form_type, str(date_filed))                       
                            self.file_list.append(filename)
                            self.filing_id_list.append(get_filing_id(file_name, str(int(company_cik))))
                        
                cur.close()
            conn.close()
            
            with open(file_list_fname, 'wb') as f:
                    pickle.dump(self.file_list, f)
            with open(filing_id_list_fname, 'wb') as f:
                    pickle.dump(self.filing_id_list, f)
        print('Populated {} filenames'.format(len(self.file_list)))    
    
    def get_filing_from_db(self):
        # read files from DB, clean them and create TaggedDocument
        conn = psycopg2.connect(settings.CONN_STRING)
        words = []
        i = 0
        for i in range(0, self.max_docs):            
            pickle_file_name = settings.BASE_PATH_FILINGS + '{}.pickle'.format(self.file_list[i])
            if os.path.isfile(pickle_file_name):
                print('Found pickle file {}, skipping cleaning/tokenization...'.format(pickle_file_name))
                with open(pickle_file_name, 'rb') as f:
                    words = pickle.load(f)
            else:   
                cur = conn.cursor()
                cur.execute('select f.filing, f.date_filed from filings f where f.filing_id = %s',
                            (self.filing_id_list[i],))
                filing_text = ''                       
                for record in cur:
                    filing_text = record[0]
                cur.close()
                
                print('Cleaning {}...'.format(self.file_list[i]))
                words = get_words_from_doc(filing_text, self.tokenizer)
                
                with open(pickle_file_name, 'wb') as f:
                    pickle.dump(words, f)
                            
            yield(doc2vec.TaggedDocument(words = words, tags=[self.file_list[i]]))               
        conn.close()
        
    def get_filings_without_binary_content(self):
        # read files from DB, clean them and create TaggedDocument
        print("Getting filings content...")
        conn = psycopg2.connect(settings.CONN_STRING)
        words = []
        i = 0
        print("Getting filings content...")
        for i in range(0, self.max_docs):
            
            pickle_file_name = settings.BASE_PATH_CLEAN_FILINGS + '{}.pickle'.format(self.file_list[i])
            if os.path.isfile(pickle_file_name):
                print('Found pickle file {}, skipping cleaning/tokenization...'.format(pickle_file_name))
                with open(pickle_file_name, 'rb') as f:
                    words = pickle.load(f)
            else:   
                cur = conn.cursor()
                cur.execute('select f.filing, f.date_filed from filings f where f.filing_id = %s',
                            (self.filing_id_list[i],))
                filing_text = ''                       
                for record in cur:
                    filing_text = record[0]
                cur.close()
                
                print('Cleaning {}...'.format(self.file_list[i]))
                words = get_words_from_doc(filing_text, self.tokenizer)
                
                with open(pickle_file_name, 'wb') as f:
                    pickle.dump(words, f)
                            
            yield(doc2vec.TaggedDocument(words = words, tags=[self.file_list[i]]))        
        conn.close()
    
    def get_filing_without_stopwords_from_db(self):
        # read files from DB, clean them and create TaggedDocument
        conn = psycopg2.connect(settings.CONN_STRING)
        words = []
        i = 0
        for i in range(0, self.max_docs):
            
            pickle_file_name = settings.BASE_PATH_CLEAN_FILINGS + '{}.pickle'.format(self.file_list[i])
            if os.path.isfile(pickle_file_name):
                print('Found pickle file {}, skipping cleaning/tokenization...'.format(pickle_file_name))
                with open(pickle_file_name, 'rb') as f:
                    words = pickle.load(f)
            else:                 
                cur = conn.cursor()
                cur.execute('select f.filing, f.date_filed from filings f where f.filing_id = %s',
                            (self.filing_id_list[i],))
                filing_text = ''                       
                for record in cur:
                    filing_text = record[0]
                cur.close()
                
                print('Cleaning {}...'.format(self.file_list[i]))
                words = get_words_from_doc(filing_text, self.tokenizer)
                
                with open(pickle_file_name, 'wb') as f:
                    pickle.dump(words, f)
                            
            yield(" ".join([w for w in words if not w in self.stops]))               
        conn.close()
            
    def get_all_filing_sentences_from_db(self):
        # read files from DB, clean them and create TaggedDocument
        conn = psycopg2.connect(settings.CONN_STRING)
        i = 0
        sentences_to_return = []
        for i in range(0, self.max_docs):            
            pickle_file_name = settings.BASE_PATH_SENTENCES + '{}_sentences.pickle'.format(self.file_list[i])
            if os.path.isfile(pickle_file_name):
                print('Found pickle file {}, skipping cleaning/tokenization...'.format(pickle_file_name))
                with open(pickle_file_name, 'rb') as f:
                    sentences = pickle.load(f)
                    sentences_to_return = sentences_to_return + sentences
            else:   
                cur = conn.cursor()
                cur.execute('select f.filing, f.date_filed from filings f where f.filing_id = %s',
                            (self.filing_id_list[i],))
                filing_text = ''                       
                for record in cur:
                    filing_text = record[0]
                cur.close()
                
                print('Cleaning {}...'.format(self.file_list[i]))
                sentences = filing_to_sentences(filing_text, self.tokenizer)
                sentences_to_return = sentences_to_return + sentences
                
                with open(pickle_file_name, 'wb') as f:
                    pickle.dump(sentences, f)
        conn.close()
        return sentences_to_return
    
    def __iter__(self):
        return self.get_filings_without_binary_content()
        