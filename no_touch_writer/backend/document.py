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
        if len(self.history) > 50:
            self.history.pop(0)
        for action in new_actions:
            if hasattr(action, "operation") and action.operation == "change_type":
                if hasattr(action, "target_line") and 0 <= action.target_line < len(self.actions):
                    self.history.append(self.actions.copy())
                    self.redo_stack.clear()
                    if len(self.history) > 50:
                        self.history.pop(0)
                    self.actions[action.target_line].type = action.type
                continue

            elif hasattr(action, "operation") and action.operation:
                self.apply_structural_action(action)
                continue

            elif action.target_heading:
                index = next((i for i, a in enumerate(self.actions)
                            if a.type == "heading" and a.content.strip().lower() == action.target_heading.strip().lower()), None)
                if index is not None:
                    self.actions.insert(index + 1, action)
                    continue

            self.actions.append(action)


    def undo_last(self, n: int = 1):
        for _ in range(n):
            if not self.history:
                return
            self.redo_stack.append(self.actions.copy())
            self.actions = self.history.pop()

    def redo_last(self, n: int = 1):
        for _ in range(n):
            if not self.redo_stack:
                return
            self.history.append(self.actions.copy())
            self.actions = self.redo_stack.pop()

    def get_content(self):
        return self.actions
    
    def to_dict(self):
        return {
            "content": [a.dict() for a in self.actions]
        }

    def apply_structural_action(self, action: Action):
        if action.target_line is None:
            # Safely append to end if no line is given
            self.actions.append(Action(
                type=action.type,
                content=action.content,
                level=action.level,
                target_heading=action.target_heading
            ))
            return

        idx = action.target_line - 1  # 1-based to 0-based index
        if action.operation == "delete":
            if 0 <= idx < len(self.actions):
                self.history.append(self.actions.copy())
                self.redo_stack.clear()
                self.actions.pop(idx)

        elif action.operation == "replace":
            if 0 <= idx < len(self.actions):
                self.history.append(self.actions.copy())
                self.redo_stack.clear()
                self.actions[idx] = Action(
                    type=action.type,
                    content=action.content,
                    level=action.level,
                    target_heading=action.target_heading
                )

        elif action.operation == "insert":
            if 0 <= idx <= len(self.actions):
                self.history.append(self.actions.copy())
                self.redo_stack.clear()
                self.actions.insert(idx, Action(
                    type=action.type,
                    content=action.content,
                    level=action.level,
                    target_heading=action.target_heading
                ))