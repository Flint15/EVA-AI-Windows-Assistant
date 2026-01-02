from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton,
    QMessageBox, QGraphicsDropShadowEffect,
    QFrame
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import logging

class LoginPage(QWidget):
    """
    Dark Mode Login Page with #8A00C4 brand colors and modern design
    """
    login_successful = pyqtSignal()
    
    # Dark Mode Color System
    PRIMARY_COLOR = "#8A00C4"          # Deep purple
    PRIMARY_HOVER = "#9D1ADB"          # Bright purple
    PRIMARY_LIGHT = "#B84AE5"          # Light purple
    PRIMARY_DARK = "#6B0094"           # Dark purple
    PRIMARY_ALPHA = "rgba(138, 0, 196, 0.15)"  # Semi-transparent purple
    PRIMARY_GLOW = "rgba(138, 0, 196, 0.3)"    # Glowing purple
    
    # Dark Theme Colors
    BACKGROUND_DARK = "#0A0A0F"        # Almost black
    BACKGROUND_CARD = "#1A1A2E"        # Dark blue-gray
    BACKGROUND_ELEVATED = "#16213E"     # Navy blue
    
    # Text Colors
    TEXT_PRIMARY = "#FFFFFF"           # White
    TEXT_SECONDARY = "#B8BCC8"         # Light gray
    TEXT_MUTED = "#6B7280"            # Medium gray
    
    # Input Colors
    INPUT_BACKGROUND = "#1F2937"       # Dark gray
    INPUT_BACKGROUND_FOCUS = "#374151" # Medium-dark graysf
    INPUT_BORDER = "#374151"           # Medium-dark gray
    INPUT_BORDER_FOCUS = PRIMARY_COLOR # Deep purple
    
    # Accent Colors
    ACCENT_CYAN = "#06B6D4"           # Bright cyan
    ACCENT_PURPLE = "#8B5CF6"         # Bright purple
    SUCCESS_COLOR = "#10B981"         # Emerald green
    ERROR_COLOR = "#EF4444"           # Bright red
    
    def __init__(self, UI_application, title_bar, parent=None):
        super().__init__(parent)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.UI_application = UI_application
        self.title_bar = title_bar
        
        # Store input references
        self.name_input = None
        self.password_input = None
        self.toggle_button = None
        self.submit_button = None
        
        # Set dark theme for the entire widget
        self.setStyleSheet(f"background-color: {self.BACKGROUND_DARK};")
        
        # Main layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Build the dark mode login content
        content = self.build_dark_mode_content()

        # Arrange components
        page_layout.addWidget(self.title_bar)
        page_layout.addWidget(content, 1)

    def build_dark_mode_content(self) -> QWidget:
        """Create dark mode background with brand-colored elements"""
        background_widget = QWidget()
        
        # Dark gradient background with brand accents
        background_widget.setStyleSheet(f'''
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.BACKGROUND_DARK}, 
                    stop:0.2 rgba(138, 0, 196, 0.05),
                    stop:0.5 {self.BACKGROUND_DARK},
                    stop:0.8 rgba(6, 182, 212, 0.03),
                    stop:1 {self.BACKGROUND_DARK});
            }}
        ''')
        
        background_layout = QVBoxLayout(background_widget)
        background_layout.setContentsMargins(40, 40, 40, 40)
        
        # Add floating elements for visual interest
        self.add_dark_floating_elements(background_widget)
        
        # Create centered container
        center_container = self.create_dark_login_container()
        background_layout.addWidget(center_container, 0, Qt.AlignCenter)
        
        return background_widget

    def add_dark_floating_elements(self, parent):
        """Add subtle glowing elements for dark mode"""
        # Create glowing orbs with brand colors
        glow_elements = [
            (0.15, 0.2, 150, self.PRIMARY_GLOW, 0.4),
            (0.85, 0.15, 100, f"rgba(6, 182, 212, 0.2)", 0.3),
            (0.9, 0.75, 120, self.PRIMARY_GLOW, 0.35),
            (0.1, 0.8, 80, f"rgba(139, 92, 246, 0.25)", 0.25)
        ]
        
        for x, y, size, color, opacity in glow_elements:
            orb = QWidget(parent)
            orb.setFixedSize(size, size)
            orb.setStyleSheet(f'''
                QWidget {{
                    background: radial-gradient(circle, {color} 0%, transparent 70%);
                    border-radius: {size//2}px;
                }}
            ''')

    def create_dark_login_container(self) -> QWidget:
        """Create the main dark login container"""
        container = QWidget()
        container.setFixedSize(460, 600)  # Slightly larger for dark mode
        
        # Dark glassmorphism effect
        container.setStyleSheet(f'''
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(26, 26, 46, 0.95),
                    stop:0.5 rgba(22, 33, 62, 0.9),
                    stop:1 rgba(26, 26, 46, 0.95));
                border-radius: 24px;
                border: 1px solid rgba(138, 0, 196, 0.2);
                backdrop-filter: blur(20px);
            }}
        ''')
        
        # Enhanced shadow with purple glow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(50)
        shadow.setXOffset(0)
        shadow.setYOffset(15)
        shadow.setColor(QColor(138, 0, 196, 120))
        container.setGraphicsEffect(shadow)
        
        # Main form layout
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(45, 45, 45, 45)
        main_layout.setSpacing(26)
        
        # Add components
        self.add_dark_header_section(main_layout)
        self.add_dark_form_section(main_layout)
        self.add_dark_footer_section(main_layout)
        
        return container

    def add_dark_header_section(self, layout: QVBoxLayout):
        """Enhanced dark header with glowing accents"""
        header_layout = QVBoxLayout()
        header_layout.setSpacing(16)
        
        # Glowing brand accent line
        accent_line = QFrame()
        accent_line.setFixedSize(80, 4)
        accent_line.setStyleSheet(f'''
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PRIMARY_COLOR}, 
                    stop:0.5 {self.PRIMARY_LIGHT},
                    stop:1 {self.ACCENT_CYAN});
                border-radius: 2px;
                border: none;
            }}
        ''')
        
        # Add glow effect to accent line
        accent_glow = QGraphicsDropShadowEffect()
        accent_glow.setBlurRadius(15)
        accent_glow.setXOffset(0)
        accent_glow.setYOffset(0)
        accent_glow.setColor(QColor(138, 0, 196, 180))
        accent_line.setGraphicsEffect(accent_glow)
        
        # Center the accent line
        accent_container = QHBoxLayout()
        accent_container.addWidget(accent_line, 0, Qt.AlignCenter)
        
        # Main title with glow
        title_label = QLabel("Welcome Back")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Inter", 30, QFont.Bold))
        title_label.setStyleSheet(f'''
            QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
                margin: 12px 0;
            }}
        ''')
        
        # Add glow to title
        title_glow = QGraphicsDropShadowEffect()
        title_glow.setBlurRadius(20)
        title_glow.setXOffset(0)
        title_glow.setYOffset(0)
        title_glow.setColor(QColor(255, 255, 255, 60))
        title_label.setGraphicsEffect(title_glow)
        
        header_layout.addLayout(accent_container)
        header_layout.addWidget(title_label)
        layout.addLayout(header_layout)

    def add_dark_form_section(self, layout: QVBoxLayout):
        """Dark mode form with enhanced styling"""
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        # Name field
        name_container = self.create_dark_input_container("Username", "Enter your username")
        self.name_input = name_container.findChild(QLineEdit)
        form_layout.addWidget(name_container)
        
        # Password field
        password_container = self.create_dark_password_container()
        form_layout.addWidget(password_container)
        
        # Options row
        options_row = self.create_dark_options_row()
        form_layout.addWidget(options_row)
        
        # Submit button
        self.submit_button = self.create_dark_submit_button()
        form_layout.addWidget(self.submit_button)
        
        layout.addLayout(form_layout)

    def create_dark_input_container(self, label_text: str, placeholder: str = "") -> QWidget:
        """Create dark mode input with neon accents"""
        container = QWidget()
        container.setStyleSheet('background: transparent; border: none;')
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        
        # Enhanced label with brand accent
        label = QLabel(label_text)
        label.setFont(QFont("Inter", 14, QFont.Medium))
        label.setStyleSheet(f'''
            QLabel {{
                color: {self.TEXT_PRIMARY};
                font-weight: 600;
                background: transparent;
            }}
        ''')
        
        # Enhanced input field
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setFixedHeight(56)
        input_field.setFont(QFont("Inter", 16))
        input_field.setStyleSheet(self.get_dark_input_style())
        
        container_layout.addWidget(label)
        container_layout.addWidget(input_field)
        
        return container

    def create_dark_password_container(self) -> QWidget:
        """Dark mode password field with glowing toggle"""
        container = QWidget()
        container.setStyleSheet('background: transparent; border: none;')
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(10)
        
        # Label
        label = QLabel("Password")
        label.setFont(QFont("Inter", 14, QFont.Medium))
        label.setStyleSheet(f'''
            QLabel {{
                color: {self.TEXT_PRIMARY};
                font-weight: 600;
                background: transparent;
            }}
        ''')
        
        # Password input container
        input_container = QWidget()
        input_container.setFixedHeight(56)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        input_layout.setSpacing(0)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(56)
        self.password_input.setFont(QFont("Inter", 16))
        self.password_input.setStyleSheet(self.get_dark_password_style())
        
        # Enhanced toggle button with glow
        self.toggle_button = QPushButton("👁")
        self.toggle_button.setFixedSize(40, 40)
        self.toggle_button.setFlat(True)
        self.toggle_button.setCursor(Qt.PointingHandCursor)
        self.toggle_button.setStyleSheet(f'''
            QPushButton {{
                border: none;
                background: transparent;
                border-radius: 20px;
                color: {self.TEXT_SECONDARY};
                font-size: 18px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.PRIMARY_ALPHA}, 
                    stop:1 rgba(6, 182, 212, 0.1));
                color: {self.PRIMARY_LIGHT};
            }}
        ''')
        self.toggle_button.clicked.connect(self.toggle_password_visibility)
        
        input_layout.addWidget(self.password_input)
        input_layout.addWidget(self.toggle_button)
        
        container_layout.addWidget(label)
        container_layout.addWidget(input_container)
        
        return container

    def create_dark_options_row(self) -> QWidget:
        """Dark mode options row with accent colors"""
        options_widget = QWidget()
        options_widget.setStyleSheet('background-color: transparent; border: none;')
        options_layout = QHBoxLayout(options_widget)
        options_layout.setContentsMargins(0, 0, 0, 0)
        
        # Remember me with custom styling
        remember_label = QLabel("Remember me")
        remember_label.setFont(QFont("Inter", 13))
        remember_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; background: transparent;")
        
        # Forgot password link with glow
        forgot_link = QLabel("Forgot password?")
        forgot_link.setFont(QFont("Inter", 13, QFont.Medium))
        forgot_link.setCursor(Qt.PointingHandCursor)
        forgot_link.setStyleSheet(f'''
            QLabel {{
                color: {self.PRIMARY_LIGHT};
                font-weight: 600;
                background: transparent;
            }}
            QLabel:hover {{
                color: {self.ACCENT_CYAN};
                text-decoration: underline;
            }}
        ''')
        
        options_layout.addWidget(remember_label)
        options_layout.addStretch()
        options_layout.addWidget(forgot_link)
        
        return options_widget

    def create_dark_submit_button(self) -> QPushButton:
        """Create stunning dark mode submit button with glow effect"""
        submit_button = QPushButton("Sign In")
        submit_button.setFixedHeight(55)
        submit_button.setFont(QFont("Inter", 16, QFont.Bold))
        submit_button.setCursor(Qt.PointingHandCursor)
        submit_button.setStyleSheet(f'''
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PRIMARY_COLOR}, 
                    stop:0.5 {self.PRIMARY_LIGHT},
                    stop:1 {self.ACCENT_CYAN});
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 25px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PRIMARY_HOVER}, 
                    stop:0.5 {self.PRIMARY_LIGHT},
                    stop:1 {self.ACCENT_CYAN});
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {self.PRIMARY_DARK};
                transform: translateY(0px);
            }}
            QPushButton:disabled {{
                background: {self.INPUT_BORDER};
                color: {self.TEXT_MUTED};
            }}
        ''')
        
        # Add glow effect to button
        button_glow = QGraphicsDropShadowEffect()
        button_glow.setBlurRadius(25)
        button_glow.setXOffset(0)
        button_glow.setYOffset(0)
        button_glow.setColor(QColor(138, 0, 196, 150))
        submit_button.setGraphicsEffect(button_glow)
        
        submit_button.clicked.connect(self.handle_login_attempt)
        return submit_button

    def add_dark_footer_section(self, layout: QVBoxLayout):
        """Dark mode footer with neon accents"""
        # Glowing divider
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet(f'''
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent, 
                    stop:0.5 {self.PRIMARY_ALPHA},
                    stop:1 transparent);
                border: none;
                margin: 12px 0;
            }}
        ''')
        
        # Sign up section
        footer_layout = QHBoxLayout()
        footer_layout.setAlignment(Qt.AlignCenter)
        
        no_account_label = QLabel("Don't have an account?")
        no_account_label.setFont(QFont("Inter", 14))
        no_account_label.setStyleSheet(f"color: {self.TEXT_SECONDARY}; background: transparent; border: none")
        
        signup_link = QLabel("Create one")
        signup_link.setFont(QFont("Inter", 14, QFont.Bold))
        signup_link.setCursor(Qt.PointingHandCursor)
        signup_link.setStyleSheet(f'''
            QLabel {{
                color: {self.ACCENT_CYAN};
                font-weight: 700;
                margin-left: 8px;
                background: transparent;
                border: none;
            }}
            QLabel:hover {{
                color: {self.PRIMARY_LIGHT};
                text-decoration: underline;
            }}
        ''')
        
        footer_layout.addWidget(no_account_label)
        footer_layout.addWidget(signup_link)
        
        layout.addWidget(divider)
        layout.addLayout(footer_layout)

    def get_dark_input_style(self) -> str:
        """Dark mode input styling with neon focus"""
        return f'''
            QLineEdit {{
                background-color: {self.INPUT_BACKGROUND};
                border: 2px solid {self.INPUT_BORDER};
                border-radius: 14px;
                padding: 16px 20px;
                color: {self.TEXT_PRIMARY};
                font-size: 16px;
                selection-background-color: {self.PRIMARY_COLOR};
            }}
            QLineEdit:focus {{
                border-color: {self.PRIMARY_COLOR};
                background-color: {self.INPUT_BACKGROUND_FOCUS};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_MUTED};
                background: transparent;
            }}
        '''

    def get_dark_password_style(self) -> str:
        """Dark mode password input styling"""
        return f'''
            QLineEdit {{
                background-color: {self.INPUT_BACKGROUND};
                border: 2px solid {self.INPUT_BORDER};
                border-radius: 14px;
                padding: 16px 55px 16px 20px;
                color: {self.TEXT_PRIMARY};
                font-size: 16px;
                selection-background-color: {self.PRIMARY_COLOR};
            }}
            QLineEdit:focus {{
                border-color: {self.PRIMARY_COLOR};
                background-color: {self.INPUT_BACKGROUND_FOCUS};
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: {self.TEXT_MUTED};
                background: transparent;
            }}
        '''

    def toggle_password_visibility(self):
        """Toggle password visibility with enhanced icons"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_button.setText("🙈")
            self.toggle_button.setToolTip("Hide password")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_button.setText("👁")
            self.toggle_button.setToolTip("Show password")

    def validate_inputs(self) -> bool:
        """Enhanced validation for dark mode"""
        username = self.name_input.text().strip()
        password = self.password_input.text()
        
        if not username:
            self.show_dark_validation_error("Username Required", "Please enter your username to continue.")
            self.name_input.setFocus()
            return False
            
        if not password:
            self.show_dark_validation_error("Password Required", "Please enter your password to continue.")
            self.password_input.setFocus()
            return False
            
        if len(password) < 6:
            self.show_dark_validation_error("Password Too Short", "Password must be at least 6 characters long.")
            self.password_input.setFocus()
            return False
            
        return True

    def show_dark_validation_error(self, title: str, message: str):
        """Dark mode validation error dialog"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet(f'''
            QMessageBox {{
                background-color: {self.BACKGROUND_CARD};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.PRIMARY_ALPHA};
                border-radius: 12px;
                min-width: 350px;
            }}
            QMessageBox QLabel {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
                min-width: 300px;
            }}
            QMessageBox QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PRIMARY_COLOR}, 
                    stop:1 {self.PRIMARY_LIGHT});
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 10px;
                padding: 12px 24px;
                font-weight: 700;
                min-width: 100px;
            }}
            QMessageBox QPushButton:hover {{
                background: {self.PRIMARY_HOVER};
            }}
            QMessageBox QPushButton::menu-indicator {{
                background: transparent;
                image: none;
                width: 0;
            }}
            QMessageBox QLabel#qt_msgbox_label {{
                color: {self.TEXT_PRIMARY};
                background: transparent;
            }}
            QMessageBox QLabel#qt_msgboxex_icon_label {{
                background: transparent;
            }}
        ''')
        msg.exec_()

    def handle_login_attempt(self):
        """Enhanced dark mode login handling"""
        if not self.validate_inputs():
            return
            
        # Enhanced loading state
        self.submit_button.setEnabled(False)
        self.submit_button.setText("🔄 Signing in...")
        self.submit_button.setStyleSheet(f'''
            QPushButton {{
                background: {self.INPUT_BORDER};
                color: {self.TEXT_MUTED};
                border: none;
                border-radius: 29px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
        ''')
        
        try:
            self.perform_login()
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            self.show_dark_validation_error("Login Failed", "Unable to sign in. Please check your credentials and try again.")
        finally:
            # Reset button state
            self.submit_button.setEnabled(True)
            self.submit_button.setText("🚀 Sign In")
            self.submit_button.setStyleSheet(f'''
                QPushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.PRIMARY_COLOR}, 
                        stop:0.5 {self.PRIMARY_LIGHT},
                        stop:1 {self.ACCENT_CYAN});
                    color: {self.TEXT_PRIMARY};
                    border: none;
                    border-radius: 29px;
                    font-weight: 700;
                    letter-spacing: 1px;
                }}
                QPushButton:hover {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {self.PRIMARY_HOVER}, 
                        stop:0.5 {self.PRIMARY_LIGHT},
                        stop:1 {self.ACCENT_CYAN});
                }}
            ''')

    def perform_login(self):
        """Perform the actual login process"""
        self.on_login_success()

    def on_login_success(self):
        """Handle successful login"""
        self.UI_application.stacked_widget.setCurrentIndex(1)
        
        """# Version check with dark mode dialog
        result: str = check_version()
        if result == 'Not matches':
            self.show_dark_update_dialog()"""

    def show_dark_update_dialog(self):
        """Dark mode update dialog with glow effects"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("🔄 Update Available")
        msg.setText("✨ New Update Available")
        msg.setInformativeText(
            "A new version is available for download.\n"
            "For optimal performance, please update the application.\n"
            "Don't forget to update your configuration settings!"
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet(f'''
            QMessageBox {{
                background-color: {self.BACKGROUND_CARD};
                color: {self.TEXT_PRIMARY};
                border: 1px solid {self.PRIMARY_ALPHA};
                border-radius: 16px;
                min-width: 400px;
            }}
            QMessageBox QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {self.PRIMARY_COLOR}, 
                    stop:1 {self.ACCENT_CYAN});
                color: {self.TEXT_PRIMARY};
                border: none;
                border-radius: 12px;
                padding: 12px 28px;
                font-weight: 700;
                min-width: 120px;
            }}
            QMessageBox QPushButton:hover {{
                background: {self.PRIMARY_HOVER};
            }}
        ''')
        msg.exec_()
