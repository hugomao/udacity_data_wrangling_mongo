import requests

data_url = 'http://overpass-api.de/api/map?bbox=-122.3383,47.7138,-122.1515,47.7867'
filename = 'kenmore.osm'

def download_file(url, file_name):
    r = requests.get(url, stream = True)
    with open(file_name, 'wb') as f:
        print "Downloading %s" % file_name, '...'
        data_size = 0
        for chunk in r.iter_content(chunk_size=1026): 
            if chunk:
                f.write(chunk)
                data_size += len(chunk)
                f.flush()
        print "Finish downloading, the data size is " + str(data_size) + "!"




if __name__ == "__main__":
    data_url = 'http://overpass-api.de/api/map?bbox=-122.3383,47.7138,-122.1515,47.7867'
    filename = 'kenmore.osm'
    download_file(data_url, filename)
    
