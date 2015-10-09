import psycopg2, urllib.request, settings, os.path, filing_iterator, nltk.data, pickle

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def populate_filings_index():
    conn = psycopg2.connect(settings.CONN_STRING)   

    insertCount = 0

    # parse fields from files
    for year in range(settings.START_YEAR, settings.END_YEAR + 1):
        for i in range(1,5):
            dir_name = 'company_index_' + str(year) + 'Q' + str(i) + '\\'
            filename = 'company.idx'
            
            # read all the lines in the file
            print("Processing " + dir_name + "...")
            f = open(settings.BASE_PATH + dir_name + filename, 'r')
            lines = f.readlines()    
            f.close()

            # parse the fields
            lineCount = 0            
            for line in lines:
                # skip the first 10 lines
                if (lineCount > 9):
                    company_name = line[0:61].strip()
                    form_type = line[62:73].strip()
                    cik = line[74:85].strip()
                    date_filed = line[86:97].strip()
                    file_name = line[98:140].strip()

                    if (form_type in settings.FORM_TYPES):
                        # insert into DB
                        cur = conn.cursor()
                        cur.execute('INSERT into filing_index(cik, company_name, date_filed, form_type, file_name) VALUES(%s, %s, %s, %s, %s)',
                                    (cik, company_name, date_filed, form_type, file_name))                    
                        cur.close()
                    
                lineCount += 1            
            conn.commit()
    
    # close DB connection
    conn.close()

def populate_filings():
    conn = psycopg2.connect(settings.CONN_STRING)   

    # load company names from file
    f = open(settings.BASE_PATH + settings.COMPANY_DEFAULT_DATES, 'r')
    lines = f.readlines()    
    f.close()
    
    for line in lines:
        company_name = line.split(sep = ',')[0]
        default_date = line.split(sep = ',')[1]
        print("Retrieving filings for {}, default-date: {} ...".format(company_name, default_date.strip()))        
        company_name_wildcard = clean_company_name(company_name) +'%'
        print(company_name_wildcard)
        # determine CIK and filing file
        cur = conn.cursor()
        cur.execute('select distinct c.cik, f.date_filed, f.form_type, f.file_name from companies c, filing_index f where c.cik = f.cik and f.date_filed < (DATE %s) and c.company_name like %s;',  (default_date, company_name_wildcard))   
        #cur.execute('select distinct c.cik, f.date_filed, f.form_type, f.file_name from companies c, filing_index f where c.cik = f.cik and c.company_name like %s;',  (company_name_wildcard, ))   
        # fetch each filing
        for record in cur:
            cik = record[0]
            date_filed = record[1]
            form_type = record[2]
            file_name = record[3]

            if (form_type in settings.FORM_TYPES):
                # fudge for file_names ending with ".tx"
                if (file_name.endswith('.txt') == False):
                    file_name = file_name + 't'

                filing_id = get_filing_id(file_name, cik)

                # check if filing already present
                cur_check = conn.cursor()
                cur_check.execute('SELECT filing_id FROM filings WHERE filing_id = %s', (filing_id,))
                cur_check.close()
                if (cur_check.rowcount != 0):
                    print('Filing {} already exists. Skipping.'.format(filing_id))
                    continue

                # if filing not found, retrieve from EDGAR
                full_filing_url = settings.EDGAR_FTP_URL + file_name
                print("Getting filing {}...".format(full_filing_url))
                filing_text = ""
                for i in range (1,4):
                    try:
                        filing_text = urllib.request.urlopen(full_filing_url).read().decode('utf=8')
                        if (filing_text != ""):
                            break
                    except:
                        print("EOFError. Retry attempt {}".format(i))

                cur2 = conn.cursor()
                cur2.execute('INSERT into filings(cik, date_filed, form_type, filing, filing_id) VALUES(%s, %s, %s, %s, %s)',
                                        (cik, date_filed, form_type, filing_text, filing_id))
                cur2.close()
                conn.commit()

        cur.close()

    conn.close()

