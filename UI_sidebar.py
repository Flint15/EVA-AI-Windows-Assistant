"""
Sidebar module for the chat application.

This modul contains the Sidebar class which provides the chat navigation interface,
including chat history management, new chat creation, and chat deletion functionality
"""

from PyQt5.QtWidgets import (
                                QVBoxLayout, QHBoxLayout, QSizePolicy, QListWidget,
                                QWidget, QToolButton, QMenu, QAction, QMessageBox,
                                QListWidgetItem, QPushButton, QButtonGroup
                            )
from PyQt5.QtGui     import     QIcon
from PyQt5.QtCore    import     Qt, QSize
import logging
from UI_main_page         import Page
import config

# Icon file paths for UI elements
ICON_PATHS = {
    'NEW_CHAT': 'new_chat.png',
    'CHAT_SETTINGS': '3_dots.png'
}

# Enhanced color constants for the dark theme with better contrast
COLORS = {
    'BACKGROUND': '#0A0A0A',          # Very dark gray, almost black background
    'SURFACE': '#151515',             # Dark gray surface color for cards/panels
    'SURFACE_HOVER': '#1F1F1F',       # Slightly lighter gray for hover effects
    'SURFACE_ACTIVE': '#262626',      # Medium gray for active/pressed states
    'PRIMARY': '#8A00C4',             # Purple color for primary actions/buttons
    'PRIMARY_HOVER': '#9D1BD6',       # Lighter purple for primary button hover
    'PRIMARY_SOFT': '#8A00C420',      # Transparent purple (20% opacity) for subtle highlights
    'TEXT_PRIMARY': '#FFFFFF',        # Pure white color for main text
    'TEXT_SECONDARY': '#CCCCCC',      # Light gray for secondary text
    'TEXT_MUTED': '#9E9E9E',          # Medium gray for less important text
    'BORDER': '#2D2D2D',              # Dark gray for subtle borders
    'BORDER_LIGHT': '#404040',        # Medium gray for more visible borders
    'ERROR': '#FF4757'                # Red color for error states/messages
}

