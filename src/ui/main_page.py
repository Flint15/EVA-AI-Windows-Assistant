from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QWidget, QToolButton, QMenu, QAction, QMessageBox, QLabel,
    QLineEdit, QSizePolicy, QFileDialog, QPushButton,
    QListWidget, QListWidgetItem, QAbstractItemView
)
from PyQt5.QtGui import (
    QMovie, QFont, QIcon, QPixmap
)
from PyQt5.QtCore import (
    Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve, pyqtSlot
)
import threading
import logging
import uuid
import re
from .toggle_button_implamantation import ToggleButton
from src.data import load_user_data
from src.features import functions
from src.core import config
from src.core import llm

# Constants for icon paths
ICON_PATHS = {
    'SIDEBAR': 'sidebar_button.png',
    'SETTINGS': 'setting.png',
    'UPLOAD': 'upload.png',
    'SEND': 'send.png',
    'JUPITER': 'jupiter.png',
    'SATURN': 'saturn.png',
    'TYPING': 'typing.gif'
}

class SmoothListWidget(QListWidget):
    def wheelEvent(self, event):
        # angleDelta().y() is in "units" of 1/8 of a degree per physical step;
        # dividing by 8*15 gives number of notches, but we can just use the raw delta
        scroll_delta = event.angleDelta().y()
        scrollbar = self.verticalScrollBar()
        # subtract because a positive delta means wheel scrolled up
        scrollbar.setValue(scrollbar.value() - scroll_delta)
        # accept so the base class doesn't also do item‐based scrolling
        event.accept()

