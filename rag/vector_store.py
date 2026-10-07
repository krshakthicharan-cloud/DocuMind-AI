import math
import re

STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "of", "to", "in", "on", "for", "and", "or",
    "what", "why", "how", "when", "where", "which",
    "this", "that", "with", "from", "by", "as",
    "do", "does", "did"
}


def get_words(text):
    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


class VectorStore:
    def __init__(self, embedding_data, chunks=None):
        self.vectors = embedding_data["vectors"]
        self.vocabulary = embedding_data["vocabulary"]
        self.chunks = chunks or []

    def search(self, query_embedding, top_k=3, query=None):
        query_vector = query_embedding["vectors"][0]
        scores = []

        query_words = []
        if query:
            query_words = [
                word for word in get_words(query)
                if word not in STOP_WORDS
            ]

        for index, document_vector in enumerate(self.vectors):

            cosine_score = self.cosine_similarity(
                query_vector,
                document_vector
            )

            phrase_score = 0.0
            word_score = 0.0
            title_score = 0.0
            definition_score = 0.0

            if query and index < len(self.chunks):
                chunk_text = self.chunks[index]["text"].lower()
                query_text = query.lower().strip()

                # Exact question phrase
                if query_text in chunk_text:
                    phrase_score += 1.0

                # Individual keyword matching
                if query_words:
                    chunk_words = set(get_words(chunk_text))

                    matched_words = sum(
                        1 for word in query_words
                        if word in chunk_words
                    )

                    word_score = matched_words / len(query_words)

                # Consecutive keyword matching
                if len(query_words) >= 2:
                    for i in range(len(query_words) - 1):
                        phrase = (
                            query_words[i]
                            + " "
                            + query_words[i + 1]
                        )

                        if phrase in chunk_text:
                            phrase_score += 0.8

                # Prefer matches near the beginning of the chunk
                first_line = chunk_text.split("\n")[0].strip()

                for word in query_words:
                    if word in first_line:
                        title_score += 0.5

                # Strongly prefer definition-style matches.
                # Example:
                # "Stack — a linear data structure..."
                for word in query_words:
                    definition_patterns = [
                        f"{word} —",
                        f"{word} -",
                        f"{word}:",
                        f"{word} is ",
                        f"{word} are "
                    ]

                    if any(
                        pattern in chunk_text
                        for pattern in definition_patterns
                    ):
                        definition_score += 1.0

            final_score = (
                0.25 * cosine_score
                + 0.25 * word_score
                + 0.15 * phrase_score
                + 0.10 * title_score
                + 0.25 * definition_score
            )

            scores.append((final_score, index))

        scores.sort(
            key=lambda item: item[0],
            reverse=True
        )

        results = scores[:top_k]

        distances = [
            1 - score
            for score, index in results
        ]

        indices = [
            index
            for score, index in results
        ]

        return [distances], [indices]

    @staticmethod
    def cosine_similarity(vector_a, vector_b):
        dot_product = sum(
            a * b
            for a, b in zip(vector_a, vector_b)
        )

        magnitude_a = math.sqrt(
            sum(a * a for a in vector_a)
        )

        magnitude_b = math.sqrt(
            sum(b * b for b in vector_b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (
            magnitude_a * magnitude_b
        )
