from pathlib import Path
from scipy.io import loadmat
import pandas as pd
import argparse


def assign_fixations_to_words(items_path, data_path, stimuli_cfg, save_path, exclude_firstfix=True, exclude_lastfix=True):
    items = [item for item in items_path.glob('*.mat') if item.name != 'Test.mat']
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
            for screen_id in screen_sequence:
                screen_dir = trial_path / f'screen_{screen_id}'
                fix_filename, lines_filename = 'fixations.pkl', 'lines.pkl'
                if screen_counter[screen_id] > 0:
                    fix_filename = f'fixations_{screen_counter[screen_id]}.pkl'
                    lines_filename = f'lines_{screen_counter[screen_id]}.pkl'
                screen_counter[screen_id] += 1
                fixations = pd.read_pickle(screen_dir / fix_filename)
                lines_pos = pd.read_pickle(screen_dir / lines_filename)
                for line_number, line in enumerate(screens_lines[screen_id]):
                    words = line['text'].split()
                    line_fixations = fixations[fixations['yAvg'].between(lines_pos[line_number], lines_pos[line_number + 1])]
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assign fixations to words')
    parser.add_argument('--stimuli', type=str, default='Stimuli')
    parser.add_argument('--cfg', type=str, default='Metadata/stimuli_config.mat')
    parser.add_argument('--data', type=str, default='Data/processed/by_participant')
    parser.add_argument('--save_path', type=str, default='Data/processed/by_item')
    args = parser.parse_args()

    stimuli_path, data_path, save_path = Path(args.stimuli), Path(args.data), Path(args.save_path)
    assign_fixations_to_words(stimuli_path, data_path, args.cfg, save_path)
