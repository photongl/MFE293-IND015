import zipfile

def unzipfile():
    for year in range(settings.START_YEAR, settings.END_YEAR + 1):
        for i in range(1,5):            
            filename = 'company_index_' + str(year) + 'Q' + str(i)
            print("Extracting " + filename + "...")    
            zip_ref = zipfile.ZipFile(settings.BASE_PATH + filename + '.zip', 'r')
            zip_ref.extractall(settings.BASE_PATH + filename + '\\')
            zip_ref.close()            
