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
    # Text normalizer: split the text in array without all spaces, stopwords, numbers
    # Stemming all words, and return only the english words.
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
    # This function returns in an array all the words of all lyrics (saved as JSON file)
    k = []
    count = 0
    for file in os.listdir(jsondir):
        try:
            with open(jsondir + "/" + file, "r") as f:
                d = json.loads(f.read())
            # print(d)
            count += 1
        except:
            continue
        word_list = wordNorm(d['lyrics'])
        for item in word_list:
            k.append(item)
        print(count, '---> JSON IN VOCABULARY')
    return k

def createVocab(allwords):
    # This function take in input an array with all words, create the set and assign an ID to each term
    # vocabulary = {term : termID}
    vocabulary = {}
    word_list = sorted(list(set(allwords)))
    for ID, elem in enumerate(word_list):
        vocabulary.update({elem : ID})
    return vocabulary

def term_freq(term, txt):
# Compute the term frequencies in a given text
    count = 0
    if len(txt) <= 0:
        return 0
    else:
        for t in txt:
            if t == term:
                count += 1
        return count / len(txt)



def invertedIndex(vocab ,jsondir):
    # invIndex = {termID : (doc, TF)}
    invIndex = {}
    counter = 0
    for file in os.listdir(jsondir):
        try:
            with open(jsondir + "/" + file, "r") as f:
                d = json.loads(f.read())
            counter += 1
            txt = wordNorm(d['lyrics'])
            for word in vocab:
                tf = term_freq(word, txt)
                if(tf>0):
                    try:
                        invIndex[vocab[word]] += [(file, tf)]
                    except:
                        invIndex[vocab[word]] = [(file, tf)]


            print(counter, "----->IN INVERTED INDEX!")
        except:
            print("!!!!!!!!!!!IN EXCEPT",file)
            pass
    return invIndex

def idf(invIndex, vocab, jsondir):
    D = len(os.listdir(jsondir))
    idf = {}
    for term in vocab:
        idf[vocab[term]] = math.log((D / len(invIndex[vocab[term]])))
    return(idf)

def getText(file):
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
