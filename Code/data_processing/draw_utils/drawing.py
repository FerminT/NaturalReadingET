from .circle import FixCircle
from .line import HLine
from .handles import onclick, move_object, release_object
from PIL import Image, ImageDraw
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def update_figure(state, fig, ax, screens, sequence_states, editable):
    current_seqid = state['sequence_index']
    screenid, fixations, lines = sequence_states[current_seqid]['screenid'], \
        sequence_states[current_seqid]['fixations'], \
        sequence_states[current_seqid]['lines']
    state['cids'] = draw_scanpath(screens[screenid], fixations, fig, ax,
                                  title=f'Screen {screenid}',
                                  lines_coords=lines,
                                  editable=editable)


def draw_scanpath(img, df_fix, fig, ax, ann_size=8, fix_size=15, min_t=250, title=None, lines_coords=None,
                  editable=False):
    """ df_fix: pd.DataFrame with columns: ['xAvg', 'yAvg', 'duration'] """
    """ Given a scanpath, draw on the img using the fig and axes """
    """ The duration of each fixation is used to determine the size of each circle """
    ax.clear()
    ax.imshow(img, cmap=mpl.colormaps['gray'])
    if title:
        ax.set_title(title)

    xs, ys, ts = df_fix['xAvg'].to_numpy(dtype=int), df_fix['yAvg'].to_numpy(dtype=int), df_fix['duration'].to_numpy()
    circles, colors = draw_circles(ax, xs, ys, ts, df_fix, min_t, fix_size, ann_size)
    arrows = draw_arrows(ax, circles, colors)
    hlines = draw_hlines(ax, lines_coords)

    cids = []
    if editable:
        last_actions = []
        cids.append(fig.canvas.mpl_connect('button_press_event',
                                           lambda event: onclick(event, circles, arrows, fig, ax, colors, last_actions,
                                                                 df_fix, lines_coords, hlines)))
        cids.append(fig.canvas.mpl_connect('motion_notify_event', lambda event: move_object(event, last_actions)))
        cids.append(fig.canvas.mpl_connect('button_release_event',
                                           lambda event: release_object(event, lines_coords, df_fix, last_actions)))

    ax.axis('off')
    fig.canvas.draw()

    return cids


def draw_circles(ax, xs, ys, ts, df_fix, min_t, fix_size, ann_size):
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
        fixation = df_fix.iloc[i]
        annotation = plt.annotate("{}".format(fixation.name + 1), xy=(x, y), fontsize=ann_size, ha="center",
                                  va="center", alpha=0.5)
        fix_circle = FixCircle(i, circle, annotation, fixation)
        circles.append(fix_circle)
    return circles, colors


def draw_arrows(ax, circles, colors):
    arrows = [draw_arrow(ax, circles[i].center(), circles[i + 1].center(), colors[i]) for i in range(len(circles) - 1)]
    return arrows


def draw_hlines(ax, lines_coords):
    hlines = []
    if lines_coords is not None:
        for i, line_coord in enumerate(lines_coords):
            line2d = ax.axhline(y=line_coord, color='black', lw=0.5)
            line = HLine(i, line2d)
            hlines.append(line)
    return hlines


def draw_arrow(ax, p1, p2, color, alpha=0.2, width=0.05):
    x1, y1 = p1
    x2, y2 = p2
    arrow = mpl.patches.Arrow(x1, y1, x2 - x1, y2 - y1, width=width, color=color, alpha=alpha)
    ax.add_patch(arrow)
    return arrow


def screen(points=[], point_size=14, height=1080, width=1920, color='grey'):
    """ Draw an empty image with the given points """
    img = Image.new('RGB', (width, height), color=color)
    draw = ImageDraw.Draw(img)
    if len(points):
        xs, ys = points['x'].to_numpy(), points['y'].to_numpy()
        for x, y in zip(xs, ys):
            draw.ellipse((x - point_size, y - point_size, x + point_size, y + point_size), fill='black')

    return np.array(img)
