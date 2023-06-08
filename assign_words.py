from pathlib import Path
from scipy.io import loadmat
from Code.data_processing import utils
import pandas as pd
import numpy as np
import argparse


def assign_fixations_to_words(items_path, subjects, save_path):
    items = [item for item in items_path.glob('*.mat') if item.name != 'Test.mat']
    for item in items:
        screens_lines = load_lines_by_screen(item)
        item_savepath = save_path / item.name[:-4]

        process_item(item, subjects, screens_lines, item_savepath)


def process_item(item, subjects, screens_lines, item_savepath):
    for subject in subjects:
        trial_path = subject / item.name[:-4]
        item_savepath = item_savepath / subject.name
        if not (trial_path.exists() and trial_is_processed(subject, item)):
            continue
        screen_sequence = pd.read_pickle(trial_path / 'screen_sequence.pkl')['currentscreenid'].to_numpy()
        trial_fixations_by_word = process_subj_trial(trial_path, screen_sequence, screens_lines)
        save_trial_word_fixations(trial_fixations_by_word, item_savepath)


def process_subj_trial(trial_path, screen_sequence, screens_lines):
    # Keep track of returning screens
    screen_counter = {screen_id: 0 for screen_id in np.unique(screen_sequence)}
    # Each screen has a list of lines, each line has a dict of words with their fixations
    trial_fixations_by_word = {screen_id: [] for screen_id in np.unique(screen_sequence)}
    for screen_id in screen_sequence:
        fixations, lines_pos = load_screen_data(trial_path, screen_id, screen_counter)
        for line_number, line in enumerate(screens_lines[screen_id]):
            words, spaces_pos = line['text'].split(), line['spaces_pos']
            line_fixations = get_line_fixations(fixations, line_number, lines_pos)
            words_fixations = assign_line_fixations_to_words(words, line_fixations, spaces_pos)

            screen_fixations, counter = trial_fixations_by_word[screen_id], screen_counter[screen_id]
            update_screen_fixations(line_number, words_fixations, counter, screen_fixations)

        screen_counter[screen_id] += 1

    return trial_fixations_by_word


def get_line_fixations(fixations, line_number, lines_pos):
    line_fixations = fixations[fixations['yAvg'].between(lines_pos[line_number],
                                                         lines_pos[line_number + 1],
                                                         inclusive='left')]
    if not line_fixations.empty:
        # Check if first screen fixation hasn't been removed yet
        if line_fixations.iloc[0].name == 0:
            line_fixations = line_fixations.drop([0])
        # Remove last fixation if it's the last fixation on the screen
        if not line_fixations.empty and line_fixations.iloc[-1].name == len(fixations) - 1:
            line_fixations = line_fixations.drop([len(fixations) - 1])

    return line_fixations


def assign_line_fixations_to_words(words, line_fixations, spaces_pos):
    words_fixations = {word: {} for word in words}
    for i in range(len(spaces_pos) - 1):
        word_fixations = line_fixations[line_fixations['xAvg'].between(spaces_pos[i],
                                                                       spaces_pos[i + 1],
                                                                       inclusive='left')]
        if word_fixations.empty:
            continue
        word_fixations = word_fixations[['index', 'duration', 'xAvg']]
        word_fixations = word_fixations.rename(columns={'index': 'fixid', 'xAvg': 'x'})
        word_fixations.reset_index(inplace=True)
        # Shift x to start at 0
        word_fixations['x'] -= spaces_pos[i]

        word = words[i]
        words_fixations[word] = word_fixations.to_dict(orient='list')

    return words_fixations


def update_screen_fixations(line_number, words_fixations, counter, screen_fixations):
    if counter == 0:
        screen_fixations.append(words_fixations)
    else:
        # Returning screen, append values
        update_line_fixations(line_number, words_fixations, screen_fixations)


def update_line_fixations(line_number, words_fixations, screen_fixations):
    for word in words_fixations:
        if len(words_fixations[word]) > 0:
            word_prev_fix = screen_fixations[line_number][word]
            for key in word_prev_fix:
                word_prev_fix[key].extend(words_fixations[word][key])


def trial_is_processed(subject, item):
    item_name = item.name[:-4]
    trial_flags = utils.load_flags([item_name], subject)

    return trial_flags[item_name]['edited'][0]


def save_trial_word_fixations(trial_fixations_by_word, item_savepath):
    item_savepath.mkdir(parents=True, exist_ok=True)
    for screen_id in trial_fixations_by_word:
        screen_savepath = item_savepath / f'screen_{screen_id}'
        screen_savepath.mkdir(exist_ok=True)
        for line_number, line in enumerate(trial_fixations_by_word[screen_id]):
            line_filename = f'line_{line_number + 1}.json'
            line_fixations = trial_fixations_by_word[screen_id][line_number]
            utils.save_json(line_fixations, screen_savepath, line_filename)


def load_screen_data(trial_path, screen_id, screen_counter):
    screen_dir = trial_path / f'screen_{screen_id}'
    fix_filename, lines_filename = 'fixations.pkl', 'lines.pkl'
    if screen_counter[screen_id] > 0:
        fix_filename = f'fixations_{screen_counter[screen_id]}.pkl'
        lines_filename = f'lines_{screen_counter[screen_id]}.pkl'
    fixations = pd.read_pickle(screen_dir / fix_filename)
    lines_pos = pd.read_pickle(screen_dir / lines_filename).sort_values('y')['y'].to_numpy()

    return fixations, lines_pos


def load_lines_by_screen(item):
    item_cfg = loadmat(str(item), simplify_cells=True)
    lines, num_screens = item_cfg['lines'], len(item_cfg['screens'])
    screens_lines = {screen_id: [] for screen_id in range(1, num_screens + 1)}
    for line in lines:
        screens_lines[line['screen']].append(line)

    return screens_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assign fixations to words')
    parser.add_argument('--stimuli', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/by_participant')
    parser.add_argument('--save_path', type=str, default='Data/processed/by_item')
    parser.add_argument('--subj', type=str, default='all')
    args = parser.parse_args()

    stimuli_path, data_path, save_path = Path(args.stimuli), Path(args.data_path), Path(args.save_path)
    if args.subj != 'all':
        subj_paths = [data_path / args.subj]
    else:
        subj_paths = utils.get_dirs(data_path)

    assign_fixations_to_words(stimuli_path, subj_paths, save_path)
