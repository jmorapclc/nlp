import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Sample text
text = "NLTK is a leading platform for building Python programs to work with human language data."

# Lowercasing
text = text.lower()

# Removing punctuation
text = re.sub(r'[^\w\s]', '', text)

# Tokenization
nltk.download('punkt')
tokens = word_tokenize(text)

# Optionally remove stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
tokens = [w for w in tokens if not w in stop_words]

print(tokens)
