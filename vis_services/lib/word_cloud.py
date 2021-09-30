
#python -m spacy download en # Downloads en_core_web_sm by default
import os
import spacy
from collections import Counter
from spacy.matcher import Matcher
import math
nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner']) # Loads en_core_web_sm by default

def generate_wordcloud(records, n_most_common = 100, accepted_pos = ('NN', 'NNP', 'NNS', 'NNPS', 'JJ', 'RB', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ')):
    # List of English POS: https://spacy.io/api/annotation
    # Segment text into tokens and assign part-of-speech tags:
    docs = []
    for doc in nlp.pipe(records, batch_size=10000):
        docs.append(doc)

    # Prepare matcher to select only some tokens
    matcher = Matcher(nlp.vocab)
    for tag in accepted_pos:
        matcher.add(tag, [[{'TAG': tag, 'IS_ALPHA': True, 'IS_PUNCT': False, 'IS_SPACE': False, 'IS_STOP': False, 'LIKE_NUM': False, 'LIKE_URL': False, 'LIKE_EMAIL': False}]])

    total_token_occurrences_counter = Counter() # Total number of occurrences
    n_records_with_token = Counter() # Number of records that contain a token
    for doc in docs:
        # Select only the tokens that interest us
        matched_tokens = []
        matches = matcher(doc)
        for match_id, start, end in matches:
            matched_token = doc[start]
            if len(matched_token) > 2:
                matched_tokens.append(doc[start])
        token_occurences_counter = Counter()
        for token in matched_tokens:
            previous_occurences = token_occurences_counter.get(token.lemma, 0)
            token_occurences_counter[token.lemma_] = previous_occurences + 1
            if previous_occurences == 0:
                # First time this token is found in this document
                n_records_with_token[token.lemma_] += 1
        total_token_occurrences_counter += token_occurences_counter

    n_records = len(records)*1.
    word_cloud_json = {}
    ## Select most common words in total
    #for token, count in total_token_occurrences_counter.most_common(n_most_common):
        #record_count = n_records_with_token[token]
        #smooth_idf = math.log10(1 + n_records / (1 + record_count))
        #word_cloud_json[token] = { "idf": smooth_idf, "record_count": record_count, "total_occurrences": count}
    ## Select top words that appear in more documents
    for token, record_count in n_records_with_token.most_common(n_most_common):
        count = total_token_occurrences_counter[token]
        smooth_idf = math.log10(1 + n_records / (1 + record_count))
        word_cloud_json[token] = { "idf": smooth_idf, "record_count": record_count, "total_occurrences": count}
    return word_cloud_json


if __name__ == "__main__":
    text1 = "This is a sentence. And this is another sentence (although less important). I bought a car at http://www.car.com."
    text2 = "Testing is good! href='#three' 2.3e2 + 4 = $\\alpha$"
    records = [text1, text2]
    word_cloud_json = generate_wordcloud(records, n_most_common = 100, accepted_pos = ('NN', 'NNP', 'NNS', 'NNPS',))