def populate_filing_for_company(cik, ticker, writeToFile = False, filePrefix = '', year_start = 2000, year_end = 2015):
    conn = psycopg2.connect(settings.CONN_STRING)
    cur = conn.cursor()
    cur.execute('select f.cik, f.date_filed, f.form_type, f.file_name from filing_index f where f.cik = %s;',  (cik, ))
    
    for record in cur:
            cik = record[0]
            date_filed = record[1]
            form_type = record[2]
            file_name = record[3]

            if (form_type in settings.FORM_TYPES and 
                (date_filed.year >= year_start and date_filed.year <= year_end)):
                # fudge for file_names ending with ".tx"
                if (file_name.endswith('.txt') == False):
                    file_name = file_name + 't'

                filing_id = get_filing_id(file_name, cik)

                # check if filing already present
                filing_exists = False
                out_filename = ''
                if writeToFile == True:
                    out_filename = '{}_{}_{}.txt'.format(filePrefix, form_type, str(date_filed))
                    if os.path.isfile(settings.BASE_PATH_FILINGS + '{}.pickle'.format(out_filename)):
                        filing_exists = True   
                else:
                    out_filename = '{}_{}_{}_{}.txt'.format(ticker, cik, form_type, str(date_filed))
                    cur_check = conn.cursor()
                    cur_check.execute('SELECT filing_id FROM filings WHERE filing_id = %s', (filing_id,))
                    cur_check.close()
                    if (cur_check.rowcount != 0):
                        filing_exists = True
                
                # if filing found, skip the rest
                if filing_exists == True:
                    if writeToFile == True:
                        file_identifier = out_filename
                    else:
                        file_identifier = filing_id
                    print('Filing {} already exists. Skipping.'.format(file_identifier))
                    continue

                # if filing not found, retrieve from EDGAR
                full_filing_url = settings.EDGAR_FTP_URL + file_name
                print("Getting filing {}...".format(full_filing_url))
                filing_text = ""
                for i in range (1,4):
                    try:
                        filing_text = urllib.request.urlopen(full_filing_url).read().decode('utf-8')                        
                        if (filing_text != ""):
                            break
                    except:
                        print("EOFError. Retry attempt {}".format(i))

                if writeToFile == True:
                    # clean the data and dump it as a pickled list
                    print('Cleaning and pickling...')
                    pickle_file_name = settings.BASE_PATH_FILINGS + '{}.pickle'.format(out_filename)
                    words = filing_iterator.get_words_from_doc(filing_text, tokenizer)                
                    with open(pickle_file_name, 'wb') as f:
                        pickle.dump(words, f)
                else:
                    cur2 = conn.cursor()
                    cur2.execute('INSERT into filings(cik, date_filed, form_type, filing, filing_id) VALUES(%s, %s, %s, %s, %s)',
                                            (cik, date_filed, form_type, filing_text, filing_id))
                    cur2.close()
                    conn.commit()
    cur.close()
    conn.close()


def create_cik_company_name_mapping():
    conn = psycopg2.connect(settings.CONN_STRING)   

    # load company names from file
    f = open(settings.BASE_PATH + settings.COMPANY_DEFAULT_DATES, 'r')
    lines = f.readlines()    
    f.close()


    # search for CIK and begin writing in mapping file
    f_mapping = open(settings.BASE_PATH + settings.COMPANY_CIK_NAMES_MAPPING, 'w')
    f_mapping.write('Issuer,CIK\n')
    for line in lines:
        company_name = line.split(sep = ',')[0]
        company_name_wildcard = clean_company_name(company_name) +'%'
        
        # determine CIK
        cur = conn.cursor()
        cur.execute('select distinct c.cik from companies c where c.company_name like %s;',  (company_name_wildcard, ))   
        
        # fetch each filing
        for record in cur:
            cik = record[0]
            print(company_name, cik)
            f_mapping.write('{},{}\n'.format(company_name, cik))
        cur.close()

    # release resources
    f_mapping.close()
    conn.close()


def get_filing_id(file_name, cik):
    txt_file_name = file_name.split(sep='/')[3].split(sep='.')[0]
    return str(cik) + '/' + txt_file_name

def clean_company_name(company_name):
    company_name = company_name.upper()
    company_name = company_name.replace("COMPANY", "CO")
    company_name = company_name.replace("INC.", "INC")
    company_name = company_name.replace("CORPORATION", "CORP")
    company_name = company_name.replace("CORP.", "CORP")
    company_name = company_name.replace("CO.", "CO")
    company_name = company_name.replace("LTD.", "LTD")
    company_name = company_name.replace("L.L.C.", "LLC")
    company_name = company_name.replace("INCORPORATED", "INC")
    company_name = company_name.replace("LIMITED", "LTD")
    company_name = company_name.replace("L.P.", "LP")
    company_name = company_name.replace("S.A.", "SA")
    return company_name.strip()
