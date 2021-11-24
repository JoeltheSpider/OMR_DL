import indexing as index
import json
import time
import numpy
import numpy as np
import matplotlib.pyplot as plt

#TODO: if doclist length is 0, return random shit
def toSearch(query, invertedInd, vocab):
# Splits and normalize inputs and return the list of the doc name with respective tf_idf
    wordToFind = index.wordNorm(query)
    IDs = []
    doclist = []
    for word in wordToFind:
        try:
            IDs.append(vocab[word])
        except:
            pass
    for id in IDs:
        doclist.extend(invertedInd[str(id)])
    return doclist


def vectorize(lyrics, invIndex, vocab, json_name, idf):
# calculate tf idf vector for a particular song
# Build number vector from lyrics song mapped on vocabulary for cosine similarity
    word_vector = []
    if type(lyrics)!=list:
        text = index.wordNorm(lyrics)
    else:
        text = lyrics
    for v in vocab:
        if v in text:
            for (file, tf) in invIndex[str(vocab[v])]:
                if file == json_name:
                    word_vector.append(tf*idf[str(vocab[v])]) 
        else:
            word_vector.append(0)
    return (word_vector)


def makeQuery(query, vocab, idf):
# Build tf vector from query mapped on vocabulary for cosine similarity
    query_vector=[]
    wordToFind = query
    # wordToFind = index.wordNorm(query)
    for v in vocab:
        if v in wordToFind:
            query_vector.append((wordToFind.count(v)/len(wordToFind))*idf[str(vocab[v])])
        else:
            query_vector.append(0)
    return query_vector


def get_cosine(vec1, vec2):
#This metod take two vectors of number and calculate the cosine similarity.
    vec_1 = numpy.array(vec1)
    vec_2 = numpy.array(vec2)

    numerator = sum(vec_1 * vec_2)
    sum1 = sum(numpy.power(vec_1,2))
    sum2 = sum(numpy.power(vec_2,2))
    denominator = numpy.sqrt(sum1) * numpy.sqrt(sum2)

    try:
        return float(numerator) / denominator
    except:
        print("Zero division error")
        return 0

def generate_ngram(words, N=2):
    tokens = ["0s"] + words + ["0e"]
    ngrams = []
    for i in range(len(words)+3-N):
        ngrams.append(tokens[i:i+N])
    return ngrams

def find_score(query, vector_query, lyrics, invIndex, vocab, file, idf):

    tf_idf = vectorize(lyrics, invIndex, vocab, file, idf)
    
    # direction score
    cosine_score = get_cosine(vector_query, tf_idf)
    
    # scale score
    dot_score = np.dot(vector_query, tf_idf) # ?

    # co-occurence score
    lyrics_ngram = generate_ngram(lyrics, 2)
    ngram_score = 0
    dup = []
    for q in generate_ngram(query):
        if q in dup:
            continue
        dup.append(q)
        ngram_score += lyrics_ngram.count(q)/len(lyrics_ngram)
    
    return cosine_score,dot_score,ngram_score

def process_scores(scores):
    def softmax(vector):
        e = np.exp(vector)
        return e / e.sum()

    cs = [_[0][0] for _ in scores]
    ds = [_[0][1] for _ in scores]
    ns = [_[0][2] for _ in scores]
    file = [_[1] for _ in scores]
    return list(zip(list(softmax(cs)+softmax(ds)+softmax(ns)), file))

def unionQuery(query, invIndex, vocab, idf):
# Union query return the 10 tuples (json_name, TF_IDF) of the searched query
    scores = []
    q = index.wordNorm(query)
    vector_query = makeQuery(q, vocab, idf)
    visited = []
    for x in set(q):
        searched = toSearch(x, invIndex, vocab)
        for file, tf in searched: #for a single word
            if file in visited:
                continue
            visited.append(file)
            lyrics = index.getText(file) # lyrics
            
            score = find_score(q, vector_query, index.wordNorm(lyrics), invIndex, vocab, file, idf)
           
            scores.append([score, file])
    return sorted(process_scores(scores))[::-1][:10]

def getIntersection(query, invIndex, vocab):
# Get intersection find the name of the shared songs of the query
    q = index.wordNorm(query)
    doc = set(tup[0] for tup in toSearch(q[0], invIndex, vocab))
    for x in q:
        doc2 = toSearch(x, invIndex, vocab)
        doc = set([tup[0] for tup in doc2]) & doc
    return doc

def andQuery(query, invIndex, vocab, idf):
# Construct the vector normalized used by kmeans algorithm, and return the word cloud of cluster.
    files = getIntersection(query, invIndex, vocab)
    q = index.wordNorm(query)
    vector_query = makeQuery(q, vocab, idf)
    
    scores = []
    for file in files:
        lyrics = index.getText(file)
       # tf_idf = vectorize(lyrics, invIndex, vocab, file, idf)

        score = find_score(q, vector_query, index.wordNorm(lyrics), invIndex, vocab, file, idf)

        scores.append([score, file])
    return sorted(process_scores(scores))[::-1][:10]

############################# MAIN #############################

if __name__ == "__main__":

    # load vocab, inverted index, idf scores from local
    with open("II.json") as f:
        inverted_index = json.load(f)
    print("info: Inverted index (with tf scores) retrieved")

    with open("V.json") as f:
        vocab = json.load(f)
    print("info: Vocabulary retrieved")

    with open("IDF.json") as f:
        idf = json.load(f)
    print("info: IDF scores retrieved")

    while(True):
        n = input('0: for Lenient query\n1: for Strict query\n\nEnter choice:\t')

        if n == '0':
            query = input('Type query:')
            print('Searching query...')
            start_time = time.time()
            results = unionQuery(query, inverted_index, vocab, idf)
            print('Execution Time:', (time.time() - start_time))
            for result in results:
                print('SCORE:',result)
        elif n == '1':
            query = input('Type query:')
            print('Searching query...')
            start_time = time.time()
            results = andQuery(query, inverted_index, vocab, idf)
            print('Execution Time:', (time.time() - start_time))
            for result in results:
                print(result)
        else:
            break