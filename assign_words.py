from pathlib import Path
from scipy.io import loadmat
from Code.data_processing import utils
import pandas as pd
import numpy as np
import argparse


def load_lines_by_screen(item):
    item_cfg = loadmat(str(item), simplify_cells=True)
    lines, num_screens = item_cfg['lines'], len(item_cfg['screens'])
    screens_lines = {screen_id: [] for screen_id in range(1, num_screens + 1)}
    for line in lines:
        screens_lines[line['screen']].append(line)

    return screens_lines


def assign_fixations_to_words(items_path, subjects, save_path):
    items = [item for item in items_path.glob('*.mat') if item.name != 'Test.mat']
    for item in items:
        screens_lines = load_lines_by_screen(item)
        item_savepath = save_path / item.name[:-4]

        process_item(item, subjects, screens_lines, item_savepath)


def trial_is_processed(subject, item):
    item_name = item.name[:-4]
    trial_flags = utils.load_flags([item_name], subject)

    return trial_flags[item_name]['edited'][0]


def process_item(item, subjects, screens_lines, item_savepath):
    for subject in subjects:
        trial_path = subject / item.name[:-4]
        if not (trial_path.exists() and trial_is_processed(subject, item)):
            continue
        screen_sequence = pd.read_pickle(trial_path / 'screen_sequence.pkl')['currentscreenid'].to_numpy()
        screen_counter = {screen_id: 0 for screen_id in np.unique(screen_sequence)}
        # Each screen has a list of lines, each line has a dict of words with their fixations
        screens_lines_fix = {screen_id: [] for screen_id in np.unique(screen_sequence)}
        for screen_id in screen_sequence:
            screen_dir = trial_path / f'screen_{screen_id}'
            fix_filename, lines_filename = 'fixations.pkl', 'lines.pkl'
            if screen_counter[screen_id] > 0:
                fix_filename = f'fixations_{screen_counter[screen_id]}.pkl'
                lines_filename = f'lines_{screen_counter[screen_id]}.pkl'
            fixations = pd.read_pickle(screen_dir / fix_filename)
            lines_pos = pd.read_pickle(screen_dir / lines_filename).sort_values('y')['y'].to_numpy()
            for line_number, line in enumerate(screens_lines[screen_id]):
                words = line['text'].split()
                spaces_pos = line['spaces_pos']
                words_fixations = {word: {} for word in words}
                line_fixations = fixations[fixations['yAvg'].between(lines_pos[line_number],
                                                                     lines_pos[line_number + 1],
                                                                     inclusive='left')]
                if not line_fixations.empty:
                    # Check if first screen fixation hasn't been removed yet
                    if line_fixations.iloc[0].name == 0:
                        line_fixations = line_fixations.drop([0])
                    # Remove last fixation if it's the last fixation of the screen
                    if not line_fixations.empty and line_fixations.iloc[-1].name == len(fixations) - 1:
                        line_fixations = line_fixations.drop([len(fixations) - 1])

                for i in range(len(spaces_pos) - 1):
                    word_fixations = line_fixations[line_fixations['xAvg'].between(spaces_pos[i],
                                                                                   spaces_pos[i + 1],
                                                                                   inclusive='left')]
                    if len(word_fixations) == 0:
                        continue
                    word_fixations = word_fixations[['index', 'duration', 'xAvg']]
                    word_fixations = word_fixations.rename(columns={'index': 'fixid', 'xAvg': 'x'})
                    word_fixations.reset_index(inplace=True)
                    # Shift x to start at 0
                    word_fixations['x'] -= spaces_pos[i]

                    word = words[i]
                    words_fixations[word] = word_fixations.to_dict(orient='list')
                if screen_counter[screen_id] > 0:
                    # Returning screen, append values
                    for word in words_fixations:
                        if len(words_fixations[word]) > 0:
                            word_prev_fix = screens_lines_fix[screen_id][line_number][word]
                            for key in word_prev_fix:
                                word_prev_fix[key].extend(words_fixations[word][key])
                else:
                    screens_lines_fix[screen_id].append(words_fixations)

            screen_counter[screen_id] += 1
        # Save trial fixations (screens_lines_fix)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assign fixations to words')
    parser.add_argument('--stimuli', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/by_participant')
    parser.add_argument('--save_path', type=str, default='Data/processed/by_item')
    parser.add_argument('--subj', type=str, default='all')
    args = parser.parse_args()

    stimuli_path, data_path, save_path = Path(args.stimuli), Path(args.data), Path(args.save_path)
    if args.subj != 'all':
        subj_paths = [data_path / args.subj]
    else:
        subj_paths = utils.get_dirs(data_path)

    assign_fixations_to_words(stimuli_path, subj_paths, save_path)
