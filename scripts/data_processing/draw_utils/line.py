import numpy as np


class HLine:
    def __init__(self, id, line):
        self.id = id
        self.line = line
        self.prev_y = None
        self.is_selected = False
        
    def contains(self, event):
        return self.line.contains(event)[0]

    def select(self):
        self.is_selected = True
        self.prev_y = self.get_y()

    def deselect(self, lines_coords):
        lines_coords[self.id] = self.get_y()
        self.is_selected = False

    def update_coords(self, x, y):
        self.line.set_ydata([y, y])

    def update_y(self, y):
        self.line.set_ydata([y, y])
        self.draw_canvas()
    
    def get_y(self):
        y = self.line.get_ydata()[0]
        if isinstance(y, np.ndarray):
            y = y[0]
        return y
    
    def restore_y(self):
        self.update_y(self.prev_y)
    
    def draw_canvas(self):
        self.line.figure.canvas.draw()
