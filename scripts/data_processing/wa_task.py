import pandas as pd

DEACC = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}

WORDS_MAPPING = {
    'anio': 'año',
    'anos': 'años',
    '21': 'veintiuno',
    'xxi': 'veintiuno',
    'pequenio': 'pequeño',
    'seniora': 'señora',
    'senior': 'señor',
    'seniorita': 'señorita',
    'maniana': 'mañana',
    'ojo': 'ojos',
}


def parse_cue(cue):
    cue = cue.lower()
    cue = ''.join([DEACC[char] if char in DEACC else char for char in cue])
    return cue


def parse_answer(answer):
    if isinstance(answer, str):
        answer = None
    else:
        answer = answer.lower()
        answer = answer.replace(';', 'ñ')
        if len(answer.split()) > 1:
            answer = answer.split()[-1]
        if answer in WORDS_MAPPING:
            answer = WORDS_MAPPING[answer]
    return answer


def get_words_associations(subjects_associations):
    freq = answers_frequency(subjects_associations)
    words_pairs = []
    for cue in freq:
        cue_answers = freq[cue]
        for answer in cue_answers.keys():
            words_pairs.append((cue, answer, cue_answers[answer]))

    words_pairs = pd.DataFrame(words_pairs, columns=['cue', 'answer', 'freq'])
    return words_pairs


def answers_frequency(words_associations, normalized=True):
    return {word: words_associations.loc[word].value_counts(normalize=normalized) for word in words_associations.index}
