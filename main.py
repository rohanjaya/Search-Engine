from index import index, new_index_of_index, doc_ids, base_directory
from search import search
import os
import time

def load_info():
    # load index of index and document ids into memory for search
    with open(os.path.join(base_directory, "dids.csv")) as f:
        for line in f:
            try:
                line = line[:-1]
                doc_ids[int(line.split(',')[0])] = line.split(',')[1]
            except:
                continue
    with open(os.path.join(base_directory, "index.csv")) as f:
        for line in f:
            line = line[:-1]
            new_index_of_index[line.split(',')[0]] = int(line.split(',')[1])

if __name__ == '__main__':
    inp = input("Do you already have an inverted index? y/n\n")
    if inp == "n":
        start = time.time()
        index()
        print(time.time()-start)
        search()
    elif inp == "y":
    # Only works if you already have "dids.csv", "index.csv", and "storage.csv"
        load_info()
        search()
    else:
        print("Invalid input")
    