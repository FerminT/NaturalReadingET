from draw_utils import handles, drawing
import utils
import matplotlib as mpl

def draw_scanpath(img, df_fix, fig, ax, ann_size=8, fix_size=15, min_t=250, title=None, lines_coords=None, editable=False):
    """ df_fix: pd.DataFrame with columns: ['xAvg', 'yAvg', 'duration'] """
    """ Given a scanpath, draw on the img using the fig and axes """
    """ The duration of each fixation is used to determine the size of each circle """
    ax.clear()
    ax.imshow(img, cmap=mpl.colormaps['gray'])
    if title:
        ax.set_title(title)

    xs, ys, ts = utils.get_fixations(df_fix)
    circles, colors = drawing.draw_circles(ax, xs, ys, ts, df_fix, min_t, fix_size, ann_size)
    arrows = drawing.draw_arrows(ax, circles, colors)
    hlines = drawing.draw_hlines(ax, lines_coords)

    cids = []
    if editable:
        last_actions = []
        cids.append(fig.canvas.mpl_connect('button_press_event', lambda event: handles.onclick(event, circles, arrows, fig, ax, colors, last_actions, df_fix, lines_coords, hlines)))
        cids.append(fig.canvas.mpl_connect('motion_notify_event', lambda event: handles.move_hline(event, last_actions)))
        cids.append(fig.canvas.mpl_connect('button_release_event', lambda event: handles.release_hline(event, lines_coords, last_actions)))

    ax.axis('off')
    fig.canvas.draw()
    
    return cids