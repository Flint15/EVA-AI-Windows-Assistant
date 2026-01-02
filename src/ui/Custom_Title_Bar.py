from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QIcon

class CustomTitleBar(QWidget):
	"""
	A custom title bar widget for a window, providing: 
	1. minimize,
	2. maximize/restore,
	3. close buttons
	as well as dragging functionality.
	"""

	def __init__(self, parent):
		"""
		Initialize the CustomTitleBar.

		Args:
			parent: The parent widget, typically the main window.
		"""
		super().__init__()
		self.parent = parent
		self.setFixedHeight(30) # Set the height of the title bar
		self.setStyleSheet('background-color: #151515;') # Set background color

		self._setup_ui()
		self._connect_buttons()

		# Initialize dragging variables
		self.dragging = False
		self.offset = QPoint()

	def _setup_ui(self) -> None:
		"""
		Set up the UI elements and layout for the title bar.
		"""
		# Create the title label
		self.title = QLabel('Joy v1.0', self)
		self.title.setStyleSheet('color: white; font-size: 14px; background-color: transparent;')

		# Create minimize button
		self.minimize_button = QPushButton()
		self.minimize_button.setIcon(QIcon('./assets/minimize.png'))
		self.minimize_button.setStyleSheet('border: none; background-color: transparent;')

		# Create maximize button
		self.maximize_button = QPushButton()
		self.maximize_button.setIcon(QIcon('./assets/maximize.png'))
		self.maximize_button.setStyleSheet('border: none; background-color: transparent;')

		# Create close button
		self.close_button = QPushButton()
		self.close_button.setIcon(QIcon('./assets/close.png'))
		self.close_button.setStyleSheet('border: none; background-color: transparent;')

		# Set up the layout
		layout = QHBoxLayout(self)
		layout.addWidget(self.title)
		layout.addStretch() # Push buttons to the right
		layout.addWidget(self.minimize_button)
		layout.addWidget(self.maximize_button)
		layout.addWidget(self.close_button)
		layout.setContentsMargins(10, 0, 10, 0)

	def _connect_buttons(self) -> None:
		"""
		Connect the buttons to their respective functions.
		"""
		self.minimize_button.clicked.connect(self.parent.showMinimized)
		self.maximize_button.clicked.connect(self.toggle_maximize_restore)
		self.close_button.clicked.connect(self.parent.close)

	def toggle_maximize_restore(self) -> None:
		"""
		Toggle the window between maximized and normal state.
		"""
		if self.parent.isMaximized():
			self.parent.showNormal()
		else:
			self.parent.showMaximized()

	def mousePressEvent(self, event):
		"""
		Handle mouse press events to start dragging the window.
		"""
		if event.button() == Qt.LeftButton:
			self.dragging = True
			# Calculate the offset from the mouse position to the window positon
			self.offset = event.globalPos() - self.parent.pos()

	def mouseMoveEvent(self, event):
		"""
		Handle mouse move events to drag the window.
		"""
		if self.dragging:
			# Move the window to the new position based on the mouse movement
			self.parent.move(event.globalPos() - self.offset)

	def mouseReleaseEvent(self, event):
		"""
		Handle mouse release events to stop dragging.
		"""
		if event.button() == Qt.LeftButton:
			self.dragging = False
