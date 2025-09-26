import torch
import torch.nn as nn
import torch.optim as optim
from collections import Counter
import numpy as np

# Example: Preprocessing and preparing data
def preprocess(text):
    return text.lower().split()

def create_skip_grams(tokenized_text, window_size):
    skip_grams = []
    for idx, center_word in enumerate(tokenized_text):
        for neighbor in tokenized_text[max(idx - window_size, 0): min(idx + window_size, len(tokenized_text)) + 1]:
            if neighbor != center_word:
                skip_grams.append([center_word, neighbor])
    return skip_grams

# Dummy corpus
text = "Your text data goes here. This is just an example."
tokenized_text = preprocess(text)
vocab = set(tokenized_text)
word_to_ix = {word: i for i, word in enumerate(vocab)}

# Skip-Gram pairs
skip_grams = create_skip_grams(tokenized_text, window_size=2)

# PyTorch Model
class SkipGramModel(nn.Module):
    def __init__(self, vocab_size, embedding_dim):
        super(SkipGramModel, self).__init__()
        self.embeddings = nn.Embedding(vocab_size, embedding_dim)
        self.linear = nn.Linear(embedding_dim, vocab_size)

    def forward(self, context_word):
        embeds = self.embeddings(context_word)
        out = self.linear(embeds)
        log_probs = torch.log_softmax(out, dim=1)
        return log_probs

# Model Initialization
EMBEDDING_DIM = 100
model = SkipGramModel(len(vocab), EMBEDDING_DIM)
loss_function = nn.NLLLoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# Training
for epoch in range(100):
    total_loss = 0
    for context, target in skip_grams:
        context_idx = torch.tensor([word_to_ix[context]], dtype=torch.long)
        log_probs = model(context_idx)
        loss = loss_function(log_probs, torch.tensor([word_to_ix[target]], dtype=torch.long))

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
    print(f'Epoch {epoch}, Loss: {total_loss}')

# Extracting Embeddings
word_embeddings = model.embeddings.weight.data
