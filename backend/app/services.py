from nltk import sent_tokenize

def parse_sentences(raw_text: str) -> list[str]:
    return sent_tokenize(raw_text.strip())