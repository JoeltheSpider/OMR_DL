from types import coroutine
import indexing as index
import json
import time
import numpy
import numpy as np
import matplotlib.pyplot as plt

def toSearch(query, invertedInd, vocab):
    """
        input:
            query, invertedIndex, vocabulary
        output:
            concatenated posting list corresponding to all terms in the query,
                where each posting list entry contains (document name, tf score of term in the document) 
    """
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


def vectorize(lyrics, invIndex, vocab, document_name, idf):
    """
        output:
            tf-idf vector
        description:
            calculate tf-idf score for document with 'document_name'
    """
    word_vector = []
    if type(lyrics)!=list:
        text = index.wordNorm(lyrics)
    else:
        text = lyrics
    for v in vocab:
        if v in text:
            for (file, tf) in invIndex[str(vocab[v])]:
                if file == document_name:
                    word_vector.append(tf*idf[str(vocab[v])]) 
        else:
            word_vector.append(0)
    return word_vector


def makeQuery(query, vocab, idf):
    """
        ouptut:
            tf-idf score of query vector
    """
    query_vector=[]
    for v in vocab:
        if v in query:
            query_vector.append((query.count(v)/len(query))*idf[str(vocab[v])])
        else:
            query_vector.append(0)
    return query_vector


def getCosine(vec1, vec2):
    """
        output:
            cosine similarity of two vectors
    """
    vec_1 = numpy.array(vec1)
    vec_2 = numpy.array(vec2)

    numerator = sum(vec_1 * vec_2)
    sum1 = sum(numpy.power(vec_1,2))
    sum2 = sum(numpy.power(vec_2,2))
    denominator = numpy.sqrt(sum1) * numpy.sqrt(sum2)

    try:
        return float(numerator) / denominator
    except:
        print("error: Zero division error")
        return 0

def generateNgram(words, N=2):
    """
        input:
            words - list of string
            N - integer (hyper param for N-gram)
        output:
            Generate N-grams from 'words'
    """
    tokens = ["0s"] + words + ["0e"]
    ngrams = []
    for i in range(len(words)+3-N):
        ngrams.append(tokens[i:i+N])
    return ngrams

def findScore(query, vector_query, lyrics, invIndex, vocab, file, idf):
    """
        description:
            Find separate scores for a document based on the query.
            - cosine score - for direction
            - dot product score - for scale
            - ngram score - for co-occurence of terms in query 
    """
    tf_idf = vectorize(lyrics, invIndex, vocab, file, idf)
    
    # direction score
    cosine_score = getCosine(vector_query, tf_idf)
    
    # scale score
    dot_score = np.dot(vector_query, tf_idf) # ?

    # co-occurence score
    lyrics_ngram = generateNgram(lyrics, 2)
    ngram_score = 0
    dup = []
    for q in generateNgram(query):
        if q in dup:
            continue
        dup.append(q)
        ngram_score += lyrics_ngram.count(q)/len(lyrics_ngram)
    
    return cosine_score,dot_score,ngram_score

def processScores(scores):
    """
        description:
            find softmax of each separate scores and compute a single score
    """
    def softmax(vector):
        e = np.exp(vector)
        return e / e.sum()

    cs = [_[0][0] for _ in scores]
    ds = [_[0][1] for _ in scores]
    ns = [_[0][2] for _ in scores]
    file = [_[1] for _ in scores]
    return list(zip(list(softmax(cs)+softmax(ds)+softmax(ns)), file))

def unionQuery(query, invIndex, vocab, idf, q_vector=[]):
    """
        description:
            Process documents even if one query term is present  
    """
    scores = []
    q = index.wordNorm(query)
    if len(q_vector)==0:
        vector_query = makeQuery(q, vocab, idf)
    else:
        vector_query = q_vector
    visited = []
    for x in set(q):
        searched = toSearch(x, invIndex, vocab)
        if searched == []:
            continue
        for file, tf in searched: 
            if file in visited:
                continue
            visited.append(file)
            lyrics = index.getText(file) 
            
            score = findScore(q, vector_query, index.wordNorm(lyrics), invIndex, vocab, file, idf)
           
            scores.append([score, file])
    if scores == []:
        print("No results found")
        return ["None"]

    return sorted(processScores(scores))[::-1][:10]

def getIntersection(query, invIndex, vocab):
    """
        description:
            Find common documents
    """
    q = index.wordNorm(query)
    doc = set(tup[0] for tup in toSearch(q[0], invIndex, vocab))
    for x in q:
        doc2 = toSearch(x, invIndex, vocab)
        doc = set([tup[0] for tup in doc2]) & doc
    return doc

def andQuery(query, invIndex, vocab, idf, q_vector=[]):
    """
        description:
            Process documents only if all query terms are present
    """
    files = getIntersection(query, invIndex, vocab)
    q = index.wordNorm(query)
    if len(q_vector)==0:
        vector_query = makeQuery(q, vocab, idf)
    else:
        vector_query = q_vector
    if files == []:
        print("No results found")
        return ["None"]

    scores = []
    for file in files:
        lyrics = index.getText(file)
        
        score = findScore(q, vector_query, index.wordNorm(lyrics), invIndex, vocab, file, idf)

        scores.append([score, file])
    return sorted(processScores(scores))[::-1][:10]

def RRFeedback(results, query, invIndex, vocab, idf, feedback, beta=0.75, gamma=0.25):
    """
        output:
            results after RR feedback
    """
    ind = 0
    vector_query = np.array(makeQuery(index.wordNorm(query), vocab, idf))
    for result in results:
        lyrics = index.getText(result[1])
        if feedback[ind]:
            vector_query += beta* np.array(vectorize(lyrics, invIndex, vocab, result[1], idf)) * (1/feedback.count(1))
        else:
            vector_query -= gamma* np.array(vectorize(lyrics, invIndex, vocab, result[1], idf)) * (1/feedback.count(0))
        ind +=1
    print("info: query vector after rocchio feedback: ", vector_query)
    return vector_query


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

    # user interface
    while(True):
        n = input('0: for Lenient query\n1: for Strict query\n\nEnter choice:\t')

        if n == '0':
            query = input('Type query:')
            print('Searching query...')
            start_time = time.time()
            results = unionQuery(query, inverted_index, vocab, idf)
            print('Execution Time:', (time.time() - start_time))
            ind = 0
            for result in results:
                print(ind+1, '- SCORE:',result)
                ind+=1
            feedback = [int(z) for z in input("Enter relevant/not: ").split(" ")]
            q_vector = RRFeedback(results, query, inverted_index, vocab, idf, feedback)
            results = unionQuery(query, inverted_index, vocab, idf, q_vector)
            ind = 0
            for result in results:
                print(ind+1, '- SCORE:',result)
                ind+=1
        elif n == '1':
            query = input('Type query:')
            print('Searching query...')
            start_time = time.time()
            results = andQuery(query, inverted_index, vocab, idf)
            print('Execution Time:', (time.time() - start_time))
            ind = 0
            for result in results:
                print(ind+1, '- SCORE:',result)
                ind+=1
            feedback = [int(z) for z in input("Enter relevant/not: ").split(" ")]
            q_vector = RRFeedback(results, query, inverted_index, vocab, idf, feedback)
            results = andQuery(query, inverted_index, vocab, idf, q_vector)
            ind = 0
            for result in results:
                print(ind+1, '- SCORE:',result)
                ind+=1
        else:
            break