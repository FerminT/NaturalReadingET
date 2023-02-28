from .et_utils import et_utils
from pathlib import Path
from scipy.io import loadmat
import argparse
import shutil
import pandas as pd
from . import utils

""" EyeLink's EDF files are assumed to having been converted to ASCII with edf2asc.exe.
    This script extracts fixations from those files and proceeds to divide them by screen for each trial.
    Only one eye is used for fixation extraction, and the eye is chosen based on the calibration results. 
    Data structures consist of dataframes in pickle format."""

def parse_item(item, participant_path, ascii_path, config_file, stimuli_path, save_path):
    print(f'Processing {item}')
    trial_metadata = loadmat(str(item), simplify_cells=True)['trial']
    trial_path     = save_path / item.name.split('.')[0]
    if trial_path.exists(): shutil.rmtree(trial_path)
    trial_path.mkdir(parents=True)
    
    stimuli_index, subj_name = trial_metadata['stimuli_index'], trial_metadata['subjname']
    trial_fix, trial_sacc, et_messages = get_eyetracking_data(participant_path / ascii_path, subj_name, stimuli_index)
    
    save_validation_fixations(et_messages, trial_fix, trial_path)
    screen_sequence = pd.DataFrame.from_records(trial_metadata['sequence'])
    stimuli = utils.load_stimuli(item.name[:-4], stimuli_path, config_file)
    divide_data_by_screen(screen_sequence, et_messages, trial_fix, trial_sacc, trial_path, stimuli, filter_outliers=True)
    
    utils.save_structs(et_messages,
                       screen_sequence,
                       pd.DataFrame(trial_metadata['questions_answers']),
                       pd.DataFrame(trial_metadata['synonyms_answers']),
                       trial_path)

def parse_participantdata(datapath, participant, ascii_path, config_file, stimuli_path, save_path):
    participant_path = datapath / participant
    out_path = save_path / participant
    if not out_path.exists(): out_path.mkdir(parents=True)
    save_profile(participant_path, out_path)
    items = participant_path.glob('*.mat')
    for item in items:
        if item.name == 'Test.mat' or item.name == 'metadata.mat': continue
        parse_item(item, participant_path, ascii_path, config_file, stimuli_path, out_path)    

def parse_rawdata(datapath, ascii_path, config_file, stimuli_path, save_path):
    participants = utils.get_dirs(datapath)
    for participant in participants:
        parse_participantdata(datapath, participant.name, ascii_path, config_file, stimuli_path, save_path)

def save_profile(participant_path, save_path):
    metafile = loadmat(str(participant_path / 'metadata.mat'), simplify_cells=True)
    stimuli_order = list(metafile['shuffled_stimuli'][1:].astype(str))
    profile  = {'name': [metafile['subjname']], 'reading_level': [int(metafile['reading_level'])], 'stimuli_order': [stimuli_order]}
    pd.DataFrame(profile).to_pickle(save_path / 'profile.pkl')
    
def save_validation_fixations(et_messages, trial_fix, trial_path, val_legend='validation', num_points=9, points_area=56):
    val_msgs = et_messages[et_messages['text'].str.contains(val_legend)]
    fin_msgindex = et_messages[et_messages['text'].str.contains('termina experimento')].index[0]
    first_val = val_msgs.loc[:fin_msgindex]
    last_val  = val_msgs.loc[fin_msgindex:]
    # Add some time to let the eye get to the last point
    first_valfix = trial_fix[(trial_fix['tStart'] >= first_val.iloc[0]['time']) & (trial_fix['tEnd'] <= first_val.iloc[-1]['time'] + 500)]
    last_valfix  = trial_fix[(trial_fix['tStart'] >= last_val.iloc[0]['time']) & (trial_fix['tEnd'] <= last_val.iloc[-1]['time'] + 500)]
    
    points_coords = val_msgs['text'].str.extract(r'(\d+),(\d+)').astype(int)[:num_points].to_numpy()
    firstval_iscorrect = check_validation_fixations(first_valfix, points_coords, num_points, points_area)
    lastval_iscorrect  = check_validation_fixations(last_valfix, points_coords, num_points, points_area)

    if not firstval_iscorrect:
        print('Validation error at the beginning of trial for participant', trial_path.parents[1].name, 'in trial', trial_path.name)
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

