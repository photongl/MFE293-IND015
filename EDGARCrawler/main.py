import settings, analyze, psycopg2

num_features = 10
model_name = "sec_filing_model"
company_name = "microsoft corp"
company_cik = 789019
company_ticker = "MSFT"
company_name_wildcard = company_name + '%'
form_type1 = "10-Q"
form_type2 = "10-K"

# get filing text from database
conn = psycopg2.connect(settings.CONN_STRING)   
cur = conn.cursor()
cur.execute('select f.filing, f.date_filed from filings f where f.cik = %s and f.form_type in (%s, %s)',
            (company_cik, form_type1, form_type2))

filing_text = ''
stcs = []
words = {}
for record in cur:
    filing_text = record[0]
    filing_date = record[1]
    print("Processing filing for date {}...".format(filing_date))
    words[filing_date] = analyze.filing_to_wordlist(filing_text)
    stcs = stcs + analyze.filing_to_sentences(filing_text)
cur.close()
conn.close()

# learn model
print(stcs)
model = analyze.deeplearn_filing(stcs, model_name, num_features)

# ==============================================================
# retrieve features for each document and store them in a file
# ==============================================================
f = open(settings.BASE_PATH + "{}_FEATURES.csv".format(company_ticker), 'w')

# Write header
f.write("Name,")
f.write("Date,")
for i in range(1, num_features + 1):
    f.write("feat_{},".format(i))
f.write("\n")

# Write data
for key in sorted(words.keys()):
    document_features = analyze.get_document_features(model, words[key], num_features)
    f.write("{},".format(company_ticker))
    f.write("{},".format(key))
    for feature in document_features:
        f.write("{},".format(feature))
    f.write("\n")
f.close()

    