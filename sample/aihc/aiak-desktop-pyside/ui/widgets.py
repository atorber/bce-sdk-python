# ui/widgets.py

from PySide6.QtWidgets import QLineEdit
from PySide6.QtGui import QColor


class PlaceholderLineEdit(QLineEdit):
    """QLineEdit widget with placeholder functionality."""

    def __init__(self, placeholder="", color=QColor('grey'), parent=None):
        super().__init__(parent)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_palette = self.palette()
        self.setPlaceholderText(self.placeholder)

        # Optional: Additional styling or behavior can be added here if needed
