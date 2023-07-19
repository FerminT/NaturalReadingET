from pathlib import Path
from scipy.io import loadmat
from Code.data_processing import utils
import pandas as pd
import numpy as np
import argparse


def assign_fixations_to_words(items_path, subjects, save_path):
    print('Assigning fixations to words...')
    items = [item for item in utils.get_files(items_path, 'mat') if item.stem != 'Test']
    for item in items:
        print(f'Processing "{item.stem}" trials')
        screens_lines = load_lines_by_screen(item)
        item_savepath = save_path / item.name[:-4]
        item_savepath.mkdir(exist_ok=True, parents=True)

        process_item(item, subjects, screens_lines, item_savepath)


def process_item(item, subjects, screens_lines, item_savepath):
    screens_text = {int(screenid): [line['text'] for line in screens_lines[screenid]] for screenid in screens_lines}
    utils.save_json(screens_text, item_savepath, 'screens_text.json')
    for subject in subjects:
        trial_path = subject / item.name[:-4]
        if not (trial_path.exists() and trial_is_correct(subject, item)):
            continue
        screen_sequence = pd.read_pickle(trial_path / 'screen_sequence.pkl')['currentscreenid'].to_numpy()
        trial_fix_by_word = process_subj_trial(subject.name, trial_path, screen_sequence, screens_lines)
        save_trial_word_fixations(trial_fix_by_word, item_savepath, subject.name)


def process_subj_trial(subj_name, trial_path, screen_sequence, screens_lines):
    # Keep track of returning screens
    screen_counter = {screen_id: 0 for screen_id in np.unique(screen_sequence)}
    # Each screen has a list of lines, each line is a list of dictionaries with the fixations of the corresponding word
    trial_fix_by_word = []
    for screen_id in screen_sequence:
        fixations, lines_pos = load_screen_data(trial_path, screen_id, screen_counter)
        word_pos = 0
        for line_num, line in enumerate(screens_lines[screen_id]):
            words, spaces_pos = line['text'].split(), line['spaces_pos']
            line_fix = get_line_fixations(fixations, line_num, lines_pos)
            assign_line_fixations_to_words(word_pos, line_fix, line_num, spaces_pos,
                                           screen_id, subj_name, trial_fix_by_word)
            word_pos += len(words)

        screen_counter[screen_id] += 1
    trial_fix_by_word = pd.DataFrame(trial_fix_by_word, columns=['subj', 'screen', 'line', 'word_pos', 'trial_fix',
                                                                 'screen_fix', 'duration', 'x'])

    return trial_fix_by_word


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


def assign_line_fixations_to_words(word_pos, line_fix, line_num, spaces_pos, screen_id, subj_name, trial_fix_by_word):
    for i in range(len(spaces_pos) - 1):
        word_fix = line_fix[line_fix['xAvg'].between(spaces_pos[i],
                                                     spaces_pos[i + 1],
                                                     inclusive='left')]
        if word_fix.empty:
            trial_fix_by_word.append([subj_name, screen_id, line_num, word_pos, None, None, None, None])
        else:
            word_fix = word_fix[['index', 'duration', 'xAvg']]
            word_fix = word_fix.rename(columns={'index': 'trial_fix', 'xAvg': 'x'})
            word_fix.reset_index(inplace=True)
            # Shift x to start at 0
            word_fix['x'] -= spaces_pos[i]
            word_fix['subj'], word_fix['screen'], word_fix['line'], word_fix['word_pos'] = \
                subj_name, screen_id, line_num, word_pos

            word_fix = word_fix[['subj', 'screen', 'line', 'word_pos', 'trial_fix', 'index', 'duration', 'x']]
            trial_fix_by_word.extend(word_fix.values.tolist())
        word_pos += 1


def trial_is_correct(subject, item):
    item_name = item.name[:-4]
    trial_flags = utils.load_flags([item_name], subject)

    return trial_flags[item_name]['edited'][0] and not trial_flags[item_name]['iswrong'][0]


def save_trial_word_fixations(trial_fix_by_word, item_savepath, subj_name):
    trial_fix_by_word = trial_fix_by_word.sort_values(['screen', 'line', 'word_pos', 'screen_fix'])
    trial_fix_by_word[['screen_fix', 'trial_fix', 'duration']] = \
        trial_fix_by_word[['screen_fix', 'trial_fix', 'duration']].astype(pd.UInt64Dtype(), copy=False)
    trial_fix_by_word.to_pickle(item_savepath / f'{subj_name}.pkl')


def load_screen_data(trial_path, screen_id, screen_counter):
    screen_dir = trial_path / f'screen_{screen_id}'
    fix_filename, lines_filename = get_screen_filenames(screen_counter[screen_id])
    fixations = pd.read_pickle(screen_dir / fix_filename)
    lines_pos = pd.read_pickle(screen_dir / lines_filename).sort_values('y')['y'].to_numpy()

    if screen_counter[screen_id] > 0:
        last_fixation_index = get_last_fixation_index(screen_dir, screen_counter[screen_id] - 1)
        fixations.index += last_fixation_index + 1

    return fixations, lines_pos


def get_screen_filenames(screen_times_read):
    fix_filename = f'fixations.pkl'
    lines_filename = f'lines.pkl'
    if screen_times_read > 0:
        fix_filename = f'fixations_{screen_times_read}.pkl'
        lines_filename = f'lines_{screen_times_read}.pkl'

    return fix_filename, lines_filename


def get_last_fixation_index(screen_dir, prev_screen_times_read):
    fix_filename, _ = get_screen_filenames(prev_screen_times_read)
    fixations = pd.read_pickle(screen_dir / fix_filename)
    last_fixation_index = fixations.iloc[-1].name

    return last_fixation_index


def load_lines_by_screen(item):
    item_cfg = loadmat(str(item), simplify_cells=True)
    lines, num_screens = item_cfg['lines'], len(item_cfg['screens'])
    screens_lines = {screen_id: [] for screen_id in range(1, num_screens + 1)}
    for line in lines:
        screens_lines[line['screen']].append({'text': line['text'],
                                              'spaces_pos': line['spaces_pos']})

    return screens_lines


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assign fixations to words')
    parser.add_argument('--stimuli', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/trials')
    parser.add_argument('--save_path', type=str, default='Data/processed/words_fixations')
    parser.add_argument('--subj', type=str, default='all')
    args = parser.parse_args()

    stimuli_path, data_path, save_path = Path(args.stimuli), Path(args.data_path), Path(args.save_path)
    if args.subj != 'all':
        subj_paths = [data_path / args.subj]
    else:
        subj_paths = utils.get_dirs(data_path)

    assign_fixations_to_words(stimuli_path, subj_paths, save_path)
