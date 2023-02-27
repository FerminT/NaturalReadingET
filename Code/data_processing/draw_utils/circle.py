class FixCircle:
    def __init__(self, id, circle, ann, fixation):
        self.id = id
        self.circle = circle
        self.ann = ann
        self.fixation = fixation
    
    def center(self):
        return self.circle.center
    
    def contains(self, event):
        return self.circle.contains(event)[0]
    
    def fix_name(self):
        return self.fixation.name
    
    def remove(self):
        self.circle.remove()
        self.ann.remove()
    
    def add_to_axes(self, ax):
        ax.add_patch(self.circle), ax.add_artist(self.ann)