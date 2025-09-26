from gensim.models import Word2Vec

chunk_generator = read_file_in_chunks('path_to_large_file.txt')
token_generator = tokenize_chunks(chunk_generator)
clean_token_generator = clean_tokens(token_generator)

model = Word2Vec(sentences=clean_token_generator, vector_size=100, window=5, min_count=1, workers=4)
