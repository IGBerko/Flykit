import sys
import os
import urllib.request
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QProgressBar, QFileDialog,
                             QGraphicsDropShadowEffect, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QPoint, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
import requests

FLYKIT_URL = "https://fly.itrypro.ru/flykit.exe"
DEFAULT_INSTALL_PATH = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Flykit')

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, url, destination):
        super().__init__()
        self.url = url
        self.destination = destination
    
    def run(self):
        try:
            # Create destination directory if it doesn't exist
            os.makedirs(os.path.dirname(self.destination), exist_ok=True)
            
            def reporthook(block_num, block_size, total_size):
                if total_size > 0:
                    downloaded = block_num * block_size
                    progress = int((downloaded / total_size) * 100)
                    self.progress.emit(min(progress, 100))
            
            urllib.request.urlretrieve(self.url, self.destination, reporthook)
            self.finished.emit(True, "Installation completed successfully!")
        except Exception as e:
            self.finished.emit(False, f"Installation failed: {str(e)}")

class DraggableTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = QPoint()
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 10, 10)
        layout.setSpacing(10)
        
        # Title
        self.title_label = QLabel("Flykit Browser Installer")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.title_label.setStyleSheet("color: #202124;")
        
        # Close button
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(45, 30)
        self.close_btn.setFont(QFont("Segoe UI", 16))
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #5f6368;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: #e81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(parent.close)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.close_btn)
        
        self.setStyleSheet("background: white;")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()

class FlykitInstaller(QWidget):
    def __init__(self):
        super().__init__()
        self.install_path = DEFAULT_INSTALL_PATH
        self.current_step = 0
        self.init_ui()
    
    def init_ui(self):
        # Frameless window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: white;
                border-radius: 12px;
            }
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 40))
        container.setGraphicsEffect(shadow)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        # Container layout
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # Title bar
        self.title_bar = DraggableTitleBar(self)
        container_layout.addWidget(self.title_bar)
        
        # Content area
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(40, 30, 40, 40)
        content_layout.setSpacing(25)
        
        url = "https://fly.itrypro.ru/favicon.png"
        data = requests.get(url).content

# Загружаем в QPixmap
        pixmap = QPixmap()
        pixmap.loadFromData(data)

