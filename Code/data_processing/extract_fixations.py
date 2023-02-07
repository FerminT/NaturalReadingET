from parse_asc import ParseEyeLinkAsc
from pathlib import Path
from scipy.io import loadmat
import argparse
import pandas as pd

def parse_rawdata(datapath, ascii_location='asc', save_path='pkl'):
    participants = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    for participant_dir in participants:
        out_path = participant_dir / save_path
        if not out_path.exists(): out_path.mkdir()
        
        mat_files = participant_dir.glob('*.mat')
        for mat_file in mat_files:
            print(f'Processing {mat_file}')
            if mat_file.name == 'Test.mat' or mat_file.name == 'metadata.mat':
                continue
            trial_metadata = loadmat(str(mat_file), simplify_cells=True)['trial']
            trial_path     = out_path / mat_file.name.split('.')[0]
            if not trial_path.exists(): trial_path.mkdir()
            trial_sequence, _, _ = save_to_pickle(trial_metadata, trial_path)
            
            stimuli_index, subj_name = trial_metadata['stimuli_index'], trial_metadata['subjname']
            trial_msgs, trial_fix = get_eyetracking_data(participant_dir / ascii_location, subj_name, stimuli_index)
            trial_msgs.to_pickle(trial_path / 'et_msgs.pkl')
            
            divide_fixations_by_screen(trial_sequence, trial_msgs, trial_fix, trial_path, subj_name)

def divide_fixations_by_screen(trial_sequence, trial_msgs, trial_fix, trial_path, subj_name):
    for i, screen_id in enumerate(trial_sequence['currentscreenid']):
        ini_time = trial_msgs[trial_msgs['text'].str.contains('ini')].iloc[i]['time']
        fin_time = trial_msgs[trial_msgs['text'].str.contains('fin')].iloc[i]['time']
        screen_fixations = trial_fix[(trial_fix['tStart'] >= ini_time) & (trial_fix['tEnd'] <= fin_time)]
        screen_path = trial_path / f'screen_{screen_id}'
        if not screen_path.exists(): screen_path.mkdir()
        fixations_files = list(sorted(screen_path.glob('fixations*.pkl')))
        # Account for repeated screens (i.e. returning to it)
        if len(fixations_files):
            fix_file = screen_path / f'fixations_{len(fixations_files)}.pkl'
            print('Repeated screen for subject ' + subj_name)
        else:
            fix_file = screen_path / 'fixations.pkl'
        screen_fixations.to_pickle(fix_file)

def save_to_pickle(trial_metadata, trial_path):
    trial_sequence = pd.DataFrame.from_records(trial_metadata['sequence'])
    trial_answers  = pd.DataFrame(trial_metadata['questions_answers'])
    trial_words    = pd.DataFrame(trial_metadata['synonyms_answers'])
    trial_sequence.to_pickle(trial_path / 'screen_sequence.pkl')
    trial_answers.to_pickle(trial_path / 'answers.pkl')
    trial_words.to_pickle(trial_path / 'words.pkl')
    
    return trial_sequence, trial_answers, trial_words

def get_eyetracking_data(asc_path, subj_name, stimuli_index):
    asc_file = asc_path / f'{subj_name}_{stimuli_index}.asc'
    _, dfMsg, dfFix, _, _, _ = ParseEyeLinkAsc(asc_file)
    best_eye = find_besteye(dfMsg)
    dfFix = dfFix[dfFix['eye'] == best_eye]
    dfMsg = filter_msgs(dfMsg)
    
    return dfMsg, dfFix

def find_besteye(dfMsg):
    val_msgs = (dfMsg[dfMsg['text'].str.contains('CAL VALIDATION')][-2:]).to_numpy(dtype=str)
    left_index  = int('LEFT' in val_msgs[1][1])
    right_index = 1 - left_index
    lefterror_index, righterror_index = val_msgs[left_index][1].split().index('ERROR'), val_msgs[right_index][1].split().index('ERROR')
    left_error  = float(val_msgs[left_index][1].split()[lefterror_index + 1])
    right_error = float(val_msgs[right_index][1].split()[righterror_index + 1])
    
    return 'L' if left_error < right_error else 'R'

def filter_msgs(dfMsg, cutout='validation'):
    first_index = dfMsg.index[dfMsg['text'].str.contains(cutout)].tolist()[0]
    
    return dfMsg[first_index:]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract fixations from EyeLink .asc file')
    parser.add_argument('-path', type=str, help='Path where participants data is stored')
    args = parser.parse_args()

    datapath = Path(args.path)
    parse_rawdata(datapath)