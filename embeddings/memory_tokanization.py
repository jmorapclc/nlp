import nltk
from nltk.tokenize import word_tokenize

def tokenize_chunks(chunk_generator):
    for chunk in chunk_generator:
        for sentence in nltk.sent_tokenize(chunk):
            yield word_tokenize(sentence)
