import os
import json
import re
import csv
import hashlib
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
from collections import defaultdict
from urllib.parse import urldefrag, urlparse

base_directory = r"C:\Users\rohan\Desktop\CS121\Assignment3-Local" # enter your base directory here, should contain DEV as resources.

__all__ = ['base_directory',...]


doc_id = 1 # doc_id is assigned to documents as they are processed
inverted_index = defaultdict(list) # token -> [(doc_id, doc_frequency)....]
index_of_index = defaultdict(list) # token -> location in file so it can be found using seek()
doc_ids = {} # doc_id -> document url
reverse_doc_ids = {} # for anchor words, document url -> doc_id
visited_pages = set() # to avoid duplicates
visited_urls = set() # to avoid duplicates
sim_hashes = set() # to avoid near duplicates
stemmer = PorterStemmer()

new_index_of_index = {} # index_of_index after merge

stop_words = {'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', "aren",
              'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by',
              "can", 'cannot', 'could', "couldn", 'did', "didn", 'do', 'does', "doesn", 'doing', "don",
              'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', "hadn't", 'has', "hasn", 'have',
              "haven", 'having', 'he', "he", "he", "he", 'her', 'here', "here", 'hers', 'herself', 'him',
              'himself', 'his', 'how', "how", 'i', "lets", "ll", "i'm", "ve", 'if', 'in', 'into', 'is', "isn",
              'it', "it", 'its', 'itself', "let", 'me', 'more', 'most', "mustn", 'my', 'myself', 'no', 'nor',
              'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out',
              'over', 'own', 'same', "shan", 'she', "she", "she", "she's", 'should', "shouldn", 'so', 'some',
              'such', 'than', 'that', "that", 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
              "there's", 'these', 'they', "they'd", "ll", "re", "ve", 'this', 'those', 'through', 'to',
              'too', 'under', 'until', 'up', 'very', 'was', "wasn't", 'we', "we'd", "we'll", "we're", "we've", 'were',
              "weren", 'what', "what's", 'when', "when's", 'where', "where's", 'which', 'while', 'who', "who's",
              'whom', 'why', "why's", 'with', "won't", 'would', "wouldn", 'you', "you'd", "you'll", "you're",
              "you've", 'your', 'yours', 'yourself', 'yourselves', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k',
              'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}

allowed_domains = ['.ics.uci.edu', '.cs.uci.edu', '.stat.uci.edu', '.informatics.uci.edu']
months = {"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"}


def has_digits(word): # restriction for n-grams
    return any(c.isdigit() for c in word)

def process_anchor_words(url, text):
    # Text in links count towards the page that is linked
    # A page can now have its score increased before or after it is processed
    # Dont take n-grams for anchor words
    global doc_id, doc_ids, reverse_doc_ids, inverted_index, stop_words, months
    try:
        if url not in reverse_doc_ids:
            doc_ids[doc_id] = url
            reverse_doc_ids[url] = doc_id
            target = doc_id
            doc_id += 1
        else:
            target = reverse_doc_ids[url]
        word_freq = defaultdict(int)
        content = re.findall(r"[a-zA-Z0-9]+", text)
        for i, token in enumerate(content):
            token = token.lower()
            if token in stop_words or has_digits(token) or token in months: # strict for tokens in anchor words
            # dont want to index date-based pages
                continue
            token = stemmer.stem(token)
            word_freq[token]+=1 # give less weight to anchor words
        for word, freq in word_freq.items():
            inverted_index[word].append((target, freq))
    except:
        return
    


def process_document(document):
    # Processes document and adds to inverted_index
    word_freq = defaultdict(int) # more like word_weight than frequency
    token_list = [] # used to keep track of document size and check for exact duplicates
    global doc_id, doc_ids, reverse_doc_ids, inverted_index, visited_pages, stop_words, sim_hashes, visited_urls, allowed_domains
    try:
        with open(document, 'r') as d:
            two_grams = 0
            three_grams = 0
            data = json.load(d)
            url = data["url"]
            url = urldefrag(url).url
            if url in visited_urls:
                return
            soup = BeautifulSoup(data['content'], features='html.parser')
            content = soup.get_text()
            content = re.findall(r"[a-zA-Z0-9]+", content) # tokenization function with regex - alphunermic words

            strong_content = soup.find_all(['b', 'h1', 'h2', 'h3']) # "strong content"
            for sc in strong_content: # count "strong content" twice while processing
                content += re.findall(r"[a-zA-Z0-9]+", sc.text)

            anchor_content = soup.find_all('a')
            for ac in anchor_content: # only process anchor text for urls in https and allowed domains
                href_value = ac.get('href')
                if href_value:
                    href_value = urldefrag(href_value).url
                    parsed = urlparse(href_value)
                    if parsed.scheme == "https":
                        valid = False
                        for domain in allowed_domains:
                            if domain in str(parsed.netloc):
                                valid = True
                        if valid:
                            process_anchor_words(href_value, ac.text)

            for i, token in enumerate(content):
                if len(token_list) > 30000: # dont index too large page
                    return
                token = token.lower()
                # 2-grams cant have stop words and only the 2nd word can be numeric
                if token not in stop_words and not has_digits(token) and i < len(content) - 1:
                    token = stemmer.stem(token)
                    next = content[i+1].lower()
                    if next not in stop_words: # 2-gram
                        next = stemmer.stem(next)
                        two_gram = token + next
                        if two_grams % 3 == 0:
                            word_freq[two_gram]+=4
                            token_list.append(two_gram)
                            two_grams +=1
                        # 3-grams also cant have stop words and can have no numeric words
                        if i < len(content)-2:
                            nextt = content[i+2].lower()
                            if nextt not in stop_words and not has_digits(nextt) and not has_digits(next): # 3-gram
                                nextt = stemmer.stem(nextt)
                                three_gram = token + next + nextt
                                if three_grams % 2 == 0:
                                    word_freq[three_gram]+=6
                                    token_list.append(three_gram)
                                    three_grams += 1
                token = stemmer.stem(token)
                word_freq[token]+=2
                token_list.append(token)

        if len(token_list) < 75:
            return # dont index small pages
        token_hash = hash(tuple(token_list)) # Check for exact duplicates
        sim_hash = simhash(word_freq) # Check for near duplicates
        if token_hash in visited_pages:
            return # dont index duplicates
        if sim_hash in sim_hashes:
            return
        visited_urls.add(url)
        visited_pages.add(token_hash)
        sim_hashes.add(sim_hash)
        if url not in reverse_doc_ids: # assign doc_id to document url
            doc_ids[doc_id] = url
            reverse_doc_ids[url] = doc_id
            target = doc_id
            doc_id += 1
        else:
            target = reverse_doc_ids[url] # document has already been seen through an anchor
        for word, freq in word_freq.items():
            inverted_index[word].append((target, freq))
    except:
        print(f'FAILED TO PROCESS {document}')

def simhash(word_freq):
    # generates 64 bit simhash to prevent near duplicates
    weighted_hashes = {}
    for token in word_freq:
        hashed_token = hashlib.md5(token.encode('utf-8')).hexdigest()
        weighted_hashes[hashed_token] = word_freq[token]
    hash_size = 64
    hash_vector = [0] * hash_size
    for weighted_hash in weighted_hashes:
        hash_int = int(weighted_hash, 16) 
        for i in range(hash_size):
            bit_mask = 1 << i
            if hash_int & bit_mask:
                hash_vector[i] += weighted_hashes[weighted_hash]
            else:
                hash_vector[i] -= weighted_hashes[weighted_hash]
    simhash_value = 0
    for i, count in enumerate(hash_vector):
        if count > 0:
            simhash_value |= 1 << i
    return simhash_value

def write_to_csv(i):
    # stores inverted_index mid indexing process
    # is called multiple times 
    global inverted_index, index_of_index
    with open(os.path.join(base_directory, f'storage{i}.csv'),mode='w',newline='') as f:
        writer = csv.writer(f)
        for word, items in inverted_index.items():
            row = [word]
            for item in items:
                row.append(item[0])
                row.append(item[1])
            index_of_index[word].append((i, f.tell())) # stores [(storage file #, location in file),...]
            writer.writerow(row)

def save_doc_ids():
    global doc_ids
    # mapping of doc_ids->url is stored in file so that it can be loaded in memory for search
    with open(os.path.join(base_directory, "dids.csv"), mode='w', newline='') as f:
        writer = csv.writer(f)
        for id, url in doc_ids.items():
            row = [id, url]
            writer.writerow(row)

def save_index_of_index():
    global new_index_of_index
    # index_of_index saved so that it can be loaded in memory for search
    # allow inverted index file to be used with seek()
    with open(os.path.join(base_directory, "index.csv"), mode='w', newline='') as f:
        writer = csv.writer(f)
        for token, loc in new_index_of_index.items():
            row = [token, loc]
            writer.writerow(row)

def merge_index():
    global index_of_index, new_index_of_index
    # combines partial index files into one csv file called storage.csv
    with open(os.path.join(base_directory, "storage.csv"), mode = 'w', newline = '') as f:
        writer = csv.writer(f)
        for word in index_of_index:
            row = [word]
            for pair in index_of_index[word]:
                file_num = pair[0]
                word_loc = pair[1]
                temp_csv = os.path.join(base_directory, f'storage{file_num}.csv')
                with open(temp_csv) as f_read:
                    f_read.seek(word_loc)
                    l = f_read.readline()
                    for thing in l[:-1].split(',')[1:]:
                        row.append(thing)
            new_index_of_index[word] = f.tell()
            writer.writerow(row)
    index_of_index.clear()

# You will need to have dids.csv, index.csv, and storage.csv in order to run search()

def index():
    global inverted_index, doc_id, new_index_of_index
    i = 1 # partial index number
    for sub_dir in os.listdir(os.path.join(base_directory, "DEV")):
        sub_dir = os.path.join(os.path.join(base_directory, "DEV"), sub_dir)
        if os.path.isdir(sub_dir):
            print(sub_dir) 
            for document in os.listdir(sub_dir):
                document = os.path.join(sub_dir, document)
                if os.path.splitext(document)[1] == '.json': # only index json documents
                    process_document(document)
                if doc_id % 10000  == 0 and len(inverted_index) > 0:
                # create a partial index every 10000 documents processed
                    write_to_csv(i)
                    i += 1
                    inverted_index.clear() # keep whole inverted_index out of memory
    if len(inverted_index) > 0: # store remaining inverted_index
        write_to_csv(i)
        inverted_index.clear()
    merge_index()
    save_doc_ids()
    save_index_of_index()

    for j in range(1, i+1): # deleted the temporary storage files after merging them
        tmp_file = os.path.join(base_directory, f'storage{j}.csv')
        os.remove(tmp_file)
        print("DELETED", tmp_file)

    print("FINISHED PROCESSING DOCUMENTS")
    print(f'DOCUMENTS INDEXED ---- {len(doc_ids)}')
    print(f'UNIQUE WORDS --------- {len(new_index_of_index)}')

   