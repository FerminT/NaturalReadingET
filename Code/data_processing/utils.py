from scipy.io import loadmat
from tkinter import messagebox
import pandas as pd
import json
import shutil


def reorder(trials, stimuli_order):
    ordered_trials = [trial for trial in stimuli_order if trial in trials]
    return ordered_trials


def get_screenpath(screenid, item_path):
    screen_path = item_path / ('screen_' + str(screenid))
    if not screen_path.exists():
        screen_path.mkdir()
    return screen_path


def get_dirs(datapath):
    dirs = [dir_ for dir_ in datapath.iterdir() if dir_.is_dir()]
    return dirs


def save_screensequence(screens_sequence, item_path, filename='screen_sequence.pkl'):
    screens_sequence.to_pickle(item_path / filename)


def load_profile(profile_path, filename='profile.pkl'):
    return pd.read_pickle(profile_path / filename)


def load_pickle(path, filename):
    return pd.read_pickle(path / filename)


def update_flags(trial_flags, trial_path, filename='flags.pkl'):
    trial_flags.to_pickle(trial_path / filename)


def load_flags(trials, datapath, filename='flags.pkl'):
    flags = {trial: pd.read_pickle(datapath / trial / filename) for trial in trials}
    return flags


def load_questions_and_words(questions_file, item):
    all_questionswords = loadmat(questions_file, simplify_cells=True)['stimuli_questions']
    questions, possible_answers, words = [], [], []
    for item_dict in all_questionswords:
        if item_dict['title'] == item:
            questions = list(item_dict['questions'])
            possible_answers = list(item_dict['possible_answers'])
            words = list(item_dict['words'])
    if not questions or not words:
        raise ValueError('Questions/words not found for item', item)

    return questions, possible_answers, words


def load_answers(trial_path, filename):
    answers = pd.read_pickle(trial_path / filename)
    return list(answers[0].to_numpy())


def load_trial(stimuli, trial_path):
    screens_lst = list(range(1, len(stimuli['screens']) + 1))
    screens, screens_fixations, screens_lines = dict.fromkeys(screens_lst), dict.fromkeys(screens_lst), dict.fromkeys(
        screens_lst)
    for screenid in screens_lst:
        screens_lines[screenid] = load_screen_linescoords(screenid, trial_path)
        screens[screenid] = load_stimuli_screen(screenid, stimuli)
        screens_fixations[screenid] = load_screen_fixations(screenid, trial_path)
    return screens, screens_fixations, screens_lines


def update_and_save_trial(sequence_states, stimuli, trial_path):
    # Screens sequence may change (e.g. if all fixations in a screen were deleted)
    del_seqindeces = [seq_id for seq_id in sequence_states if len(sequence_states[seq_id]['fixations']) == 0]
    screens_lst = list(range(1, len(stimuli['screens']) + 1))
    screens_fixations, screens_lines = {screenid: [] for screenid in screens_lst},\
        {screenid: [] for screenid in screens_lst}
    for seq_id in sequence_states:
        screenid = sequence_states[seq_id]['screenid']
        screens_fixations[screenid].append(sequence_states[seq_id]['fixations'])
        screens_lines[screenid].append(sequence_states[seq_id]['lines'])
    save_trial(screens_fixations, screens_lines, del_seqindeces, trial_path)
    messagebox.showinfo(title='Saved', message='Trial saved successfully')


def save_json(dict_, save_path, filename):
    with (save_path / filename).open('w') as file:
        json.dump(dict_, file, indent=4)


def save_trial(screens_fixations, screens_lines, del_seqindices, item_path):
    fix_filename = 'fixations.pkl'
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
                screenfix_filename = f'{fix_filename[:-4]}_{len(fixations_files)}.pkl'
                screenlines_filename = f'{lines_filename[:-4]}_{len(fixations_files)}.pkl'
            if len(fixations):
                fixations.to_pickle(screen_path / screenfix_filename)
                save_linescoords(lines, screen_path, screenlines_filename)

    screen_sequence = load_screensequence(item_path)
    screen_sequence.drop(index=screen_sequence.iloc[del_seqindices].index, inplace=True)
    save_screensequence(screen_sequence, item_path)


