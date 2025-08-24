# -*- coding: utf-8 -*-
import sys
import os
import json
import requests
import math
import time
import random # For effects
from datetime import datetime # For timestamps
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QComboBox, QColorDialog, QListWidget, QListWidgetItem,
    QHBoxLayout, QTabWidget, QSlider, QMessageBox, QSplitter,
    QFrame, QGridLayout, QInputDialog, QStyle, QGroupBox,
    QMainWindow, QDialog, QLineEdit, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QStatusBar
)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont, QAction, QCursor
from PyQt6.QtCore import Qt, QSize, QTimer
from phue import Bridge, PhueRegistrationException

# --- Internationalization (i18n) ---
TRANSLATIONS = {
    "sv": {
        # General
        "app_title": "Enhanced Hue Controller",
        "app_title_connected": "Hue Controller - {bridge_name}",
        "status_connected": "Ansluten till: {bridge_name}",
        "welcome_title": "Välkommen",
        "welcome_text": "Ingen brygga är konfigurerad.",
        "error_title": "Fel",
        "info_title": "Info",
        "confirm_title": "Bekräfta",
        "warning_title": "Varning",

        # Top Bar
        "bridge": "Brygga:",
        "add_bridge": "Lägg till",
        "remove_bridge": "Ta bort",
        "reload": "Ladda om",

        # Menus
        "file": "&Arkiv",
        "exit": "A&vsluta",
        "view": "&Visa",
        "theme": "&Tema",
        "language": "&Språk",
        "help": "&Hjälp",
        "about": "&Om...",
        "about_text": "Hue Controller v1.4",

        # Tabs
        "groups": "Grupper",
        "lights": "Lampor",
        "scenes": "Scener",
        "sensors": "Sensorer",
        "effects": "Effekter",
        "other_scenes": "Övriga Scener",

        # Control Panel
        "select_device": "Välj en enhet",
        "power_on_off": "På/Av",
        "power_on": "Tänd",
        "power_off": "Släck",
        "brightness": "Ljusstyrka:",
        "change_color": "Ändra Färg",
        "random_color_tooltip": "Slumpmässig färg",
        "favorite_colors": "Favoritfärger",
        "favorite_tooltip": "Vänsterklicka för att använda, högerklicka för att spara.",
        "information": "Information",
        "model": "Modell: {model}",
        "type": "Typ: {type}",

        # Effects Panel
        "dynamic_effects": "Dynamiska Effekter",
        "speed": "Hastighet:",
        "speed_tooltip": "Justerar hastigheten på anpassade effekter.",
        "stop_all_effects": "Stoppa Alla Effekter",

        # Dialogs
        "add_bridge_title": "Lägg till Brygga",
        "add_bridge_prompt": "Ange Hue Bridge IP-adress:",
        "press_button_title": "Tryck på knappen",
        "press_button_prompt": "Tryck på knappen på bryggan ({ip}) och klicka OK.",
        "pair_fail_prompt": "Kunde inte parkoppla med {ip}:\n{e}",
        "remove_bridge_prompt": "Ta bort {ip}?",
        "no_name_warning": "Gruppen måste ha ett namn.",
        "create_group_fail": "Kunde inte skapa grupp:\n{e}",
        "edit_group_fail": "Kunde inte redigera grupp:\n{e}",
        "delete_group_prompt": "Ta bort gruppen '{group_name}'?",
        "delete_group_fail": "Kunde inte ta bort grupp:\n{e}",
        "save_scene_title": "Spara Scen",
        "save_scene_prompt": "Ange namn för ny scen för gruppen '{group_name}':",
        "save_scene_success": "Scenen '{scene_name}' har sparats.",
        "save_scene_fail": "Kunde inte spara scen:\n{e}",

        # Context Menus
        "show_info": "Visa Info...",
        "create_new_group": "Skapa ny grupp...",
        "edit_group": "Redigera grupp...",
        "save_as_scene": "Spara som Scen...",
        "delete_group": "Ta bort grupp...",

        # Group Editor
        "edit_group_title": "Redigera Grupp",
        "create_group_title": "Skapa Ny Grupp",
        "group_name": "Gruppnamn:",
        "select_lights": "Välj lampor:",
    },
    "en": {
        # General
        "app_title": "Enhanced Hue Controller",
        "app_title_connected": "Hue Controller - {bridge_name}",
        "status_connected": "Connected to: {bridge_name}",
        "welcome_title": "Welcome",
        "welcome_text": "No bridge is configured.",
        "error_title": "Error",
        "info_title": "Info",
        "confirm_title": "Confirm",
        "warning_title": "Warning",

        # Top Bar
        "bridge": "Bridge:",
        "add_bridge": "Add",
        "remove_bridge": "Remove",
        "reload": "Reload",

        # Menus
        "file": "&File",
        "exit": "E&xit",
        "view": "&View",
        "theme": "&Theme",
        "language": "&Language",
        "help": "&Help",
        "about": "&About...",
        "about_text": "Hue Controller v1.4",

        # Tabs
        "groups": "Groups",
        "lights": "Lights",
        "scenes": "Scenes",
        "sensors": "Sensors",
        "effects": "Effects",
        "other_scenes": "Other Scenes",

        # Control Panel
        "select_device": "Select a device",
        "power_on_off": "On/Off",
        "power_on": "Turn On",
        "power_off": "Turn Off",
        "brightness": "Brightness:",
        "change_color": "Change Color",
        "random_color_tooltip": "Random color",
        "favorite_colors": "Favorite Colors",
        "favorite_tooltip": "Left-click to apply, right-click to save.",
        "information": "Information",
        "model": "Model: {model}",
        "type": "Type: {type}",

        # Effects Panel
        "dynamic_effects": "Dynamic Effects",
        "speed": "Speed:",
        "speed_tooltip": "Adjusts the speed of custom effects.",
        "stop_all_effects": "Stop All Effects",

        # Dialogs
        "add_bridge_title": "Add Bridge",
        "add_bridge_prompt": "Enter Hue Bridge IP address:",
        "press_button_title": "Press the button",
        "press_button_prompt": "Press the button on the bridge ({ip}) and click OK.",
        "pair_fail_prompt": "Could not pair with {ip}:\n{e}",
        "remove_bridge_prompt": "Remove {ip}?",
        "no_name_warning": "The group must have a name.",
        "create_group_fail": "Could not create group:\n{e}",
        "edit_group_fail": "Could not edit group:\n{e}",
        "delete_group_prompt": "Delete the group '{group_name}'?",
        "delete_group_fail": "Could not delete group:\n{e}",
        "save_scene_title": "Save Scene",
        "save_scene_prompt": "Enter name for new scene for group '{group_name}':",
        "save_scene_success": "Scene '{scene_name}' has been saved.",
        "save_scene_fail": "Could not save scene:\n{e}",

        # Context Menus
        "show_info": "Show Info...",
        "create_new_group": "Create new group...",
        "edit_group": "Edit group...",
        "save_as_scene": "Save as Scene...",
        "delete_group": "Delete group...",

        # Group Editor
        "edit_group_title": "Edit Group",
        "create_group_title": "Create New Group",
        "group_name": "Group name:",
        "select_lights": "Select lights:",
    }
}

# Global language variable
current_language = "sv"

def tr(key, **kwargs):
    """Translate a key using the current language, with optional formatting."""
    # Fallback to Swedish if the current language is missing
    translation = TRANSLATIONS.get(current_language, TRANSLATIONS["sv"]).get(key, key)
    if kwargs:
        try:
            return translation.format(**kwargs)
        except (KeyError, IndexError):
            return key # Return key if formatting fails
    return translation

