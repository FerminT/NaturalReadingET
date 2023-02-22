from scipy.io import loadmat
import pandas as pd
import shutil

def get_dirs(datapath):
    dirs = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    return dirs

def get_fixations(df_fix):
    return df_fix['xAvg'].to_numpy(dtype=int), df_fix['yAvg'].to_numpy(dtype=int), df_fix['duration'].to_numpy()

def load_screensequence(data_path, filename='screen_sequence.pkl'):
    screen_sequence = pd.read_pickle(data_path / filename)['currentscreenid'].to_numpy()
    return screen_sequence

def save_screensequence(screens_sequence, data_path, filename='screen_sequence.pkl'):
    screens_sequence.to_pickle(data_path / filename)

def load_stimuli(item, stimuli_path, config_file):
    stimuli_file = stimuli_path / (item + '.mat')
    if not stimuli_file.exists():
        raise ValueError('Stimuli file does not exist: ' + str(stimuli_file))
    stimuli = loadmat(str(stimuli_file), simplify_cells=True)
    config  = loadmat(str(config_file), simplify_cells=True)['config']
    stimuli['config'] = config
    
    return stimuli

def load_stimuli_screen(screenid, stimuli):
    return stimuli['screens'][screenid - 1]['image']

def load_screen_fixations(screenid, subjitem_path):
    screen_path = subjitem_path / ('screen_' + str(screenid))
    fixations_files  = screen_path.glob('fixations*.pkl')
    screen_fixations = [pd.read_pickle(fix_file) for fix_file in fixations_files]
    if not screen_fixations:
        raise ValueError('No fixations found for screen ' + str(screenid) + ' in ' + str(subjitem_path))
    return screen_fixations

def load_screen_linescoords(screenid, stimuli):
    # TODO: load lines if the file exists
    linespacing = stimuli['config']['linespacing']
    # line['bbox'] = [x1, y1, x2, y2]
    screen_linescoords = [line['bbox'][1] - (linespacing // 2) for line in stimuli['lines'] if line['screen'] == screenid]
    # Add additional line to enclose the last line
    screen_linescoords.append(screen_linescoords[-1] + linespacing)
    return screen_linescoords

def save_trial(screens_fixations, screens_lines, del_seqindices, data_path):    
    for screen_id in screens_fixations:
        screen_path = data_path / ('screen_' + str(screen_id))
        screen_fixations, screen_lines = screens_fixations[screen_id], screens_lines[screen_id]
        if screen_path.exists(): shutil.rmtree(screen_path)
        screen_path.mkdir()
        
        fix_filename   = 'fixations.pkl'
        lines_filename = 'lines.pkl'
        for fixations, lines in zip(screen_fixations, screen_lines):
            fixations_files = list(sorted(screen_path.glob(f'{fix_filename}*')))
            # Account for repeated screens (i.e. returning to it)
            if len(fixations_files):
                fix_filename   = f'{fix_filename[:-4]}_{len(fixations_files)}.pkl'
                lines_filename = f'{lines_filename[:-4]}_{len(fixations_files)}.pkl'
            if len(fixations) > 0:
                fixations.to_pickle(screen_path / fix_filename)
                lines.to_pickle(screen_path / lines_filename)
                
    screen_sequence = load_screensequence(data_path)
    screen_sequence.drop(del_seqindices, inplace=True)
    save_screensequence(screen_sequence, data_path)
    
def save_structs(et_messages, screen_sequence, answers, words, trial_path):
    et_messages.to_pickle(trial_path / 'et_messages.pkl')
    screen_sequence.to_pickle(trial_path / 'screen_sequence.pkl')
    answers.to_pickle(trial_path / 'answers.pkl')
    words.to_pickle(trial_path / 'words.pkl')

def find_besteye(dfMsg, default='R'):
    val_msgs = (dfMsg[dfMsg['text'].str.contains('CAL VALIDATION')][-2:]).to_numpy(dtype=str)
    if 'ABORTED' in val_msgs[0][1]: return default
    
    left_index  = int('LEFT' in val_msgs[1][1])
    right_index = 1 - left_index
    lefterror_index, righterror_index = val_msgs[left_index][1].split().index('ERROR'), val_msgs[right_index][1].split().index('ERROR')
    left_error  = float(val_msgs[left_index][1].split()[lefterror_index + 1])
    right_error = float(val_msgs[right_index][1].split()[righterror_index + 1])
    
    return 'L' if left_error < right_error else 'R'

def filter_msgs(dfMsg, cutout='validation'):
    first_index = dfMsg.index[dfMsg['text'].str.contains(cutout)].tolist()[0]
    
    return dfMsg[first_index:]