def save_linescoords(lines, screen_path, filename='lines.pkl'):
    pd.DataFrame(lines, columns=['y']).to_pickle(screen_path / filename)


def save_calibrationdata(cal_points, val_points, val_offsets, trial_path):
    save_path = trial_path / 'calibration'
    if not save_path.exists():
        save_path.mkdir()
    cal_points.to_pickle(save_path / 'cal_points.pkl')
    val_points.to_pickle(save_path / 'val_points.pkl'), val_offsets.to_pickle(save_path / 'val_offsets.pkl')


def save_structs(et_messages, screen_sequence, answers, words, flags, trial_path):
    et_messages.to_pickle(trial_path / 'et_messages.pkl')
    screen_sequence.to_pickle(trial_path / 'screen_sequence.pkl')
    answers.to_pickle(trial_path / 'answers.pkl')
    words.to_pickle(trial_path / 'words.pkl')
    flags.to_pickle(trial_path / 'flags.pkl')


def load_calibrationdata(calibration_path):
    cal_points = load_pickle(calibration_path, 'cal_points.pkl')
    val_points = load_pickle(calibration_path, 'val_points.pkl')
    val_offsets = load_pickle(calibration_path, 'val_offsets.pkl')

    return cal_points, val_points, val_offsets


def load_screensequence(item_path, filename='screen_sequence.pkl'):
    screen_sequence = pd.read_pickle(item_path / filename)
    return screen_sequence


def load_stimuli(item, stimuli_path, config_file=None):
    stimuli_file = stimuli_path / (item + '.mat')
    if not stimuli_file.exists():
        raise ValueError('Stimuli file does not exist: ' + str(stimuli_file))
    stimuli = loadmat(str(stimuli_file), simplify_cells=True)
    if config_file:
        config = loadmat(str(config_file), simplify_cells=True)['config']
        stimuli['config'] = config

    return stimuli


def load_stimuli_screen(screenid, stimuli):
    return stimuli['screens'][screenid - 1]['image']


def load_screen_fixations(screenid, item_path):
    screen_path = get_screenpath(screenid, item_path)
    fixations_files = screen_path.glob('fixations*.pkl')
    screen_fixations = [pd.read_pickle(fix_file) for fix_file in sorted(fixations_files, reverse=True)]
    return screen_fixations


def load_screen_linescoords(screenid, item_path):
    screen_path = get_screenpath(screenid, item_path)
    lines_files = screen_path.glob('lines*.pkl')
    screen_lines = [pd.read_pickle(lines_file).to_numpy() for lines_file in sorted(lines_files, reverse=True)]
    return screen_lines


def default_screen_linescoords(screenid, stimuli):
    linespacing = stimuli['config']['linespacing']
    screen_linescoords = [line['bbox'][1] - (linespacing // 2) for line in stimuli['lines'] if
                          line['screen'] == screenid]
    # Add additional line to enclose the last line
    screen_linescoords.append(screen_linescoords[-1] + linespacing)

    return screen_linescoords


def get_points_coords(val_msgs, num_points):
    points = val_msgs['text'].str.extract(r'(\d+),(\d+)').astype(int)[:num_points]
    points.columns = ['x', 'y']
    return points


def load_manualvaldata(manualval_path, trial_path):
    et_msgs = load_pickle(trial_path, 'et_messages.pkl')
    val_msgs = et_msgs[et_msgs['text'].str.contains('validation')]
    manualval_points = get_points_coords(val_msgs, num_points=9)
    manualval_fixs = [load_pickle(manualval_path, 'first.pkl'), load_pickle(manualval_path, 'last.pkl')]

    return manualval_fixs, manualval_points


def add_offsets(cal_points, val_points, val_offsets, screen_size):
    cal_fixs = cal_points
    if not cal_points.empty:
        cal_fixs += (screen_size[1] / 2, screen_size[0] / 2)
        cal_augfactor = (cal_fixs - cal_fixs.iloc[0]) * 5
        cal_fixs += cal_augfactor
    val_fixs = val_points + val_offsets
    cal_fixs['duration'] = 1
    val_fixs['duration'] = 1

    return cal_fixs, val_fixs