def divide_data_by_screen(trial_sequence, et_messages, trial_fix, trial_sacc, trial_path, stimuli, filter_outliers=True):
    fix_filename, sacc_filename, lines_filename = 'fixations.pkl', 'saccades.pkl', 'lines.pkl'
    for i, screen_id in enumerate(trial_sequence['currentscreenid']):
        ini_time = et_messages[et_messages['text'].str.contains('ini')].iloc[i]['time']
        fin_time = et_messages[et_messages['text'].str.contains('fin')].iloc[i]['time']
        screen_fixations = trial_fix[(trial_fix['tStart'] > ini_time) & (trial_fix['tEnd'] < fin_time)]
        screen_saccades  = trial_sacc[(trial_sacc['tStart'] > ini_time) & (trial_sacc['tEnd'] < fin_time)]
        if filter_outliers:
            screen_fixations = screen_fixations[(screen_fixations['duration'] > 50) & (screen_fixations['duration'] < 1000)]
        if screen_fixations.empty:
            trial_sequence.drop(i, inplace=True)
            continue
        
        screen_path  = utils.get_screenpath(screen_id, trial_path)
        lines_coords = utils.default_screen_linescoords(screen_id, stimuli)
        fixations_files = list(sorted(screen_path.glob(f'{fix_filename[:-4]}*')))
        screenfix_filename, screensacc_filename, screenlines_filename = fix_filename, sacc_filename, lines_filename
        # Account for repeated screens (i.e. returning to it)
        if len(fixations_files):
            screenfix_filename   = f'{fix_filename[:-4]}_{len(fixations_files)}.pkl'
            screensacc_filename  = f'{sacc_filename[:-4]}_{len(fixations_files)}.pkl'
            screenlines_filename = f'{lines_filename[:-4]}_{len(fixations_files)}.pkl'
        
        screen_fixations.reset_index(inplace=True), screen_saccades.reset_index(inplace=True)
        screen_fixations.to_pickle(screen_path / screenfix_filename), screen_saccades.to_pickle(screen_path / screensacc_filename)
        utils.save_linescoords(lines_coords, screen_path, screenlines_filename)
        
def get_eyetracking_data(asc_path, subj_name, stimuli_index):
    asc_file = asc_path / f'{subj_name}_{stimuli_index}.asc'
    _, dfMsg, dfFix, dfSacc, _, _ = et_utils.parse_asc(asc_file, verbose=False)
    dfFix, dfSacc = et_utils.keep_besteye(dfFix, dfSacc, dfMsg)
    dfMsg = et_utils.filter_msgs(dfMsg)
    
    return dfFix, dfSacc, dfMsg

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract data from EyeLink .asc files and save them to .pkl')
    parser.add_argument('--path', type=str, default='Data/raw', help='Path where participants data is stored')
    parser.add_argument('--ascii_path', type=str, default='asc', help='Path where .asc files are stored in a participants folder')
    parser.add_argument('--config', type=str, default='Metadata/stimuli_config.mat', help='Config file with the stimuli information')
    parser.add_argument('--stimuli_path', type=str, default='Stimuli', help='Path where the stimuli are stored')
    parser.add_argument('--save_path', type=str, default='Data/processed/per_participant', help='Path where to save the processed data')
    parser.add_argument('--subj', type=str, help='Subject name', required=False)
    args = parser.parse_args()

    data_path, stimuli_path, save_path = Path(args.path), Path(args.stimuli_path), Path(args.save_path)
    if not args.subj:
        parse_rawdata(data_path, args.ascii_path, args.config, stimuli_path, save_path)
    else:
        parse_participantdata(data_path, args.subj, args.ascii_path, args.config, stimuli_path, save_path)