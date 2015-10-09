# date range
START_YEAR = 1993
END_YEAR = 2014

# Database connection string
CONN_STRING = "host=127.0.0.1 dbname=mfe_citi user=mfe_citi_rw password=mfe123#"

# data paths
# Windows
BASE_PATH = "E:\\Books and Papers\\Citi_Seniority_Recovery\\R Code\\"
BASE_PATH_CLEAN_FILINGS = "G:\\clean_filings\\"
BASE_PATH_FILINGS = "G:\\clean_filings\\"

# Linux
#BASE_PATH = "/home/akshaym/E/Books and Papers/Citi_Seniority_Recovery/R Code/"
#BASE_PATH_CLEAN_FILINGS = "/media/akshaym/SSD/clean_filings/"
#BASE_PATH_FILINGS = "/media/akshaym/SSD/clean_filings/"
#BASE_PATH_FILINGS = "/home/akshaym/E/Books and Papers/Citi_Seniority_Recovery/Data/company_filings_data/"
#BASE_PATH_FILINGS = "/media/akshaym/Data2/SEC filings pickles/company_filings_data/"
#BASE_PATH_SENTENCES = "/media/akshaym/Data2/SEC filings pickles/company_filings_sentences/"
#BASE_PATH_FEATURES = "/media/akshaym/Data2/SEC filings pickles/company_filings_features/"

COMPANY_NAMES = "company_names.txt"
COMPANY_DEFAULT_DATES = "company_default_dates.csv"
COMPANY_CIK_NAMES_MAPPING = "company_names_cik_mapping.csv"
COMPANY_CIK_SP500 = "company_cik_sp500.csv"
COMPANY_CAPITAL_STRUCTURE = "company_capital_structure.csv"

# SEC common form types
#FORM_TYPES = ['F-1', 'D', '3', '4', '5', 'S-1', '13D', '144', '20-F', 'ARS', '6-K', '10-Q', '10-K', '8-K']
#FORM_TYPES = ['424A', '424B1', '424B2', '424B3', '424B4', '424B5', '424B6', '424B7', '424B8', '10-Q', '10-K']
FORM_TYPES = ['10-Q', '10-K']
EDGAR_FTP_URL = "ftp://ftp.sec.gov/"
