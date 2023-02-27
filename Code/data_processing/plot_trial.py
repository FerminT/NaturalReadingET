import argparse
import utils
import matplotlib.pyplot as plt
from plot_scanpath import draw_scanpath
from tkinter import messagebox
from pathlib import Path

def plot_trial(stimuli, data_path):
    screens, screens_fixations, screens_lines = load_trial(stimuli, data_path)
    screens_sequence   = utils.load_screensequence(data_path)['currentscreenid'].to_numpy()
    sequence_lines     = [screens_lines[screenid].pop() for screenid in screens_sequence]
    sequence_fixations = [screens_fixations[screenid].pop() for screenid in screens_sequence]
    # dict indexed by sequence index, containing screenid, fixations and lines, to allow editing
    sequence_states = build_sequence_states(sequence_fixations, screens_sequence, sequence_lines)
    
    state = {'sequence_index': 0, 'cids': []}
    fig, ax = plt.subplots()
    # TODO: add screen id to figure in the top right corner
    current_seqid = state['sequence_index']
    screenid, fixations, lines = sequence_states[current_seqid]['screenid'], sequence_states[current_seqid]['fixations'], sequence_states[current_seqid]['lines']
    state['cids'] = draw_scanpath(screens[screenid], fixations, fig, ax, hlines=lines, editable=True)

    fig.canvas.mpl_connect('key_press_event', lambda event: update_figure(event, state, screens, screens_sequence, sequence_states, ax, fig))
    plt.show()
    
    save_files = messagebox.askyesno(title='Modified trial', message='Do you want to save the trial?')
    if save_files:
        # Screens sequence may change (e.g. if all fixations in a screen were deleted)
        del_seqindeces = [seq_id for seq_id in sequence_states if len(sequence_states[seq_id]['fixations']) == 0]
        screens_lst = list(range(1, len(stimuli['screens']) + 1))
        screens_fixations, screens_lines = {screenid: [] for screenid in screens_lst}, {screenid: [] for screenid in screens_lst}
        for seq_id in sequence_states:
            screenid = sequence_states[seq_id]['screenid']
            screens_fixations[screenid].append(sequence_states[seq_id]['fixations'])
            screens_lines[screenid].append(sequence_states[seq_id]['lines'])
        utils.save_trial(screens_fixations, screens_lines, del_seqindeces, data_path)
        messagebox.showinfo(title='Saved', message='Trial saved successfully')
    
    
def update_figure(event, state, screens, screens_sequence, sequence_states, ax, fig):
    prev_seq = state['sequence_index']
    if event.key == 'right' and prev_seq < len(screens_sequence) - 1:
        state['sequence_index'] += 1
    elif event.key == 'left' and prev_seq > 0:
        state['sequence_index'] -= 1
    current_seqid = state['sequence_index']
    if prev_seq != current_seqid:
        screenid, fixations, lines = sequence_states[current_seqid]['screenid'], sequence_states[current_seqid]['fixations'], sequence_states[current_seqid]['lines']
        for cid in state['cids']:
            fig.canvas.mpl_disconnect(cid)
        state['cids'] = draw_scanpath(screens[screenid], fixations, fig, ax, hlines=lines, editable=True)

def build_sequence_states(sequence_fixations, screens_sequence, sequence_lines):
    seq_states = {}
    for seq, screenid in enumerate(screens_sequence):
        seq_states[seq] = {'screenid': screenid, 'fixations': sequence_fixations[seq], 'lines': sequence_lines[seq]}
    return seq_states

def load_trial(stimuli, trial_path):
    screens_lst = list(range(1, len(stimuli['screens']) + 1))
    screens, screens_fixations, screens_lines = dict.fromkeys(screens_lst), dict.fromkeys(screens_lst), dict.fromkeys(screens_lst)
    for screenid in screens_lst:
        screens_lines[screenid] = utils.load_screen_linescoords(screenid, trial_path)
        screens[screenid] = utils.load_stimuli_screen(screenid, stimuli)
        screens_fixations[screenid] = utils.load_screen_fixations(screenid, trial_path)
    return screens, screens_fixations, screens_lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stimuli_path', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/per_participant')
    parser.add_argument('--subj', type=str, required=True)
    parser.add_argument('--item', type=str, required=True)
    args = parser.parse_args()
    
    data_path = Path(args.data_path) / args.subj / args.item
    stimuli   = utils.load_stimuli(args.item, Path(args.stimuli_path))
    
    plot_trial(stimuli, data_path)