# --- Settings and Bridge Manager ---
# This class replaces the need for a separate hue_manager.py file
class HueManager:
    """Manages saving/loading of bridge configurations and UI settings."""
    def __init__(self, config_file='hue_bridges.json', settings_file='hue_settings.json'):
        self.config_file = config_file
        self.settings_file = settings_file
        self.bridges = self._load_json(self.config_file, {})
        self.settings = self._load_json(self.settings_file, {})

    def _load_json(self, file, default):
        """Safely loads a JSON file."""
        try:
            if os.path.exists(file):
                with open(file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError):
            return default # Return default value if file is corrupt or unreadable
        return default

    def _save_json(self, file, data):
        """Saves data to a JSON file."""
        try:
            with open(file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except IOError as e:
            print(f"Error saving {file}: {e}")

    def add_bridge(self, ip, username):
        self.bridges[ip] = {'username': username}
        self._save_json(self.config_file, self.bridges)

    def remove_bridge(self, ip):
        if ip in self.bridges:
            del self.bridges[ip]
            self._save_json(self.config_file, self.bridges)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def save_setting(self, key, value):
        self.settings[key] = value
        self._save_json(self.settings_file, self.settings)

# --- Icon Management ---
ICON_DIR = "icons"
DEFAULT_ICON_SIZE = QSize(16, 16)

# Global icon variables
icon_light, icon_group, icon_scene, icon_sensor, icon_bridge, icon_dimmer = (QIcon() for _ in range(6))
icon_refresh, icon_add, icon_remove, icon_on, icon_off, icon_color = (QIcon() for _ in range(6))
icon_effect, icon_theme, icon_info_alt, icon_exit, icon_warning, icon_info = (QIcon() for _ in range(6))
icon_error, icon_edit, icon_save, icon_random = (QIcon() for _ in range(4))

def load_icons(app_style):
    """Loads icons from Qt's standard set for stability."""
    global icon_light, icon_group, icon_scene, icon_sensor, icon_bridge, icon_dimmer, icon_refresh, icon_add, icon_remove
    global icon_on, icon_off, icon_color, icon_effect, icon_theme, icon_info_alt, icon_exit, icon_edit, icon_save, icon_random
    global icon_warning, icon_info, icon_error

    icon_light = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogYesButton)
    icon_group = app_style.standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
    icon_scene = app_style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
    icon_sensor = app_style.standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
    icon_bridge = app_style.standardIcon(QStyle.StandardPixmap.SP_DriveNetIcon)
    icon_dimmer = app_style.standardIcon(QStyle.StandardPixmap.SP_ArrowRight)
    icon_refresh = app_style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload)
    icon_add = app_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder)
    icon_remove = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton)
    icon_on = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton)
    icon_off = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton)
    icon_color = app_style.standardIcon(QStyle.StandardPixmap.SP_DesktopIcon)
    icon_effect = app_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView)
    icon_theme = app_style.standardIcon(QStyle.StandardPixmap.SP_ToolBarHorizontalExtensionButton)
    icon_info_alt = app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
    icon_exit = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogDiscardButton)
    icon_edit = app_style.standardIcon(QStyle.StandardPixmap.SP_FileLinkIcon)
    icon_save = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
    icon_random = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton)
    icon_warning = app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
    icon_info = app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
    icon_error = app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
    print("Icons loaded.")


# --- Qt Style Sheets (Themes) ---
def create_container_styles(bg_light, border, accent_yellow, fg_color, bg_main):
    return f"""
    QGroupBox {{ background-color: {bg_light}; border: 1px solid {border}; border-radius: 4px; margin-top: 10px; padding: 15px 5px 5px 5px; }}
    QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 3px; color: {accent_yellow}; background-color: {bg_light}; border-radius: 3px; }}
    QMenuBar {{ background-color: {bg_light}; color: {fg_color}; border-bottom: 1px solid {border}; }}
    QMenuBar::item {{ background-color: transparent; padding: 4px 8px; }}
    QMenuBar::item:selected {{ background-color: {accent_yellow}; color: {bg_main}; }}
    QMenu {{ background-color: {bg_light}; color: {fg_color}; border: 1px solid {border}; padding: 5px; }}
    QMenu::item:selected {{ background-color: {accent_yellow}; color: {bg_main}; }}
    QMenu::separator {{ height: 1px; background-color: {border}; margin: 4px 0; }}
    """
