from pathlib import Path
import utils
import argparse
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

def plot_scanpath(img, lst_fixs, editable=True):
    for fixs in lst_fixs:
        fig, ax = plt.subplots()
        draw_scanpath(img, fixs, fig, ax, editable)
        plt.show()

def draw_scanpath(img, df_fix, fig, ax, hlines=None, editable=True):
    """ df_fix: pd.DataFrame with columns: ['xAvg', 'yAvg', 'duration'] """
    """ Given a scanpath, draw on the img using the fig and axes """
    """ The duration of each fixation is used to determine the size of each circle """
    ax.clear()
    ax.imshow(img, cmap=mpl.colormaps['gray'])

    xs, ys, ts = utils.get_fixations(df_fix)
    colors = mpl.colormaps['rainbow'](np.linspace(0, 1, xs.shape[0]))
    circles, circles_anns = [], []
    cir_rad_min, cir_rad_max = 10, 70
    rad_per_T = (cir_rad_max - cir_rad_min) / (ts.max() - ts.min())
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
        add_arrow(ax, circles[i].center, circles[i + 1].center, colors[i], arrows, i)

    drawn_hlines = []
    if hlines:
        for line_coord in hlines:
            line = ax.axhline(y=line_coord, color='black', lw=0.5)
            drawn_hlines.append(line)
    removed_fixations = []
    if editable:
        last_actions = []
        def onclick(event):
            if event.button == 1:
                remove_fixation(event, circles, circles_anns, arrows, ax, colors, last_actions, removed_fixations)
            elif event.button == 3:
                undo_lastaction(last_actions, circles, circles_anns, arrows, ax, colors, hlines, removed_fixations)
            fig.canvas.draw()
        fig.canvas.mpl_connect("button_press_event", onclick)

    ax.axis('off')
    fig.canvas.draw()

def undo_lastaction(last_actions, circles, circles_anns, arrows, ax, colors, lines, removed_fixations):
    if last_actions:
        last_action, index, ann = last_actions.pop()
        if isinstance(last_action, mpl.patches.Circle):
            circles.insert(index, last_action)
            circles_anns.insert(index, ann)
            removed_fixations.remove(int(ann.get_text()))
            ax.add_patch(last_action), ax.add_artist(ann)
            
            if index > 0 and index < len(circles) - 1:
                arrows[index - 1].remove(), arrows.pop(index - 1)
            if index > 0:
                add_arrow(ax, circles[index - 1].center, circles[index].center, colors[index], arrows, index - 1)
            if index < len(circles) - 1:
                add_arrow(ax, circles[index].center, circles[index + 1].center, colors[index], arrows, index)
        elif isinstance(last_action, mpl.lines.Line2D):
            last_action.remove()
            lines.pop(index)

def add_hline(event, lines, last_actions, ax):
    line = ax.axhline(y=event.ydata, color='black')
    lines.append(event.ydata)
    last_actions.append((line, len(lines) - 1, -1))

def remove_fixation(event, circles, circles_anns, arrows, ax, colors, last_actions, removed_fixations):
    for i, circle in enumerate(circles):
        if circle.contains(event)[0]:
            last_actions.append((circle, i, circles_anns[i]))
            if i < len(circles) - 1:
                arrows[i].remove(), arrows.pop(i)
            if i > 0:
                arrows[i - 1].remove(), arrows.pop(i - 1)
            if i > 0 and i < len(circles) - 1:
                add_arrow(ax, circles[i - 1].center, circles[i + 1].center, colors[i], arrows, i - 1)
                
            circle.remove(), circles.pop(i)
            removed_fixations.append(int(circles_anns[i].get_text()))
            circles_anns[i].remove(), circles_anns.pop(i)
            break

def add_arrow(ax, p1, p2, color, arrows_list, index, alpha=0.2, width=0.05):
    x1, y1 = p1
    x2, y2 = p2
    arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=width, color=color, alpha=alpha)
    arrows_list.insert(index, arrow)
    ax.add_patch(arrow)

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

    stimuli = utils.load_stimuli(args.item, Path(args.stimuli_path))
    screen  = utils.load_stimuli_screen(args.screenid, stimuli)
    fixations = utils.load_screen_fixations(args.screenid, subjitem_path)
    
    plot_scanpath(screen, fixations)