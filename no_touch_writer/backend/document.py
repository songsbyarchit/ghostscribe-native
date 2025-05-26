from backend.models import Action
from typing import List

class Document:
    def __init__(self):
        self.actions: List[Action] = []
        self.history: List[List[Action]] = []
        self.redo_stack: List[List[Action]] = []

    def apply_actions(self, new_actions: List[Action]):
        self.history.append(self.actions.copy())
        self.redo_stack.clear()  # clear redo after new changes
        if len(self.history) > 10:
            self.history.pop(0)
        for action in new_actions:
            if action.target_heading:
                index = next((i for i, a in enumerate(self.actions)
                              if a.type == "heading" and a.content.strip().lower() == action.target_heading.strip().lower()), None)
                if index is not None:
                    self.actions.insert(index + 1, action)
                    continue
            self.actions.append(action)

    def undo_last(self, n: int = 1):
        if not self.history:
            return
        self.redo_stack.append(self.actions.copy())
        self.actions = self.history[-n]
        self.history = self.history[:-n]

    def redo_last(self, n: int = 1):
        if not self.redo_stack:
            return
        self.history.append(self.actions.copy())
        self.actions = self.redo_stack.pop()

    def get_content(self):
        return self.actions
