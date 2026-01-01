from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

class ToggleButton(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.is_checked = False
        self.initialize_ui()
        self.setup_animation()

    def initialize_ui(self) -> None:
        """Initialize UI components and basic properties"""
        self.setFixedSize(60, 30)
        self.create_button()

    def create_button(self) -> None:
        """Create the moveable button widget"""
        self.button = QWidget(self)
        self.button.setFixedSize(26, 26)
        self.reset_button_position()

    def reset_button_position(self) -> None:
        """Reset button to initial position"""
        self.button.move(2, 2)

    def setup_animation(self) -> None:
        """Configure the button movement animation"""
        self.animation = QPropertyAnimation(self.button, b'geometry')
        self.animation.setDuration(200)  # Add animation duration for better control

    def paintEvent(self, event) -> None:
        """Handle custom painting of the widget"""
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)

            self.draw_background(painter)
            self.draw_button(painter)
        finally:
            painter.end()

    def draw_background(self, painter) -> None:
        """Draw the toggle switch background"""
        bg_color = QColor(34, 34, 34) if self.is_checked else QColor('black')
        painter.setBrush(bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

    def draw_button(self, painter) -> None:
        """Draw the moveable button"""
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(self.button.geometry())

    def mousePressEvent(self, event) -> None:
        """Handle mouse click events"""
        self.toggle_state()

    def toggle_state(self) -> None:
        """Toggle the switch state and initiate animation"""
        self.is_checked = not self.is_checked
        self.configure_animation()
        self.update_visuals()
        self.notify_state_change()

    def configure_animation(self) -> None:
        """Set up animation parameters"""
        start_geometry = QRect(2, 2, 26, 26)
        end_geometry = self.calculate_end_position()

        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)

    def calculate_end_position(self) -> QRect:
        """Calculate button position based on current state"""
        return QRect(self.width() - 28, 2, 26, 26) if self.is_checked else QRect(2, 2, 26, 26)

    def update_visuals(self) -> None:
        """Update widget appearance and start animation"""
        self.update()
        self.animation.start()

    def notify_state_change(self) -> None:
        """Emit state change signal"""
        self.toggled.emit(self.is_checked)