NORD_DARK_STYLESHEET = """
QWidget { background-color: #2E3440; color: #ECEFF4; font-family: Segoe UI, Arial, sans-serif; font-size: 10pt; }
QPushButton { background-color: #88C0D0; color: #2E3440; border: 1px solid #434C5E; padding: 8px 12px; border-radius: 4px; min-width: 80px; }
QPushButton:hover { background-color: #95c9d9; }
QPushButton:disabled { background-color: #4C566A; color: #434C5E; }
QPushButton#removeButton { background-color: #BF616A; color: #ECEFF4; }
QPushButton#onOffButton[onState="false"] { background-color: #A3BE8C; color: #2E3440; }
QPushButton#onOffButton[onState="true"] { background-color: #BF616A; color: #ECEFF4; }
QPushButton.effectButton:checked { background-color: #EBCB8B; color: #2E3440; }
QPushButton.presetButton { min-width: 40px; padding: 4px; font-size: 8pt; }
QComboBox { background-color: #3B4252; border: 1px solid #434C5E; padding: 5px; border-radius: 3px; }
QComboBox QAbstractItemView { background-color: #3B4252; selection-background-color: #88C0D0; selection-color: #2E3440; }
QTabWidget::pane { border: 1px solid #434C5E; background-color: #3B4252; }
QTabBar::tab { background-color: #3B4252; border: 1px solid #434C5E; padding: 8px 15px; }
QTabBar::tab:selected { background-color: #88C0D0; color: #2E3440; }
QListWidget, QTreeWidget { background-color: #3B4252; border: 1px solid #434C5E; alternate-background-color: #4C566A; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #88C0D0; color: #2E3440; }
QHeaderView::section { background-color: #4C566A; border: 1px solid #434C5E; }
QSlider::groove:horizontal { background: #3B4252; }
QSlider::handle:horizontal { background: #88C0D0; }
QSlider::sub-page:horizontal { background: #A3BE8C; }
QStatusBar { background-color: #3B4252; border-top: 1px solid #434C5E; }
""" + create_container_styles("#3B4252", "#434C5E", "#EBCB8B", "#ECEFF4", "#2E3440")
LIGHT_STYLESHEET = """
QWidget { background-color: #f0f0f0; color: #000000; font-family: Segoe UI, Arial, sans-serif; font-size: 10pt; }
QPushButton { background-color: #dcdcdc; border: 1px solid #b0b0b0; padding: 8px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #e8e8e8; }
QPushButton:disabled { background-color: #e0e0e0; color: #a0a0a0; }
QPushButton#removeButton { background-color: #d9534f; color: #ffffff; }
QPushButton#onOffButton[onState="false"] { background-color: #5cb85c; color: #ffffff; }
QPushButton#onOffButton[onState="true"] { background-color: #d9534f; color: #ffffff; }
QPushButton.effectButton:checked { background-color: #5bc0de; color: #ffffff; }
QPushButton.presetButton { min-width: 40px; padding: 4px; font-size: 8pt; }
QComboBox { background-color: #ffffff; border: 1px solid #b0b0b0; padding: 5px; }
QComboBox QAbstractItemView { selection-background-color: #0078d7; selection-color: #ffffff; }
QTabWidget::pane { border: 1px solid #c0c0c0; background-color: #f8f8f8; }
QTabBar::tab { background-color: #e0e0e0; border: 1px solid #c0c0c0; padding: 8px 15px; }
QTabBar::tab:selected { background-color: #ffffff; }
QListWidget, QTreeWidget { background-color: #ffffff; border: 1px solid #c0c0c0; alternate-background-color: #f5f5f5; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #0078d7; color: #ffffff; }
QHeaderView::section { background-color: #e8e8e8; border: 1px solid #c0c0c0; }
QSlider::groove:horizontal { background: #e0e0e0; }
QSlider::handle:horizontal { background: #0078d7; }
QSlider::sub-page:horizontal { background: #90ee90; }
QStatusBar { background-color: #e8e8e8; border-top: 1px solid #c0c0c0; }
""" + create_container_styles("#f8f8f8", "#c0c0c0", "#0078d7", "#000000", "#ffffff")
DRACULA_STYLESHEET = """
QWidget { background-color: #282a36; color: #f8f8f2; font-family: Consolas, Courier New, monospace; }
QPushButton { background-color: #6272a4; border: 1px solid #44475a; padding: 8px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #7082b6; border-color: #bd93f9; }
QPushButton:disabled { background-color: #44475a; color: #6272a4; }
QPushButton#removeButton { background-color: #ff5555; }
QPushButton#onOffButton[onState="false"] { background-color: #50fa7b; color: #282a36; }
QPushButton#onOffButton[onState="true"] { background-color: #ff5555; }
QPushButton.effectButton:checked { background-color: #ff79c6; color: #282a36; }
QPushButton.presetButton { min-width: 40px; padding: 4px; font-size: 8pt; }
QComboBox { background-color: #44475a; border: 1px solid #6272a4; padding: 5px; }
QComboBox QAbstractItemView { background-color: #44475a; selection-background-color: #bd93f9; selection-color: #282a36; }
QTabWidget::pane { border: 1px solid #44475a; background-color: #2f313e; }
QTabBar::tab { background-color: #44475a; border: 1px solid #6272a4; padding: 8px 15px; }
QTabBar::tab:selected { background-color: #bd93f9; color: #282a36; }
QListWidget, QTreeWidget { background-color: #2f313e; border: 1px solid #44475a; alternate-background-color: #383a47; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #bd93f9; color: #282a36; }
QHeaderView::section { background-color: #44475a; border: 1px solid #6272a4; }
QSlider::groove:horizontal { background: #44475a; }
QSlider::handle:horizontal { background: #bd93f9; }
QSlider::sub-page:horizontal { background: #50fa7b; }
QStatusBar { background-color: #44475a; border-top: 1px solid #6272a4; }
""" + create_container_styles("#44475a", "#6272a4", "#ff79c6", "#f8f8f2", "#282a36")
MATRIX_STYLESHEET = """
QWidget { background-color: #000000; color: #00FF41; font-family: 'Courier New', Courier, monospace; font-size: 11pt; }
QPushButton { background-color: #0D2A13; border: 1px solid #00FF41; padding: 8px 12px; border-radius: 0px; }
QPushButton:hover { background-color: #103b19; border-color: #5CFF8B; }
QPushButton:disabled { background-color: #051007; color: #005F15; }
QPushButton#removeButton { border-color: #ff0000; }
QPushButton#removeButton:hover { color: #ff0000; }
QPushButton#onOffButton[onState="false"] { color: #5CFF8B; }
QPushButton#onOffButton[onState="true"] { color: #ff0000; }
QPushButton.effectButton:checked { background-color: #00FF41; color: #000000; }
QPushButton.presetButton { min-width: 40px; padding: 4px; font-size: 8pt; }
QComboBox { background-color: #051007; border: 1px solid #00FF41; border-radius: 0px; padding: 5px; }
QComboBox QAbstractItemView { background-color: #051007; selection-background-color: #00FF41; selection-color: #000000; }
QTabWidget::pane { border: 1px solid #00FF41; background-color: #051007; }
QTabBar::tab { background-color: #0D2A13; border: 1px solid #00FF41; padding: 8px 15px; }
QTabBar::tab:selected { background-color: #103b19; color: #5CFF8B; }
QListWidget, QTreeWidget { background-color: #051007; border: 1px solid #00FF41; alternate-background-color: #081a0c; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #00FF41; color: #000000; }
QHeaderView::section { background-color: #0D2A13; border: 1px solid #00FF41; }
QSlider::groove:horizontal { height: 2px; background: #0D2A13; }
QSlider::handle:horizontal { background: #00FF41; width: 12px; height: 20px; margin: -10px 0; }
QSlider::sub-page:horizontal { background: #00FF41; }
QStatusBar { background-color: #0D2A13; border-top: 1px solid #00FF41; }
""" + create_container_styles("#0D2A13", "#00FF41", "#5CFF8B", "#00FF41", "#000000")
SYNTHWAVE_STYLESHEET = """
QWidget { background-color: #261B3E; color: #F0F0F0; font-family: 'Lucida Console', Monaco, monospace; }
QPushButton { background-color: #4A2F6D; border: 1px solid #FF00FF; padding: 8px 12px; border-radius: 8px; }
QPushButton:hover { background-color: #6A4F8D; border: 2px solid #FFFF00; }
QPushButton:disabled { background-color: #3A2755; color: #6A4F8D; }
QPushButton#removeButton { background-color: #FF00FF; color: #261B3E; }
QPushButton#onOffButton[onState="false"] { background-color: #00FFFF; color: #261B3E; }
QPushButton#onOffButton[onState="true"] { background-color: #FF00FF; color: #261B3E; }
QPushButton.effectButton:checked { background-color: #FFFF00; color: #261B3E; }
QPushButton.presetButton { min-width: 40px; padding: 4px; font-size: 8pt; }
QComboBox { background-color: #3A2755; border: 1px solid #FF00FF; padding: 5px; border-radius: 5px; }
QComboBox QAbstractItemView { background-color: #3A2755; selection-background-color: #FF00FF; selection-color: #261B3E; }
QTabWidget::pane { border: 2px solid #FF00FF; background-color: #3A2755; }
QTabBar::tab { background-color: #4A2F6D; border: 1px solid #FF00FF; padding: 8px 15px; }
QTabBar::tab:selected { background-color: #FF00FF; color: #261B3E; }
QListWidget, QTreeWidget { background-color: #3A2755; border: 1px solid #FF00FF; alternate-background-color: #4A2F6D; }
QListWidget::item:selected, QTreeWidget::item:selected { background-color: #FF00FF; color: #261B3E; }
QHeaderView::section { background-color: #4A2F6D; border: 1px solid #FF00FF; }
QSlider::groove:horizontal { background: #3A2755; }
QSlider::handle:horizontal { background: #00FFFF; }
QSlider::sub-page:horizontal { background: #FFFF00; }
QStatusBar { background-color: #4A2F6D; border-top: 1px solid #FF00FF; }
""" + create_container_styles("#4A2F6D", "#FF00FF", "#FFFF00", "#F0F0F0", "#261B3E")

THEMES = { "Nord Dark": NORD_DARK_STYLESHEET, "Light": LIGHT_STYLESHEET, "Dracula": DRACULA_STYLESHEET, "Matrix": MATRIX_STYLESHEET, "Synthwave": SYNTHWAVE_STYLESHEET }

def create_message_box(parent, icon, title, text, informative_text="", buttons=QMessageBox.StandardButton.Ok):
    msg_box = QMessageBox(parent)
    msg_box.setStyleSheet(QApplication.instance().styleSheet())
    msg_box.setIconPixmap(icon.pixmap(QSize(48, 48)))
    msg_box.setWindowTitle(title); msg_box.setText(text)
    if informative_text: msg_box.setInformativeText(informative_text)
    msg_box.setStandardButtons(buttons)
    return msg_box

class GroupEditorDialog(QDialog):
    def __init__(self, parent, bridge, existing_group=None):
        super().__init__(parent)
        self.bridge = bridge; self.existing_group = existing_group
        self.setWindowTitle(tr("edit_group_title") if existing_group else tr("create_group_title"))
        self.setMinimumWidth(400); self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(tr("group_name"))); self.name_edit = QLineEdit()
        self.layout.addWidget(self.name_edit); self.layout.addWidget(QLabel(tr("select_lights")))
        self.lights_list_widget = QListWidget(); self.lights_list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.layout.addWidget(self.lights_list_widget)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept); self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box); self.populate_lights()
        if self.existing_group: self.load_existing_group_data()
    def populate_lights(self):
        try:
            for light in sorted(self.bridge.get_light_objects('list'), key=lambda l: l.name.lower()):
                item = QListWidgetItem(light.name); item.setData(Qt.ItemDataRole.UserRole, light.light_id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable); item.setCheckState(Qt.CheckState.Unchecked)
                self.lights_list_widget.addItem(item)
        except Exception as e: create_message_box(self, icon_error, tr("error_title"), f"Could not fetch lights:\n{e}").exec()
    def load_existing_group_data(self):
        self.name_edit.setText(self.existing_group.name)
        group_light_ids = [str(lid) for lid in self.existing_group.lights]
        for i in range(self.lights_list_widget.count()):
            item = self.lights_list_widget.item(i)
            if str(item.data(Qt.ItemDataRole.UserRole)) in group_light_ids:
                item.setCheckState(Qt.CheckState.Checked)
    def get_selected_data(self):
        name = self.name_edit.text().strip(); selected_light_ids = []
        for i in range(self.lights_list_widget.count()):
            item = self.lights_list_widget.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_light_ids.append(str(item.data(Qt.ItemDataRole.UserRole)))
        return name, selected_light_ids

