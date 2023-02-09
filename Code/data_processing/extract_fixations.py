from parse_asc import ParseEyeLinkAsc
from pathlib import Path
from scipy.io import loadmat
import argparse
import shutil
import pandas as pd

def parse_rawdata(datapath, participant=None, ascii_location='asc', save_path='pkl'):
    participants = get_dirs(datapath, participant)
    for participant_path in participants:
        out_path = participant_path / save_path
        if not out_path.exists(): out_path.mkdir()
        save_profile(participant_path, out_path)
        mat_files = participant_path.glob('*.mat')
        for mat_file in mat_files:
            print(f'Processing {mat_file}')
            if mat_file.name == 'Test.mat' or mat_file.name == 'metadata.mat':
                continue
            trial_metadata = loadmat(str(mat_file), simplify_cells=True)['trial']
            trial_path     = out_path / mat_file.name.split('.')[0]
            if trial_path.exists(): shutil.rmtree(trial_path)
            trial_path.mkdir()
            trial_sequence, _, _ = save_to_pickle(trial_metadata, trial_path)
            
            stimuli_index, subj_name = trial_metadata['stimuli_index'], trial_metadata['subjname']
            trial_msgs, trial_fix, trial_sacc = get_eyetracking_data(participant_path / ascii_location, subj_name, stimuli_index)
            trial_msgs.to_pickle(trial_path / 'et_messages.pkl')
            
            save_validation_fixations(trial_msgs, trial_fix, trial_path)
            divide_data_by_screen(trial_sequence, trial_msgs, trial_fix, trial_sacc, trial_path, subj_name)

def get_dirs(datapath, participant):
    if participant:
        dirs = [datapath / participant]
        if not dirs[0].exists():
            raise FileNotFoundError(f'Participant {participant} not found')
    else:
        dirs = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
        
    return dirs

def save_profile(participant_path, save_path):
    metafile = loadmat(str(participant_path / 'metadata.mat'), simplify_cells=True)
    stimuli_order = list(metafile['shuffled_stimuli'][1:].astype(str))
    profile  = {'name': [metafile['subjname']], 'reading_level': [int(metafile['reading_level'])], 'stimuli_order': [stimuli_order]}
    pd.DataFrame(profile).to_pickle(save_path / 'profile.pkl')
    
def save_validation_fixations(trial_msgs, trial_fix, trial_path, val_legend='validation', num_points=9, points_area=56):
    val_msgs = trial_msgs[trial_msgs['text'].str.contains(val_legend)]
    fin_msgindex = trial_msgs[trial_msgs['text'].str.contains('termina experimento')].index[0]
    first_val = val_msgs.loc[:fin_msgindex]
    last_val  = val_msgs.loc[fin_msgindex:]
    # Add some time to let the eye get to the last point
    first_valfix = trial_fix[(trial_fix['tStart'] >= first_val.iloc[0]['time']) & (trial_fix['tEnd'] <= first_val.iloc[-1]['time'] + 500)]
    last_valfix  = trial_fix[(trial_fix['tStart'] >= last_val.iloc[0]['time']) & (trial_fix['tEnd'] <= last_val.iloc[-1]['time'] + 500)]
    
    points_coords = val_msgs['text'].str.extract(r'(\d+),(\d+)').astype(int)[:num_points].to_numpy()
    firstval_iscorrect = check_validation_fixations(first_valfix, points_coords, num_points, points_area)
    lastval_iscorrect  = check_validation_fixations(last_valfix, points_coords, num_points, points_area)

    if not firstval_iscorrect:
        print('Validation error at the begining of trial for participant', trial_path.parent[1].name, 'in trial', trial_path.name)
    if not lastval_iscorrect:
        print('Validation error at the end of trial for participant', trial_path.parents[1].name, 'in trial', trial_path.name)
        
    val_path = trial_path / 'validation'
    if not val_path.exists(): val_path.mkdir()
    first_valfix.to_pickle(val_path / 'first.pkl')
    last_valfix.to_pickle(val_path / 'last.pkl')
    
def check_validation_fixations(fixations, points_coords, num_points, points_area, error_margin=30):
    """ For each fixation, check if it is inside the area of the point.
        As we only advance the point index once we find a fixation inside the area,
        the validation is correct only if the point index matches the number of points - 1. """
    fix_coords  = fixations.loc[:, ['xAvg', 'yAvg']].astype(int).to_numpy()
    point_index = 0
    for (x, y) in fix_coords:
        lower_bound, upper_bound = points_coords[point_index] - (points_area + error_margin), points_coords[point_index] + (points_area + error_margin)
        if x in range(lower_bound[0], upper_bound[0]) and y in range(lower_bound[1], upper_bound[1]):
            point_index += 1
            if point_index == num_points - 1: break
    
    return point_index == num_points - 1

def divide_data_by_screen(trial_sequence, trial_msgs, trial_fix, trial_sacc, trial_path, subj_name):
    for i, screen_id in enumerate(trial_sequence['currentscreenid']):
        ini_time = trial_msgs[trial_msgs['text'].str.contains('ini')].iloc[i]['time']
        fin_time = trial_msgs[trial_msgs['text'].str.contains('fin')].iloc[i]['time']
        # TODO: Check where to make a strict cut, if at the beginning or at the end
        screen_fixations = trial_fix[(trial_fix['tStart'] >= ini_time) & (trial_fix['tEnd'] <= fin_time)]
        screen_saccades  = trial_sacc[(trial_sacc['tStart'] >= ini_time) & (trial_sacc['tEnd'] <= fin_time)]
        screen_path = trial_path / f'screen_{screen_id}'
        if not screen_path.exists(): screen_path.mkdir()
        fixations_files = list(sorted(screen_path.glob('fixations*.pkl')))
        # Account for repeated screens (i.e. returning to it)
        if len(fixations_files):
            fix_file  = screen_path / f'fixations_{len(fixations_files)}.pkl'
            sacc_file = screen_path / f'saccades_{len(fixations_files)}.pkl'
            print('Repeated screen for participant ' + subj_name)
        else:
            fix_file  = screen_path / 'fixations.pkl'
            sacc_file = screen_path / 'saccades.pkl'
            
        screen_fixations.to_pickle(fix_file), screen_saccades.to_pickle(sacc_file)

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
    _, dfMsg, dfFix, dfSacc, _, _ = ParseEyeLinkAsc(asc_file)
    binocular = len(dfFix['eye'].unique()) > 1
    if binocular:
        best_eye = find_besteye(dfMsg)
        dfFix    = dfFix[dfFix['eye'] == best_eye]
        dfSacc   = dfSacc[dfSacc['eye'] == best_eye]
    dfMsg = filter_msgs(dfMsg)
    
    return dfMsg, dfFix, dfSacc

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
    parser.add_argument('--subj', type=str, help='Subject name', required=False)
    args = parser.parse_args()

    datapath = Path(args.path)
    parse_rawdata(datapath, args.subj)