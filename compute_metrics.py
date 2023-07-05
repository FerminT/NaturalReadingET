from Code.data_processing import utils
from pathlib import Path
from assign_fix_to_words import assign_fixations_to_words
import argparse
import pandas as pd

WEIRD_CHARS = ['¿', '?', '¡', '!', '.']  # Excluded '(', ')' and ',', ';', ':', '—', '«', '»', '“', '”', '‘', '’'
CHARS_MAP = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
             'Á': 'A', 'É': 'E', 'I': 'I', 'Ó': 'O', 'Ú': 'U',
             '—': '', '«': '', '»': '', '“': '', '”': '', '‘': '', '’': '', '\'': '', '\"': '',
             '(': '', ')': '', ';': '', ',': '', ':': ''}

""" Script to compute eye-tracking measures for each item based on words fixations.
    Measures computed on a single trial basis:
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
    
    Measures computed across trials:
        Early:
            - LS (Likelihood of Skipping): number of first pass fixations divided by the number of trials
        Intermediate:
            - RR (Regression Rate): number of trials with a regression divided by the number of trials
"""


def compute_metrics(items, save_file, chars_mapping):
    metrics_by_word = {}
    for item in items:
        screens_text = utils.load_json(item, 'screens_text.json')
        process_item_screens(screens_text, item, metrics_by_word, chars_mapping)

    utils.save_json(metrics_by_word, save_file.parent, save_file.name)


def process_item_screens(screens_text, item, metrics_by_word, chars_mapping):
    measurements = pd.DataFrame(columns=['subj', 'word', 'FFD', 'SFD', 'FPRT', 'RPD', 'TFD', 'RRT', 'SPRT', 'FC', 'RC'])
    for screenid in screens_text:
        screen_text = screens_text[screenid]
        screen_path = item / f'screen_{screenid}'
        trials = utils.get_dirs(screen_path)
        for trial in trials:
            compute_trial_metrics(trial, screen_text, metrics_by_word, chars_mapping)


def compute_trial_metrics(trial, screen_text, metrics_by_word, chars_mapping):
    for num_line, line in enumerate(screen_text):
        line_fixations = utils.load_json(trial, f'line_{num_line + 1}.json')
        line_words = line.split()
        for word_pos, word in enumerate(line_words):
            word_fixations = line_fixations[word_pos]
            if has_no_fixations(word_fixations) or has_weird_chars(word) or \
                    is_first_word(word_pos) or is_last_word(word_pos, line_words):
                continue
            word = word.lower().translate(chars_mapping)
            fixations_on_word = count_fixations_on_word(word_fixations)
            if word not in metrics_by_word:
                metrics_by_word[word] = fixations_on_word
            else:
                metrics_by_word[word] += fixations_on_word


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
    compute_metrics(item_paths, save_file, chars_mapping)
