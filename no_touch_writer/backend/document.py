from backend.models import Action
from typing import List

class Document:
    def __init__(self):
        self.actions: List[Action] = []
        self.history: List[List[Action]] = []

    def apply_actions(self, new_actions: List[Action]):
        self.history.append(self.actions.copy())
        if len(self.history) > 10:
            self.history.pop(0)

        for action in new_actions:
            if action.target_heading:
                # Try to find the heading in the current doc
                index = next((i for i, a in enumerate(self.actions)
                            if a.type == "heading" and a.content.strip().lower() == action.target_heading.strip().lower()), None)
                if index is not None:
                    # Insert right after the found heading
                    self.actions.insert(index + 1, action)
                    continue  # Skip appending to bottom
            self.actions.append(action)

    def undo_last(self, n: int = 1):
        if not self.history:
            return
        self.actions = self.history[-n]
        self.history = self.history[:-n]

    def get_content(self):
        return self.actions
