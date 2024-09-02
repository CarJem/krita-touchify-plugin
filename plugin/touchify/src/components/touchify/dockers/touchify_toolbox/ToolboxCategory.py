class ToolboxCategory:

    def __init__(self, name):
        self.name = name
        self.buttons = {} # Each ToolCategory has a dictionary of ToolButton.name : ToolButton items

    def addTool(self, btn):
        self.buttons[btn.name] = btn