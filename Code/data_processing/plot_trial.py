import argparse
import utils
import matplotlib.pyplot as plt
from draw_utils import drawing, handles
from tkinter import messagebox
from pathlib import Path

def plot_trial(stimuli, data_path):
    screens, screens_fixations, screens_lines = utils.load_trial(stimuli, data_path)
    sequence_states, screens_sequence = build_sequence_states(screens_fixations, screens_lines, data_path)
    
    state = {'sequence_index': 0, 'cids': []}
    fig, ax = plt.subplots()
    drawing.update_figure(state, fig, ax, screens, sequence_states)
    fig.canvas.mpl_connect('key_press_event', lambda event: handles.advance_sequence(event, state, screens, screens_sequence, sequence_states, ax, fig))
    plt.show()
    
    save_files = messagebox.askyesno(title='Modified trial', message='Do you want to save the trial?')
    if save_files:
        utils.update_and_save_trial(sequence_states, stimuli, data_path)

def build_sequence_states(screens_fixations, screens_lines, data_path):
    screens_sequence   = utils.load_screensequence(data_path)['currentscreenid'].to_numpy()
    sequence_lines     = [screens_lines[screenid].pop() for screenid in screens_sequence]
    sequence_fixations = [screens_fixations[screenid].pop() for screenid in screens_sequence]
    seq_states = {}
    for seq, screenid in enumerate(screens_sequence):
        seq_states[seq] = {'screenid': screenid, 'fixations': sequence_fixations[seq], 'lines': sequence_lines[seq]}
    return seq_states, screens_sequence

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stimuli_path', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/by_participant')
    parser.add_argument('--subj', type=str, required=True)
    parser.add_argument('--item', type=str, required=True)
    args = parser.parse_args()
    
    data_path = Path(args.data_path) / args.subj / args.item
    stimuli   = utils.load_stimuli(args.item, Path(args.stimuli_path))
    
    plot_trial(stimuli, data_path)