class EffectsPanel(QWidget):
    def __init__(self, control_panel_ref):
        super().__init__()
        self.control_panel = control_panel_ref
        self.setObjectName("effectsPanelWidget")

        self.effect_timer = QTimer(self)
        self.effect_timer.timeout.connect(self.run_effect_step)
        self.current_effect_type = None
        self.effect_state_counter = 0

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.effects_group_box = QGroupBox(tr("dynamic_effects"))
        group_layout = QVBoxLayout()
        self.effects_group_box.setLayout(group_layout)

        effects_grid = QGridLayout()
        effects_grid.setSpacing(10)

        self.effect_buttons = {}
        effects_to_add = [
            ("Color Loop", "colorloop"), ("Candlelight", "candle"), ("Fireplace", "fireplace"),
            ("Thunderstorm", "thunderstorm"), ("Police", "police"), ("Ocean", "ocean"),
            ("Disco", "disco"), ("Aurora", "aurora"), ("Sunrise", "sunrise"),
            ("Rainbow", "rainbow"), ("Alert", "alert"), ("Starlight", "starlight"),
            ("TV Flicker", "tv_flicker")
        ]

        for i, (text, name) in enumerate(effects_to_add):
            button = QPushButton(text)
            button.setCheckable(True)
            button.setProperty("class", "effectButton")
            button.toggled.connect(lambda checked, n=name: self._handle_effect_toggle(n, checked))
            self.effect_buttons[name] = button
            effects_grid.addWidget(button, i // 3, i % 3)

        group_layout.addLayout(effects_grid)
        
        speed_layout = QHBoxLayout()
        self.speed_label = QLabel(tr("speed"))
        speed_layout.addWidget(self.speed_label)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setMinimum(1); self.speed_slider.setMaximum(10); self.speed_slider.setValue(5)
        self.speed_slider.setToolTip(tr("speed_tooltip"))
        speed_layout.addWidget(self.speed_slider)
        group_layout.addLayout(speed_layout)

        self.stop_effects_button = QPushButton(tr("stop_all_effects"))
        self.stop_effects_button.setObjectName("removeButton")
        self.stop_effects_button.setIcon(icon_off)
        self.stop_effects_button.clicked.connect(self.on_stop_effects_clicked)
        group_layout.addWidget(self.stop_effects_button)

        self.layout.addWidget(self.effects_group_box)
        self.layout.addStretch()
        self.set_enabled(False)

    def retranslate_ui(self):
        self.effects_group_box.setTitle(tr("dynamic_effects"))
        self.speed_label.setText(tr("speed"))
        self.speed_slider.setToolTip(tr("speed_tooltip"))
        self.stop_effects_button.setText(tr("stop_all_effects"))

    def _handle_effect_toggle(self, effect_name, checked):
        if not self.control_panel.current_target:
            self.effect_buttons[effect_name].setChecked(False)
            return
        if checked:
            for name, button in self.effect_buttons.items():
                if name != effect_name:
                    button.blockSignals(True); button.setChecked(False); button.blockSignals(False)
            self.start_effect(effect_name)
        else:
            if self.current_effect_type == effect_name:
                self.stop_custom_effect()

    def on_stop_effects_clicked(self):
        self.stop_custom_effect()

    def set_enabled(self, enabled):
        for button in self.effect_buttons.values():
            button.setEnabled(enabled)
        self.stop_effects_button.setEnabled(enabled)
        self.speed_slider.setEnabled(enabled)
        if not enabled:
            self.stop_custom_effect()

    def update_effect_buttons_state(self, bridge_effect):
        self.effect_buttons['colorloop'].setChecked(bridge_effect == 'colorloop')
        if self.current_effect_type is None:
            for name, button in self.effect_buttons.items():
                if name != 'colorloop': button.setChecked(False)

    def stop_custom_effect(self):
        if self.effect_timer.isActive(): self.effect_timer.stop()
        if self.control_panel.current_target:
            self.control_panel._send_command({'effect': 'none'}, None)
        print(f"Stopped effect: {self.current_effect_type}")
        self.current_effect_type = None
        for button in self.effect_buttons.values():
            button.blockSignals(True); button.setChecked(False); button.blockSignals(False)

    def start_effect(self, effect_type):
        if not self.control_panel.current_target: return
        self.current_effect_type = effect_type
        self.effect_state_counter = 0
        print(f"Starting effect: {self.current_effect_type}")
        self.control_panel._send_command({'on': True, 'effect': 'none'}, None)
        self.run_effect_step()

    def _run_thunderstorm_flash(self):
        if not self.control_panel.current_target: return
        self.control_panel._send_command({'bri': 254, 'xy': [0.32, 0.33], 'transitiontime': 0}, None)
        QTimer.singleShot(80, lambda: self.control_panel._send_command({'on': False, 'transitiontime': 0}, None))
        QTimer.singleShot(150, lambda: self.control_panel._send_command({'on': True, 'bri': 200, 'transitiontime': 0}, None))
        QTimer.singleShot(300, lambda: self.control_panel._send_command({'on': True, 'bri': 20, 'xy': [0.2, 0.15], 'transitiontime': 5}, None))

    def run_effect_step(self):
        if not self.control_panel.current_target or not self.current_effect_type:
            self.stop_custom_effect(); return

        params = {}; speed_multiplier = (11 - self.speed_slider.value()) / 5.0
        base_interval = 500

        if self.current_effect_type == 'candle':
            params = {'bri': random.randint(50, 150), 'xy': [round(0.5+random.uniform(-0.05,0.05),4), round(0.4+random.uniform(-0.03,0.03),4)], 'transitiontime': 3}
            base_interval = 300 + random.randint(-150, 150)
        elif self.current_effect_type == 'fireplace':
            params = {'bri': random.randint(80, 200), 'xy': [round(0.6+random.uniform(-0.06,0.04),4), round(0.35+random.uniform(-0.04,0.04),4)], 'transitiontime': 4}
            base_interval = 500 + random.randint(-200, 150)
        elif self.current_effect_type == 'colorloop': params = {'effect': 'colorloop'}
        elif self.current_effect_type == 'thunderstorm':
            if random.random() < 0.25: self._run_thunderstorm_flash()
            else: params = {'bri': 20, 'xy': [0.2, 0.15], 'transitiontime': 30}
            base_interval = random.randint(1000, 6000)
        elif self.current_effect_type == 'police':
            params = {'xy': [0.67, 0.32] if self.effect_state_counter == 0 else [0.14, 0.08], 'bri': 254, 'transitiontime': 1}
            self.effect_state_counter = 1 - self.effect_state_counter
            base_interval = 400
        elif self.current_effect_type == 'ocean':
            params = {'xy': random.choice([[0.16, 0.2], [0.15, 0.25], [0.17, 0.3]]), 'bri': random.randint(120, 220), 'transitiontime': int(40 * speed_multiplier)}
            base_interval = 4500
        elif self.current_effect_type == 'disco':
            params = {'xy': random.choice([[0.5,0.4],[0.15,0.1],[0.2,0.7],[0.4,0.5],[0.6,0.3]]), 'bri': 254, 'transitiontime': 1}
            base_interval = 300
        elif self.current_effect_type == 'aurora':
            params = {'xy': random.choice([[0.18, 0.45], [0.25, 0.2], [0.3, 0.6]]), 'bri': random.randint(80, 180), 'transitiontime': int(50 * speed_multiplier)}
            base_interval = 5500
        elif self.current_effect_type == 'sunrise':
            sunrise_states = [{'xy': [0.2, 0.1], 'bri': 20}, {'xy': [0.4, 0.2], 'bri': 80}, {'xy': [0.5, 0.4], 'bri': 150}, {'xy': [0.45, 0.45], 'bri': 254}]
            params = {**sunrise_states[self.effect_state_counter], 'transitiontime': int(150 * speed_multiplier)}
            self.effect_state_counter = (self.effect_state_counter + 1) % len(sunrise_states)
            base_interval = 15000
        elif self.current_effect_type == 'rainbow':
            rainbow_hues = [0, 6000, 12000, 25500, 46920, 56100]
            params = {'hue': rainbow_hues[self.effect_state_counter], 'sat': 254, 'bri': 200, 'transitiontime': int(40 * speed_multiplier)}
            self.effect_state_counter = (self.effect_state_counter + 1) % len(rainbow_hues)
            base_interval = 4000
        elif self.current_effect_type == 'alert':
            params = {'bri': 254 if self.effect_state_counter == 0 else 50, 'xy': [0.55, 0.4], 'transitiontime': int(10 * speed_multiplier)}
            self.effect_state_counter = 1 - self.effect_state_counter
            base_interval = 1000
        elif self.current_effect_type == 'starlight':
            if random.random() < 0.1: params = {'bri': 254, 'xy': [0.32, 0.33], 'transitiontime': 0}
            else: params = {'bri': 1, 'xy': [0.2, 0.15], 'transitiontime': 5}
            base_interval = 200
        elif self.current_effect_type == 'tv_flicker':
            params = {'bri': random.randint(100, 200), 'xy': random.choice([[0.28, 0.3], [0.32, 0.33], [0.35, 0.35]]), 'transitiontime': 1}
            base_interval = 150 + random.randint(-50, 50)

        if params: self.control_panel._send_command(params, None)
        
        final_interval = max(100, int(base_interval * speed_multiplier))
        self.effect_timer.start(final_interval)

class ControlPanel(QWidget):
    def __init__(self, bridge_callback, effects_panel_ref):
        super().__init__(); self.bridge_callback = bridge_callback; self.effects_panel = effects_panel_ref
        self.current_target = None; self.target_type = None; self.is_group = False
        self.setObjectName("controlPanelWidget"); self.layout = QVBoxLayout(); self.setLayout(self.layout)
        self.title_label = QLabel(tr("select_device")); font = self.title_label.font(); font.setPointSize(14); font.setBold(True)
        self.title_label.setFont(font); self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label); self.controls_widget = QWidget()
        self.controls_layout = QGridLayout(); self.controls_widget.setLayout(self.controls_layout)
        self.layout.addWidget(self.controls_widget); self.on_off_button = QPushButton(tr("power_on_off"))
        self.on_off_button.setObjectName("onOffButton"); self.on_off_button.setCheckable(True)
        self.on_off_button.toggled.connect(self.toggle_power_state); self.controls_layout.addWidget(self.on_off_button, 0, 0, 1, 4)
        
        self.brightness_label = QLabel(tr("brightness")); self.controls_layout.addWidget(self.brightness_label, 1, 0)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal); self.brightness_slider.setMinimum(1); self.brightness_slider.setMaximum(254)
        self.brightness_slider.sliderReleased.connect(self.set_brightness_released)
        self.brightness_slider.valueChanged.connect(lambda v: self.brightness_value_label.setText(str(v)))
        self.controls_layout.addWidget(self.brightness_slider, 1, 1, 1, 2)
        self.brightness_value_label = QLabel("128"); self.brightness_value_label.setMinimumWidth(35)
        self.controls_layout.addWidget(self.brightness_value_label, 1, 3)
        
        preset_layout = QHBoxLayout()
        for val in [25, 50, 75, 100]:
            btn = QPushButton(f"{val}%"); btn.setProperty("class", "presetButton")
            btn.clicked.connect(lambda _, v=val: self.set_brightness_preset(v))
            preset_layout.addWidget(btn)
        self.controls_layout.addLayout(preset_layout, 2, 0, 1, 4)

        color_layout = QHBoxLayout()
        self.color_button = QPushButton(tr("change_color")); self.color_button.setIcon(icon_color); self.color_button.clicked.connect(self.select_color)
        color_layout.addWidget(self.color_button)
        self.random_color_button = QPushButton(); self.random_color_button.setIcon(icon_random); self.random_color_button.setToolTip(tr("random_color_tooltip"))
        self.random_color_button.clicked.connect(self.set_random_color)
        color_layout.addWidget(self.random_color_button)
        self.controls_layout.addLayout(color_layout, 3, 0, 1, 4)
        
        self.favorites_group = QGroupBox(tr("favorite_colors"))
        favorites_layout = QHBoxLayout()
        self.favorite_buttons = []
        for i in range(5):
            btn = QPushButton(); btn.setFixedSize(30,30); btn.setToolTip(tr("favorite_tooltip"))
            btn.setStyleSheet("background-color: #444;"); btn.setProperty("color_xy", None)
            btn.clicked.connect(lambda _, b=btn: self.apply_favorite_color(b))
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, b=btn: self.save_favorite_color(b))
            self.favorite_buttons.append(btn)
            favorites_layout.addWidget(btn)
        self.favorites_group.setLayout(favorites_layout)
        self.controls_layout.addWidget(self.favorites_group, 4, 0, 1, 4)

        self.info_group_box = QGroupBox(tr("information")); self.info_layout = QVBoxLayout()
        self.info_group_box.setLayout(self.info_layout); self.layout.addWidget(self.info_group_box)
        self.info_model_label = QLabel(tr("model", model="-")); self.info_model_label.setObjectName("infoLabel")
        self.info_layout.addWidget(self.info_model_label); self.info_type_label = QLabel(tr("type", type="-"))
        self.info_type_label.setObjectName("infoLabel"); self.info_layout.addWidget(self.info_type_label)
        self.info_group_box.hide(); self.layout.addStretch(); self.controls_widget.hide()

    def retranslate_ui(self):
        self.title_label.setText(tr("select_device") if not self.current_target else self.current_target.name)
        self.on_off_button.setText(tr("power_on_off"))
        self.brightness_label.setText(tr("brightness"))
        self.color_button.setText(tr("change_color"))
        self.random_color_button.setToolTip(tr("random_color_tooltip"))
        self.favorites_group.setTitle(tr("favorite_colors"))
        for btn in self.favorite_buttons:
            btn.setToolTip(tr("favorite_tooltip"))
        self.info_group_box.setTitle(tr("information"))
        self.update_on_off_button_style(self.on_off_button.isChecked()) # Update text for on/off

    def update_display(self, type, obj):
        self.target_type = type; self.current_target = obj; bridge = self.bridge_callback()
        self.effects_panel.set_enabled(bool(obj)); self.info_group_box.hide()
        if not bridge or not self.current_target: self.title_label.setText(tr("select_device")); self.controls_widget.hide(); return
        self.is_group = self.target_type == 'group'
        try:
            is_on=False; bri=128; color_capable=False; effect='none'; model='-'; l_type='-'; current_xy = [0.3127, 0.3290]
            if self.is_group:
                name = self.current_target.name; state = bridge.get_group(self.current_target.group_id)
                is_on = state.get('state', {}).get('any_on', False); bri = state.get('action', {}).get('bri', 128)
                effect = state.get('action', {}).get('effect', 'none'); color_capable = True; l_type = "Group/Room"
                current_xy = state.get('action', {}).get('xy', current_xy)
            else:
                name = self.current_target.name; info = bridge.get_light(self.current_target.light_id)
                if info:
                    model=info.get('modelid','-'); l_type=info.get('type','-')
                    if 'state' in info: is_on=info['state'].get('on',False); bri=info['state'].get('bri',128); effect=info['state'].get('effect','none'); color_capable='xy' in info['state']; current_xy = info['state'].get('xy', current_xy)
            self.title_label.setText(name); self.color_button.setEnabled(color_capable); self.random_color_button.setEnabled(color_capable)
            self.on_off_button.setChecked(is_on); self.update_on_off_button_style(is_on)
            self.brightness_slider.setValue(bri); self.brightness_value_label.setText(str(bri))
            self.effects_panel.update_effect_buttons_state(effect)
            self.info_model_label.setText(tr("model", model=model)); self.info_type_label.setText(tr("type", type=l_type))
            self.info_group_box.show(); self.controls_widget.show()
        except Exception as e:
            create_message_box(self, icon_warning, tr("error_title"), f"Could not fetch status:\n{e}").exec()
    def update_on_off_button_style(self, is_on):
        self.on_off_button.setText(tr("power_off") if is_on else tr("power_on")); self.on_off_button.setIcon(icon_off if is_on else icon_on)
        self.on_off_button.setProperty("onState", is_on); self.on_off_button.style().unpolish(self.on_off_button); self.on_off_button.style().polish(self.on_off_button)
    def _send_command(self, cmd, val):
        bridge = self.bridge_callback()
        if not bridge or not self.current_target: return False
        id = self.current_target.group_id if self.is_group else self.current_target.light_id
        try:
            params = cmd if isinstance(cmd, dict) else {cmd: val}
            if self.is_group: bridge.set_group(id, params)
            else: bridge.set_light(id, params)
            return True
        except Exception as e: print(f"ERROR: {e}"); return False
    def toggle_power_state(self, c):
        if not self.current_target: return
        self.effects_panel.on_stop_effects_clicked(); self.update_on_off_button_style(c)
        if self._send_command('on', c) and c and self.brightness_slider.value()==0: self._send_command('bri', 1); self.brightness_slider.setValue(1)
    def set_brightness_released(self):
        if not self.current_target: return
        v = self.brightness_slider.value()
        if self._send_command('bri', v) and v>0 and not self.on_off_button.isChecked():
            if self._send_command('on', True): self.on_off_button.setChecked(True)
    def set_brightness_preset(self, percentage):
        value = int(254 * (percentage / 100.0))
        self.brightness_slider.setValue(value)
        self.set_brightness_released()
    def set_random_color(self):
        if not self.current_target: return
        xy = [round(random.random(), 4), round(random.random(), 4)]
        self._send_command({'on': True, 'xy': xy}, None)
    def select_color(self):
        if not self.current_target: return
        self.effects_panel.on_stop_effects_clicked()
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            r,g,b,_=color.getRgb(); xy=self.rgb_to_xy(r,g,b); bri=self.brightness_slider.value()
            params={'on':True, 'xy':xy, 'effect':'none', 'bri': max(bri,50) if bri<25 else bri}
            if self._send_command(params, None): self.brightness_slider.setValue(params['bri']); self.on_off_button.setChecked(True)
    def save_favorite_color(self, button):
        if not self.current_target: return
        try:
            state = self.bridge_callback().get_light(self.current_target.light_id) if not self.is_group else self.bridge_callback().get_group(self.current_target.group_id)
            xy = state['action']['xy'] if self.is_group else state['state']['xy']
            r, g, b = self.xy_to_rgb(xy[0], xy[1])
            button.setStyleSheet(f"background-color: rgb({r},{g},{b});")
            button.setProperty("color_xy", xy)
        except Exception as e:
            print(f"Could not save favorite color: {e}")
    def apply_favorite_color(self, button):
        xy = button.property("color_xy")
        if xy and self.current_target:
            self.effects_panel.on_stop_effects_clicked()
            self._send_command({'on': True, 'xy': xy}, None)
    def rgb_to_xy(self,r,g,b):
        r,g,b=(x/255.0 for x in (r,g,b)); r=((r+0.055)/1.055)**2.4 if r>0.04045 else r/12.92; g=((g+0.055)/1.055)**2.4 if g>0.04045 else g/12.92; b=((b+0.055)/1.055)**2.4 if b>0.04045 else b/12.92
        X=r*0.664511+g*0.154324+b*0.162028; Y=r*0.283881+g*0.668433+b*0.047685; Z=r*0.000088+g*0.072310+b*0.986039
        t=X+Y+Z; return [round(X/t,4),round(Y/t,4)] if t>0 else [0.3127,0.3290]
    def xy_to_rgb(self, x, y, bri=254):
        Y=bri/254.0; X=(Y/y)*x; Z=(Y/y)*(1-x-y)
        r=X*3.2406-Y*1.5372-Z*0.4986; g=-X*0.9689+Y*1.8758+Z*0.0415; b=X*0.0557-Y*0.2040+Z*1.0570
        r,g,b = (12.92*c if c<=0.0031308 else 1.055*c**(1/2.4)-0.055 for c in (r,g,b))
        return max(0,min(255,int(r*255))), max(0,min(255,int(g*255))), max(0,min(255,int(b*255)))

class HueEnhancedApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1280, 720)
        self.hue_manager = HueManager()
        
        # Load settings: language and theme
        global current_language
        current_language = self.hue_manager.get_setting('language', 'sv')
        self.current_theme_name = self.hue_manager.get_setting('theme', 'Dracula') # Dracula as default

        self.current_bridge = None; self.current_ip = None
        self.bridge_config = {}; self.theme_menu = None; self.lang_menu = None
        
        self.init_ui()
        self.create_menus()
        self.apply_styles() # Apply loaded theme
        self.update_ui_icons()
        
        if self.hue_manager.bridges:
            first_ip = next(iter(self.hue_manager.bridges))
            self.bridge_selector.setCurrentText(first_ip)
            if self.bridge_selector.currentIndex() == 0: self.handle_bridge_selection()
        else: self.show_welcome_or_add_bridge()

    def init_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        top_bar = QHBoxLayout()
        self.bridge_label = QLabel(tr("bridge"))
        top_bar.addWidget(self.bridge_label)
        self.bridge_selector = QComboBox(); self.bridge_selector.addItems(self.hue_manager.bridges.keys())
        self.bridge_selector.currentIndexChanged.connect(self.handle_bridge_selection)
        top_bar.addWidget(self.bridge_selector, 1)
        self.add_bridge_btn = QPushButton(tr("add_bridge")); self.add_bridge_btn.clicked.connect(self.add_bridge_flow)
        top_bar.addWidget(self.add_bridge_btn)
        self.remove_bridge_btn = QPushButton(tr("remove_bridge")); self.remove_bridge_btn.setObjectName("removeButton")
        self.remove_bridge_btn.clicked.connect(self.remove_selected_bridge)
        top_bar.addWidget(self.remove_bridge_btn); top_bar.addSpacing(20)
        self.refresh_btn = QPushButton(tr("reload")); self.refresh_btn.clicked.connect(self.refresh_all_from_bridge)
        top_bar.addWidget(self.refresh_btn); self.main_layout.addLayout(top_bar)
        self.splitter = QSplitter(Qt.Orientation.Horizontal); self.list_tabs = QTabWidget()
        self.lights_list = QListWidget(); self.groups_list = QListWidget()
        self.scenes_tree = QTreeWidget(); self.scenes_tree.setHeaderHidden(True)
        self.sensors_list = QListWidget()
        
        self.lights_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.lights_list.customContextMenuRequested.connect(self.show_light_context_menu)
        self.groups_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.groups_list.customContextMenuRequested.connect(self.show_group_context_menu)
        self.sensors_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.sensors_list.customContextMenuRequested.connect(self.show_sensor_context_menu)

        self.control_panel = ControlPanel(lambda: self.current_bridge, None)
        self.effects_panel = EffectsPanel(self.control_panel); self.control_panel.effects_panel = self.effects_panel
        self.list_tabs.addTab(self.groups_list, tr("groups")); self.list_tabs.addTab(self.lights_list, tr("lights"))
        self.list_tabs.addTab(self.scenes_tree, tr("scenes")); self.list_tabs.addTab(self.sensors_list, tr("sensors"))
        self.list_tabs.addTab(self.effects_panel, tr("effects"))
        self.splitter.addWidget(self.list_tabs); self.splitter.addWidget(self.control_panel)
        self.splitter.setSizes([480, 520]); self.main_layout.addWidget(self.splitter, 1)
        
        self.lights_list.itemClicked.connect(self.handle_light_selection)
        self.groups_list.itemClicked.connect(self.handle_group_selection)
        self.scenes_tree.itemClicked.connect(self.handle_scene_selection)
        self.sensors_list.itemClicked.connect(self.handle_sensor_selection)

        self.refresh_btn.setEnabled(False); self.remove_bridge_btn.setEnabled(False); self.setStatusBar(QStatusBar(self))

    def create_menus(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu(tr("file"))
        self.exit_action = QAction(icon_exit, tr("exit"), self); self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_action)
        
        self.view_menu = self.menu_bar.addMenu(tr("view"))
        self.theme_menu = self.view_menu.addMenu(icon_theme, tr("theme"))
        for theme_name in THEMES.keys():
            action = QAction(theme_name, self, checkable=True)
            action.setChecked(theme_name == self.current_theme_name)
            action.triggered.connect(lambda c, name=theme_name: self.change_theme(name))
            self.theme_menu.addAction(action)
        
        self.lang_menu = self.view_menu.addMenu(tr("language"))
        sv_action = QAction("Svenska", self, checkable=True); sv_action.setChecked(current_language == 'sv')
        sv_action.triggered.connect(lambda: self.change_language('sv'))
        en_action = QAction("English", self, checkable=True); en_action.setChecked(current_language == 'en')
        en_action.triggered.connect(lambda: self.change_language('en'))
        self.lang_menu.addAction(sv_action); self.lang_menu.addAction(en_action)

        self.help_menu = self.menu_bar.addMenu(tr("help"))
        self.about_action = QAction(icon_info_alt, tr("about"), self); self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)

    def retranslate_ui(self):
        """Update all UI text elements to the current language."""
        self.setWindowTitle(tr("app_title"))
        self.bridge_label.setText(tr("bridge"))
        self.add_bridge_btn.setText(tr("add_bridge"))
        self.remove_bridge_btn.setText(tr("remove_bridge"))
        self.refresh_btn.setText(tr("reload"))
        
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.groups_list), tr("groups"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.lights_list), tr("lights"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.scenes_tree), tr("scenes"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.sensors_list), tr("sensors"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.effects_panel), tr("effects"))

        # Menus
        self.file_menu.setTitle(tr("file")); self.exit_action.setText(tr("exit"))
        self.view_menu.setTitle(tr("view")); self.theme_menu.setTitle(tr("theme")); self.lang_menu.setTitle(tr("language"))
        self.help_menu.setTitle(tr("help")); self.about_action.setText(tr("about"))

        # Child widgets
        self.control_panel.retranslate_ui()
        self.effects_panel.retranslate_ui()

        # Update status bar and title if connected
        if self.current_bridge and self.bridge_config:
            bridge_name = self.bridge_config.get('name', self.current_ip)
            self.setWindowTitle(tr("app_title_connected", bridge_name=bridge_name))
            self.statusBar().showMessage(tr("status_connected", bridge_name=bridge_name))
        
    def update_ui_icons(self):
        self.setWindowIcon(icon_light)
        self.add_bridge_btn.setIcon(icon_add); self.remove_bridge_btn.setIcon(icon_remove)
        self.refresh_btn.setIcon(icon_refresh)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.groups_list), icon_group)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.lights_list), icon_light)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.scenes_tree), icon_scene)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.sensors_list), icon_sensor)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.effects_panel), icon_effect)

    def apply_styles(self):
        stylesheet = THEMES.get(self.current_theme_name, DRACULA_STYLESHEET)
        self.setStyleSheet(stylesheet)
        if self.theme_menu:
            for action in self.theme_menu.actions():
                action.setChecked(action.text() == self.current_theme_name)

    def change_theme(self, name):
        if name in THEMES: 
            self.current_theme_name = name
            self.hue_manager.save_setting('theme', name)
            self.apply_styles()

    def change_language(self, lang_code):
        global current_language
        if lang_code in TRANSLATIONS:
            current_language = lang_code
            self.hue_manager.save_setting('language', lang_code)
            for action in self.lang_menu.actions():
                action.setChecked(action.text().lower().startswith(lang_code))
            self.retranslate_ui()

    def show_about_dialog(self): create_message_box(self, icon_info, tr("about"), tr("about_text")).exec()
    def show_welcome_or_add_bridge(self): create_message_box(self, icon_info, tr("welcome_title"), tr("welcome_text")).exec()
    def handle_bridge_selection(self):
        ip = self.bridge_selector.currentText()
        if ip: self.connect_bridge(ip)
        else: self.current_bridge=None; self.refresh_btn.setEnabled(False); self.remove_bridge_btn.setEnabled(False)
    def connect_bridge(self, ip):
        username = self.hue_manager.bridges.get(ip, {}).get("username")
        if not username: create_message_box(self, icon_error, tr("error_title"), f"Username missing for {ip}.").exec(); return
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            bridge = Bridge(ip, username=username); api_info = bridge.get_api()
            self.current_bridge = bridge; self.current_ip = ip; self.bridge_config = api_info.get('config', {})
            bridge_name = self.bridge_config.get('name', ip)
            self.setWindowTitle(tr("app_title_connected", bridge_name=bridge_name))
            self.statusBar().showMessage(tr("status_connected", bridge_name=bridge_name))
            self.refresh_btn.setEnabled(True); self.remove_bridge_btn.setEnabled(True)
            self.refresh_all_from_bridge()
        except Exception as e: create_message_box(self, icon_error, tr("error_title"), f"Could not connect to {ip}:\n{e}").exec()
        finally: QApplication.restoreOverrideCursor()
    def add_bridge_flow(self):
        ip, ok = QInputDialog.getText(self, tr("add_bridge_title"), tr("add_bridge_prompt"))
        if ok and ip:
            try:
                temp_bridge = Bridge(ip)
                if create_message_box(self, icon_info, tr("press_button_title"), tr("press_button_prompt", ip=ip), buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel).exec() == QMessageBox.StandardButton.Ok:
                    temp_bridge.connect(); self.hue_manager.add_bridge(ip, temp_bridge.username)
                    self.bridge_selector.addItem(ip); self.bridge_selector.setCurrentText(ip)
            except Exception as e: create_message_box(self, icon_error, tr("error_title"), tr("pair_fail_prompt", ip=ip, e=e)).exec()
    def remove_selected_bridge(self):
        ip = self.bridge_selector.currentText()
        if ip and create_message_box(self, icon_warning, tr("confirm_title"), tr("remove_bridge_prompt", ip=ip), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No).exec() == QMessageBox.StandardButton.Yes:
            self.hue_manager.remove_bridge(ip); self.bridge_selector.removeItem(self.bridge_selector.currentIndex())

    def clear_lists(self): self.lights_list.clear(); self.groups_list.clear(); self.scenes_tree.clear(); self.sensors_list.clear()

    def refresh_all_from_bridge(self):
        if not self.current_bridge: return
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor); self.clear_lists(); self.control_panel.update_display(None, None); QApplication.processEvents()
        try:
            if self.bridge_config:
                bridge_name = self.bridge_config.get('name', self.current_ip)
                bridge_item = QListWidgetItem(icon_bridge, f"Bridge: {bridge_name} ({self.current_ip})")
                bridge_item.setData(Qt.ItemDataRole.UserRole, ("bridge", self.bridge_config)); self.sensors_list.addItem(bridge_item)
            
            lights = sorted(self.current_bridge.get_light_objects('list'), key=lambda l: l.name.lower())
            for l in lights: item = QListWidgetItem(icon_light, l.name); item.setData(Qt.ItemDataRole.UserRole, ("light", l)); self.lights_list.addItem(item)
            
            groups = sorted([g for g in self.current_bridge.groups if g.group_id != 0], key=lambda g: g.name.lower())
            for g in groups: item = QListWidgetItem(icon_group, g.name); item.setData(Qt.ItemDataRole.UserRole, ("group", g)); self.groups_list.addItem(item)
            
            scenes = self.current_bridge.get_scene(); scenes_by_group = {}; other_scenes = []
            group_names = {str(g.group_id): g.name for g in self.current_bridge.groups}
            for sid, sdata in scenes.items():
                gid = sdata.get('group'); s_tuple = (sid, sdata.get("name", f"Scene {sid}"), sdata)
                if gid and gid in group_names: scenes_by_group.setdefault(gid, []).append(s_tuple)
                else: other_scenes.append(s_tuple)
            
            for gid in sorted(scenes_by_group.keys(), key=lambda g: group_names.get(g, '').lower()):
                group_item = QTreeWidgetItem(self.scenes_tree, [group_names.get(gid, f"Group {gid}")]); group_item.setIcon(0, icon_group)
                for sid, sname, sdata in sorted(scenes_by_group[gid], key=lambda s: s[1].lower()):
                    scene_item = QTreeWidgetItem(group_item, [sname]); scene_item.setIcon(0, icon_scene); scene_item.setData(0, Qt.ItemDataRole.UserRole, ("scene", sid))
            if other_scenes:
                other_item = QTreeWidgetItem(self.scenes_tree, [tr("other_scenes")]); other_item.setIcon(0, icon_scene)
                for sid, sname, sdata in sorted(other_scenes, key=lambda s: s[1].lower()):
                    scene_item = QTreeWidgetItem(other_item, [sname]); scene_item.setIcon(0, icon_scene); scene_item.setData(0, Qt.ItemDataRole.UserRole, ("scene", sid))
            self.scenes_tree.expandAll()

            sensors = sorted(self.current_bridge.get_sensor_objects('list'), key=lambda s: s.name.lower())
            for sensor in sensors:
                stext = sensor.name; item_icon = icon_sensor; add = False; tooltip = f"ID: {sensor.sensor_id}\nType: {sensor.type}\nModel: {sensor.modelid}"
                if sensor.type == 'ZLLTemperature' and 'temperature' in sensor.state:
                    stext += f": {sensor.state['temperature']/100.0:.1f}°C"; add = True
                elif sensor.type == 'ZLLPresence' and 'presence' in sensor.state:
                    stext += f": {'Motion' if sensor.state['presence'] else 'No motion'}"; add = True
                elif sensor.type == 'ZLLSwitch':
                    item_icon = icon_dimmer; add = True
                if add:
                    item = QListWidgetItem(item_icon, stext); item.setData(Qt.ItemDataRole.UserRole, ("sensor", sensor)); item.setToolTip(tooltip); self.sensors_list.addItem(item)

        except Exception as e: create_message_box(self, icon_error, tr("error_title"), f"Could not load data:\n{e}").exec()
        finally: QApplication.restoreOverrideCursor()

    def handle_light_selection(self, item):
        if item: self.control_panel.update_display('light', item.data(Qt.ItemDataRole.UserRole)[1])
    def handle_group_selection(self, item):
        if item: self.control_panel.update_display('group', item.data(Qt.ItemDataRole.UserRole)[1])
    def handle_scene_selection(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == 'scene': self.activate_scene(data[1], item.text(0))
    def handle_sensor_selection(self, item):
        if item: print(f"Selected sensor: {item.text()}")

    def activate_scene(self, scene_id, scene_name):
        if not self.current_bridge: return
        try:
            self.current_bridge.set_group(0, 'scene', scene_id)
            QTimer.singleShot(500, lambda: self.control_panel.update_display(self.control_panel.target_type, self.control_panel.current_target) if self.control_panel.current_target else None)
        except Exception as e:
            create_message_box(self, icon_error, tr("error_title"), f"Could not activate scene '{scene_name}':\n{e}").exec()

    def show_light_context_menu(self, position):
        item = self.lights_list.itemAt(position)
        if not item: return
        menu = QMenu(); menu.setStyleSheet(self.styleSheet())
        info_action = QAction(icon_info, tr("show_info"), self)
        info_action.triggered.connect(lambda: self.show_device_info_dialog(item.data(Qt.ItemDataRole.UserRole)[1], 'light'))
        menu.addAction(info_action); menu.exec(self.lights_list.mapToGlobal(position))

    def show_group_context_menu(self, position):
        menu = QMenu(); menu.setStyleSheet(self.styleSheet())
        item = self.groups_list.itemAt(position)
        create_action = QAction(icon_add, tr("create_new_group"), self)
        create_action.triggered.connect(self.create_new_group); menu.addAction(create_action)
        if item:
            menu.addSeparator()
            info_action = QAction(icon_info, tr("show_info"), self)
            info_action.triggered.connect(lambda: self.show_device_info_dialog(item.data(Qt.ItemDataRole.UserRole)[1], 'group'))
            menu.addAction(info_action)
            edit_action = QAction(icon_edit, tr("edit_group"), self)
            edit_action.triggered.connect(lambda: self.edit_group(item)); menu.addAction(edit_action)
            save_scene_action = QAction(icon_save, tr("save_as_scene"), self)
            save_scene_action.triggered.connect(lambda: self.save_group_as_scene(item))
            menu.addAction(save_scene_action)
            delete_action = QAction(icon_remove, tr("delete_group"), self)
            delete_action.triggered.connect(lambda: self.delete_group(item)); menu.addAction(delete_action)
        menu.exec(self.groups_list.mapToGlobal(position))

    def show_sensor_context_menu(self, position):
        item = self.sensors_list.itemAt(position)
        if not item: return
        data = item.data(Qt.ItemDataRole.UserRole)
        if not data: return
        menu = QMenu(); menu.setStyleSheet(self.styleSheet())
        action_text = tr("show_info")
        if data[0] == 'bridge': action_callback = lambda: self.show_bridge_info_dialog(data[1])
        else: action_callback = lambda: self.show_device_info_dialog(data[1], data[0])
        info_action = QAction(icon_info, action_text, self); info_action.triggered.connect(action_callback)
        menu.addAction(info_action); menu.exec(self.sensors_list.mapToGlobal(position))

    def show_device_info_dialog(self, obj, type):
        try:
            if type == 'light': info = self.current_bridge.get_light(obj.light_id)
            elif type == 'group': info = self.current_bridge.get_group(obj.group_id)
            elif type == 'sensor': info = self.current_bridge.get_sensor(obj.sensor_id)
            else: return
            details = json.dumps(info, indent=4, ensure_ascii=False)
            msg_box = create_message_box(self, icon_info, f"Info: {info.get('name', 'Unknown')}", details)
            msg_box.layout().itemAt(0).widget().setMinimumWidth(400); msg_box.exec()
        except Exception as e: create_message_box(self, icon_error, tr("error_title"), f"Could not fetch info:\n{e}").exec()
    
    def show_bridge_info_dialog(self, bridge_config):
         details = json.dumps(bridge_config, indent=4, ensure_ascii=False)
         msg_box = create_message_box(self, icon_info, f"Bridge Info: {bridge_config.get('name', 'Unknown')}", details)
         msg_box.layout().itemAt(0).widget().setMinimumWidth(450); msg_box.exec()

    def create_new_group(self):
        if not self.current_bridge: return
        dialog = GroupEditorDialog(self, self.current_bridge)
        if dialog.exec():
            name, light_ids = dialog.get_selected_data()
            if not name: create_message_box(self, icon_warning, tr("warning_title"), tr("no_name_warning")).exec(); return
            try: self.current_bridge.create_group(name, light_ids); self.refresh_all_from_bridge()
            except Exception as e: create_message_box(self, icon_error, tr("error_title"), tr("create_group_fail", e=e)).exec()
    def edit_group(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        dialog = GroupEditorDialog(self, self.current_bridge, existing_group=group_obj)
        if dialog.exec():
            name, light_ids = dialog.get_selected_data()
            if not name: create_message_box(self, icon_warning, tr("warning_title"), tr("no_name_warning")).exec(); return
            try: self.current_bridge.set_group(group_obj.group_id, {'name': name, 'lights': light_ids}); self.refresh_all_from_bridge()
            except Exception as e: create_message_box(self, icon_error, tr("error_title"), tr("edit_group_fail", e=e)).exec()
    def delete_group(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        if create_message_box(self, icon_warning, tr("confirm_title"), tr("delete_group_prompt", group_name=group_obj.name), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No).exec() == QMessageBox.StandardButton.Yes:
            try: self.current_bridge.delete_group(group_obj.group_id); self.refresh_all_from_bridge()
            except Exception as e: create_message_box(self, icon_error, tr("error_title"), tr("delete_group_fail", e=e)).exec()
    def save_group_as_scene(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        scene_name, ok = QInputDialog.getText(self, tr("save_scene_title"), tr("save_scene_prompt", group_name=group_obj.name))
        if ok and scene_name:
            try:
                result = self.current_bridge.create_group_scene(group_obj.group_id, scene_name)
                print(f"Result from create_group_scene: {result}")
                create_message_box(self, icon_info, tr("info_title"), tr("save_scene_success", scene_name=scene_name)).exec()
                self.refresh_all_from_bridge()
            except Exception as e:
                create_message_box(self, icon_error, tr("error_title"), tr("save_scene_fail", e=e)).exec()

if __name__ == "__main__":
    if sys.platform == 'win32':
        try:
             QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
             QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        except AttributeError: pass
    app = QApplication(sys.argv)
    load_icons(app.style())
    window = HueEnhancedApp()
    window.show()
    sys.exit(app.exec())
