import sys
import os
import json
import zipfile
import shutil
import time
import gc
from PyQt5.QtWidgets import (QApplication, QMainWindow, QToolBar, QAction, QLineEdit, 
                             QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QListWidget, QMessageBox, QWidget, QMenu, QGraphicsDropShadowEffect,
                             QTabWidget, QTabBar)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QPainter, QPainterPath
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineScript
from PyQt5.QtCore import QUrl, Qt, QFile, QIODevice, QPropertyAnimation, QEasingCurve, QRect, QPoint

# Путь установки
INSTALL_PATH = os.path.join(os.path.expanduser("~"), ".expb")
SETTINGS_FILE = os.path.join(INSTALL_PATH, "settings.json")
CACHE_DIR = os.path.join(INSTALL_PATH, "cache")
EXTENSIONS_DIR = os.path.join(INSTALL_PATH, "extensions")

# Проверяем папки
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(EXTENSIONS_DIR, exist_ok=True)

# Сохраняем настройки
if not os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"homepage": "https://www.fly.itrypro.ru/alp/index.html"}, f, indent=4)

class ExtensionInstallDialog(QDialog):
    def __init__(self, extension_name, extension_icon=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Установка расширения")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(480, 280)
        self.result_value = False
        
        container = QWidget(self)
        container.setGeometry(10, 10, 460, 260)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 16px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)
        
        close_btn = QPushButton("×", container)
        close_btn.setGeometry(420, 10, 32, 32)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #5f6368;
                font-size: 24px;
                font-weight: 300;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                color: #202124;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        header_layout = QHBoxLayout()
        header_layout.setSpacing(16)
        
        if extension_icon and os.path.exists(extension_icon):
            icon_label = QLabel()
            pixmap = QPixmap(extension_icon).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setStyleSheet("border-radius: 12px;")
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(f"{extension_name}")
        title_label.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 24px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        desc_label = QLabel("Это расширение получит доступ к:")
        desc_label.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-top: 8px;
            }
        """)
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        permissions_label = QLabel("• Чтение и изменение данных на всех сайтах\n• Хранение данных локально")
        permissions_label.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
                line-height: 1.6;
                padding-left: 8px;
            }
        """)
        layout.addWidget(permissions_label)
        
        layout.addStretch()
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #dadce0;
                padding: 0px 24px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                color: #1a73e8;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
                border-color: #1a73e8;
            }
            QPushButton:pressed {
                background-color: #e8f0fe;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        install_btn = QPushButton("Установить расширение")
        install_btn.setFixedHeight(40)
        install_btn.setCursor(Qt.PointingHandCursor)
        install_btn.setStyleSheet("""
            QPushButton {
                background-color: #1a73e8;
                color: white;
                border: none;
                padding: 0px 32px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #1765cc;
            }
            QPushButton:pressed {
                background-color: #1557b0;
            }
        """)
        install_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(install_btn)
        layout.addLayout(button_layout)
        
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()

class ExtensionsManager(QDialog):
    def __init__(self, browser, parent=None):
        super().__init__(parent)
        self.browser = browser
        self.setWindowTitle("Расширения")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(720, 520)
        
        container = QWidget(self)
        container.setGeometry(10, 10, 700, 500)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 16px;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setXOffset(0)
        shadow.setYOffset(4)
        shadow.setColor(QColor(0, 0, 0, 60))
        container.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        
        header_layout = QHBoxLayout()
        title = QLabel("Расширения")
        title.setStyleSheet("""
            QLabel {
                color: #202124;
                font-size: 28px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #5f6368;
                font-size: 28px;
                font-weight: 300;
                border-radius: 18px;
            }
            QPushButton:hover {
                background-color: #f1f3f4;
                color: #202124;
            }
        """)
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)
        
        subtitle = QLabel("Управляйте установленными расширениями")
        subtitle.setStyleSheet("""
            QLabel {
                color: #5f6368;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                margin-bottom: 8px;
            }
        """)
        layout.addWidget(subtitle)
        
        self.extensions_list = QListWidget()
        self.extensions_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e8eaed;
                border-radius: 12px;
                padding: 8px;
                background-color: #fafafa;
                outline: none;
            }
            QListWidget::item {
                padding: 16px;
                border-radius: 8px;
                margin: 4px;
                background-color: white;
                color: #202124;
                font-size: 14px;
                font-family: 'Segoe UI', Arial, sans-serif;
                border: 1px solid #e8eaed;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
                border-color: #dadce0;
            }
            QListWidget::item:selected {
                background-color: #e8f0fe;
                border-color: #1a73e8;
                color: #1a73e8;
            }
        """)
        layout.addWidget(self.extensions_list)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        remove_btn = QPushButton("Удалить выбранное")
        remove_btn.setFixedHeight(40)
        remove_btn.setCursor(Qt.PointingHandCursor)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #d93025;
                color: white;
                border: none;
                padding: 0px 28px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #c5221f;
            }
            QPushButton:pressed {
                background-color: #b31412;
            }
        """)
        remove_btn.clicked.connect(self.remove_extension)
        btn_layout.addWidget(remove_btn)
        
        layout.addLayout(btn_layout)
        
        self.load_extensions()
        
        self.setWindowOpacity(0)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(200)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
    
    def load_extensions(self):
        self.extensions_list.clear()
        for ext_name in os.listdir(EXTENSIONS_DIR):
            ext_path = os.path.join(EXTENSIONS_DIR, ext_name)
            if os.path.isdir(ext_path):
                manifest_path = os.path.join(ext_path, "manifest.json")
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                        self.extensions_list.addItem(f"📦 {manifest.get('name', ext_name)} (v{manifest.get('version', '1.0')})")
    
    def remove_extension(self):
        current_item = self.extensions_list.currentItem()
        if current_item:
            ext_name = current_item.text().split(" (v")[0].replace("📦 ", "")
            reply = QMessageBox.question(self, "Удаление расширения", 
                                        f"Удалить расширение '{ext_name}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                for folder in os.listdir(EXTENSIONS_DIR):
                    manifest_path = os.path.join(EXTENSIONS_DIR, folder, "manifest.json")
                    if os.path.exists(manifest_path):
                        try:
                            with open(manifest_path, "r", encoding="utf-8") as f:
                                manifest = json.load(f)
                                if manifest.get('name') == ext_name:
                                    ext_folder = os.path.join(EXTENSIONS_DIR, folder)
                                    
                                    # Try to delete with retries
                                    max_retries = 3
                                    for attempt in range(max_retries):
                                        try:
                                            # Force garbage collection to release file handles
                                            gc.collect()
                                            
                                            # Try to delete the folder
                                            shutil.rmtree(ext_folder)
                                            
                                            self.load_extensions()
                                            self.browser.load_extensions()
                                            QMessageBox.information(self, "Успех", "Расширение удалено!")
                                            return
                                        except PermissionError as e:
                                            if attempt < max_retries - 1:
                                                # Wait a bit and try again
                                                time.sleep(0.5)
                                            else:
                                                # Final attempt failed
                                                QMessageBox.warning(self, "Ошибка удаления", 
                                                    f"Не удалось удалить расширение.\n\n"
                                                    f"Файлы расширения используются браузером.\n"
                                                    f"Пожалуйста, перезапустите браузер и попробуйте снова.")
                                                return
                                    break
                        except Exception as e:
                            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
                            return

class ChromeTabBar(QTabBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDrawBase(False)
        self.setExpanding(False)
        self.setMovable(True)
        self.setTabsClosable(True)
        self.setStyleSheet("""
            QTabBar {
                background-color: #202124;
                border: none;
            }
            QTabBar::tab {
                background-color: #35363a;
                color: #9aa0a6;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 16px;
                margin-right: 1px;
                min-width: 120px;
                max-width: 240px;
                font-size: 13px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #202124;
            }
            QTabBar::tab:hover:!selected {
                background-color: #3c4043;
                color: #e8eaed;
            }
            QTabBar::close-button {
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDRMNCA4TDEyIDEyIiBzdHJva2U9IiM5YWEwYTYiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIi8+Cjwvc3ZnPgo=);
                subcontrol-position: right;
                margin: 4px;
            }
            QTabBar::close-button:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }
        """)

class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setFixedHeight(40)
        self.setStyleSheet("background-color: #202124;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(0)
        
        # App icon and title
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setStyleSheet("margin-left: 8px; margin-right: 8px;")
        layout.addWidget(self.icon_label)
        
        # Tab bar
        self.tab_bar = ChromeTabBar(self)
        layout.addWidget(self.tab_bar, 1)
        
        # New tab button
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(32, 32)
        self.new_tab_btn.setCursor(Qt.PointingHandCursor)
        self.new_tab_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9aa0a6;
                font-size: 20px;
                font-weight: 300;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #3c4043;
                color: #e8eaed;
            }
        """)
        layout.addWidget(self.new_tab_btn)
        
        layout.addStretch()
        
        # Window controls
        self.minimize_btn = QPushButton("−")
        self.minimize_btn.setFixedSize(46, 40)
        self.minimize_btn.setCursor(Qt.PointingHandCursor)
        self.minimize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9aa0a6;
                font-size: 20px;
                font-weight: 300;
            }
            QPushButton:hover {
                background-color: #3c4043;
                color: #e8eaed;
            }
        """)
        self.minimize_btn.clicked.connect(self.minimize_window)
        layout.addWidget(self.minimize_btn)
        
        self.maximize_btn = QPushButton("□")
        self.maximize_btn.setFixedSize(46, 40)
        self.maximize_btn.setCursor(Qt.PointingHandCursor)
        self.maximize_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9aa0a6;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3c4043;
                color: #e8eaed;
            }
        """)
        self.maximize_btn.clicked.connect(self.maximize_window)
        layout.addWidget(self.maximize_btn)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(46, 40)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #9aa0a6;
                font-size: 24px;
                font-weight: 300;
            }
            QPushButton:hover {
                background-color: #e81123;
                color: white;
            }
        """)
        self.close_btn.clicked.connect(self.close_window)
        layout.addWidget(self.close_btn)
        
        self.drag_position = None
    
    def minimize_window(self):
        self.parent_window.showMinimized()
    
    def maximize_window(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.maximize_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.maximize_btn.setText("❐")
    
    def close_window(self):
        self.parent_window.close()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent_window.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        self.drag_position = None

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flykit Browser")
        self.setWindowIcon(QIcon("https://cdn.itrypro.ru/flkt-ico.png"))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.resize(1280, 860)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBar(self.title_bar.tab_bar)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background-color: white;
            }
        """)
        
        self.title_bar.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.title_bar.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.title_bar.tab_bar.currentChanged.connect(self.tab_changed)
        
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
                border: none;
                border-bottom: 1px solid #e8eaed;
                spacing: 4px;
                padding: 12px 16px;
                min-height: 56px;
            }
            QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 20px;
                padding: 8px;
                margin: 0px 2px;
                color: #5f6368;
                font-size: 20px;
                min-width: 40px;
                min-height: 40px;
            }
            QToolButton:hover {
                background-color: #f1f3f4;
                color: #202124;
            }
            QToolButton:pressed {
                background-color: #e8eaed;
            }
        """)
        self.addToolBar(toolbar)

        back_action = QAction("←", self)
        back_action.triggered.connect(self.browser_back)
        toolbar.addAction(back_action)

        forward_action = QAction("→", self)
        forward_action.triggered.connect(self.browser_forward)
        toolbar.addAction(forward_action)

        reload_action = QAction("⟳", self)
        reload_action.triggered.connect(self.browser_reload)
        toolbar.addAction(reload_action)

        toolbar.addSeparator()

        self.urlbar = QLineEdit()
        self.urlbar.setPlaceholderText("Поиск в Google или введите URL")
        self.urlbar.setMinimumHeight(44)
        self.urlbar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e8eaed;
                border-radius: 22px;
                padding: 0px 20px;
                background-color: white;
                font-size: 14px;
                color: #202124;
                font-family: 'Segoe UI', Arial, sans-serif;
                selection-background-color: #d2e3fc;
            }
            QLineEdit:hover {
                border-color: #dadce0;
            }
            QLineEdit:focus {
                border: 2px solid #1a73e8;
                padding: 0px 19px;
                background-color: white;
            }
        """)
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.urlbar)

        toolbar.addSeparator()

        extensions_action = QAction("⋮", self)
        extensions_action.triggered.connect(self.show_extensions_manager)
        toolbar.addAction(extensions_action)

        self.current_browser = None
        
        main_layout.addWidget(toolbar)
        main_layout.addWidget(self.tab_widget)

        self.profile = QWebEngineProfile.defaultProfile()
        self.add_new_tab()

        self.profile.downloadRequested.connect(self.handle_download)
        self.load_extensions()
    
    def add_new_tab(self, url=None):
        browser = QWebEngineView()
        
        if url is None:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
            url = settings.get("homepage", "https://www.fly.itrypro.ru/alp/index.html")
        
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda q: self.update_urlbar(q) if browser == self.current_browser else None)
        browser.titleChanged.connect(lambda title: self.update_tab_title(browser, title))
        
        index = self.tab_widget.addTab(browser, "Новая вкладка")
        self.tab_widget.setCurrentIndex(index)
        self.current_browser = browser
        
        return browser
    
    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            widget = self.tab_widget.widget(index)
            self.tab_widget.removeTab(index)
            widget.deleteLater()
        else:
            self.close()
    
    def tab_changed(self, index):
        if index >= 0:
            self.current_browser = self.tab_widget.widget(index)
            if self.current_browser:
                self.update_urlbar(self.current_browser.url())
    
    def update_tab_title(self, browser, title):
        index = self.tab_widget.indexOf(browser)
        if index >= 0:
            # Truncate long titles
            if len(title) > 20:
                title = title[:20] + "..."
            self.tab_widget.setTabText(index, title)

    def browser_back(self):
        if self.current_browser:
            self.current_browser.back()
    
    def browser_forward(self):
        if self.current_browser:
            self.current_browser.forward()
    
    def browser_reload(self):
        if self.current_browser:
            self.current_browser.reload()

    def handle_download(self, download):
        file_path = download.path()
        if file_path.endswith('.ebx'):
            download.accept()
            download.finished.connect(lambda: self.install_extension(download.path()))
        else:
            download.accept()
    
    def install_extension(self, ebx_path):
        try:
            temp_dir = os.path.join(EXTENSIONS_DIR, "temp_extract")
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(ebx_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            manifest_path = os.path.join(temp_dir, "manifest.json")
            if not os.path.exists(manifest_path):
                QMessageBox.warning(self, "Ошибка", "Неверный формат расширения: отсутствует manifest.json")
                shutil.rmtree(temp_dir)
                return
            
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            
            ext_name = manifest.get("name", "Unknown Extension")
            ext_id = manifest.get("id", ext_name.lower().replace(" ", "_"))
            
            final_dir = os.path.join(EXTENSIONS_DIR, ext_id)
            if os.path.exists(final_dir):
                reply = QMessageBox.question(self, "Расширение установлено", 
                                            f"Расширение '{ext_name}' уже установлено. Удалить его?",
                                            QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    try:
                        shutil.rmtree(final_dir)
                        QMessageBox.information(self, "Успех", "Расширение удалено!")
                    except PermissionError:
                        QMessageBox.warning(self, "Ошибка", "Не удалось удалить расширение. Закройте браузер и попробуйте снова.")
                shutil.rmtree(temp_dir)
                return
            
            icon_path = os.path.join(temp_dir, "icons", "icon48.png")
            if not os.path.exists(icon_path):
                icon_path = None
            
            dialog = ExtensionInstallDialog(ext_name, icon_path, self)
            if dialog.exec_() == QDialog.Accepted:
                shutil.move(temp_dir, final_dir)
                QMessageBox.information(self, "Успех", f"Расширение '{ext_name}' установлено!")
                self.load_extensions()
            else:
                shutil.rmtree(temp_dir)
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить расширение: {str(e)}")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    
    def show_extensions_manager(self):
        manager = ExtensionsManager(self, self)
        manager.exec_()
    
    def navigate_to_url(self):
        if not self.current_browser:
            return
            
        url = self.urlbar.text()

        if url.startswith("flykit:"):
            redirect = url.split(":", 1)[1]
            self.current_browser.setUrl(QUrl(f"https://flykit.itrypro.ru/?data={redirect}"))
            return

        if url.startswith("ut://"):
            code = url.split("://", 1)[1]
            self.current_browser.setHtml(f"<h1>Ошибка {code}</h1><p>Служебная страница Flykit</p>")
            return

        if not url.startswith("http"):
            url = "https://" + url

        self.current_browser.setUrl(QUrl(url))

    def update_urlbar(self, q):
        self.urlbar.setText(q.toString())

    def load_extensions(self):
        for ext_name in os.listdir(EXTENSIONS_DIR):
            ext_path = os.path.join(EXTENSIONS_DIR, ext_name)
            if os.path.isdir(ext_path) and ext_name != "temp_extract":
                manifest_path = os.path.join(ext_path, "manifest.json")
                if os.path.exists(manifest_path):
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = json.load(f)
                    
                    content_js_path = os.path.join(ext_path, "content.js")
                    if os.path.exists(content_js_path):
                        with open(content_js_path, "r", encoding="utf-8") as f:
                            content_js = f.read()
                        
                        script = QWebEngineScript()
                        script.setName(manifest.get("name", ext_name))
                        script.setSourceCode(content_js)
                        script.setInjectionPoint(QWebEngineScript.DocumentReady)
                        script.setWorldId(QWebEngineScript.MainWorld)
                        script.setRunsOnSubFrames(True)
                        
                        self.profile.scripts().insert(script)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    app.setFont(QFont("Segoe UI", 10))
    
    window = Browser()
    window.show()
    sys.exit(app.exec_())
