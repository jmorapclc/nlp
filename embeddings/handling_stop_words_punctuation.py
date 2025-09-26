from nltk.corpus import stopwords
import string

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def clean_tokens(token_generator):
    for tokens in token_generator:
        # Removing stop words and punctuation
        yield [token.lower() for token in tokens if token not in stop_words and token not in string.punctuation]
