from .circle import FixCircle
from .line import HLine
from .drawing import draw_arrow

def onclick(event, circles, arrows, fig, ax, colors, last_actions, df_fix, lines_coords, hlines):
    if event.button == 1:
        handle_click(event, hlines, circles, arrows, ax, colors, last_actions, df_fix)
    elif event.button == 3:
        undo_lastaction(last_actions, circles, arrows, ax, colors, lines_coords, df_fix)
    fig.canvas.draw()

def handle_click(event, hlines, circles, arrows, ax, colors, last_actions, df_fix):
    clicked_fixation = remove_fixation(event, circles, arrows, ax, colors, last_actions, df_fix)
    if not clicked_fixation:
        select_hline(event, hlines, last_actions)

def release_hline(event, lines_coords, last_actions):
    if event.button == 1 and last_actions:
        selected_line = last_actions[-1]
        if isinstance(selected_line, HLine) and selected_line.is_selected:
            lines_coords[selected_line.id] = selected_line.get_y()
            selected_line.desselect()

def move_hline(event, last_actions):
    if not last_actions: return
    selected_line = last_actions[-1]
    if isinstance(selected_line, HLine) and selected_line.is_selected:
        selected_line.update_y(event.ydata)
        
def select_hline(event, hlines, last_actions):
    for line in hlines:
        if line.contains(event):
            line.select()
            last_actions.append(line)
            break

def undo_lastaction(last_actions, circles, arrows, ax, colors, lines_coords, df_fix):
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
            lines_coords[line.id] = line.get_y()

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