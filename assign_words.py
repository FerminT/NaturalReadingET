from pathlib import Path
from scipy.io import loadmat
import pandas as pd
import argparse


def assign_fixations_to_words(items_path, data_path, stimuli_cfg, save_path, exclude_firstfix=True, exclude_lastfix=True):
    items = [item for item in items_path.glob('*.mat') if item.name != 'Test.mat']
    if data_path.name != 'by_participant':
        subjects = [data_path]
    else:
        subjects = [subj for subj in data_path.iterdir() if subj.is_dir()]
    cfg = loadmat(stimuli_cfg, simplify_cells=True)['config']
    for item in items:
        item_cfg = loadmat(str(item), simplify_cells=True)
        item_savepath = save_path / item.name[:-4]
        item_lines, item_numscreens = item_cfg['lines'], len(item_cfg['screens'])
        screens_lines = {screen_id: [] for screen_id in range(1, item_numscreens + 1)}
        for line in item_lines:
            screen_id = line['screen']
            screens_lines[screen_id].append(line)
        for subject in subjects:
            trial_path = subject / item.name[:-4]
            if not trial_path.exists():
                continue
            screen_sequence = pd.read_pickle(trial_path / 'screen_sequence.pkl')['currentscreenid'].to_numpy()
            screen_counter = {screen_id: 0 for screen_id in screen_sequence.unique()}
            screens_lines_fix = {screen_id: [] for screen_id in screen_sequence.unique()}
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
                    # Check if first screen fixation hasn't been removed yet
                    if exclude_firstfix and line_fixations.iloc[0].name == 0:
                        line_fixations.drop([0], inplace=True)
                    if exclude_lastfix and line_fixations.iloc[-1].name == len(fixations) - 1:
                        line_fixations.drop([len(fixations) - 1], inplace=True)
                    if len(line_fixations) == 0:
                        continue
                    for i in range(len(spaces_pos) - 1):
                        word_fixations = line_fixations[line_fixations['xAvg'].between(spaces_pos[i],
                                                                                       spaces_pos[i + 1],
                                                                                       inclusive='left')]
                        if len(word_fixations) == 0:
                            continue
                        word_fixations = word_fixations[['index', 'duration', 'xAvg']]
                        word_fixations = word_fixations.rename(columns={'index': 'fixid', 'xAvg': 'x'})
                        word_fixations.reset_index(names=['num'], inplace=True)
                        # Shift x to start at 0
                        word_fixations['x'] -= spaces_pos[i]

                        word = words[i]
                        words_fixations[word] = word_fixations.to_dict(orient='list')
                    if screen_counter[screen_id] > 0:
                        # Returning screen, append values
                        for word in words_fixations:
                            word_prev_fix = screens_lines_fix[screen_id][line_number][word]
                            for key in word_prev_fix:
                                word_prev_fix[key].extend(words_fixations[word][key])
                    else:
                        screens_lines_fix[screen_id].append(words_fixations)

                screen_counter[screen_id] += 1
            # Save trial fixations (screens_lines_fix)
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assign fixations to words')
    parser.add_argument('--stimuli', type=str, default='Stimuli')
    parser.add_argument('--cfg', type=str, default='Metadata/stimuli_config.mat')
    parser.add_argument('--data', type=str, default='Data/processed/by_participant')
    parser.add_argument('--save_path', type=str, default='Data/processed/by_item')
    parser.add_argument('--subj', type=str, default='all')
    args = parser.parse_args()

    stimuli_path, data_path, save_path = Path(args.stimuli), Path(args.data), Path(args.save_path)
    if args.subj != 'all':
        data_path = data_path / args.subj
    assign_fixations_to_words(stimuli_path, data_path, args.cfg, save_path)
