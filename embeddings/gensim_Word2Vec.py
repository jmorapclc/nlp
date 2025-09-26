from gensim.models import Word2Vec

# Your tokenized sentences
sentences = [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'sentence']]

# Train a model
model = Word2Vec(sentences, vector_size=100, window=5, min_count=1, workers=4)

# Get an embedding for a word
word_embedding = model.wv['sentence']
