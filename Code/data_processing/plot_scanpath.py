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
    circles, circles_anns = [], []
    for i, (x, y, t) in enumerate(zip(xs, ys, ts)):
        aug_factor = 1 if t <= min_t else t / min_t
        radius = int(fix_size * aug_factor)
        circle = mpl.patches.Circle((x, y),
                                radius=radius,
                                color=colors[i],
                                alpha=0.3)
        ax.add_patch(circle)
        circle_anns = plt.annotate("{}".format(df_fix.iloc[i].name + 1), xy=(x, y + 3), fontsize=ann_size, ha="center", va="center", alpha=0.5)
        circles.append(circle), circles_anns.append(circle_anns)

    arrows = []
    for i in range(len(circles) - 1):
        draw_arrow(ax, circles[i].center, circles[i + 1].center, colors[i], arrows, i)

    drawn_hlines = []
    if hlines is not None:
        for line_coord in hlines:
            line = ax.axhline(y=line_coord, color='black', lw=0.5)
            drawn_hlines.append(line)

    cids = []
    if editable:
        last_actions = []
        def onclick(event):
            if event.button == 1:
                handle_click(event, drawn_hlines, circles, circles_anns, arrows, ax, colors, last_actions, hlines, df_fix)
            elif event.button == 3:
                undo_lastaction(last_actions, circles, circles_anns, arrows, ax, colors, hlines, df_fix)
            fig.canvas.draw()
        cids.append(fig.canvas.mpl_connect('button_press_event', onclick))
        cids.append(fig.canvas.mpl_connect('motion_notify_event', lambda event: move_hline(event, last_actions)))
        cids.append(fig.canvas.mpl_connect('button_release_event', lambda event: release_hline(event, hlines, last_actions)))

    ax.axis('off')
    fig.canvas.draw()
    
    return cids

def handle_click(event, drawn_hlines, circles, circles_anns, arrows, ax, colors, last_actions, hlines, df_fix):
    clicked_fixation = remove_fixation(event, circles, circles_anns, arrows, ax, colors, last_actions, df_fix)
    if not clicked_fixation:
        select_hline(event, drawn_hlines, last_actions)

def release_hline(event, hlines, last_actions):
    if event.button == 1:
        selected_line, index, y0, is_selected = last_actions[-1]
        if isinstance(selected_line, mpl.lines.Line2D) and is_selected:
            hlines[index] = selected_line.get_ydata()[0]
            last_actions[-1] = (selected_line, index, y0, False)
            selected_line.figure.canvas.draw()

def move_hline(event, last_actions):
    if not last_actions: return
    selected_line, _, y0, is_selected = last_actions[-1]
    if isinstance(selected_line, mpl.lines.Line2D) and is_selected:
        dy = event.ydata - y0
        selected_line.set_ydata([y0 + dy, y0 + dy])
        selected_line.figure.canvas.draw()
        
def select_hline(event, drawn_hlines, last_actions):
    for i, line in enumerate(drawn_hlines):
        if line.contains(event)[0]:
            y0 = line.get_ydata()[0][0]
            last_actions.append((line, i, y0, True))
            break

def undo_lastaction(last_actions, circles, circles_anns, arrows, ax, colors, hlines, df_fix):
    if last_actions:
        # TODO: restructure last_actions with a proper class
        last_action, index, ann, fixation = last_actions.pop()
        if isinstance(last_action, mpl.patches.Circle):
            circles.insert(index, last_action)
            circles_anns.insert(index, ann)
            ax.add_patch(last_action), ax.add_artist(ann)
            fix_index = int(ann.get_text()) - 1
            df_fix.loc[fix_index] = fixation
            df_fix.sort_index(inplace=True)

            if index > 0 and index < len(circles) - 1:
                arrows[index - 1].remove(), arrows.pop(index - 1)
            if index > 0:
                draw_arrow(ax, circles[index - 1].center, circles[index].center, colors[index], arrows, index - 1)
            if index < len(circles) - 1:
                draw_arrow(ax, circles[index].center, circles[index + 1].center, colors[index], arrows, index)
        elif isinstance(last_action, mpl.lines.Line2D) and not fixation:
            last_action.set_ydata([ann, ann])
            hlines[index] = ann

def remove_fixation(event, circles, circles_anns, arrows, ax, colors, last_actions, df_fix):
    removed_fix = False
    for i, circle in enumerate(circles):
        if circle.contains(event)[0]:
            fix_index = int(circles_anns[i].get_text()) - 1
            fixation  = df_fix.loc[fix_index]
            last_actions.append((circle, i, circles_anns[i], fixation))
            if i < len(circles) - 1:
                arrows[i].remove(), arrows.pop(i)
            if i > 0:
                arrows[i - 1].remove(), arrows.pop(i - 1)
            if i > 0 and i < len(circles) - 1:
                draw_arrow(ax, circles[i - 1].center, circles[i + 1].center, colors[i], arrows, i - 1)
                
            circle.remove(), circles.pop(i)
            df_fix.drop(fix_index, inplace=True)
            circles_anns[i].remove(), circles_anns.pop(i)
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