# QLabel с картинкой
        logo_label = QLabel()
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Welcome text
        self.welcome_label = QLabel("Welcome to Flykit Browser")
        self.welcome_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.welcome_label.setAlignment(Qt.AlignCenter)
        self.welcome_label.setStyleSheet("color: #202124;")
        
        # Description
        self.desc_label = QLabel("A modern, fast, and secure web browser")
        self.desc_label.setFont(QFont("Segoe UI", 11))
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setStyleSheet("color: #5f6368;")
        
        # Installation path section
        path_container = QWidget()
        path_container.setStyleSheet("""
            QWidget {
                background: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        path_layout = QVBoxLayout(path_container)
        path_layout.setSpacing(10)
        
        path_label = QLabel("Installation Directory:")
        path_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        path_label.setStyleSheet("color: #202124; background: transparent; padding: 0;")
        
        path_input_layout = QHBoxLayout()
        path_input_layout.setSpacing(10)
        
        self.path_input = QLineEdit(self.install_path)
        self.path_input.setFont(QFont("Segoe UI", 10))
        self.path_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 1px solid #dadce0;
                border-radius: 6px;
                padding: 10px 12px;
                color: #202124;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                padding: 9px 11px;
            }
        """)
        self.path_input.textChanged.connect(self.on_path_changed)
        
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setFont(QFont("Segoe UI", 10, QFont.Medium))
        self.browse_btn.setFixedHeight(40)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #dadce0;
                border-radius: 6px;
                padding: 0 20px;
                color: #1a73e8;
            }
            QPushButton:hover {
                background: #f8f9fa;
                border-color: #1a73e8;
            }
            QPushButton:pressed {
                background: #e8f0fe;
            }
        """)
        self.browse_btn.clicked.connect(self.browse_directory)
        
        path_input_layout.addWidget(self.path_input)
        path_input_layout.addWidget(self.browse_btn)
        
        path_layout.addWidget(path_label)
        path_layout.addLayout(path_input_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: #e8eaed;
                border-radius: 4px;
                border: none;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a73e8, stop:1 #4285f4);
                border-radius: 4px;
            }
        """)
        self.progress_bar.hide()
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Segoe UI", 10))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #5f6368;")
        self.status_label.hide()
        
        # Install button
        self.install_btn = QPushButton("Install Flykit Browser")
        self.install_btn.setFont(QFont("Segoe UI", 11, QFont.Medium))
        self.install_btn.setFixedHeight(48)
        self.install_btn.setCursor(Qt.PointingHandCursor)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1a73e8, stop:1 #4285f4);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 0 32px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1557b0, stop:1 #1a73e8);
            }
            QPushButton:pressed {
                background: #1557b0;
            }
            QPushButton:disabled {
                background: #e8eaed;
                color: #9aa0a6;
            }
        """)
        self.install_btn.clicked.connect(self.start_installation)
        
        # Add widgets to content layout
        content_layout.addWidget(logo_label)
        content_layout.addWidget(self.welcome_label)
        content_layout.addWidget(self.desc_label)
        content_layout.addSpacing(10)
        content_layout.addWidget(path_container)
        content_layout.addWidget(self.progress_bar)
        content_layout.addWidget(self.status_label)
        content_layout.addStretch()
        content_layout.addWidget(self.install_btn)
        
        container_layout.addWidget(content)
        
        # Window properties
        self.setFixedSize(600, 650)
        self.setWindowTitle("Flykit Browser Installer")
        
        # Center window
        self.center_window()
        
        # Fade in animation
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def center_window(self):
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def on_path_changed(self, text):
        self.install_path = text
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Installation Directory",
            self.install_path
        )
        if directory:
            self.install_path = directory
            self.path_input.setText(directory)
    
    def start_installation(self):
        self.install_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.path_input.setEnabled(False)
        self.progress_bar.show()
        self.status_label.show()
        self.status_label.setText("Downloading Flykit Browser...")
        
        # Start download
        exe_path = os.path.join(self.install_path, "flykit.exe")
        self.download_thread = DownloadThread(FLYKIT_URL, exe_path)
        self.download_thread.progress.connect(self.update_progress)
        self.download_thread.finished.connect(self.installation_finished)
        self.download_thread.start()
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value < 100:
            self.status_label.setText(f"Downloading Flykit Browser... {value}%")
        else:
            self.status_label.setText("Installing...")
    
    def installation_finished(self, success, message):
        if success:
            self.status_label.setText("✓ Installation completed successfully!")
            self.status_label.setStyleSheet("color: #1e8e3e; font-weight: bold;")
            self.install_btn.setText("Launch Flykit Browser")
            self.install_btn.setEnabled(True)
            self.install_btn.clicked.disconnect()
            self.install_btn.clicked.connect(self.launch_browser)
            
            # Create desktop shortcut (optional)
            self.create_shortcuts()
        else:
            self.status_label.setText(f"✗ {message}")
            self.status_label.setStyleSheet("color: #d93025; font-weight: bold;")
            self.install_btn.setText("Retry Installation")
            self.install_btn.setEnabled(True)
            self.browse_btn.setEnabled(True)
            self.path_input.setEnabled(True)
    
    def create_shortcuts(self):
        try:
            # Create start menu shortcut
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            start_menu = winshell.start_menu()
            
            exe_path = os.path.join(self.install_path, "flykit.exe")
            
            # Desktop shortcut
            desktop_shortcut = os.path.join(desktop, "Flykit Browser.lnk")
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(desktop_shortcut)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = self.install_path
            shortcut.IconLocation = exe_path
            shortcut.save()
            
            # Start menu shortcut
            start_menu_shortcut = os.path.join(start_menu, "Flykit Browser.lnk")
            shortcut = shell.CreateShortCut(start_menu_shortcut)
            shortcut.Targetpath = exe_path
            shortcut.WorkingDirectory = self.install_path
            shortcut.IconLocation = exe_path
            shortcut.save()
        except:
            pass  # Shortcuts are optional
    
    def launch_browser(self):
        try:
            exe_path = os.path.join(self.install_path, "flykit.exe")
            os.startfile(exe_path)
            self.close()
        except Exception as e:
            self.status_label.setText(f"Failed to launch: {str(e)}")
            self.status_label.setStyleSheet("color: #d93025;")

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # Set application font
    app.setFont(QFont("Segoe UI", 10))
    
    installer = FlykitInstaller()
    installer.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