class Sidebar(QWidget):
    """
    A sidebar widget that provides chat navigation and management functionality.
    
    This class creates a collapsible sidebar containing:
    - New chat button
    - Chat history list
    - Individual chat management options (delete, rename, etc.)
    
    Attributes:
        ui_application: Reference to the main UI application
        sidebar_is_visible (bool): Current visibility state of the sidebar
        animation_duration (int): Duration for sidebar animations in milliseconds
        chat_history_list (QListWidget): Widget containing the list of chat sessions
        new_chat_button (QPushButton): Button to create new chat sessions
        chat_buttons_group (QButtonGroup): Group managing chat selection buttons
    """
    
    def __init__(self, ui_application, parent=None):
        super().__init__(parent)

        # Set up logging for debugging and monitoring
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Store reference to main application
        self.ui_application = ui_application

        # To track which chat widget id, None by default
        self.chat_widget_id: str = None

        # Initialize the sidebar UI
        self.create_sidebar()

    def create_sidebar(self) -> QWidget:
        """
        Create and configure the main sidebar widget structure.
        
        Sets up the sidebar layout, styling, and initializes all child components
        including the new chat button, chat history list, and animation properties.
        """
        # Apply enhanced dark theme styling to the sidebar
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['BACKGROUND']};
                border: none;
            }}
        """)

        # Initially hide the sidebar by setting width to 0
        self.setMaximumWidth(0)

        # Create main vertical layout for sidebar content
        main_sidebar_layout = QVBoxLayout()
        main_sidebar_layout.setContentsMargins(12, 16, 12, 16)  # Add proper padding
        main_sidebar_layout.setSpacing(16)  # Consistent spacing
        self.setLayout(main_sidebar_layout)

        # Create and configure the header section with action buttons
        header_buttons_layout = QHBoxLayout()
        header_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.new_chat_button = self.create_new_chat_button()

        # Add stretch to push the new chat button to the right side
        header_buttons_layout.addStretch()
        header_buttons_layout.addWidget(self.new_chat_button)

        # Wrap header buttons in a widget and add to main layout
        header_buttons_container = QWidget()
        header_buttons_container.setStyleSheet('background: transparent;')
        header_buttons_container.setLayout(header_buttons_layout)
        header_buttons_container.setFixedHeight(40)  # Consistent header height
        main_sidebar_layout.addWidget(header_buttons_container, alignment=Qt.AlignTop)

        # Create and add the chat history list
        self.chat_history_list = self.create_chat_history_list_widget()
        main_sidebar_layout.addWidget(self.chat_history_list)

        # Initialize sidebar state and animation properties
        self.sidebar_is_visible = False  # Sidebar starts hidden
        self.animation_duration = 300    # Animation duration in milliseconds

    def create_chat_history_list_widget(self) -> QWidget:
        """
        Create and configure the chat history list widget.
        
        This widget displays all existing chat sessions and handles user interactions
        such as hover effects and selection states.
        
        Returns:
            QListWidget: Configured chat history list widget
        """
        chat_history_list = QListWidget()
        
        # Configure list widget properties
        chat_history_list.setSpacing(4)  # Tighter spacing for cleaner look
        chat_history_list.setFocusPolicy(Qt.NoFocus)  # Prevent focus rectangle
        chat_history_list.setMouseTracking(True)  # Enable hover effects
        chat_history_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)  # Smooth scrolling
        
        # Apply enhanced styling for dark theme with improved readability
        chat_history_list.setStyleSheet(f"""
            QListWidget {{
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 14px;
                font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
                font-weight: 500;
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                background-color: transparent;
                border-radius: 8px;
                margin: 0px 0px 2px 0px;
                padding: 0px;
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
            }}
            QListWidget::item:selected {{
                color: {COLORS['TEXT_PRIMARY']};
                background-color: {COLORS['PRIMARY_SOFT']};
                border: 1px solid {COLORS['PRIMARY']};
            }}
            QListWidget::item:selected:hover {{
                background-color: {COLORS['PRIMARY_SOFT']};
                border: 1px solid {COLORS['PRIMARY_HOVER']};
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 6px;
                border: none;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['BORDER']};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['BORDER_LIGHT']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)
        
        return chat_history_list

    def create_new_chat_button(self) -> QPushButton:
        """
        Create and configure the "New Chat" button for the sidebar header.
        
        This button allows users to create new chat sessions and is styled
        with an icon and modern hover effects to match the sidebar theme.

        Returns:
            QPushButton: Configured new chat button
        """
        new_chat_button = QPushButton()
        
        # Set fixed size for consistent appearance
        new_chat_button.setFixedSize(36, 36)
        
        # Configure button icon and enhanced styling
        new_chat_button.setIcon(QIcon(ICON_PATHS['NEW_CHAT']))
        new_chat_button.setIconSize(QSize(20, 20))
        new_chat_button.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['SURFACE']};
                border: 1px solid {COLORS['BORDER']};
                border-radius: 8px;
                padding: 6px;
            }}
            QPushButton:hover {{
                background: {COLORS['PRIMARY_HOVER']};
                border: 1px solid {COLORS['PRIMARY_HOVER']};
                transform: scale(1.05);
            }}
            QPushButton:pressed {{
                background: {COLORS['PRIMARY']};
                border: 1px solid {COLORS['PRIMARY']};
            }}
        """)

        # Create button group to manage chat selection (radio button behavior)
        self.chat_buttons_group = QButtonGroup(self)
        self.chat_buttons_group.buttonClicked[int].connect(self.ui_application.switch_chat)

        # Connect button click to new chat creation handler
        new_chat_button.clicked.connect(self.create_new_chat)

        return new_chat_button
    
    def create_new_chat(self) -> None:
        """
        Create a new chat session and add it to the application.
        
        This method:
        1. Increments the global chat counter
        2. Creates a new chat history item in the sidebar
        3. Creates a new Page instance for the chat content
        4. Adds the page to the chat stack
        5. Switches to the newly created chat
        """
        # Increment global chat counter
        config.chats_quantity += 1
        
        # Create visual representation in sidebar
        self.create_chat_history_item()

        # Create new page instance for chat content
        new_chat_page = Page(self, self.ui_application)
        
        # Save page reference and add to chat stack
        self.ui_application.save_page(new_chat_page)
        self.ui_application.chat_stack.addWidget(new_chat_page)

        # Switch to the newly created chat (0-indexed)
        self.ui_application.chat_stack.setCurrentIndex(config.chats_quantity - 1)
        
        # Reset first message flag
        self.is_first_message = False

        # Log chat creation for debugging
        self.logger.info(f'Total chat sessions: {config.chats_quantity}')

    def create_chat_history_item(self) -> None:
        """
        Create a new chat history item and add it to the sidebar list.
        
        Each chat item consists of:
        - A main button with the chat name that allows switching between chats
        - A settings button (3-dots) that opens a context menu for chat management
        - Delete functionality through the context menu
        
        The item is added to the chat history list widget as a custom widget item.
        """
        # Create container widget for the chat item
        self.chat_widget = QWidget()
        self.chat_widget.setFixedHeight(40)  # Slightly taller for better touch targets
        
        # Store reference to the chat_widget position, to have ability to delete that chat_widget(page) later from self.existed_page
        self.ui_application.existed_pages_widgets[self.chat_widget] = config.chats_quantity-1

        # Apply enhanced styling for chat item components
        self.chat_widget.setStyleSheet(f"""
            QWidget {{
                background-color: transparent;
                border-radius: 8px;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 14px;
                font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
                font-weight: 500;
                text-align: left;
                padding: 10px 14px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
                color: {COLORS['TEXT_PRIMARY']};
            }}
            QPushButton:checked {{
                background-color: {COLORS['PRIMARY_SOFT']};
                color: {COLORS['PRIMARY']};
                font-weight: 600;
                border: 1px solid {COLORS['PRIMARY']};
            }}
            QPushButton:checked:hover {{
                background-color: {COLORS['PRIMARY_SOFT']};
                border: 1px solid {COLORS['PRIMARY_HOVER']};
            }}
            QToolButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 2px;
            }}
            QToolButton:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
            }}
            QToolButton:pressed {{
                background-color: {COLORS['SURFACE_ACTIVE']};
            }}
            QMenu {{
                background-color: {COLORS['SURFACE']};
                border: 1px solid {COLORS['BORDER_LIGHT']};
                border-radius: 12px;
                padding: 8px;
                font-size: 13px;
                font-family: "Segoe UI", system-ui, -apple-system, sans-serif;
                font-weight: 500;
                color: {COLORS['TEXT_PRIMARY']};
                min-width: 120px;
            }}
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 6px;
                margin: 2px;
                background-color: transparent;
                border: none;
            }}
            QMenu::item:selected {{
                background-color: {COLORS['SURFACE_HOVER']};
                color: {COLORS['TEXT_PRIMARY']};
            }}
            QMenu::item:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {COLORS['BORDER']};
                margin: 4px 8px;
            }}
        """)
        
        # Create horizontal layout for chat item components
        chat_item_layout = QHBoxLayout()
        chat_item_layout.setSpacing(4)
        chat_item_layout.setContentsMargins(0, 0, 0, 0)
        self.chat_widget.setLayout(chat_item_layout)

        # Create main chat button with auto-generated name
        chat_selection_button = QPushButton(f'Chat #{config.chats_quantity}')
        chat_selection_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add button to group for exclusive selection behavior
        self.chat_buttons_group.addButton(chat_selection_button, config.chats_quantity - 1)
        
        # Create settings button with dropdown menu
        chat_settings_button = QToolButton(self)
        chat_settings_button.setPopupMode(QToolButton.InstantPopup)
        chat_settings_button.setFixedSize(32, 32)
        chat_settings_button.setIcon(QIcon(ICON_PATHS['CHAT_SETTINGS']))
        chat_settings_button.setIconSize(QSize(16, 16))

        # Create context menu for chat management
        settings_menu = QMenu(chat_settings_button)

        # Add delete action to the menu
        self.delete_current_chat_action = QAction('Delete Chat', self)
        self.delete_current_chat_action.triggered.connect(self.handle_chat_deletion)
        settings_menu.addAction(self.delete_current_chat_action)

        # Attach menu to settings button
        chat_settings_button.setMenu(settings_menu)

        # Add components to the chat item layout
        chat_item_layout.addWidget(chat_selection_button)
        chat_item_layout.addWidget(chat_settings_button)

        # Create list widget item and add the custom widget
        chat_list_item = QListWidgetItem()
        chat_list_item.setSizeHint(self.chat_widget.sizeHint())
        
        # Add item to the chat history list
        self.chat_history_list.addItem(chat_list_item)
        self.chat_history_list.setItemWidget(chat_list_item, self.chat_widget)

    def handle_chat_deletion(self):
        """
        Handle the deletion of a chat session from the sidebar and application.
        
        This method:
        1. Validates that multiple chats exist (prevents deleting the last chat)
        2. Shows confirmation dialog to the user
        3. Removes the chat widget from the UI
        4. Properly cleans up widget references to prevent memory leaks
        
        Note: This method only handles UI cleanup. The actual chat data cleanup
        should be handled by the main application.
        """
        # Prevent deletion of the last remaining chat
        if config.chats_quantity == 1:
            QMessageBox.information(
                self, 
                'Chat Deletion', 
                'Cannot delete the last remaining chat. At least one chat must exist.'
            )
            return
        
        # Show confirmation dialog
        confirmation_result = QMessageBox.question(
            self, 
            'Delete Chat?', 
            'Are you sure you want to delete this chat? This action cannot be undone.'
        )
        
        # Exit if user cancels the deletion
        if confirmation_result != QMessageBox.Yes:
            return
        
        # Delete from page(chat_widget=page) from `self.existed_pages`
        self.ui_application.delete_page(self.chat_widget)

        # Remove the corresponding QListWidgetItem from the chat history list
        for i in range(self.chat_history_list.count()):
            item = self.chat_history_list.item(i)
            if self.chat_history_list.itemWidget(item) == self.chat_widget:
                self.chat_history_list.takeItem(i)
                break

        # Remove chat widget from its layout
        chat_item_layout = self.chat_widget.layout()
        if chat_item_layout:
            # Remove all child widgets from the layout
            while chat_item_layout.count():
                child_item = chat_item_layout.takeAt(0)
                if child_item.widget():
                    child_item.widget().deleteLater()
        
        # Detach widget from parent to allow Qt cleanup
        self.chat_widget.setParent(None)
        
        # Schedule widget for deletion in next event loop iteration
        self.chat_widget.deleteLater()
        
        # Clear reference to allow garbage collection
        self.chat_widget = None
        
        # Log successful deletion
        self.logger.info(f'Chat deleted. Remaining chats: {config.chats_quantity - 1}')