class Page(QWidget):
    """
    Create a single Page.
    """

    """
    Message widget hierarchy:
    QListWidget (message_display_area)
    └── QListWidgetItem
        └── QWidget (message_container)
            └── QHBoxLayout
                ├── QLabel (avatar_icon - Saturn/Jupiter)
                ├── QVBoxLayout (message_bubble)
                │   ├── QLabel (message_text)
                │   └── QLabel (optional_image)
                └── Stretch (for alignment)
    """
    
    """
    1. User sends message -> Displays instantly
    2. LLM placeholder → Shows typing GIF
    3. LLM response ready → Replaces typing indicator with streaming text widget
    """

    """
    --LLM Messages--

    Phase 1 - Typing Indicator:
        LLM request starts -> add_llm_placeholder() -> add_message('LLM', '')
        -> _create_message() detects empty LLM message -> _create_typing_indicator()
    
    Phase 2 - Response Ready:
        LLM completes -> update_llm_response(text) -> Find & replace entire widget
        -> _create_message() with actual text -> Rich text formatting applied
    """

    def __init__(self, sidebar, ui_application, parent=None):
        super().__init__(parent)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        # Create an id
        self.page_id = uuid.uuid4().hex
        self.sidebar = sidebar
        self.ui_application = ui_application
        self.llm = llm.LLM()

        self._last_llm_widget = None
        self._last_typing_widget = None
        self._current_llm_text_label = None # Track current streaming text label
        self._accumulated_text = '' # Store accumulated chunk

        # Layout for content Widget
        self.main_layout = QVBoxLayout(self)

        # Layout to contain Sidebar and Settings buttons
        self.top_buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_buttons_layout)

        # Sidebar and Settings buttons
        self.sidebar_button = self._create_sidebar_button()
        self.settings_button = self._create_settings_button()

        # Add this buttons to a main_buttons_layout
        self.top_buttons_layout.addWidget(self.sidebar_button)
        self.top_buttons_layout.addStretch()
        self.top_buttons_layout.addWidget(self.settings_button)

        # Create a base elements of the page
        self._create_welcome_text()
        self._create_message_display()
        self._create_input_bar()
        self._connect_signals()
        self._assemble_layout()

        self.is_first_message = False

    def _create_sidebar_button(self) -> QWidget:
        sidebar_button = QPushButton()
        sidebar_button.setIcon(QIcon(ICON_PATHS['SIDEBAR']))
        sidebar_button.setIconSize(QSize(30, 30))
        sidebar_button.setFixedSize(30, 30)
        sidebar_button.setStyleSheet('background: transparent;')
        sidebar_button.clicked.connect(self._handle_sidebar_toggle)
        return sidebar_button

    def _handle_sidebar_toggle(self) -> None:
        # Determine start/end width
        start_width = self.sidebar.maximumWidth()
        end_width = 250 if not self.sidebar.sidebar_is_visible else 0

        # Create the animation
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b'maximumWidth')
        self.sidebar_animation.setDuration(self.sidebar.animation_duration)
        self.sidebar_animation.setStartValue(start_width)
        self.sidebar_animation.setEndValue(end_width)
        self.sidebar_animation.setEasingCurve(QEasingCurve.InOutQuart)
        self.sidebar_animation.start()

        # Flip state
        self.sidebar.sidebar_is_visible = not self.sidebar.sidebar_is_visible

    def _create_settings_button(self) -> QWidget:
        """
        Create and configure the main menu button and actions.
        """
        # Create menu button
        settings_button = QToolButton(self)
        # Set the icon
        settings_button.setIcon(QIcon(ICON_PATHS['SETTINGS']))
        settings_button.setIconSize(QSize(30, 30))
        settings_button.setFixedSize(30, 30)

        settings_button.setPopupMode(QToolButton.InstantPopup)
        settings_button.setGeometry(10, 10, 30, 30)
        settings_button.setStyleSheet("""
            QToolButton:hover {
                border: 1px solid #242424;
                border-radius: 3px;
            }
            QToolButton {
                background-color: transparent; /* Button background color */
                border: none; /* No border */
            }
            """)
        settings_menu = QMenu(settings_button)
        settings_menu.setStyleSheet("""
            QMenu {
                background: #242424;
                color: white;
            }
            QAction::item:selected {
                background: 303030;
            }
        """)

        self.voice_output_action = QAction('Voicing', self)
        self.voice_output_action.setCheckable(True)
        self.voice_output_action.setChecked(load_user_data.load_user_voice_status())

        # Add Settings action
        self.settings_action = QAction('Settings', self)
        settings_menu.addAction(self.settings_action)

        # Add About action
        self.about_action = QAction('About', self)
        
        self._connect_settings_actions()

        settings_menu.addAction(self.voice_output_action)
        settings_menu.addAction(self.about_action)

        settings_button.setMenu(settings_menu)

        return settings_button

    def _connect_settings_actions(self) -> None:
        self.voice_output_action.toggled.connect(lambda: functions.save_user_settings(self.voice_output_action.isChecked()))
        self.settings_action.triggered.connect(self._show_settings_page)
        self.about_action.triggered.connect(self._show_about)

    def _show_settings_page(self) -> None:
        """
        Switch view to display settings page.
        """
        self.ui_application.stacked_widget.setCurrentIndex(2)

    def _show_about(self) -> None:
        """
        Display application about dialog.
        """
        QMessageBox.information(
            self,
            'About Joy',
            'Joy Virtual Assistant\nVersion 1.0.0\n\nCreated by Alpheratz corporation'
        )

    def _create_welcome_text(self) -> None:
        self.welcome_text = QLabel('What can i help with?')
        self.welcome_text.setStyleSheet("""
            QLabel {
                font-size: 29px;
                color: #666;
                margin-top: 150px;
            }
        """)

    def _create_message_display(self) -> None:
        # Creating a main display area
        self.message_display_area = SmoothListWidget()
        self.message_display_area.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: transparent;
            }
            QScrollBar::handle:vertical {
                background: #292929;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-page, QScrollBar::sub-page{
                background: #181818;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical{
                height: 0px;
                background: transparent;
            }
        """)
        self.message_display_area.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        # Delete an opportuinity to select each item
        self.message_display_area.setSelectionMode(QAbstractItemView.NoSelection)
        self.message_display_area.setSpacing(4) # Space between messages
        self.message_display_area.setFrameShape(QListWidget.NoFrame) # Remove border
        self.message_display_area.setMinimumSize(520, 380)

    def _create_input_bar(self) -> None:
        """
        This method is responsible for configuration input bar
        """
        self.input_bar_container = QWidget()
        input_bar_layout = QHBoxLayout(self.input_bar_container)
        self.input_bar_container.setStyleSheet("""
            border: 1px solid darkgray;
            border-radius: 15px;
            background-color: #232323;
        """)

        # Create a files button
        self.upload_button = QPushButton()
        self.upload_button.setStyleSheet('''
            background: transparent;
            border: none;
        ''')
        self.upload_button.setIcon(QIcon(ICON_PATHS['UPLOAD']))
        self.upload_button.setIconSize(QSize(30, 30))

        # Creating a toggle button
        self.voice_toggle = ToggleButton()
        self.voice_toggle.setStyleSheet('border: none; background-color: transparent;')

        # Creating a input box
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('Message to Joy...')
        self.message_input.setFont(QFont('Segoe UI'))
        self.message_input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 15px;
            }
        """)
        self.message_input.setFixedHeight(41)

        # Create a button for sending messages
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon(ICON_PATHS['SEND']))
        self.send_button.setIconSize((QSize(30, 30)))
        self.send_button.setFixedSize(40, 40)
        self.send_button.setStyleSheet('border: none; background: transparent;')

        # Add all widget to layout
        input_bar_layout.addWidget(self.upload_button)
        input_bar_layout.addWidget(self.voice_toggle)
        input_bar_layout.addWidget(self.message_input, 1)
        input_bar_layout.addWidget(self.send_button)

    def _connect_signals(self) -> None:
        self.upload_button.clicked.connect(self._handle_file_upload)
        self.voice_toggle.toggled.connect(self._handle_voice_toggle)
        self.message_input.returnPressed.connect(self._handle_message_send)
        self.send_button.clicked.connect(self._handle_message_send)

    def _assemble_layout(self) -> None:
        self.main_layout.addWidget(self.welcome_text, alignment=Qt.AlignHCenter)
        self.main_layout.addWidget(self.message_display_area)
        self.main_layout.addWidget(self.input_bar_container)

    def _handle_file_upload(self):
        # Get the file_path
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'Select File',
                ''
                ''
            )
            if file_path:
                # Get the name of the app
                file_name = file_path.lower().split('/')[-1]
                response = functions.start_file_processing(file_path, file_name)
                self.send_message(file_name)
                self.add_message('Joy', response)

        except Exception as e:
            self.logger.error(f'Error in GUI, `_handle_file_upload` method, error - {e}')

    def _handle_voice_toggle(self, is_enabled: bool) -> None:
        """
        Handle toggle button state changes for voice input.

        Args:
            is_enabled (bool): Current state of the toggle button
        """
        self.message_input.setEnabled(not is_enabled)
        if is_enabled and not self.ui_application.voice_input_thread.isRunning():
            self.logger.info('Starting voice_input_thread')  # Debug
            # voice_input_thread was initialized in `EVA_main.py`
            self.ui_application.voice_input_thread._running = True
            self.ui_application.voice_input_thread.start()
        else:
            self.logger.info('Stopping voice_input_thread')  # Debug
            self.ui_application.voice_input_thread.stop()

    def _handle_message_send(self):
        message_text = self.message_input.text().strip()
        if message_text:
            self.send_message(message_text)
            self.ui_application.message_was_sended(message_text, self.page_id)

    def _remove_welcome_text(self) -> None:
        if not self.is_first_message:
            self.main_layout.removeWidget(self.welcome_text)
            self.welcome_text.hide()
            self.is_first_message = True

    def send_message(self, message: str, sender: str = 'You') -> None:
        """
        This method is responsible for sending a messages to add_messages, to display message from User
        """
        self._remove_welcome_text()
        self.add_message('You', message)

    def _create_image_label(self, image_path: str, max_size: int = 100) -> QLabel:
        """
        Helper to create a QLabel containing a scaled image.
        """
        image_label = QLabel()
        image_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(max_size, max_size, Qt.KeepAspectRatio)
            image_label.setPixmap(pixmap)
        return image_label

    def _create_text_label(self, sender: str, message: str, is_llm: bool = False) -> QLabel:
        """
        Create a text label with consistent styling for all message types
        """
        
        text_label = QLabel()
        text_label.setWordWrap(True)
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Allow text selection
        
        # Set size policy to allow natural width expansion up to maximum
        text_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        # Set maximum width constraint (adjust this value as needed)
        max_width = 600  # You can adjust this based on your UI needs
        text_label.setMaximumWidth(max_width)
        
        # Don't set minimum width - let it shrink to content
        text_label.setMinimumWidth(0)
        
        if sender == 'You':
            text_label.setText(message)
            text_label.setStyleSheet('''
                background-color: #171717;
                padding: 10px;
                border-radius: 10px;
                color: white;
                font-size: 16px;
            ''')
        else:  # Joy or LLM messages
            if is_llm:
                # For LLM messages, we'll set rich text content
                html_content = self._convert_markdown_to_html(message)
                text_label.setText(html_content)
                text_label.setTextFormat(Qt.RichText)  # Enable rich text rendering
            else:
                text_label.setText(message)
                
            text_label.setStyleSheet('''
                color: white;
                font-size: 16px;
                padding: 10px;
                background-color: transparent;
            ''')

        # Adjust size to content after setting text
        text_label.adjustSize()
        
        return text_label

    def _get_image_path(self, sender: str, message: str):
        try:
            is_image_message = any(ext in message.lower() for ext in ('.png', '.jpg'))
            if is_image_message:
                # Determine which path to use (user vs. Joy)
                if sender == 'You':
                    image_path = config.user_chat_files.get(config.user_file_name, '')
                else:
                    image_path = config.new_image_path or ''
                    # Reset the new_image_path after grabbing it
                    config.new_image_path = ''
                return image_path
            return None
        except Exception as e:
            self.logger.error(f'Error in _get_image_path, error - {e}')

    def _create_message(self, sender: str, message: str, llm_message: bool = False) -> QWidget:
        """
        Create a chat bubble widget with optional image below the text.
        Now handles LLM messages with the same styling as normal messages.
        """
        message_container = QWidget()
        message_layout = QHBoxLayout(message_container)
        message_layout.setContentsMargins(10, 5, 10, 5)  # Add some margins
        
        # 1) Create the round icon on either side
        avatar_label = QLabel()
        avatar_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        if sender == 'You':
            avatar_pixmap = QPixmap(ICON_PATHS['JUPITER']).scaled(20, 20, Qt.KeepAspectRatio)
            avatar_label.setPixmap(avatar_pixmap)
            message_layout.addStretch()  # Push message to right
        else:
            avatar_pixmap = QPixmap(ICON_PATHS['SATURN']).scaled(20, 20, Qt.KeepAspectRatio)
            avatar_label.setPixmap(avatar_pixmap)
            message_layout.addWidget(avatar_label)

        # 2) Check if this is the special "LLM typing" placeholder
        if sender == 'LLM' and message == '':  # Empty message means show typing indicator
            # Create typing indicator with same layout as other messages
            typing_widget = self._create_typing_indicator()
            self._last_llm_widget = message_container  # Store reference to the entire widget
            self._last_typing_widget = typing_widget  # Store reference to typing indicator
            
            message_layout.addWidget(typing_widget)
            message_layout.addStretch()
            return message_container

        # 3) Create normal message bubble
        bubble_layout = QVBoxLayout()
        bubble_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins from bubble layout
        
        # Text label with LLM formatting if needed
        is_llm = llm_message or sender in ['Joy', 'LLM']
        text_label = self._create_text_label(sender, message, is_llm)
        bubble_layout.addWidget(text_label)

        # Optional image under the text
        try:
            image_path = self._get_image_path(sender, message)
            if image_path:
                image_label = self._create_image_label(image_path)
                bubble_layout.addWidget(image_label)
        except Exception as e:
            self.logger.error(f'Error while trying to load image, error - {e}')

        # Create a container widget for the bubble to control its sizing
        bubble_container = QWidget()
        bubble_container.setLayout(bubble_layout)
        bubble_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        # Position bubble based on sender
        if sender == 'You':
            message_layout.addWidget(bubble_container)
            message_layout.addWidget(avatar_label)
        else:
            message_layout.addWidget(bubble_container)
            message_layout.addStretch()  # Push message to left

        return message_container

    def _convert_markdown_to_html(self, markdown_text: str) -> str:
        """
        Convert basic Markdown to HTML for rich text display
        (Moved from LLMMessage class for reuse)
        """
        html = markdown_text
        
        # Headers
        html = re.sub(r'^# (.*?)$', r'<h1 style="color: #4CAF50; font-size: 24px; margin: 10px 0;">\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2 style="color: #2196F3; font-size: 20px; margin: 8px 0;">\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3 style="color: #FF9800; font-size: 18px; margin: 6px 0;">\1</h3>', html, flags=re.MULTILINE)
        
        # Bold text
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color: #FFF; font-weight: bold;">\1</strong>', html)
        html = re.sub(r'__(.*?)__', r'<strong style="color: #FFF; font-weight: bold;">\1</strong>', html)
        
        # Italic text
        html = re.sub(r'\*(.*?)\*', r'<em style="color: #E0E0E0; font-style: italic;">\1</em>', html)
        html = re.sub(r'_(.*?)_', r'<em style="color: #E0E0E0; font-style: italic;">\1</em>', html)
        
        # Code blocks
        html = re.sub(r'```(.*?)```', r'<pre style="background-color: #2D2D2D; padding: 10px; border-radius: 5px; color: #A0A0A0; font-family: Consolas, monospace; margin: 5px 0;"><code>\1</code></pre>', html, flags=re.DOTALL)
        
        # Inline code
        html = re.sub(r'`(.*?)`', r'<code style="background-color: #3D3D3D; padding: 2px 4px; border-radius: 3px; color: #A0A0A0; font-family: Consolas, monospace;">\1</code>', html)
        
        # Lists
        html = re.sub(r'^[\*\-\+] (.*?)$', r'<li style="margin: 2px 0;">\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li.*?</li>)', r'<ul style="margin: 5px 0; padding-left: 20px;">\1</ul>', html, flags=re.DOTALL)
        
        # Line breaks
        html = html.replace('\n\n', '<br><br>')
        html = html.replace('\n', '<br>')
        
        return html

    def _create_typing_indicator(self) -> QWidget:
        """
        Create a typing indicator widget that matches the message bubble styling
        """
        typing_container = QWidget()
        typing_layout = QVBoxLayout(typing_container)
        typing_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create GIF label
        gif_label = QLabel()
        gif_label.setAlignment(Qt.AlignLeft)
        gif_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        # Load and configure GIF
        typing_gif = QMovie(ICON_PATHS['TYPING'])
        typing_gif.setScaledSize(QSize(60, 45))  # Smaller size to match text height better
        gif_label.setMovie(typing_gif)
        typing_gif.start()
        
        typing_layout.addWidget(gif_label)
        typing_container.setMaximumWidth(700)
        
        # Store references for later cleanup
        typing_container.gif = typing_gif
        typing_container.gif_label = gif_label
        
        return typing_container

    def start_llm_streaming(self, min_typing_duration: int = 500, max_typing_duration: int = 3000):
        """
        Initialize LLM streaming by replacing typing indicator with empty message widget
        
        Args:
            min_typing_duration (int): Minimum time to show typing indicator (default: 800ms)
            max_typing_duration (int): Maximum time to show typing indicator before transitioning anyway (default: 3000ms)
        """
        if self._last_llm_widget is None:
            return

        import time
        self._transition_start_time = time.time() * 1000  # Convert to milliseconds
        
        def _perform_transition():
            try:
                # Find the item in the list widget
                for i in range(self.message_display_area.count()):
                    item = self.message_display_area.item(i)
                    widget = self.message_display_area.itemWidget(item)
                    if widget == self._last_llm_widget:
                        # Remove the old widget
                        self.message_display_area.takeItem(i)
                        
                        # Clean up the typing indicator
                        if hasattr(self, '_last_typing_widget') and self._last_typing_widget:
                            if hasattr(self._last_typing_widget, 'gif'):
                                self._last_typing_widget.gif.stop()
                        
                        # Create new message with empty content initially
                        new_widget = self._create_message('Joy', '', llm_message=True)
                        
                        # Create new item and add it back
                        new_item = QListWidgetItem()
                        new_item.setFlags(Qt.NoItemFlags)
                        new_item.setSizeHint(new_widget.sizeHint())
                        
                        self.message_display_area.insertItem(i, new_item)
                        self.message_display_area.setItemWidget(new_item, new_widget)
                        self.message_display_area.scrollToBottom()

                        # Find and store the text label for streaming updates
                        for child in new_widget.findChildren(QLabel):
                            if isinstance(child, QLabel) and not child.pixmap():
                                self._current_llm_text_label = child
                                break

                        # Reset accumulated text
                        self._accumulated_text = ""
                        
                        # Mark as ready for streaming
                        self._streaming_ready = True
                        
                        # Process any buffered chunks immediately
                        if hasattr(self, '_buffered_chunks') and self._buffered_chunks:
                            for buffered_chunk in self._buffered_chunks:
                                self._process_chunk(buffered_chunk)
                            self._buffered_chunks = []
                        break
                        
            except Exception as e:
                self.logger.error(f'Error starting LLM streaming: {e}')
            finally:
                # Clean up references
                self._last_llm_widget = None
                if hasattr(self, '_last_typing_widget'):
                    self._last_typing_widget = None

        def _check_transition_conditions():
            """Check if we should transition based on timing and chunk availability"""
            current_time = time.time() * 1000
            elapsed = current_time - self._transition_start_time
            
            has_chunks = hasattr(self, '_buffered_chunks') and len(self._buffered_chunks) > 0
            min_time_passed = elapsed >= min_typing_duration
            max_time_passed = elapsed >= max_typing_duration
            
            # Transition if:
            # 1. We have chunks AND minimum time has passed, OR
            # 2. Maximum time has passed (even without chunks)
            should_transition = (has_chunks and min_time_passed) or max_time_passed
            
            if should_transition:
                _perform_transition()
                return  # Stop checking
            
            # Check again in 50ms
            QTimer.singleShot(50, _check_transition_conditions)
        
        # Initialize state
        self._streaming_ready = False
        self._buffered_chunks = []
        
        # Start checking transition conditions
        _check_transition_conditions()

    @pyqtSlot(str)
    def add_llm_chunk(self, chunk: str):
        """
        Add a new chunk from LLM stream to the current message
        Args:
            chunk (str): New text chunk from LLM stream
        """
        try:
            # Defensive: Ensure chunk is a string
            if not isinstance(chunk, str):
                self.logger.error(f"Received non-string chunk in add_llm_chunk: {type(chunk)}")
                return

            # If the chunk is an error message, display it directly and clear accumulated text
            if 'Error occurs' in chunk:
                self._accumulated_text = chunk
                if self._current_llm_text_label is not None:
                    self._current_llm_text_label.setText(chunk)
                    self._current_llm_text_label.setTextFormat(Qt.PlainText)
                    self._update_message_size()
                    self.message_display_area.scrollToBottom()
                return

            # If streaming hasn't been initialized yet, buffer the chunk
            if not hasattr(self, '_streaming_ready') or not self._streaming_ready:
                if not hasattr(self, '_buffered_chunks'):
                    self._buffered_chunks = []
                self._buffered_chunks.append(chunk)
                return

            # Process any buffered chunks first
            if hasattr(self, '_buffered_chunks') and self._buffered_chunks:
                for buffered_chunk in self._buffered_chunks:
                    try:
                        self._process_chunk(buffered_chunk)
                    except Exception as e:
                        self.logger.error(f"Error processing buffered chunk: {e}")
                self._buffered_chunks = []

            # Process the current chunk
            self._process_chunk(chunk)
        except Exception as e:
            self.logger.error(f"Exception in add_llm_chunk: {e}")

    def _process_chunk(self, chunk: str):
        """
        Internal method to process a single chunk
        """
        try:
            if self._current_llm_text_label is None:
                self.logger.warning("No active LLM text label for streaming")
                return

            # Defensive: Ensure chunk is a string
            if not isinstance(chunk, str):
                self.logger.error(f"_process_chunk received non-string chunk: {type(chunk)}")
                return

            # Accumulate the chunk
            self._accumulated_text += chunk

            # Convert markdown to HTML for rich text display
            try:
                html_content = self._convert_markdown_to_html(self._accumulated_text)
            except Exception as e:
                self.logger.error(f"Error converting markdown to HTML: {e}")
                html_content = self._accumulated_text  # Fallback to plain text

            try:
                self._current_llm_text_label.setText(html_content)
                self._current_llm_text_label.setTextFormat(Qt.RichText)
            except Exception as e:
                self.logger.error(f"Error setting text on QLabel: {e}")

            # Update the size hint of the list widget item
            try:
                self._update_message_size()
            except Exception as e:
                self.logger.error(f"Error updating message size: {e}")

            # Ensure the message is visible
            try:
                self.message_display_area.scrollToBottom()
            except Exception as e:
                self.logger.error(f"Error scrolling to bottom: {e}")

        except Exception as e:
            self.logger.error(f'Error processing LLM chunk: {e}')

    @pyqtSlot()
    def finish_llm_streaming(self):
        """
        Called when LLM streaming is complete
        """
        try:
            # Final update to ensure everything is displayed correctly
            if self._current_llm_text_label and self._accumulated_text:
                html_content = self._convert_markdown_to_html(self._accumulated_text)
                self._current_llm_text_label.setText(html_content)
                self._current_llm_text_label.setTextFormat(Qt.RichText)
                self._update_message_size()
                
            # Start voicing thread for the complete message
            if self._accumulated_text:
                thread = threading.Thread(
                    target=functions.check_voicing_flag,
                    args=(self._accumulated_text,)
                )
                thread.start()
                
        except Exception as e:
            self.logger.error(f'Error finishing LLM streaming: {e}')
        finally:
            # Clean up streaming references
            self._current_llm_text_label = None
            self._accumulated_text = ""

    def _update_message_size(self):
        """
        Helper method to update the size of the current streaming message
        """
        if self._current_llm_text_label is None:
            return
            
        # Find the widget containing the text label and update its size
        for i in range(self.message_display_area.count()):
            item = self.message_display_area.item(i)
            widget = self.message_display_area.itemWidget(item)
            if widget and self._current_llm_text_label in widget.findChildren(QLabel):
                # Force the widget to update its size hint
                widget.updateGeometry()
                # Update the item's size hint
                item.setSizeHint(widget.sizeHint())
                break

    # REMOVE OR REPLACE the old update_llm_response method
    def update_llm_response(self, actual_text: str):
        """
        DEPRECATED: Use start_llm_streaming(), add_llm_chunk(), and finish_llm_streaming() instead
        This method is kept for backward compatibility but should be replaced
        """
        self.logger.warning("update_llm_response is deprecated. Use streaming methods instead.")
        
        # For backward compatibility, simulate streaming with the complete text
        self.start_llm_streaming()
        self.add_llm_chunk(actual_text)
        self.finish_llm_streaming()

    # ... (keep all other existing methods unchanged)

    def add_message(self, sender: str, message: str, llm_message: bool = False) -> None:
        """
        Insert a new message into the QListWidget.
        If sender == 'LLM', we first insert the GIF placeholder.
        Once the real LLM text arrives, call update_llm_text(...) from outside.

        Args:
            sender (str): Message originator ('You' or 'Joy')
            message (str): Text content to display
            llm_message (bool): Whether this is an LLM message
        """
        try:
            if sender == 'Joy' and message:  # Only start voicing thread for actual messages
                thread = threading.Thread(
                    target=functions.check_voicing_flag,
                    args=(message,)
                )
                thread.start()
            
            # Create the message widget
            message_widget = self._create_message(sender, message, llm_message)    

            # Wrap it in a QListWidgetItem
            item = QListWidgetItem()
            item.setFlags(Qt.NoItemFlags)
            item.setSizeHint(message_widget.sizeHint())
            
            self.message_display_area.addItem(item)
            self.message_display_area.setItemWidget(item, message_widget)
            self.message_display_area.scrollToBottom()

            if sender != 'LLM':  # Don't clear input for LLM placeholder messages
                self.message_input.clear()

        except Exception as e:
            self.logger.error(f'Error in add_message, error - {e}')

    # Method to add LLM placeholder
    def add_llm_placeholder(self):
        """
        Add a typing indicator for LLM response
        """
        print('llm_placeholder')
        self.add_message('LLM', '', llm_message=True)
