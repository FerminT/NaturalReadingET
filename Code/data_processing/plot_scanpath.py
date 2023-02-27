from pathlib import Path
from draw_utils.circle import FixCircle
from draw_utils.line import HLine
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

def draw_scanpath(img, df_fix, fig, ax, ann_size=8, fix_size=15, min_t=250, title=None, hlines=None, editable=False):
    """ df_fix: pd.DataFrame with columns: ['xAvg', 'yAvg', 'duration'] """
    """ Given a scanpath, draw on the img using the fig and axes """
    """ The duration of each fixation is used to determine the size of each circle """
    ax.clear()
    ax.imshow(img, cmap=mpl.colormaps['gray'])
    if title:
        ax.set_title(title)

    xs, ys, ts = utils.get_fixations(df_fix)
    colors = mpl.colormaps['rainbow'](np.linspace(0, 1, xs.shape[0]))
    circles = []
    for i, (x, y, t) in enumerate(zip(xs, ys, ts)):
        aug_factor = 1 if t <= min_t else t / min_t
        radius = int(fix_size * aug_factor)
        circle = mpl.patches.Circle((x, y),
                                radius=radius,
                                color=colors[i],
                                alpha=0.3)
        ax.add_patch(circle)
        fixation   = df_fix.iloc[i]
        annotation = plt.annotate("{}".format(fixation.name + 1), xy=(x, y + 3), fontsize=ann_size, ha="center", va="center", alpha=0.5)
        fix_circle = FixCircle(i, circle, annotation, fixation)
        circles.append(fix_circle)

    arrows = []
    for i in range(len(circles) - 1):
        draw_arrow(ax, circles[i].center(), circles[i + 1].center(), colors[i], arrows, i)

    drawn_hlines = []
    if hlines is not None:
        for i, line_coord in enumerate(hlines):
            line2d = ax.axhline(y=line_coord, color='black', lw=0.5)
            line = HLine(i, line2d)
            drawn_hlines.append(line)

    cids = []
    if editable:
        last_actions = []
        cids.append(fig.canvas.mpl_connect('button_press_event', lambda event: onclick(event, circles, arrows, fig, ax, colors, last_actions, df_fix, hlines, drawn_hlines)))
        cids.append(fig.canvas.mpl_connect('motion_notify_event', lambda event: move_hline(event, last_actions)))
        cids.append(fig.canvas.mpl_connect('button_release_event', lambda event: release_hline(event, hlines, last_actions)))

    ax.axis('off')
    fig.canvas.draw()
    
    return cids

def onclick(event, circles, arrows, fig, ax, colors, last_actions, df_fix, hlines, drawn_hlines):
    if event.button == 1:
        handle_click(event, drawn_hlines, circles, arrows, ax, colors, last_actions, df_fix)
    elif event.button == 3:
        undo_lastaction(last_actions, circles, arrows, ax, colors, hlines, df_fix)
    fig.canvas.draw()

def handle_click(event, drawn_hlines, circles, arrows, ax, colors, last_actions, df_fix):
    clicked_fixation = remove_fixation(event, circles, arrows, ax, colors, last_actions, df_fix)
    if not clicked_fixation:
        select_hline(event, drawn_hlines, last_actions)

def release_hline(event, hlines, last_actions):
    if event.button == 1:
        selected_line = last_actions[-1]
        if isinstance(selected_line, HLine) and selected_line.is_selected:
            hlines[selected_line.id] = selected_line.get_y()
            selected_line.desselect()

def move_hline(event, last_actions):
    if not last_actions: return
    selected_line = last_actions[-1]
    if isinstance(selected_line, HLine) and selected_line.is_selected:
        selected_line.update_y(event.ydata)
        
def select_hline(event, drawn_hlines, last_actions):
    for line in drawn_hlines:
        if line.contains(event):
            line.select()
            last_actions.append(line)
            break

def undo_lastaction(last_actions, circles, arrows, ax, colors, hlines, df_fix):
    if last_actions:
        last_action = last_actions.pop()
        if isinstance(last_action, FixCircle):
            fix_circle = last_action
            index = fix_circle.id
            circles.insert(index, fix_circle)
            fix_circle.add_to_axes(ax)
            df_fix.loc[fix_circle.fix_name()] = fix_circle.fixation
            df_fix.sort_index(inplace=True)

            if index > 0 and index < len(circles) - 1:
                arrows[index - 1].remove(), arrows.pop(index - 1)
            if index > 0:
                draw_arrow(ax, circles[index - 1].center(), circles[index].center(), colors[index], arrows, index - 1)
            if index < len(circles) - 1:
                draw_arrow(ax, circles[index].center(), circles[index + 1].center(), colors[index], arrows, index)
        elif isinstance(last_action, HLine) and not last_action.is_selected:
            line = last_action
            line.restore_y()
            hlines[line.id] = line.get_y()

def remove_fixation(event, circles, arrows, ax, colors, last_actions, df_fix):
    removed_fix = False
    for i, fix_circle in enumerate(circles):
        if fix_circle.contains(event):
            if i < len(circles) - 1:
                arrows[i].remove(), arrows.pop(i)
            if i > 0:
                arrows[i - 1].remove(), arrows.pop(i - 1)
            if i > 0 and i < len(circles) - 1:
                draw_arrow(ax, circles[i - 1].center(), circles[i + 1].center(), colors[i], arrows, i - 1)
            
            last_actions.append(fix_circle)
            fix_circle.remove(), circles.pop(i)
            df_fix.drop(fix_circle.fix_name(), inplace=True)
            removed_fix = True
            break
    return removed_fix

def draw_arrow(ax, p1, p2, color, arrows_list, index, alpha=0.2, width=0.05):
    x1, y1 = p1
    x2, y2 = p2
    arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=width, color=color, alpha=alpha)
    arrows_list.insert(index, arrow)
    ax.add_patch(arrow)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--stimuli_path', type=str, default='Stimuli')
    parser.add_argument('--data_path', type=str, default='Data/processed/per_participant')
    parser.add_argument('--subj', type=str, required=True)
    parser.add_argument('--item', type=str, required=True)
    parser.add_argument('--screenid', type=int, default=1)
    args = parser.parse_args()

    subjitem_path = Path(args.data_path) / args.subj / args.item

    stimuli = utils.load_stimuli(args.item, Path(args.stimuli_path))
    screen  = utils.load_stimuli_screen(args.screenid, stimuli)
    fixations = utils.load_screen_fixations(args.screenid, subjitem_path)
    
    plot_scanpath(screen, fixations)