from collections import Counter
from os import listdir, path, pardir
import spacy

texts_dir   = path.join(pardir, pardir, 'Texts')
texts_files = listdir(texts_dir)

full_texts = ""
for text_file in texts_files:
    if text_file == 'Test': continue
    with open(path.join(texts_dir, text_file), 'r') as fp:
        text = fp.readlines()

    for line in text:
        full_texts += ' ' + line

nlp = spacy.load('es_dep_news_trf')
doc = nlp(full_texts)
# all tokens that arent stop words or punctuations
words = [token.text
         for token in doc
         if not token.is_stop and not token.is_punct]

word_freq = Counter(words)
print(word_freq)