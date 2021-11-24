import nltk
from nltk.tokenize import RegexpTokenizer
nltk.download("stopwords")
from nltk.corpus import stopwords
import os.path
from os.path import expanduser
import json
import codecs
import math
import enchant
from nltk.stem.snowball import SnowballStemmer

def wordNorm(text):
    """
        input:
            lyrics/query (original text)
        output:
            list of words after the following processes.
                - tokenize
                - remove stop words
                - stemming
                - remove non-english words
    """
    stemmer = SnowballStemmer("english")
    new_text = []
    tokenizer = RegexpTokenizer(r'\w+')
    # tokenize
    word_list = tokenizer.tokenize(text.lower())
    # remove stop words
    filtered_words_en = [word for word in word_list if word not in stopwords.words('english')]
    # stemming
    stemming_words = [stemmer.stem(word) for word in filtered_words_en]
    # remove non-english words
    d = enchant.Dict("en_US")
    for word in stemming_words:
        if not word.isdigit() and len(word)>1 and d.check(word):
            new_text.append(word)
    return new_text #list of processed words

def allWords(jsondir):
    """
        input:
            path to json directory containing all lyric jsons
        output:
            bag of words - list
    """
    k = []
    count = 0
    for file in os.listdir(jsondir):
        try:
            with open(jsondir + "/" + file, "r") as f:
                d = json.loads(f.read())
            
            count += 1
        except:
            continue
        word_list = wordNorm(d['lyrics'])
        for item in word_list:
            k.append(item)
        print("info: ",count, 'json file processed into Vocabulary')
    return k

def createVocab(allwords):
    """
        input:
            bag of words - list
        output:
            vocabulary - dict
                with term - termID mapping
    """
    vocabulary = {}
    word_list = sorted(list(set(allwords)))
    for ID, elem in enumerate(word_list):
        vocabulary.update({elem : ID})
    return vocabulary

def termFreq(term, txt):
    """
       input:
            term - word (string)
            text - document/lyrics (string)
       ouput:
            normalized term frequency (float)
    """
    count = 0
    if len(txt) <= 0:
        return 0
    else:
        for t in txt:
            if t == term:
                count += 1
        return count / len(txt)



def invertedIndex(vocab ,jsondir):
    """
        input:
            vocab   - Vocabulary
            jsondir - path of folder containing all lyric dictionaries
        ouput:
            invertedIndex
                termID: posting list mapping,
                    where each posting list entry contains (document name, tf score of term in the document)
    """
    invIndex = {}
    counter = 0
    for file in os.listdir(jsondir):
        try:
            with open(jsondir + "/" + file, "r") as f:
                d = json.loads(f.read())
            counter += 1
            txt = wordNorm(d['lyrics'])
            for word in vocab:
                tf = termFreq(word, txt)
                if(tf>0):
                    try:
                        invIndex[vocab[word]] += [(file, tf)]
                    except:
                        invIndex[vocab[word]] = [(file, tf)]


            print("info: ",counter, " lyrics processed into Inverted Index")
        except:
            print("error: Issue with ",file)
            pass
    return invIndex

def idf(invIndex, vocab, jsondir):
    """
        description:
            returns idf scores of each term in the vocabulary
    """
    N = len(os.listdir(jsondir))
    idf = {}
    for term in vocab:
        idf[vocab[term]] = math.log((N / len(invIndex[vocab[term]])))
    return(idf)

def getText(file):
    """
        description:
            gets lyrics of a particular song, using the file name
    """
    with open("json/"+file) as f:
        lyrics = json.load(f)["lyrics"]
    return lyrics

############################# MAIN #############################

if __name__ == "__main__":
    bow = allWords("json")
    vocab = createVocab(bow)
    inverted_index = invertedIndex(vocab, "json")

    with open("II.json","w") as f:
        json.dump(inverted_index, f)
    print("info: Inverted index (with tf scores) saved")

    with open("V.json","w") as f:
        json.dump(vocab, f)
    print("info: Vocabulary saved")

    idf_scores = idf(inverted_index, vocab, "json")
    with open("IDF.json","w") as f:
        json.dump(idf_scores, f)
    print("info: IDF scores saved")
