"""
UI.py

Main UI module for the Joy virtual assistant application. Defines the MainWindow class, which manages the main interface, chat pages, settings, and system tray integration using PyQt5.
"""
from dataclasses import dataclass
import logging
import sys
from PyQt5.QtWidgets import (
                                QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                                QWidget, QMenu, QAction, QMessageBox,
                                QStackedWidget, QSystemTrayIcon, QDesktopWidget,
                            )
from PyQt5.QtGui     import     QIcon
from PyQt5.QtCore    import (
                                Qt, pyqtSignal
                            )
from UI_login_page        import LoginPage
from UI_settings_page     import SettingPage
from UI_sidebar import Sidebar
from UI_Threads           import (
    AlarmMonitorThread, GrayscalingThreadMonitor,
)
from Custom_Title_Bar     import CustomTitleBar
import functions
import config

class MainWindow(QMainWindow):
    """
    Main application window for Joy virtual assistant.

    Attributes:
        stacked_widget (QStackedWidget): Manages multiple application pages.
        main_page (QWidget): Primary interface with chat components.
        settings_page (QWidget): Configuration settings page.
        voice_input_thread (VoiceRequistHandler): Background thread for voice processing.
    """

    message_signal = pyqtSignal(tuple)
    def __init__(self) -> None:
        """
        Initialize main window components and UI layout.
        Sets up title bars, pages, threads, and connects signals.
        """
        super().__init__()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.setWindowFlags(Qt.FramelessWindowHint) # Remove the default title bar

        # Window configuration
        self.setWindowTitle('Joy v1.0.0')
        self.setFixedSize(910, 810)

        # Store reference to existed pages (QWidget) by it's uniq id
        self.existed_pages: dict = {}
        # Store reference to existed pages (QWidget) by it's creation position, to track which page is opened now
        self.pages_position: dict = {}
        # Store reference to existed chat widgets (QWidget) by it's creation position, to have the ability to delete that chat and pages later
        self.existed_pages_widgets: dict = {}

        # Application Setup
        self._create_title_bars()
        self._center_programm()
        self._apply_stylesheet()
        
        self._setup_page()
        # self._setup_tray_icon()
        # self._setup_tray_menu()

        # Start alarm monitoring thread
        self.alarm_monitor = AlarmMonitorThread()
        self.alarm_monitor.alarm_triggered.connect(self.print_alarm)
        self.alarm_monitor.start()
        
        # Start grayscaling monitor thread
        self.grayscaling_thread = GrayscalingThreadMonitor()
        self.grayscaling_thread.grayscaling_thread_ended.connect(self.notify_grayscaling_ended)

        self.logger.info('MainWindow initialized successfully')

    def _create_title_bars(self) -> None:
        """
        Create custom title bars for login, main, and settings pages.
        """
        self.login_title_bar = CustomTitleBar(self)
        self.main_window_title_bar = CustomTitleBar(self)

    def _center_programm(self) -> None:
        """
        Center the main window on the screen.
        """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def notify_grayscaling_ended(self) -> None:
        """
        Notify the user when the grayscaling image process is finished.
        """
        self.display_response('Grayscaling was finished, you can check a new image in your folder', config.current_page)

    def print_alarm(self) -> None:
        """
        Display an alarm message when triggered by the alarm monitor thread.
        """
        self.display_response(functions.trigger_alarm(), config.current_page)

    def _setup_tray_icon(self) -> None:
        """
        Set up the system tray icon for the application.
        """
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('hy_lig_dri.jpg'))
        self.tray_icon.show()

        # Restore window when tray icon is clicked
        self.tray_icon.activated.connect(self.handle_click)

    def handle_click(self, event) -> None:
        """
        Handle system tray icon click events.
        """
        if event == QSystemTrayIcon.Trigger:
            self.showNormal()  # Restore the window
            self.activateWindow()  # Bring it to the front
        else:
            pass

    def _setup_tray_menu(self) -> None:
        """
        Create and set the system tray context menu.
        """
        config.tray_activation = True

        tray_menu = QMenu()
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.confirm_exit)
        tray_menu.addAction(exit_action)

        restore_action =QAction('Restore', self)
        restore_action.triggered.connect(self.showNormal)
        tray_menu.addAction(restore_action)

        self.tray_icon.setContextMenu(tray_menu)

    def confirm_exit(self):
        """
        Show a confirmation dialog before exiting the application.
        """
        reply = QMessageBox.question(
            self, 'Confirm Exit', 'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No  # Set the default button to No
        )
        if reply == QMessageBox.No:
            return None
        else:
            QApplication.quit()

    def closeEvent(self, event) -> None:
        """
        Handle the window close event. If tray is enabled, hide instead of closing.
        """
        if not config.tray_activation:
            self.alarm_monitor.stop()
            config.stop_scaning.set()
            self.logger.info(f'Stop scaning')
            if self.current_llm_thread:
                self.current_llm_thread.stop()
            event.accept()    
        else:    
            # Hide instead of closing when minimized to tray
            event.ignore()
            self.hide()
            if not self.voice_input_thread.isRunning():
                self.voice_input_thread.start()

    def _apply_stylesheet(self) -> None:
        """
        Apply the main application stylesheet.
        """
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:6.5,
                    stop:0 rgba(0, 0, 0, 255),
                    stop:1 rgba(0, 0, 75, 255)
                );
            }
        """)

    def message_was_sended(self, text: str, page_id) -> None:
        """
        Handle message sending and trigger LLM processing.
        """
        self.message_signal.emit((text, page_id))

    def _setup_page(self) -> None:
        """
        Initialize the stacked widget and application pages.
        """
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Create and add pages
        self.main_page = self.create_main_page()
        self.settings_page = SettingPage(self, self) # The second arg is UI, by itself
        self.login_page = LoginPage(self, self.login_title_bar)
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.settings_page)

    def display_response(self, page_id=None, placeholder=False, message: str = None, llm_response: bool = False) -> None:
        """
        Display a response message in the chat interface.
        """
        page = self.existed_pages[page_id]
        if placeholder:
            page.add_llm_placeholder()
        elif llm_response:
            page.update_llm_response(message)

    def create_main_page(self) -> QWidget:
        """
        Create the main chat interface page.

        Returns:
            QWidget: Configured main page widget.
        """
        # Create the main Window widget
        window = QWidget()
        # Main Vertical Layout for 1. Title Bar, 2. Page Area
        self.main_layout = QVBoxLayout()
        window.setLayout(self.main_layout)

        # Add Title Bar first to arrange it on the top
        self.main_layout.addWidget(self.main_window_title_bar)

        # Create Stacked Widget to contain all chats like separate Widget
        self.chat_stack = QStackedWidget()

        # Create Page Area widget
        self.page_widget = QWidget()
        # Create Horizontal Layout to arrange Sidebar and Content horizontally
        self.page_layout = QHBoxLayout()
        self.page_widget.setLayout(self.page_layout)
        self.main_layout.addWidget(self.page_widget)

        # Create sidebar and add to the page Layout
        self.sidebar = Sidebar(self)
        self.page_layout.addWidget(self.sidebar)
        self.page_layout.addWidget(self.chat_stack)

        # Init Chat
        self.sidebar.create_new_chat()
        
        return window

    def save_page(self, page) -> None:
        """
        Save a reference to a chat page by its unique id.
        """
        config.current_page = page
        self.existed_pages[page.page_id] = page
        self.pages_position[config.chats_quantity] = page

    def delete_page(self, page_widget: QWidget) -> None:
        """
        Delete page from self.existed_page.

        Arg:
            page_widget (QWidget): chat_widget from sidebar chats history.
        """
        page_position_in_existed_pages: int = self.existed_pages_widgets[page_widget]
        key = list(self.existed_pages.keys())[page_position_in_existed_pages]

        del self.existed_pages[key]
        del self.existed_pages_widgets[page_widget]
        del self.pages_position[page_position_in_existed_pages+1]

    def switch_chat(self, chat_id: int) -> None:
        """
        Change the current Chat, working due to managing button in ButtonGroup.
        """
        print(chat_id, self.existed_pages_widgets)
        print(chat_id, self.existed_pages)
        print(chat_id, self.pages_position)
        config.current_page_widget_id = chat_id
        config.current_page = self.pages_position[chat_id+1]
        self.chat_stack.setCurrentIndex(chat_id)

    def show_settings_page(self) -> None:
        """
        Switch view to display settings page.
        """
        self.stacked_widget.setCurrentIndex(2)

    def save_user_voice_output_settings(self, status: bool) -> None:
        """
        Save user voice output settings using the functions module.
        """
        functions.save_user_settings(status)

    def show_about(self) -> None:
        """
        Display application about dialog.
        """
        QMessageBox.information(
            self,
            'About Joy',
            'Joy Virtual Assistant\nVersion 1.0.0\n\nCreated by Alpheratz corporation'
        )

if __name__ == '__main__':
    """
    Main entry point for the Joy application.
    Initializes the QApplication, main window, and starts the event loop.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
