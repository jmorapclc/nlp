from gensim.models import KeyedVectors

# Load pre-trained Word2Vec model
model = KeyedVectors.load_word2vec_format('path/to/word2vec/model.bin', binary=True)

# Get an embedding for a word
word_embedding = model['computer']
