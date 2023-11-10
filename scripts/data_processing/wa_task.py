import pandas as pd
from scripts.data_processing.utils import load_matfile, get_dirs, load_answers

DEACC = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}

WORDS_MAPPING = {
    'messi': '',
    'matias': '',
    'tomas': '',
    'anios': 'años',
    'anio': 'año',
    'anos': 'años',
    '10': 'diez',
    '21': 'veintiuno',
    'xxi': 'veintiuno',
    'pequenio': 'pequeño',
    'seniora': 'señora',
    'senior': 'señor',
    'seniorita': 'señorita',
    'maniana': 'mañana',
    'ojo': 'ojos',
}


def parse_wa_task(questions_file, participants_path):
    questions = load_matfile(str(questions_file))['stimuli_questions']
    subjects = get_dirs(participants_path)
    items_words = {}
    subjects_associations = {}
    for item_dict in questions:
        item = item_dict['title']
        items_words[item] = list(item_dict['words'])

    for subj in subjects:
        subj_trials = {trial.name: trial for trial in get_dirs(subj)}
        for item in items_words:
            item_words = map(parse_cue, items_words[item])
            trial_answers = []
            if item in subj_trials:
                trial_answers = load_answers(subj_trials[item], filename='words.pkl')
            for i, word in enumerate(item_words):
                answer = None
                if i < len(trial_answers):
                    answer = parse_answer(trial_answers[i])
                subjects_associations[word] = subjects_associations.get(word, []) + [answer]

    subjects_associations = pd.DataFrame.from_dict(subjects_associations, orient='index')
    subjects_associations = subjects_associations.loc[:, :len(subjects) - 1]
    subjects_associations.columns = [subj.name for subj in subjects]
    words_associations = get_words_associations(subjects_associations)

    return subjects_associations, words_associations


def parse_cue(cue):
    cue = cue.lower()
    cue = ''.join([DEACC[char] if char in DEACC else char for char in cue])
    return cue


def parse_answer(answer):
    if not isinstance(answer, str):
        answer = None
    else:
        answer = answer.lower()
        answer = answer.replace(';', 'ñ')
        if len(answer.split()) > 1:
            answer = answer.split()[-1]
        if answer in WORDS_MAPPING:
            answer = WORDS_MAPPING[answer]
        answer = ''.join([char for char in answer if char.isalpha()])
    return answer


def get_words_associations(subjects_associations):
    answers_freq = answers_frequency(subjects_associations)
    n_answers = answers_frequency(subjects_associations, normalized=False)
    words_pairs = []
    for cue in answers_freq:
        cue_answers = answers_freq[cue]
        for answer in cue_answers.keys():
            words_pairs.append((cue, answer, n_answers[cue][answer], cue_answers[answer]))

    words_pairs = pd.DataFrame(words_pairs, columns=['cue', 'answer', 'n', 'freq'])
    return words_pairs


def answers_frequency(words_associations, normalized=True):
    return {word: words_associations.loc[word].value_counts(normalize=normalized) for word in words_associations.index}
