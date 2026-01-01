from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QRadioButton, QFrame,
    QWidget, QMessageBox, QLabel, QStackedWidget, 
    QLineEdit, QSizePolicy, QFileDialog,
    QListWidget, QListWidgetItem, QPushButton, QButtonGroup
)
from PyQt5.QtGui import QIcon

from PyQt5.QtCore import Qt, QSettings, QSize
from pathlib import Path
import threading
import logging
from Custom_Title_Bar import CustomTitleBar
import save_user_settings
import load_user_data
import config

# Constants for icon paths
ICON_PATHS = {
    'EXIT_BUTTON': 'icon_exit_button.png',
}

# Enhanced color scheme
COLORS = {
    'PRIMARY': '#8A00C4',      # CTA color
    'PRIMARY_HOVER': '#A020E0',
    'PRIMARY_PRESSED': '#6A0094',
    'BACKGROUND': '#0F0F0F',   # Darker main background
    'SURFACE': '#1A1A1A',      # Card/surface color
    'SURFACE_HOVER': '#252525',
    'BORDER': '#333333',
    'TEXT_PRIMARY': '#FFFFFF',
    'TEXT_SECONDARY': '#B0B0B0',
    'TEXT_MUTED': '#808080',
    'SUCCESS': '#00C851',
    'WARNING': '#FF8800',
    'ERROR': '#FF4444',
    'ACCENT': '#00D4FF'
}

class Languages:
    """
    Represents a language with all its properties.
    """
    def __init__(self):
        self.languages_list: list = [{
            'id': 1,
            'code': 'en',
            'display_name': 'English',
            'variable_name': 'english'
        }]

    def add_new_language(self, code: str, display_name: str, variable_name: str):
        self.languages_list.append({
            'id': len(self.languages_list)+1,
            'code': code,
            'display_name': display_name,
            'variable_name': variable_name,
        })

    def get_id_by_code(self, current_language_code: str) -> int:
        for language in self.languages_list:
            for parameter, value in language.items():
                if value == current_language_code:
                    return language['id']
        return 1  # Default to English if not found

