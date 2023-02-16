import argparse
import utils
import matplotlib as mpl
import matplotlib.pyplot as plt
from plot_scanpath import draw_scanpath
from pathlib import Path

def plot_trial(stimuli, data_path):
    screens, screens_fixations, screens_lines = load_trial(stimuli, data_path)
    screens_sequence   = utils.load_screensequence(data_path)
    sequence_fixations = [screens_fixations[screenid].pop() for screenid in screens_sequence]
    # dict indexed by sequence index, containing screenid, fixations and lines, to allow editing
    sequence_states = build_sequence_states(sequence_fixations, screens_sequence, screens_lines)
    
    state = {'sequence_index': 0}
    fig, ax = plt.subplots()
    
    current_seq = state['sequence_index']
    screenid, fixations, lines = sequence_states[current_seq]['screenid'], sequence_states[current_seq]['fixations'], sequence_states[current_seq]['lines']
    draw_scanpath(screens[screenid], fixations, fig, ax, hlines=lines, editable=False)

    fig.canvas.mpl_connect('key_press_event', lambda event: update_figure(event, state, screens, screens_sequence, sequence_states, ax, fig))
    plt.show()
    
def update_figure(event, state, screens, screens_sequence, sequence_states, ax, fig):
    prev_seq = state['sequence_index']
    if event.key == 'right':
        if prev_seq < len(screens_sequence) - 1:
            state['sequence_index'] += 1
    elif event.key == 'left':
        if prev_seq > 0:
            state['sequence_index'] -= 1
    current_seq = state['sequence_index']
    if prev_seq != current_seq:
        screenid, fixations, lines = sequence_states[current_seq]['screenid'], sequence_states[current_seq]['fixations'], sequence_states[current_seq]['lines']
        draw_scanpath(screens[screenid], fixations, fig, ax, hlines=lines, editable=False)

def build_sequence_states(sequence_fixations, screens_sequence, screens_lines):
    seq_states = {}
    for seq, screenid in enumerate(screens_sequence):
        seq_states[seq] = {'screenid': screenid, 'fixations': sequence_fixations[seq], 'lines': screens_lines[screenid]}
    return seq_states

def load_trial(stimuli, trial_path):
    screens_lst = list(range(1, len(stimuli['screens']) + 1))
    screens, screens_fixations, screens_lines = dict.fromkeys(screens_lst), dict.fromkeys(screens_lst), dict.fromkeys(screens_lst)
    for screenid in screens_lst:
        screens_lines[screenid] = utils.load_screen_linescoords(screenid, stimuli)
        screens[screenid] = utils.load_stimuli_screen(screenid, stimuli)
        screens_fixations[screenid] = utils.load_screen_fixations(screenid, trial_path)
    return screens, screens_fixations, screens_lines

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='Metadata/stimuli_config.mat')
    parser.add_argument('--stimuli_path', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/raw')
    parser.add_argument('--data_format', type=str, default='pkl')
    parser.add_argument('--subj', type=str, required=True)
    parser.add_argument('--item', type=str, required=True)
    args = parser.parse_args()
    
    data_path = Path(args.data_path) / args.subj / args.data_format / args.item
    stimuli   = utils.load_stimuli(args.item, Path(args.stimuli_path), Path(args.config))
    
    plot_trial(stimuli, data_path)