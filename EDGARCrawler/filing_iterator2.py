import settings, psycopg2, pickle, os, re
from bs4 import BeautifulSoup
from gensim.models import doc2vec
from nltk.corpus import stopwords

def clean_filing(filing_text):
    """Cleans the filing text by stripping HTML"""    

    start = 0      
    doc_start_indices = [m.start() for m in re.finditer("<BODY ", filing_text)]
    
    for index in doc_start_indices:
        start = index
        break
    
    end = len(filing_text)
    doc_end_indices = [m.start() for m in re.finditer("</BODY>", filing_text)]    
    for index in doc_end_indices:
        end = index
        break
    
    return BeautifulSoup(filing_text[start:end]).get_text().lower().encode().decode("ascii", "ignore")

def filing_to_wordlist(filing_text):
    words = filing_text.split()
    return words

def get_words_from_doc(filing_text, tokenizer):
    clean_text = clean_filing(filing_text)
    raw_sentences = tokenizer.tokenize(clean_text.strip())            
    words = []
    for raw_sentence in raw_sentences:
        if len(raw_sentence) > 0:
            words += filing_to_wordlist(raw_sentence)
    
    return words

class filings_iterator2(object):
    """Iterates through filings"""
    def __init__(self, tokenizer, year_start = 2000, year_end=2015,
                  file_sp500 = settings.BASE_PATH + settings.COMPANY_CIK_SP500,
                  useDB = False, N = 1):
        self.year_start = year_start
        self.year_end = year_end
        self.tokenizer = tokenizer
        self.stops = set(stopwords.words("english"))
    
    def get_filing_without_stopwords_from_db(self):
        for file in os.listdir("E:\\slo\\"):
            if file.endswith(".txt"):
                f = open("E:\\slo\\"+file, 'r')        
                filing_text = f.read()
                words = get_words_from_doc(filing_text, self.tokenizer)
                f.close()
            yield(" ".join([w for w in words if not w in self.stops]))
    
    def __iter__(self):
        return self.get_filing_without_stopwords_from_db()
        