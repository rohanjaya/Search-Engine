from index import stemmer, new_index_of_index, doc_ids, stop_words, has_digits, base_directory
from collections import defaultdict
import math
import re
import time
import os

# def find_shared_docs(sorted_lists): # finds shared documents between tokens
#     # BOOLEAN SEARCH
#     # DONT USE - BROKEN
#     if not sorted_lists:
#         return []
#     if len(sorted_lists) == 1:
#         return sorted_lists[0]
#     curr = sorted_lists[0]
#     for l in sorted_lists[1:]:
#         comb = []
#         i1 = 0
#         i2 = 0
#         while(i1 < len(curr) and i2 < len(l)):
#             if int(curr[i1]) == int(l[i2]):
#                 comb.append(curr[i1])
#                 i1+=2
#                 i2+=2
#             else:
#                 if int(curr[i1]) < int(l[i2]):
#                     i1+=2
#                 else:
#                     i2+=2
#         curr = comb
#     return curr

def compute_k_best_docs(token_docs, k): # calculate tf-idf scores
    rank = defaultdict(int)
    for token_doc in token_docs:
        # the even items are the document ids
        # the odd items are the weights
        for i in range(0, len(token_doc), 2):
            rank[int(token_doc[i])] += (1+math.log(int(token_doc[i+1]),10)) * math.log( (len(doc_ids)) / (len(token_doc)//2) , 10)
    rank_list = [] # turn scores into list so they can be sorted
    for d, r in rank.items():
            rank_list.append((r,d))
    rank_list.sort(reverse=True)
    print(len(rank_list), "results") # how many possible matches there were
    if len(rank_list) < k:
        return rank_list
    return rank_list[:k] # returns k best


def search():
    global stop_words
    with open(os.path.join(base_directory, "storage.csv")) as f:
        # inverted index is opened but not loaded into memory
        print('Enter exit* to quit')
        while(True):
            try:
                search = input(">> ")
                start = time.time() # used to check how long retrieval takes
                if search == "exit*":
                    return
                content = re.findall(r'[a-zA-Z0-9]+', search) # query content is tokenized the same way as the documents were

                non_stop = 0
                use_stop_words = True
                for word in content:
                    if word not in stop_words:
                        non_stop+=1
                if non_stop > 0.4 * len(content): # if less than 40% of query is stop words dont use them
                    use_stop_words = False

                token_docs = []
                # each item in the list is a line from the inverted index file
                for i, token in enumerate(content):
                    token = token.lower()
                    if not use_stop_words and token in stop_words:
                        continue
                    token = stemmer.stem(token)
                    if token in new_index_of_index:
                        f.seek(new_index_of_index[token])
                        l = f.readline()
                        token_docs.append(l[:-1].split(',')[1:]) # avoid new-line and also first value which is token

                    if i < len(content) -1:
                        next = content[i+1].lower()
                        if next not in stop_words and not has_digits(token): # 2-gram
                            next = stemmer.stem(next)
                            two_gram = token + next
                            if two_gram in new_index_of_index:
                                f.seek(new_index_of_index[two_gram])
                                l = f.readline()
                                token_docs.append(l[:-1].split(',')[1:])
                            if i < len(content)-2:
                                nextt = content[i+2].lower()
                                if nextt not in stop_words and (not has_digits(nextt) and not has_digits(next)): # 3-gram
                                    nextt = stemmer.stem(nextt)
                                    three_gram = token + next + nextt
                                    if three_gram in new_index_of_index:
                                        f.seek(new_index_of_index[three_gram])
                                        l = f.readline()
                                        token_docs.append(l[:-1].split(',')[1:])


                five_best = compute_k_best_docs(token_docs, 5)
                for d in five_best:
                    print(doc_ids[int(d[1])])
                print(time.time()-start, "seconds")
            except:
                continue
