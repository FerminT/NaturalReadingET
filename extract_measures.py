from Code.data_processing import utils
from pathlib import Path
from assign_fix_to_words import assign_fixations_to_words
import argparse
import pandas as pd

WEIRD_CHARS = ['¿', '?', '¡', '!', '.']  # Excluded '(', ')' and ',', ';', ':', '—', '«', '»', '“', '”', '‘', '’'
CHARS_MAP = {'—': '', '«': '', '»': '', '“': '', '”': '', '\'': '', '\"': '',
             '(': '', ')': '', ';': '', ',': '', ':': '',  '‘': '', '’': ''}

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
            - RC (Regression Count): number of regressions from a word
    
    Measures extracted across trials:
        Early:
            - LS (Likelihood of Skipping): number of first pass fixation durations of 0 divided by the number of trials
        Intermediate:
            - RR (Regression Rate): number of trials with a regression divided by the number of trials
"""


def extract_measures(items, chars_mapping, save_file):
    for item in items:
        screens_text = utils.load_json(item, 'screens_text.json')
        item_measures = process_item_screens(screens_text, item, chars_mapping)

        utils.save_measures_by_subj(item_measures, save_file)


def process_item_screens(screens_text, item, chars_mapping):
    measures = pd.DataFrame(columns=['subj', 'screen_idx', 'word_idx', 'word', 'excluded',
                                     'FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'RRT', 'SPRT', 'FC', 'RC'])
    word_index = 0
    for screenid in screens_text:
        screen_text = screens_text[screenid]
        screen_path = item / f'screen_{screenid}'
        trials = utils.get_dirs(screen_path)
        for trial in trials:
            extract_trial_screen_measures(trial, screen_text, chars_mapping, measures)

    return measures


def extract_trial_screen_measures(trial, screen_text, chars_mapping, measures):
    subj_name = trial.name
    screen_id = int(trial.parent.name.split('_')[1])
    word_index = get_word_pos_in_item(screen_id, measures, subj_name)
    for num_line, line in enumerate(screen_text):
        line_fixations = utils.load_json(trial, f'line_{num_line + 1}.json')
        line_words = line.split()
        for word_pos, word in enumerate(line_words):
            measures.loc[len(measures)] = [subj_name, screen_id, word_index, word, False, 0, 0, 0, 0, 0, 0, 0, 0]

            word_fixations = line_fixations[word_pos]
            is_left_out = has_weird_chars(word) or is_first_word(word_pos) or is_last_word(word_pos, line_words)
            if has_no_fixations(word_fixations) or is_left_out:
                measures.loc[word_index, 'excluded'] = is_left_out
                continue

            word = word.lower().translate(chars_mapping)
            fixation_count = count_fixations_on_word(word_fixations)

            word_index += 1


def get_word_pos_in_item(screen_id, measures, subj_name):
    word_index = 0 if screen_id == 1 else measures[measures['subj'] == subj_name]['word_idx'].max() + 1
    return word_index


def count_fixations_on_word(word_fixations):
    fixation_counter = 0
    for fixation in word_fixations['index']:
        # Count consecutive fixations on the word
        # This discards inter-word regressions, but counts intra-word regressions
        if fixation_counter == 0:
            prev_fix = fixation
        elif fixation != prev_fix + 1:
            break
        fixation_counter += 1
    return fixation_counter


def is_first_word(word_pos):
    return word_pos == 0


def is_last_word(word_pos, line_nwords):
    return word_pos == len(line_nwords) - 1


def has_weird_chars(word):
    return any(char in word for char in WEIRD_CHARS)


def has_no_fixations(word_fixations):
    return len(word_fixations) == 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Compute metrics based on words fixations')
    parser.add_argument('--data_path', type=str, default='Data/processed/words_fixations',
                        help='Where items\' fixations by word are stored')
    parser.add_argument('--stimuli', type=str, default='Stimuli',
                        help='Stimuli path. Used only for assigning fixations to words')
    parser.add_argument('--trials_path', type=str, default='Data/processed/trials',
                        help='Path to trials data. Used only for assigning fixations to words')
    parser.add_argument('--save_file', type=str, default='Data/processed/metrics.json')
    parser.add_argument('--item', type=str, default='all')
    args = parser.parse_args()

    data_path, save_file = Path(args.data_path), Path(args.save_file)
    if not data_path.exists():
        subj_paths = utils.get_dirs(Path(args.trials_path))
        assign_fixations_to_words(Path(args.stimuli), subj_paths, data_path)

    if args.item != 'all':
        item_paths = [data_path / args.item]
    else:
        item_paths = utils.get_dirs(data_path)

    chars_mapping = str.maketrans(CHARS_MAP)
    extract_measures(item_paths, chars_mapping, save_file)
