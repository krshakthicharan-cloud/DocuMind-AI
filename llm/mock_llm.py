import re


STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were",
    "of", "to", "in", "on", "for", "and", "or",
    "what", "why", "how", "when", "where", "which",
    "this", "that", "with", "from", "by", "as",
    "do", "does", "did"
}


def get_keywords(question):
    words = re.findall(
        r"\b[a-zA-Z0-9]+\b",
        question.lower()
    )

    return [
        word
        for word in words
        if word not in STOP_WORDS
    ]


def clean_text(text):
    text = re.sub(
        r"Page \d+ of \d+",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def split_into_sentences(text):
    text = clean_text(text)

    # Handle PDF line breaks as sentence boundaries
    parts = re.split(
        r"(?<=[.!?])\s+|(?<=\.)\s*(?=[A-Z])",
        text
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def score_sentence(sentence, keywords):

    sentence_lower = sentence.lower()

    score = 0

    for keyword in keywords:

        if keyword in sentence_lower:
            score += 1

    # Strong bonus when the question's main phrase
    # appears directly in the sentence.
    if len(keywords) >= 2:

        phrase = " ".join(keywords)

        if phrase in sentence_lower:
            score += 5

    return score


def find_best_sentence(question, text):

    keywords = get_keywords(question)

    if not keywords:
        return ""

    sentences = split_into_sentences(text)

    scored_sentences = []

    for sentence in sentences:

        score = score_sentence(
            sentence,
            keywords
        )

        if score > 0:

            scored_sentences.append(
                (score, sentence)
            )

    if not scored_sentences:
        return ""

    scored_sentences.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return scored_sentences[0][1]


def generate_mock_answer(question, retrieved_results):

    if not retrieved_results:

        return (
            "The information is not available "
            "in the uploaded document."
        )

    best_answer = ""
    best_score = -1
    best_page = None

    keywords = get_keywords(question)

    for result in retrieved_results:

        sentences = split_into_sentences(
            result["text"]
        )

        for sentence in sentences:

            score = score_sentence(
                sentence,
                keywords
            )

            if score > best_score:

                best_score = score
                best_answer = sentence
                best_page = result["page"]

    if not best_answer:

        return (
            "The information is not available "
            "in the uploaded document."
        )

    return (
        "Based on the uploaded document:\n\n"
        f"{best_answer}\n\n"
        f"Source: Page {best_page}"
    )