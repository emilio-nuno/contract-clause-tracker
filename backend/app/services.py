from nltk import sent_tokenize

def parse_sentences(raw_text: str) -> list[str]:
    
    sentence_list = sent_tokenize(raw_text)
    
    return sentence_list