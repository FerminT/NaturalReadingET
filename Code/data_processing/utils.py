from scipy.io import loadmat
import pandas as pd
import shutil

def get_screenpath(screenid, item_path):
    screen_path = item_path / ('screen_' + str(screenid))
    if not screen_path.exists(): screen_path.mkdir()
    return screen_path

def get_dirs(datapath):
    dirs = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    return dirs

def get_fixations(df_fix):
    return df_fix['xAvg'].to_numpy(dtype=int), df_fix['yAvg'].to_numpy(dtype=int), df_fix['duration'].to_numpy()

def save_screensequence(screens_sequence, item_path, filename='screen_sequence.pkl'):
    screens_sequence.to_pickle(item_path / filename)
    
def save_trial(screens_fixations, screens_lines, del_seqindices, item_path):    
    fix_filename   = 'fixations.pkl'
    lines_filename = 'lines.pkl'
    for screen_id in screens_fixations:
        screen_fixations, screen_lines = screens_fixations[screen_id], screens_lines[screen_id]
        screen_path = get_screenpath(screen_id, item_path)
        if screen_path.exists(): shutil.rmtree(screen_path)
        screen_path.mkdir()
        
        screenfix_filename = fix_filename
        screenlines_filename = lines_filename
        for fixations, lines in zip(screen_fixations, screen_lines):
            fixations_files = list(sorted(screen_path.glob(f'{fix_filename[:-4]}*')))
            # Account for repeated screens (i.e. returning to it)
            if len(fixations_files):
                screenfix_filename   = f'{fix_filename[:-4]}_{len(fixations_files)}.pkl'
                screenlines_filename = f'{lines_filename[:-4]}_{len(fixations_files)}.pkl'
            if len(fixations):
                fixations.to_pickle(screen_path / screenfix_filename)
                save_linescoords(lines, screen_path, screenlines_filename)
                
    screen_sequence = load_screensequence(item_path)
    screen_sequence.drop(index=screen_sequence.iloc[del_seqindices].index, inplace=True)
    save_screensequence(screen_sequence, item_path)

def save_linescoords(lines, screen_path, filename='lines.pkl'):
    pd.DataFrame(lines, columns=['y']).to_pickle(screen_path / filename)

def save_structs(et_messages, screen_sequence, answers, words, trial_path):
    et_messages.to_pickle(trial_path / 'et_messages.pkl')
    screen_sequence.to_pickle(trial_path / 'screen_sequence.pkl')
    answers.to_pickle(trial_path / 'answers.pkl')
    words.to_pickle(trial_path / 'words.pkl')
    
def load_screensequence(item_path, filename='screen_sequence.pkl'):
    screen_sequence = pd.read_pickle(item_path / filename)
    return screen_sequence

def load_stimuli(item, stimuli_path, config_file=None):
    stimuli_file = stimuli_path / (item + '.mat')
    if not stimuli_file.exists():
        raise ValueError('Stimuli file does not exist: ' + str(stimuli_file))
    stimuli = loadmat(str(stimuli_file), simplify_cells=True)
    if config_file:
        config  = loadmat(str(config_file), simplify_cells=True)['config']
        stimuli['config'] = config
    
    return stimuli

def load_stimuli_screen(screenid, stimuli):
    return stimuli['screens'][screenid - 1]['image']

def load_screen_fixations(screenid, item_path):
    screen_path = get_screenpath(screenid, item_path)
    fixations_files  = screen_path.glob('fixations*.pkl')
    screen_fixations = [pd.read_pickle(fix_file) for fix_file in sorted(fixations_files, reverse=True)]
    if not screen_fixations:
        raise ValueError('No fixations found for screen ' + str(screenid) + ' in ' + str(item_path))
    return screen_fixations

def load_screen_linescoords(screenid, item_path):
    screen_path  = get_screenpath(screenid, item_path)
    lines_files  = screen_path.glob('lines*.pkl')
    screen_lines = [pd.read_pickle(lines_file).to_numpy() for lines_file in lines_files]
    return screen_lines

def default_screen_linescoords(screenid, stimuli):
    linespacing  = stimuli['config']['linespacing']
    screen_linescoords = [line['bbox'][1] - (linespacing // 2) for line in stimuli['lines'] if line['screen'] == screenid]
    # Add additional line to enclose the last line
    screen_linescoords.append(screen_linescoords[-1] + linespacing)

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