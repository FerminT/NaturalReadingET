from os import listdir, path, pardir
import pandas as pd
import spacy
import json

texts_dir   = path.join(path.pardir, 'Texts')
texts_files = listdir(texts_dir)

nlp = spacy.load('es_dep_news_trf')

max_chars = 10
min_word_freq = 100
min_sentence_length = 5
max_sentence_length = 30
uncommon_characters = ['¿', '?', '¡', '!', '\"', '”', '“', '«', '»', '(', ')', '—']

words_freq_stats = 'words_freq.csv'
words_freq = pd.read_csv(words_freq_stats)

texts_properties = {}

for text_file in texts_files:
    with open(path.join(texts_dir, text_file), 'r', encoding='utf-8') as fp:
        text = fp.read()
    
    parsed_text = nlp(text)
    short_sentences  = []
    long_sentences   = []
    unfrequent_words = {}

    total_uncommon_chars = 0
    total_sentences = 0
    total_words     = 0
    total_long_words = 0
    for sentence in parsed_text.sents:
        words = sentence.text.split(' ')
        number_of_words = len(words)
        # Exclude sentences consisting only of line breaks ('\n')
        if number_of_words <= 1: continue
        total_sentences += 1
        total_words += number_of_words

        if number_of_words <= min_sentence_length:
            short_sentences.append(sentence.text)
        elif number_of_words >= max_sentence_length:
            long_sentences.append(sentence.text)
        
        for token in sentence:
            if token.is_punct:
                if token.text in uncommon_characters:
                    total_uncommon_chars += 1
                continue

            word = token.text

            if len(word) >= max_chars:
                total_long_words += 1

            lowercase_word_freq = words_freq[words_freq['word'] == word.lower()]
            word_freq = lowercase_word_freq if not lowercase_word_freq.empty else words_freq[words_freq['word'] == word]
            if not word_freq.empty:
                if (word_freq['cnt'] <= min_word_freq).bool():
                    if not word in unfrequent_words:
                        unfrequent_words[word] = 1
                    else:
                        unfrequent_words[word] += 1

    texts_properties[text_file] = {'long_words': str(total_long_words) + '/' + str(total_words),
        '#short_sentences': str(len(short_sentences)) + '/' + str(total_sentences), \
            '#long_sentences': str(len(long_sentences)) + '/' + str(total_sentences), \
                '#weird_chars': total_uncommon_chars, \
                    '#unfrequent_words': str(len(unfrequent_words)) + '/' + str(total_words), \
                        'short_sentences': short_sentences, 'unfrequent_words': unfrequent_words}

with open('texts_properties.json', 'w', encoding='utf-8') as fp:
    json.dump(texts_properties, fp, indent=4, ensure_ascii=False)