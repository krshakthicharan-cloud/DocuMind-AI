import re
import math
from collections import Counter


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "of", "to", "in", "on", "for", "and", "or",
    "what", "why", "how", "when", "where", "which",
    "this", "that", "with", "from", "by", "as"
}


def tokenize(text):
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def create_embeddings(texts):
    tokenized = [tokenize(text) for text in texts]

    vocabulary = sorted(
        set(
            word
            for tokens in tokenized
            for word in tokens
        )
    )

    word_to_index = {
        word: index
        for index, word in enumerate(vocabulary)
    }

    document_count = len(texts)

    document_frequency = Counter()

    for tokens in tokenized:
        for word in set(tokens):
            document_frequency[word] += 1

    vectors = []

    for tokens in tokenized:

        term_frequency = Counter(tokens)

        vector = [0.0] * len(vocabulary)

        for word, count in term_frequency.items():

            index = word_to_index[word]

            tf = count / max(len(tokens), 1)

            idf = math.log(
                (document_count + 1)
                / (document_frequency[word] + 1)
            ) + 1

            vector[index] = tf * idf

        vectors.append(vector)

    return {
        "vectors": vectors,
        "vocabulary": vocabulary
    }
