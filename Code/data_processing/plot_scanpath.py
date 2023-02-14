from scipy.io import loadmat
from pathlib import Path
import argparse
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def plot_scanpath(img, fixs_list, interactive=True):
    for fixs in fixs_list:
        xs, ys, ts = fixs['xAvg'].to_numpy(dtype=int), fixs['yAvg'].to_numpy(dtype=int), fixs['duration'].to_numpy()
        fig, ax = plt.subplots()
        ax.imshow(img, cmap=mpl.colormaps['gray'])
        color_map = mpl.colormaps['rainbow']
        colors = color_map(np.linspace(0, 1, xs.shape[0]))
        
        cir_rad_min, cir_rad_max = 10, 70
        rad_per_T = (cir_rad_max - cir_rad_min) / (ts.max() - ts.min())

        circles, circles_anns = [], []
        for i, (x, y, t) in enumerate(zip(xs, ys, ts)):
            radius = int(10 + rad_per_T * (t - ts.min()))
            circle = mpl.patches.Circle((x, y),
                                    radius=radius,
                                    color=colors[i],
                                    alpha=0.3)
            ax.add_patch(circle)
            circle_anns = plt.annotate("{}".format(i + 1), xy=(x, y + 3), fontsize=10, ha="center", va="center", alpha=0.5)
            circles.append(circle), circles_anns.append(circle_anns)

        arrows = []
        for i in range(len(circles) - 1):
            x1, y1 = circles[i].center
            x2, y2 = circles[i + 1].center
            arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=0.05, color=colors[i], alpha=0.2)
            arrows.append(arrow)
            ax.add_patch(arrow)

        lines = []
        removed_fixations = []
        if interactive:
            latest_action = []
            def onclick(event):
                inside_circle = False
                if event.button == 1:
                    for i, circle in enumerate(circles):
                        if circle.contains(event)[0]:
                            inside_circle = True
                            # remove the circle from the plot
                            latest_action.append((circle, i, circles_anns[i]))
                            circle.remove(), circles.pop(i)
                            removed_fixations.append(int(circles_anns[i].get_text()))
                            circles_anns[i].remove(), circles_anns.pop(i)
                            fig.canvas.draw()
                            
                            # update the arrows
                            for i in range(len(arrows) - 1, -1, -1):
                                arrows[i].remove()
                                arrows.pop(i)
                            
                            for i in range(len(circles) - 1):
                                x1, y1 = circles[i].center
                                x2, y2 = circles[i + 1].center
                                arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=0.05, color=colors[i], alpha=0.2)
                                arrows.append(arrow)
                                ax.add_patch(arrow)

                            fig.canvas.draw()
                            break
                    if not inside_circle:
                        line = ax.axhline(y=event.ydata, color='black')
                        lines.append(event.ydata)
                        latest_action.append((line, len(lines) - 1, -1))
                        fig.canvas.draw()
                elif event.button == 3:
                    if latest_action:
                        last_action, index, ann = latest_action.pop()
                        if isinstance(last_action, mpl.patches.Circle):
                            circles.insert(index, last_action)
                            circles_anns.insert(index, ann)
                            removed_fixations.remove(int(ann.get_text()))
                            ax.add_patch(last_action)
                            ax.add_artist(ann)
                            # update the arrows
                            for i in range(len(arrows) - 1, -1, -1):
                                arrows[i].remove()
                                arrows.pop(i)
                            
                            for i in range(len(circles) - 1):
                                x1, y1 = circles[i].center
                                x2, y2 = circles[i + 1].center
                                arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=0.05, color=colors[i], alpha=0.2)
                                arrows.append(arrow)
                                ax.add_patch(arrow)

                            fig.canvas.draw()
                        elif isinstance(last_action, mpl.lines.Line2D):
                            last_action.remove()
                            lines.pop(index)
                            fig.canvas.draw()

            fig.canvas.mpl_connect("button_press_event", onclick)

        ax.axis('off')
        plt.show()
        print(removed_fixations)
        print(lines)

def load_stimuli(item, stimuli_path):
    stimuli_file = stimuli_path / (item + '.mat')
    if not stimuli_file.exists():
        raise ValueError('Stimuli file does not exist: ' + str(stimuli_file))
    stimuli = loadmat(str(stimuli_file), simplify_cells=True)
    return stimuli

def load_stimuli_screen(screenid, stimuli):
    return stimuli['screens'][screenid - 1]['image']

def load_screen_fixations(screenid, subjitem_path, dataformat='pkl'):
    screen_path = subjitem_path / ('screen_' + str(screenid))
    fixations_files  = screen_path.glob('fixations*.%s'%dataformat)
    screen_fixations = [pd.read_pickle(fix_file) for fix_file in fixations_files]
    if not screen_fixations:
        raise ValueError('No fixations found for screen ' + str(screenid) + ' in ' + str(subjitem_path))
    return screen_fixations

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stimuli_path', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/raw')
    parser.add_argument('--data_format', type=str, default='pkl')
    parser.add_argument('--subj', type=str, required=True)
    parser.add_argument('--item', type=str, required=True)
    parser.add_argument('--screenid', type=int, default=1)
    args = parser.parse_args()

    subjitem_path = Path(args.data_path) / args.subj / args.data_format / args.item

    stimuli = load_stimuli(args.item, Path(args.stimuli_path))
    screen  = load_stimuli_screen(args.screenid, stimuli)
    fixations = load_screen_fixations(args.screenid, subjitem_path)
    
    plot_scanpath(screen, fixations)