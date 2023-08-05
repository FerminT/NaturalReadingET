from scripts.data_processing import utils
from pathlib import Path
from scripts.data_processing.assign_fix_to_words import assign_fixations_to_words
import argparse
import pandas as pd

PUNCTUATION_MARKS = ['?', '!', '.']
WEIRD_CHARS = ['¿', '?', '¡', '!', '.', '−', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
# Not excluded: '(', ')', ',', ';', ':', '—', '«', '»', '“', '”', '‘', '’'
CHARS_MAP = {'—': '', '‒': '', '−': '', '-': '', '«': '', '»': '',
             '“': '', '”': '', '\'': '', '\"': '', '‘': '', '’': '',
             '(': '', ')': '', ';': '', ',': '', ':': '', '.': '', '…': '',
             '¿': '', '?': '', '¡': '', '!': ''}

""" Script to compute eye-tracking measures for each item based on words fixations.
    Measures extracted on a single trial basis:
        Early:
            - FFD (First Fixation Duration): duration of the first, and only the first, fixation on a word
            - SFD (Single Fixation Duration): duration of the first and only fixation on a word 
                (equal to FFD for single fixations). Zero if the word has more than one fixation.
            - FPRT (First Pass Reading Time/Gaze Duration): sum of all fixations on a word before exiting
                (either to the right or to the left)
    
        Intermediate:
            - RPD (Regression Path Duration): sum of all fixations on a word after exiting it
    
        Late:
            - TFD (Total Fixation Duration): sum of all fixations on a word, including regressions
            - RRT (Re-Reading Time): regression path duration minus first pass reading time
            - SPRT (Second Pass Reading Time): sum of fixations after a word has been exited for the first time
            - FC (Fixation Count): number of fixations on a word
            - RC (Regression Count): number of regressions on a word
    
    Measures extracted across trials:
        Early:
            - LS (Likelihood of Skipping): number of first pass fixation durations of 0 divided by the number of trials
        Intermediate:
            - RR (Regression Rate): number of trials with a regression divided by the number of trials
"""


def extract_measures(items_wordsfix, chars_mapping, items_path, save_path):
    print(f'Extracting eye-tracking measures from trials...')
    for item in items_wordsfix:
        print(f'Processing "{item.stem}" trials')
        screens_text = utils.load_lines_text_by_screen(item.stem, items_path)
        item_measures, item_scanpaths = extract_item_measures(screens_text, item, chars_mapping)
        item_measures = add_aggregated_measures(item_measures)

        utils.save_measures_by_subj(item_measures, save_path / 'measures' / item.name)
        utils.save_subjects_scanpaths(item_scanpaths, save_path / 'scanpaths' / item.name)


def extract_item_measures(screens_text, item, chars_mapping):
    measures, words_fix = [], []
    trials = [pd.read_pickle(trial) for trial in utils.get_files(item, 'pkl')]
    for trial in trials:
        add_trial_measures(trial, screens_text, chars_mapping, measures, words_fix)

    measures = pd.DataFrame(measures, columns=['subj', 'screen', 'word_idx', 'word', 'excluded',
                                               'FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'RRT', 'SPRT', 'FC', 'RC'])

    words_fix = pd.DataFrame(words_fix, columns=['subj', 'fix_idx', 'fix_duration', 'word_idx'])
    scanpaths = build_scanpaths(words_fix, screens_text, chars_mapping)

    return measures, scanpaths


def build_scanpaths(words_fix, screens_text, chars_mapping):
    words_fix = words_fix.sort_values(['subj', 'fix_idx'])
    item_text = pd.DataFrame(divide_into_words(screens_text))
    scanpaths = {}
    for subj in words_fix['subj'].unique():
        subj_scanpath = item_text.iloc[words_fix[words_fix['subj'] == subj]['word_idx']][0].to_list()
        subj_scanpath = remove_consecutive_punctuations(subj_scanpath, chars_mapping)
        scanpaths[subj] = subj_scanpath

    return scanpaths


def add_aggregated_measures(item_measures):
    valid_measures = item_measures[~item_measures['excluded']]
    item_measures['LS'] = valid_measures.groupby(['word_idx'])['FPRT'].transform(lambda x: sum(x == 0) / len(x))
    item_measures['RR'] = valid_measures.groupby(['word_idx'])['RPD'].transform(lambda x: sum(x > 0) / len(x))

    return item_measures


def add_trial_measures(trial, screens_text, chars_mapping, measures, words_fix):
    word_idx = 0
    for screen in screens_text:
        screen_words, screen_fix = split_text_into_words(screens_text[screen]), trial[trial['screen'] == int(screen)]
        for word_pos, word in enumerate(screen_words):
            prev_word = screen_words[word_pos - 1] if word_pos > 0 else ''
            clean_word = word.lower().translate(chars_mapping)
            exclude = should_exclude_word(prev_word, word, clean_word, word_pos, line_num_words(word_pos, screen_fix))

            word_fix = screen_fix[screen_fix['word_pos'] == word_pos]
            add_word_fixations(word_fix, word_idx, words_fix)
            add_word_measures(word_idx, clean_word, exclude, word_fix, screen_fix, measures)
            word_idx += 1


def add_word_fixations(word_fix, word_idx, words_fix):
    if not has_no_fixations(word_fix):
        words_fix.extend([word_fix['subj'].iloc[0], fix_idx, fix_duration, word_idx]
                         for fix_idx, fix_duration in zip(word_fix['trial_fix'], word_fix['duration']))


def add_word_measures(word_idx, clean_word, exclude, word_fix, screen_fix, measures):
    subj_name, screen = word_fix['subj'].iloc[0], word_fix['screen'].iloc[0]
    if has_no_fixations(word_fix) or exclude:
        measures.append([subj_name, screen, word_idx, clean_word, exclude, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    else:
        ffd, sfd, fprt, rpd, tfd, rrt, sprt, fc, rc = word_measures(word_fix, screen_fix)
        measures.append([subj_name, screen, word_idx, clean_word, exclude, ffd, sfd, fprt, rpd, tfd, rrt, sprt, fc, rc])


def word_measures(word_fix, screen_fix):
    n_first_pass_fix = first_pass_n_fix(word_fix, screen_fix)
    ffd = word_fix['duration'].iloc[0] if n_first_pass_fix > 0 else 0
    sfd = ffd if len(word_fix['screen_fix']) == 1 else 0
    fprt = word_fix['duration'][:n_first_pass_fix].sum()
    rpd = word_fix['duration'][n_first_pass_fix:].sum()
    tfd = word_fix['duration'].sum()
    rrt = rpd - fprt
    sprt = tfd - fprt
    fc = len(word_fix['screen_fix'])
    rc = fc - n_first_pass_fix

    return ffd, sfd, fprt, rpd, tfd, rrt, sprt, fc, rc


def first_pass_n_fix(word_fix, screen_fix):
    # Count number of first pass reading fixations on word
    word_pos, fst_fix = word_fix['word_pos'].iloc[0], word_fix['screen_fix'].iloc[0]
    following_words_fix = screen_fix[screen_fix['word_pos'] > word_pos].dropna()
    regressive_saccade = (following_words_fix['screen_fix'] < fst_fix).values.any()
    if regressive_saccade:
        # Word was first skipped and then fixated (i.e., right-to-left saccade)
        return 0
    else:
        # This disregards intra-word regressions; inter-word regressions (rightward or leftward) are considered
        return n_consecutive_fix(word_fix['screen_fix'])


def n_consecutive_fix(fix_indices):
    fix_counter = 1
    for i, fix_idx in enumerate(fix_indices[:-1]):
        if fix_idx != fix_indices.iloc[i + 1] - 1:
            break
        fix_counter += 1

    return fix_counter


def remove_consecutive_punctuations(subj_scanpath, chars_mapping):
    for i, word in enumerate(subj_scanpath[:-1]):
        next_word = subj_scanpath[i + 1]
        subj_scanpath[i] = word if word != next_word else word.translate(chars_mapping)

    return subj_scanpath


def divide_into_words(screens_text):
    item_text = []
    for screenid in screens_text:
        screen_text = screens_text[screenid]
        item_text.extend(split_text_into_words(screen_text))
    return item_text


def split_text_into_words(text):
    return [word for line in text for word in line.split()]


def word_pos_in_item(screen_id, screens_text):
    word_index = sum([num_words(screens_text[str(screen)]) for screen in range(1, int(screen_id))])
    return word_index


def num_words(text):
    return sum([len(line.split()) for line in text])


def line_num_words(word_pos, screen_fix):
    line_num = screen_fix[screen_fix['word_pos'] == word_pos]['line'].iloc[0]
    line_nwords = screen_fix[screen_fix['line'] == line_num]['word_pos'].max()

    return line_nwords


def is_end_of_sentence(prev_word):
    return bool([char for char in PUNCTUATION_MARKS if char in prev_word])


def should_exclude_word(prev_word, word, clean_word, word_pos, line_nwords):
    return has_weird_chars(word) or has_no_chars(clean_word) or is_end_of_sentence(prev_word) \
            or is_first_word_in_line(word_pos) or is_last_word_in_line(word_pos, line_nwords)


def is_first_word_in_line(word_pos):
    return word_pos == 0


def is_last_word_in_line(word_pos, line_max_wordpos):
    return word_pos == line_max_wordpos


def has_no_chars(word):
    return len(word) == 0


def has_weird_chars(word):
    return any(char in word for char in WEIRD_CHARS)


def has_no_fixations(word_fix):
    return word_fix['trial_fix'].isna().all()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute metrics based on words fixations')
    parser.add_argument('--data_path', type=str, default='data/processed/words_fixations',
                        help='Where items\' fixations by word are stored')
    parser.add_argument('--items_path', type=str, default='stimuli',
                        help='Items path, from which the stimuli (items\' text) is extracted')
    parser.add_argument('--trials_path', type=str, default='data/processed/trials',
                        help='Path to trials data.')
    parser.add_argument('--save_path', type=str, default='data/processed')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, trials_path, items_path, save_path = Path(args.data_path), Path(args.trials_path), \
        Path(args.items_path), Path(args.save_path)
    if not data_path.exists():
        subjects = utils.get_dirs(trials_path)
        items = utils.get_items(items_path, args.item)
        assign_fixations_to_words(items, subjects, data_path)

    if args.item != 'all':
        items_wordsfix = [data_path / args.item]
    else:
        items_wordsfix = utils.get_dirs(data_path)

    chars_mapping = str.maketrans(CHARS_MAP)
    extract_measures(items_wordsfix, chars_mapping, items_path, save_path)