class SettingPage(QWidget):
    def __init__(self, ui_application, parent=None):
        super().__init__(parent)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.ui_application = ui_application
        
        # Initialize languages
        self.languages = Languages()
        self._create_languages()

        # Load User language settings
        load_user_data.load_user_language_settings(self.languages)

        self.settings_title_bar = CustomTitleBar(self)

        self.create_settings_window()
        self.create_content()
        self.apply_global_styles()

    def _create_languages(self) -> None:
        """
        Initialize the languages list with all supported languages.
        """
        # Add all supported languages with correct display names
        self.languages.add_new_language('ja', '日本語', 'Japanese')      
        self.languages.add_new_language('ru', 'Русский', 'Russian')     
        self.languages.add_new_language('de', 'Deutsch', 'German')      
        self.languages.add_new_language('es', 'Español', 'Spanish')     
        self.languages.add_new_language('fr', 'Français', 'French')     
        self.languages.add_new_language('it', 'Italiano', 'Italian')    
        self.languages.add_new_language('pt', 'Português', 'Portuguese') 
        self.languages.add_new_language('zh', '中文', 'Chinese')         
        self.languages.add_new_language('ko', '한국어', 'Korean')        
        self.languages.add_new_language('ar', 'العربية', 'Arabic')      
        self.languages.add_new_language('hi', 'हिन्दी', 'Hindi')         
        self.languages.add_new_language('nl', 'Nederlands', 'Dutch')    
        self.languages.add_new_language('pl', 'Polski', 'Polish')       
        self.languages.add_new_language('sv', 'Svenska', 'Swedish')    
        self.languages.add_new_language('no', 'Norsk', 'Norwegian')     
        self.languages.add_new_language('da', 'Dansk', 'Danish')        
        self.languages.add_new_language('fi', 'Suomi', 'Finnish')

    def apply_global_styles(self):
        """Apply global styles to the settings window."""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['BACKGROUND']};
                color: {COLORS['TEXT_PRIMARY']};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}
            
            QLabel {{
                color: {COLORS['TEXT_PRIMARY']};
                font-weight: 600;
            }}
            
            QPushButton {{
                background-color: {COLORS['SURFACE']};
                border: 1px solid {COLORS['BORDER']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                color: {COLORS['TEXT_PRIMARY']};
                min-height: 32px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
                border-color: {COLORS['PRIMARY']};
            }}
            
            QPushButton:pressed {{
                background-color: {COLORS['PRIMARY_PRESSED']};
            }}
            
            QLineEdit {{
                background-color: {COLORS['SURFACE']};
                border: 2px solid {COLORS['BORDER']};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                color: {COLORS['TEXT_PRIMARY']};
                min-height: 20px;
            }}
            
            QLineEdit:focus {{
                border-color: {COLORS['PRIMARY']};
                background-color: {COLORS['SURFACE_HOVER']};
            }}
            
            QLineEdit:hover {{
                border-color: {COLORS['TEXT_MUTED']};
            }}
        """)

    def create_settings_window(self):
        # Layout for setting page
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
    
        # Widget that contain settings
        settings_page_widget = QWidget()
        settings_page_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.settings_page_layout = QHBoxLayout()
        self.settings_page_layout.setContentsMargins(0, 0, 0, 0)
        self.settings_page_layout.setSpacing(0)
        settings_page_widget.setLayout(self.settings_page_layout)

        # Add main widget and settings's widget to the common layout
        self.main_layout.addWidget(self.settings_title_bar)
        self.main_layout.addWidget(settings_page_widget)

    def create_content(self):
        # Create Settings panel
        self.settings_panel = self.create_settings_sidebar()

        # Content area using QStackedWidget
        self.settings_pages = QStackedWidget()
        self.settings_pages.addWidget(self.create_languages_page())
        self.settings_pages.addWidget(self.create_paths_page())

        # Add settings pages to the layout
        self.settings_page_layout.addWidget(self.settings_panel)
        self.settings_page_layout.addWidget(self.settings_pages, 1)

    def create_settings_sidebar(self) -> QListWidget:
        """
        Create the enhanced sidebar for navigating settings pages.
        """
        settings_panel = QListWidget()
        settings_panel.setFocusPolicy(Qt.NoFocus)
        settings_panel.setMouseTracking(True)
        settings_panel.addItems(['🌐 Languages', '📁 Paths'])
        settings_panel.setFixedWidth(200)
        
        # Apply modern sidebar styling
        settings_panel.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['SURFACE']};
                border: none;
                border-right: 1px solid {COLORS['BORDER']};
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 15px;
                font-weight: 500;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: transparent;
                padding: 16px 20px;
                margin: 4px 8px;
                border-radius: 8px;
                border-left: 3px solid transparent;
            }}
            
            QListWidget::item:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
                border-left-color: {COLORS['PRIMARY']};
            }}
            
            QListWidget::item:selected {{
                background-color: {COLORS['PRIMARY']};
                color: white;
                font-weight: 600;
                border-left-color: white;
            }}
            
            QListWidget::item:selected:hover {{
                background-color: {COLORS['PRIMARY_HOVER']};
            }}
        """)
        
        # Connect items clicking to the pages switching
        settings_panel.currentRowChanged.connect(self.switch_page)
        return settings_panel
    
    def switch_page(self, index: int) -> None:
        """
        Switch the settings page based on sidebar selection.
        """
        self.settings_pages.setCurrentIndex(index)

    def create_languages_page(self) -> QWidget:
        """
        Create the enhanced language selection page for settings.
        """
        # Create main container
        languages_page_widget = QWidget()
        languages_page_layout = QVBoxLayout()
        languages_page_layout.setContentsMargins(32, 24, 32, 24)
        languages_page_layout.setSpacing(24)
        languages_page_widget.setLayout(languages_page_layout)

        # Header section with title and exit button
        header_section = self.create_page_header("Languages", "🌐", "Choose your preferred language")
        languages_page_layout.addWidget(header_section)

        # Languages selection section
        languages_section = self.create_languages_section()
        languages_page_layout.addWidget(languages_section, 1)

        return languages_page_widget

    def create_page_header(self, title: str, icon: str, subtitle: str) -> QWidget:
        """Create a modern page header with title, icon, and subtitle."""
        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)
        header_widget.setLayout(header_layout)

        # Title row with icon and exit button
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        
        # Title with icon
        title_container = QHBoxLayout()
        title_container.setSpacing(12)
        
        title_label = QLabel(f"{icon} {title}")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 28px;
                font-weight: 700;
                margin: 0;
                padding: 0;
            }}
        """)
        title_container.addWidget(title_label)
        title_container.addStretch()
        
        # Exit button
        exit_button = self.create_modern_exit_button()
        
        title_row.addLayout(title_container)
        title_row.addWidget(exit_button)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_SECONDARY']};
                font-size: 16px;
                font-weight: 400;
                margin: 0;
                padding: 0;
            }}
        """)
        
        header_layout.addLayout(title_row)
        header_layout.addWidget(subtitle_label)
        
        return header_widget

    def create_modern_exit_button(self) -> QPushButton:
        """Create a modern, styled exit button."""
        exit_button = QPushButton("✕")
        exit_button.setFixedSize(40, 40)
        exit_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['SURFACE']};
                border: 2px solid {COLORS['BORDER']};
                border-radius: 20px;
                color: {COLORS['TEXT_SECONDARY']};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['ERROR']};
                border-color: {COLORS['ERROR']};
                color: white;
            }}
            
            QPushButton:pressed {{
                background-color: #CC0000;
            }}
        """)
        exit_button.clicked.connect(self.exit_settings_logic)
        return exit_button

    def create_languages_section(self) -> QWidget:
        """Create the enhanced languages selection section."""
        section_widget = QFrame()
        section_widget.setFrameStyle(QFrame.NoFrame)
        section_layout = QVBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(16)
        section_widget.setLayout(section_layout)

        # Create the enhanced list widget
        self.languages_list = QListWidget()
        self.languages_list.setSpacing(4)
        self.languages_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {COLORS['SURFACE']};
                border: 2px solid {COLORS['BORDER']};
                border-radius: 12px;
                padding: 8px;
                outline: none;
            }}
            
            QListWidget::item {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
                margin: 2px;
                padding: 0;
                min-height: 56px;
            }}
            
            QListWidget::item:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
            }}
            
            QListWidget::item:selected {{
                background-color: transparent;
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: transparent;
                width: 12px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['BORDER']};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['TEXT_MUTED']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: transparent;
            }}
        """)

        # Create button group and radio buttons
        self.languages_group = QButtonGroup(self)
        self.radio_buttons = {}

        for language in self.languages.languages_list:
            item_widget = self.create_language_item(language)
            
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 60))
            self.languages_list.addItem(item)
            self.languages_list.setItemWidget(item, item_widget)

        # Connect button group
        self.languages_group.buttonClicked[int].connect(self.language_changed)
        
        section_layout.addWidget(self.languages_list)
        return section_widget

    def create_language_item(self, language: dict) -> QWidget:
        """Create an enhanced language selection item."""
        item_widget = QWidget()
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(20, 12, 20, 12)
        item_layout.setSpacing(16)
        item_widget.setLayout(item_layout)

        # Radio button
        radio_button = QRadioButton()
        radio_button.setChecked(language['code'] == config.current_language_code)
        radio_button.setStyleSheet(f"""
            QRadioButton::indicator {{
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid {COLORS['BORDER']};
                background-color: {COLORS['SURFACE']};
            }}
            
            QRadioButton::indicator:hover {{
                border-color: {COLORS['PRIMARY']};
            }}
            
            QRadioButton::indicator:checked {{
                border-color: {COLORS['PRIMARY']};
                background-color: {COLORS['PRIMARY']};
                background-image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iMTIiIHZpZXdCb3g9IjAgMCAxMiAxMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNiIgY3k9IjYiIHI9IjMiIGZpbGw9IndoaXRlIi8+Cjwvc3ZnPgo=);
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        # Language info
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        # Display name
        name_label = QLabel(language['display_name'])
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 16px;
                font-weight: 600;
                margin: 0;
                padding: 0;
            }}
        """)

        # Language code
        code_label = QLabel(f"Code: {language['code'].upper()}")
        code_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_SECONDARY']};
                font-size: 12px;
                font-weight: 400;
                margin: 0;
                padding: 0;
            }}
        """)

        info_layout.addWidget(name_label)
        info_layout.addWidget(code_label)

        # Add to button group
        self.languages_group.addButton(radio_button, language['id'])
        self.radio_buttons[language['code']] = radio_button

        # Layout assembly
        item_layout.addWidget(radio_button)
        item_layout.addLayout(info_layout)
        item_layout.addStretch()

        return item_widget
    
    def create_exit_button(self) -> QPushButton:
        """
        Create the exit button for the settings page.
        """
        exit_button = QPushButton()
        exit_button.setIcon(QIcon(ICON_PATHS['EXIT_BUTTON']))
        exit_button.setIconSize(QSize(30,30))
        exit_button.setFixedSize(30, 30)

        # Connect button to a slot(method)
        exit_button.clicked.connect(self.exit_settings_logic)
        return exit_button
    
    def exit_settings_logic(self) -> None:
        """
        Handle logic for exiting the settings page, including language change confirmation.
        """
        try:
            # Check if language actually changed
            if config.current_language_code != config.available_languages[config.current_language_id]:
                # Show confirmation dialog
                answer = QMessageBox.question(
                    self, 
                    'Confirm Language change',
                    'Are you sure you want to change the language?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No  # Set default to No
                )
                
                if answer == QMessageBox.Yes:
                    # Apply the change
                    config.current_language_code = config.available_languages[config.current_language_id]
                    
                    # Save to file in the background thread
                    thread = threading.Thread(
                        target=save_user_settings.save_language_settings,
                        args=[config.current_language_code]
                    )
                    thread.start()

                else:
                    # Revert UI to previous selection
                    for language in self.languages.languages_list:
                        if language['code'] == config.current_language_code:
                            config.current_language_id = language['id']
                            self.radio_buttons[language['code']].setChecked(True)
                            break

        except Exception as e:
            self.logger.error(f"Error in exit_settings_logic: {e}")
        
        # Set main page
        self.ui_application.stacked_widget.setCurrentIndex(1)

    def create_choices_languages(self) -> QVBoxLayout:
        """
        Create the layout containing language selection radio buttons in a scrollable list.
        """
        # Create layout to contain languages
        languages_layout = QVBoxLayout()
        languages_layout.setSpacing(0)  # Remove spacing since list handles it
        languages_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

        # Create the list widget to hold radio buttons
        self.languages_list = QListWidget()
        self.languages_list.setSpacing(2)  # Add spacing between items
        self.languages_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['SURFACE']};
                border: none;
                color: white;
                font-size: 15px;
                font-family: "Segoe UI";
            }}
            QListWidget::item {{
                padding: 12px 15px;  /* Increased padding for better spacing */
                border-bottom: 1px solid {COLORS['BORDER']};
                min-height: 40px;  /* Increased minimum height */
                margin: 2px 0px;   /* Add vertical margin between items */
            }}
            QListWidget::item:selected {{
                background: transparent;
            }}
            QListWidget::item:hover {{
                background: {COLORS['SURFACE_HOVER']};
                border-radius: 5px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {COLORS['SURFACE']};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLORS['BORDER']};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {COLORS['TEXT_MUTED']};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

        # Create the button group
        self.languages_group = QButtonGroup(self)
        self.radio_buttons = {}  # map code -> QRadioButton

        # Create radio buttons for each language and add them to the list
        for language in self.languages.languages_list:
            # Create a widget to hold the radio button
            item_widget = QWidget()
            item_widget.setMinimumHeight(45)  # Ensure minimum height
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 8, 15, 8)  # Better margins
            item_layout.setSpacing(10)  # Add spacing between elements
            
            # Create and configure the radio button
            radio_button = QRadioButton(language['display_name'])
            radio_button.setStyleSheet(f"""
                QRadioButton {{
                    color: white;
                    font-size: 15px;
                    font-family: "Segoe UI";
                    font-weight: bold;
                    padding: 5px;
                }}
                QRadioButton::indicator {{
                    width: 18px;
                    height: 18px;
                    margin-right: 8px;
                }}
                QRadioButton:hover {{
                    background: transparent;
                }}
            """)
            radio_button.setChecked(language['code'] == config.current_language_code)
            
            # Add radio button to the button group
            self.languages_group.addButton(radio_button, language['id'])
            self.radio_buttons[language['code']] = radio_button
            
            # Add radio button to the item layout
            item_layout.addWidget(radio_button)
            item_layout.addStretch()  # Push radio button to the left
            
            # Create list item and set its widget
            item = QListWidgetItem()
            item.setSizeHint(QSize(-1, 45))  # Set fixed height for consistency
            self.languages_list.addItem(item)
            self.languages_list.setItemWidget(item, item_widget)

        # Connect button group to language change handler
        self.languages_group.buttonClicked[int].connect(self.language_changed)

        # Add list to layout
        languages_layout.addWidget(self.languages_list)

        return languages_layout
    
    def create_paths_page(self) -> QWidget:
        """
        Create the enhanced page where user can add Programs and path to this program.
        """
        paths_page_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(32, 24, 32, 24)
        main_layout.setSpacing(24)
        paths_page_widget.setLayout(main_layout)

        # Header section
        header_section = self.create_page_header("Application Paths", "📁", "Configure application paths and names")
        main_layout.addWidget(header_section)

        # Form section
        form_section = self.create_paths_form_section()
        main_layout.addWidget(form_section, 1)

        # Buttons section
        buttons_section = self.create_paths_buttons_section()
        main_layout.addWidget(buttons_section)

        return paths_page_widget

    def create_paths_form_section(self) -> QWidget:
        """Create the form section for paths configuration."""
        section_widget = QFrame()
        section_widget.setFrameStyle(QFrame.NoFrame)
        section_widget.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['SURFACE']};
                border: 2px solid {COLORS['BORDER']};
                border-radius: 12px;
                padding: 24px;
            }}
        """)
        
        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(24, 24, 24, 24)
        form_layout.setSpacing(24)
        section_widget.setLayout(form_layout)

        # Application Path Section
        path_section = self.create_form_field(
            "Application Path",
            "Select the executable file for your application",
            is_path_field=True
        )
        form_layout.addWidget(path_section)

        # Application Name Section
        name_section = self.create_form_field(
            "Application Name", 
            "Enter a display name for your application"
        )
        form_layout.addWidget(name_section)

        # Load saved values
        self.load_settings()

        return section_widget

    def create_form_field(self, label_text: str, description: str, is_path_field: bool = False) -> QWidget:
        """Create a form field with label, description, and input."""
        field_widget = QWidget()
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(8)
        field_widget.setLayout(field_layout)

        # Label
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_PRIMARY']};
                font-size: 16px;
                font-weight: 600;
                margin: 0;
                padding: 0;
            }}
        """)

        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['TEXT_SECONDARY']};
                font-size: 14px;
                font-weight: 400;
                margin: 0;
                padding: 0;
            }}
        """)

        # Input section
        if is_path_field:
            input_section = self.create_path_input_section()
        else:
            input_section = self.create_name_input_section()

        field_layout.addWidget(label)
        field_layout.addWidget(desc_label)
        field_layout.addWidget(input_section)

        return field_widget

    def create_path_input_section(self) -> QWidget:
        """Create the path input section with browse button."""
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(12)
        input_widget.setLayout(input_layout)

        # Path input
        self.app_path_input = QLineEdit()
        self.app_path_input.setPlaceholderText("Click 'Browse' to select an application...")

        # Browse button
        browse_btn = QPushButton("Browse")
        browse_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['PRIMARY']};
                border: none;
                color: white;
                font-weight: 600;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['PRIMARY_HOVER']};
            }}
            
            QPushButton:pressed {{
                background-color: {COLORS['PRIMARY_PRESSED']};
            }}
        """)
        browse_btn.clicked.connect(self.browse_app_path)

        input_layout.addWidget(self.app_path_input, 1)
        input_layout.addWidget(browse_btn)

        return input_widget

    def create_name_input_section(self) -> QWidget:
        """Create the name input section."""
        self.app_name_input = QLineEdit()
        self.app_name_input.setPlaceholderText("Enter application name...")
        return self.app_name_input

    def create_paths_buttons_section(self) -> QWidget:
        """Create the buttons section for the paths page."""
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(12)
        buttons_widget.setLayout(buttons_layout)

        # Back button
        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['SURFACE']};
                border: 2px solid {COLORS['BORDER']};
                color: {COLORS['TEXT_SECONDARY']};
                font-weight: 500;
                min-width: 100px;
            }}
            
            QPushButton:hover {{
                background-color: {COLORS['SURFACE_HOVER']};
                border-color: {COLORS['TEXT_MUTED']};
                color: {COLORS['TEXT_PRIMARY']};
            }}
        """)
        back_btn.clicked.connect(self.on_back_clicked)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['SUCCESS']};
                border: none;
                color: white;
                font-weight: 600;
                min-width: 120px;
            }}
            
            QPushButton:hover {{
                background-color: #00B844;
            }}
            
            QPushButton:pressed {{
                background-color: #009933;
            }}
        """)
        save_btn.clicked.connect(self.save_settings_manually)

        buttons_layout.addStretch()
        buttons_layout.addWidget(back_btn)
        buttons_layout.addWidget(save_btn)

        return buttons_widget

    def save_settings_manually(self) -> None:
        """Manually save settings when save button is clicked."""
        if self.validate_settings():
            self.save_settings()
    
    def on_back_clicked(self) -> None:
        """
        Handle back button click event from settings page.
        """
        if self.validate_settings():
            self.save_settings()
            self.ui_application.stacked_widget.setCurrentIndex(1)

    def validate_settings(self) -> bool:
        """
        Validate settings page input fields with enhanced error dialog.
        """
        errors = []
        
        # Check if app path is provided and exists
        app_path = self.app_path_input.text().strip()
        if not app_path:
            errors.append('Application path cannot be empty')
        elif not Path(app_path).exists():
            errors.append('Invalid application path - file does not exist')
        
        # Check if app name is provided
        app_name = self.app_name_input.text().strip()
        if not app_name:
            errors.append('Application name cannot be empty')

        if errors:
            self.show_error_dialog('Validation Errors', '\n'.join(errors))
            return False
        return True

    def show_error_dialog(self, title: str, message: str) -> None:
        """Show a styled error dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['SURFACE']};
                color: {COLORS['TEXT_PRIMARY']};
            }}
            QMessageBox QPushButton {{
                background-color: {COLORS['PRIMARY']};
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {COLORS['PRIMARY_HOVER']};
            }}
        """)
        msg_box.exec_()

    def show_success_dialog(self, title: str, message: str) -> None:
        """Show a styled success dialog."""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {COLORS['SURFACE']};
                color: {COLORS['TEXT_PRIMARY']};
            }}
            QMessageBox QPushButton {{
                background-color: {COLORS['SUCCESS']};
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: #00B844;
            }}
        """)
        msg_box.exec_()
    
    def save_settings(self) -> None:
        """
        Save current settings to QSettings registry and JSON file.
        """
        settings = QSettings('Alpheratz', 'Joy')
        settings.setValue('AppName', self.app_name_input.text())
        settings.setValue('AppPath', self.app_path_input.text())
        load_user_data.save_user_data((self.app_name_input.text(), self.app_path_input.text()))
        self.show_success_dialog('Settings Saved', 'Settings have been saved successfully.')

    def load_settings(self) -> None:
        """
        Load persisted settings from QSettings registry.
        """
        settings = QSettings('Alpheratz', 'Joy')
        self.app_path_input.setText(settings.value('AppPath', ''))
        self.app_name_input.setText(settings.value('AppName', ''))

    def browse_app_path(self) -> None:
        """
        Open file dialog to select application executable.
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            'Select Application',
            '',
            'Executable Files (*.exe);;All Files (*)'
        )
        if path:
            self.app_path_input.setText(path)

    def language_changed(self, id_: int) -> None:
        """
        Update the selected language id when a radio button is clicked.
        """
        try:
            if id_ != config.current_language_id: 
                config.current_language_id = id_
                self.logger.info(f"Language changed to ID: {id_}")
        except Exception as e:
            self.logger.error(f"Error changing language: {e}")