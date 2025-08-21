import sys
import subprocess
from datetime import date
from pathlib import Path

from PyQt6.QtWidgets import ( # type: ignore
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QScrollArea, QGroupBox, QRadioButton, QPushButton,
    QLabel, QLineEdit, QSpinBox, QCheckBox, QTextEdit, QColorDialog,
    QMessageBox, QButtonGroup, QTabWidget, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal # type: ignore
from PyQt6.QtGui import QFont, QColor # type: ignore 

class ColorButton(QPushButton):
    colorChanged = pyqtSignal(str)
    
    def __init__(self, initial_color="#000000"):
        super().__init__() 
        self.color = initial_color
        self.setFixedSize(60, 25)
        self.update_color() 
        self.clicked.connect(self.choose_color)
    
    def update_color(self): 
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: 1px solid #ccc;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
        """) 
    
    def choose_color(self):
        color = QColorDialog.getColor(QColor(self.color), self, "Choose Color")
        if color.isValid():
            self.color = color.name()
            self.update_color()
            self.colorChanged.emit(self.color)
    
    def set_color(self, color):
        self.color = color
        self.update_color()


class TimeVisualizerGUI(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.setWindowTitle("Count")
        self.setGeometry(100, 100, 650, 700)
        self.script_path = Path(__file__).parent / "script.py"
        
        self.setup_variables()
        self.init_ui()
        self.update_command_preview()
        self.update_cron_command()

        self.center_on_screen()
    
    def setup_variables(self):
        self.mode = "day"
        self.show_percentage = True
        self.preview_only = False
        self.no_cleanup = False
        self.bg_color = "#000000"
        self.filled_color = "#ffffff"
        self.hollow_color = "#ffffff"
        self.percentage_color = "#ffffff"
        self.dob = "2010-12-22"
        self.life_expectancy = 90
        
        self.cron_frequency = "hourly"
        self.cron_minute = 0
        self.cron_hour = 8
        self.cron_day = 1
        self.cron_weekday = 1
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.tab_widget = QTabWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(self.tab_widget)

        self.create_main_tab()

        self.create_cron_tab()
    
    def create_main_tab(self):
        main_tab = QWidget()
        self.tab_widget.addTab(main_tab, "Configuration")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded) 

        content_widget = QWidget()
        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(main_tab)
        main_layout.addWidget(scroll)

        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.addWidget(self.create_mode_group())
        layout.addWidget(self.create_colors_group())
        layout.addWidget(self.create_lifetime_group())
        layout.addWidget(self.create_options_group())
        layout.addWidget(self.create_command_group())
        layout.addWidget(self.create_buttons())
        layout.addStretch()
    
    def create_cron_tab(self):
        cron_tab = QWidget()
        self.tab_widget.addTab(cron_tab, "Cron")
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(cron_tab)
        main_layout.addWidget(scroll)
        
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)
        layout.addWidget(self.create_cron_frequency_group())
        layout.addWidget(self.create_cron_timing_group())
        layout.addWidget(self.create_cron_command_group())
        layout.addWidget(self.create_cron_buttons())
        layout.addStretch()
    
    def create_cron_frequency_group(self):
        group = QGroupBox("Schedule Frequency")
        layout = QVBoxLayout(group)
        
        self.cron_frequency_group = QButtonGroup()
        
        frequencies = [
            ("every_minute", "Every minute"),
            ("every_5min", "Every 5 minutes"),
            ("every_15min", "Every 15 minutes"),
            ("every_30min", "Every 30 minutes"),
            ("hourly", "Every hour"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
            ("monthly", "Monthly")
        ]
        
        for freq_key, freq_desc in frequencies:
            radio = QRadioButton(freq_desc)
            radio.setObjectName(freq_key)
            if freq_key == "hourly":
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, key=freq_key: self.on_cron_frequency_changed(checked, key))
            layout.addWidget(radio)
            self.cron_frequency_group.addButton(radio)
        
        return group
    
    def create_cron_timing_group(self):
        group = QGroupBox("Timing Settings")
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Minute (0-59):"), 0, 0)
        self.cron_minute_spin = QSpinBox()
        self.cron_minute_spin.setRange(0, 59)
        self.cron_minute_spin.setValue(self.cron_minute)
        self.cron_minute_spin.valueChanged.connect(self.on_cron_minute_changed)
        layout.addWidget(self.cron_minute_spin, 0, 1)
        
        layout.addWidget(QLabel("Hour (0-23):"), 1, 0)
        self.cron_hour_spin = QSpinBox()
        self.cron_hour_spin.setRange(0, 23)
        self.cron_hour_spin.setValue(self.cron_hour)
        self.cron_hour_spin.valueChanged.connect(self.on_cron_hour_changed)
        layout.addWidget(self.cron_hour_spin, 1, 1)
        
        layout.addWidget(QLabel("Day of month (1-31):"), 2, 0)
        self.cron_day_spin = QSpinBox()
        self.cron_day_spin.setRange(1, 31)
        self.cron_day_spin.setValue(self.cron_day)
        self.cron_day_spin.valueChanged.connect(self.on_cron_day_changed)
        layout.addWidget(self.cron_day_spin, 2, 1)
        
        layout.addWidget(QLabel("Weekday:"), 3, 0)
        self.cron_weekday_combo = QComboBox()
        weekdays = [
            "Monday", "Tuesday", "Wednesday", "Thursday", 
            "Friday", "Saturday", "Sunday"
        ]
        self.cron_weekday_combo.addItems(weekdays)
        self.cron_weekday_combo.setCurrentIndex(self.cron_weekday)
        self.cron_weekday_combo.currentIndexChanged.connect(self.on_cron_weekday_changed)
        layout.addWidget(self.cron_weekday_combo, 3, 1)
        
        self.cron_timing_widgets = {
            'minute': (QLabel("Minute (0-59):"), self.cron_minute_spin),
            'hour': (QLabel("Hour (0-23):"), self.cron_hour_spin),
            'day': (QLabel("Day of month (1-31):"), self.cron_day_spin),
            'weekday': (QLabel("Weekday:"), self.cron_weekday_combo)
        }
        
        self.cron_minute_label = layout.itemAtPosition(0, 0).widget()
        self.cron_hour_label = layout.itemAtPosition(1, 0).widget()
        self.cron_day_label = layout.itemAtPosition(2, 0).widget()
        self.cron_weekday_label = layout.itemAtPosition(3, 0).widget()
        
        self.update_cron_timing_visibility()
        
        return group
    
    def create_cron_command_group(self):
        group = QGroupBox("Generated Cron Command")
        layout = QVBoxLayout(group)
        
        layout.addWidget(QLabel("Cron line to add to crontab:"))
        self.cron_command_text = QTextEdit()
        self.cron_command_text.setMaximumHeight(60)
        self.cron_command_text.setReadOnly(True)
        self.cron_command_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.cron_command_text)
        
        layout.addWidget(QLabel("To install, run: crontab -e"))
        layout.addWidget(QLabel("Then add the line above to your crontab file."))
        
        return group
    
    def create_cron_buttons(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        copy_cron_btn = QPushButton("Copy Cron Command")
        copy_cron_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                color: white;
            }
        """)
        copy_cron_btn.clicked.connect(self.copy_cron_command)
        layout.addWidget(copy_cron_btn)
        
        test_cron_btn = QPushButton("Test Command")
        test_cron_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                color: white;
            }
        """)
        test_cron_btn.clicked.connect(self.test_cron_command)
        layout.addWidget(test_cron_btn)
        
        layout.addStretch()
        return widget
    
    def create_mode_group(self):
        group = QGroupBox("Visualization Mode")
        layout = QGridLayout(group)
        
        self.mode_button_group = QButtonGroup()
        
        modes = [
            ("day", "Day (hours)"),
            ("day-5min", "Day (5-minute chunks)"),
            ("month-day", "Month (days)"),
            ("month-hours", "Month (hours)"),
            ("year-months", "Year (months)"),
            ("year-days", "Year (days)"),
            ("lifetime-years", "Lifetime (years)"),
            ("lifetime-months", "Lifetime (months)")
        ]
        
        for i, (mode_key, mode_desc) in enumerate(modes):
            radio = QRadioButton(mode_desc)
            radio.setObjectName(mode_key)
            if mode_key == "day":
                radio.setChecked(True)
            radio.toggled.connect(lambda checked, key=mode_key: self.on_mode_changed(checked, key))
            
            row = i // 2
            col = i % 2
            layout.addWidget(radio, row, col)
            self.mode_button_group.addButton(radio)
        
        return group
    
    def create_colors_group(self):
        group = QGroupBox("Colors")
        layout = QGridLayout(group)
        
        color_configs = [
            ("Background:", "bg_color", self.bg_color),
            ("Filled Circles:", "filled_color", self.filled_color),
            ("Hollow Circles:", "hollow_color", self.hollow_color),
            ("Percentage Text:", "percentage_color", self.percentage_color)
        ]
        
        self.color_buttons = {}
        self.color_entries = {}
        
        for i, (label_text, attr_name, initial_color) in enumerate(color_configs):
            label = QLabel(label_text)
            layout.addWidget(label, i, 0)
            
            color_btn = ColorButton(initial_color)
            color_btn.colorChanged.connect(lambda color, attr=attr_name: self.on_color_changed(attr, color))
            layout.addWidget(color_btn, i, 1)
            self.color_buttons[attr_name] = color_btn
            
            entry = QLineEdit(initial_color)
            entry.setMaximumWidth(80)
            entry.textChanged.connect(lambda text, attr=attr_name: self.on_color_entry_changed(attr, text))
            layout.addWidget(entry, i, 2)
            self.color_entries[attr_name] = entry
        
        return group 
    
    def create_lifetime_group(self):
        group = QGroupBox("Lifetime Setting")
        layout = QGridLayout(group)

        layout.addWidget(QLabel("Date of Birth (YYYY-MM-DD):"), 0, 0)
        self.dob_entry = QLineEdit(self.dob)
        self.dob_entry.textChanged.connect(self.on_dob_changed)
        layout.addWidget(self.dob_entry, 0, 1)
        
        layout.addWidget(QLabel("Life Expectancy (years):"), 1, 0)
        self.life_expectancy_spin = QSpinBox()
        self.life_expectancy_spin.setRange(50, 120)
        self.life_expectancy_spin.setValue(self.life_expectancy)
        self.life_expectancy_spin.valueChanged.connect(self.on_life_expectancy_changed)
        layout.addWidget(self.life_expectancy_spin, 1, 1)
        
        return group
    
    def create_options_group(self):
        group = QGroupBox("Options")
        layout = QVBoxLayout(group)
        
        self.show_percentage_cb = QCheckBox("Show Percentage")
        self.show_percentage_cb.setChecked(self.show_percentage)
        self.show_percentage_cb.toggled.connect(self.on_show_percentage_changed)
        layout.addWidget(self.show_percentage_cb)
        
        self.preview_cb = QCheckBox("Preview Only (don't set wallpaper)")
        self.preview_cb.setChecked(self.preview_only)
        self.preview_cb.toggled.connect(self.on_preview_changed)
        layout.addWidget(self.preview_cb)

        self.no_cleanup_cb = QCheckBox("Keep Old Wallpapers")
        self.no_cleanup_cb.setChecked(self.no_cleanup)
        self.no_cleanup_cb.toggled.connect(self.on_no_cleanup_changed)
        layout.addWidget(self.no_cleanup_cb)
        
        return group
    
    def create_command_group(self):
        group = QGroupBox("Generated Command")
        layout = QVBoxLayout(group)
        
        self.command_text = QTextEdit()
        self.command_text.setMaximumHeight(100)
        self.command_text.setReadOnly(True)
        self.command_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.command_text)
        
        return group
    
    def create_buttons(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        run_btn = QPushButton("Run Script")
        run_btn.setStyleSheet("""
            QPushButton { 
                background-color: #ffffff;
                color: black;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                color: white;
            }
        """)
        run_btn.clicked.connect(self.run_script)
        layout.addWidget(run_btn) 
        
        copy_btn = QPushButton("Copy Command")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                color: white;
            }
        """)
        copy_btn.clicked.connect(self.copy_command)
        layout.addWidget(copy_btn)
        
        reset_btn = QPushButton("Reset to Defaults") 
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: black;
                border: none;
                padding: 4px 8px; 
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
                color: white;
            }
        """)
        reset_btn.clicked.connect(self.reset_defaults)
        layout.addWidget(reset_btn)
        
        layout.addStretch()
        return widget
    
    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        window = self.geometry()
        self.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )

    def on_mode_changed(self, checked, mode_key): 
        if checked:
            self.mode = mode_key
            self.update_command_preview()
            self.update_cron_command()
    
    def on_color_changed(self, attr_name, color):
        setattr(self, attr_name, color)
        self.color_entries[attr_name].setText(color)
        self.update_command_preview()
        self.update_cron_command()
    
    def on_color_entry_changed(self, attr_name, text):
        setattr(self, attr_name, text)
        if text.startswith("#") and len(text) == 7:
            self.color_buttons[attr_name].set_color(text)
        self.update_command_preview()
        self.update_cron_command()
    
    def on_dob_changed(self, text):
        self.dob = text
        self.update_command_preview()
        self.update_cron_command()
    
    def on_life_expectancy_changed(self, value):
        self.life_expectancy = value
        self.update_command_preview()
        self.update_cron_command()
    
    def on_show_percentage_changed(self, checked):
        self.show_percentage = checked
        self.update_command_preview()
        self.update_cron_command()
    
    def on_preview_changed(self, checked):
        self.preview_only = checked
        self.update_command_preview()
        self.update_cron_command()
    
    def on_no_cleanup_changed(self, checked):
        self.no_cleanup = checked
        self.update_command_preview()
        self.update_cron_command()
    
    # Cron event handlers
    def on_cron_frequency_changed(self, checked, freq_key):
        if checked:
            self.cron_frequency = freq_key
            self.update_cron_timing_visibility()
            self.update_cron_command()
    
    def on_cron_minute_changed(self, value):
        self.cron_minute = value
        self.update_cron_command()
    
    def on_cron_hour_changed(self, value):
        self.cron_hour = value
        self.update_cron_command()
    
    def on_cron_day_changed(self, value):
        self.cron_day = value
        self.update_cron_command()
    
    def on_cron_weekday_changed(self, index):
        self.cron_weekday = index
        self.update_cron_command()
    
    def update_cron_timing_visibility(self):
        freq = self.cron_frequency

        minute_enabled = freq not in ['every_minute']
        self.cron_minute_label.setEnabled(minute_enabled)
        self.cron_minute_spin.setEnabled(minute_enabled)
        
        hour_enabled = freq in ['daily', 'weekly', 'monthly']
        self.cron_hour_label.setEnabled(hour_enabled)
        self.cron_hour_spin.setEnabled(hour_enabled)
        
        day_enabled = freq == 'monthly'
        self.cron_day_label.setEnabled(day_enabled)
        self.cron_day_spin.setEnabled(day_enabled)

        weekday_enabled = freq == 'weekly'
        self.cron_weekday_label.setEnabled(weekday_enabled)
        self.cron_weekday_combo.setEnabled(weekday_enabled)
    
    def build_command(self):
        if not self.script_path.exists():
            return f"# Error: script.py not found at {self.script_path}"
        
        cmd_parts = [sys.executable, str(self.script_path)]
        
        cmd_parts.extend(["--mode", self.mode])
        
        if self.bg_color != "#000000":
            cmd_parts.extend(["--bg-color", '"'+self.bg_color+'"'])

        if self.filled_color != "#ffffff":
            cmd_parts.extend(["--filled-color", '"'+self.filled_color+'"']) 

        if self.hollow_color != "#ffffff":
            cmd_parts.extend(["--hollow-color", '"'+self.hollow_color+'"'])

        if self.percentage_color != "#ffffff":
            cmd_parts.extend(["--percentage-color", '"'+self.percentage_color+'"'])

        if self.show_percentage:
            cmd_parts.append("--show-percentage")
        
        if self.preview_only:
            cmd_parts.append("--preview")
        
        if self.no_cleanup:
            cmd_parts.append("--no-cleanup")

        if self.mode.startswith("lifetime"):
            if self.dob != "1990-01-01":  
                cmd_parts.extend(["--dob", self.dob])
            
            if self.life_expectancy != 90: 
                cmd_parts.extend(["--life-expectancy", str(self.life_expectancy)])
        
        return " ".join(cmd_parts)
    
    def build_cron_command(self):
        base_command = self.build_command()
        
        if "--preview" in base_command:
            base_command = base_command.replace("--preview", "").strip()
            base_command = " ".join(base_command.split())
        
        freq = self.cron_frequency
        
        if freq == "every_minute":
            cron_time = "* * * * *"
        elif freq == "every_5min":
            cron_time = "*/5 * * * *"
        elif freq == "every_15min":
            cron_time = "*/15 * * * *"
        elif freq == "every_30min":
            cron_time = "*/30 * * * *"
        elif freq == "hourly":
            cron_time = f"{self.cron_minute} * * * *"
        elif freq == "daily":
            cron_time = f"{self.cron_minute} {self.cron_hour} * * *"
        elif freq == "weekly":
            cron_weekday = (self.cron_weekday + 1) % 7
            cron_time = f"{self.cron_minute} {self.cron_hour} * * {cron_weekday}"
        elif freq == "monthly":
            cron_time = f"{self.cron_minute} {self.cron_hour} {self.cron_day} * *"
        else:
            cron_time = "0 * * * *" 

        log_redirect = f">> /tmp/time_visualizer.log 2>&1"
        
        return f"{cron_time} {base_command} {log_redirect}"
    
    def update_command_preview(self):
        command = self.build_command()
        self.command_text.setPlainText(command)
    
    def update_cron_command(self):
        if hasattr(self, 'cron_command_text'):
            cron_command = self.build_cron_command()
            self.cron_command_text.setPlainText(cron_command)
    
    def validate_settings(self):
        if self.mode.startswith("lifetime"):
            try:
                dob_parts = self.dob.split("-")
                if len(dob_parts) != 3:
                    raise ValueError()
                year, month, day = map(int, dob_parts)
                date(year, month, day)  
            except ValueError:
                return "Invalid date of birth format. Please use YYYY-MM-DD."
        
        colors = [
            ("Background", self.bg_color),
            ("Filled", self.filled_color),
            ("Hollow", self.hollow_color),
            ("Percentage", self.percentage_color)
        ]
        
        for color_name, color in colors:
            color = color.strip()
            if not color.startswith("#") or len(color) != 7:
                return f"Invalid {color_name} color format. Please use #RRGGBB format."
        
        return None 
    
    def run_script(self):
        error = self.validate_settings()
        if error:
            QMessageBox.critical(self, "Invalid Settings", error)
            return
        
        if not self.script_path.exists():
            QMessageBox.critical(self, "Script Not Found", 
                               f"Could not find script.py at {self.script_path}")
            return
        
        command = self.build_command()
        
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Success", 
                                      f"Script completed successfully!\n\nOutput:\n{result.stdout}")
            else:
                QMessageBox.critical(self, "Error", 
                                   f"Script failed with error:\n{result.stderr}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to run script: {str(e)}")
    
    def copy_command(self):
        command = self.build_command()
        clipboard = QApplication.clipboard()
        clipboard.setText(command)
        QMessageBox.information(self, "Copied", "Command copied to clipboard!")
    
    def copy_cron_command(self):
        cron_command = self.build_cron_command()
        clipboard = QApplication.clipboard()
        clipboard.setText(cron_command)
        QMessageBox.information(self, "Copied", "Cron command copied to clipboard!\n\n" +
                              "To install:\n1. Run 'crontab -e'\n2. Paste the line\n3. Save and exit")
    
    def test_cron_command(self):
        error = self.validate_settings()
        if error:
            QMessageBox.critical(self, "Invalid Settings", error)
            return
        
        if not self.script_path.exists():
            QMessageBox.critical(self, "Script Not Found", 
                               f"Could not find script.py at {self.script_path}")
            return
        
        base_command = self.build_command()
        if "--preview" in base_command:
            base_command = base_command.replace("--preview", "").strip()
            base_command = " ".join(base_command.split())
        
        try:
            result = subprocess.run(base_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                QMessageBox.information(self, "Test Successful", 
                                      f"Cron command test completed successfully!\n\nOutput:\n{result.stdout}")
            else:
                QMessageBox.critical(self, "Test Failed", 
                                   f"Cron command test failed with error:\n{result.stderr}")
                
        except Exception as e:
            QMessageBox.critical(self, "Test Error", f"Failed to test cron command: {str(e)}")
    
    def reset_defaults(self):
        self.mode = "day"
        self.show_percentage = True
        self.preview_only = False
        self.no_cleanup = False
        self.bg_color = "#000000"
        self.filled_color = "#ffffff"
        self.hollow_color = "#ffffff"
        self.percentage_color = "#ffffff"
        self.dob = "1990-01-01"
        self.life_expectancy = 90

        for button in self.mode_button_group.buttons():
            if button.objectName() == "day":
                button.setChecked(True)
            else:
                button.setChecked(False)
        
        self.show_percentage_cb.setChecked(True)
        self.preview_cb.setChecked(False)
        self.no_cleanup_cb.setChecked(False)
        
        colors = {
            "bg_color": "#000000",
            "filled_color": "#ffffff",
            "hollow_color": "#ffffff",
            "percentage_color": "#ffffff"
        }
        
        for attr_name, color in colors.items():
            self.color_buttons[attr_name].set_color(color)
            self.color_entries[attr_name].setText(color)
        
        self.dob_entry.setText("1990-01-01")
        self.life_expectancy_spin.setValue(90)

        self.cron_frequency = "hourly"
        self.cron_minute = 0
        self.cron_hour = 8
        self.cron_day = 1
        self.cron_weekday = 1
        
        for button in self.cron_frequency_group.buttons():
            if button.objectName() == "hourly":
                button.setChecked(True)
            else:
                button.setChecked(False)
        
        self.cron_minute_spin.setValue(0)
        self.cron_hour_spin.setValue(8)
        self.cron_day_spin.setValue(1)
        self.cron_weekday_combo.setCurrentIndex(1)
        
        self.update_cron_timing_visibility()
        self.update_command_preview()
        self.update_cron_command()


def main():
    app = QApplication(sys.argv)

    app.setStyle('Fusion')
    window = TimeVisualizerGUI()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
