from scipy.io import loadmat
import pandas as pd

def get_dirs(datapath):
    dirs = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    return dirs

def get_fixations(df_fix):
    return df_fix['xAvg'].to_numpy(dtype=int), df_fix['yAvg'].to_numpy(dtype=int), df_fix['duration'].to_numpy()

def load_screensequence(data_path, filename='screen_sequence.pkl'):
    screen_sequence = pd.read_pickle(data_path / filename)['currentscreenid'].to_numpy()
    return screen_sequence

def load_stimuli(item, stimuli_path):
    stimuli_file = stimuli_path / (item + '.mat')
    if not stimuli_file.exists():
        raise ValueError('Stimuli file does not exist: ' + str(stimuli_file))
    stimuli = loadmat(str(stimuli_file), simplify_cells=True)
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