# -*- coding: utf-8 -*-
import sys
import os
import json
import requests
import math
import time
import random
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLabel,
    QComboBox, QColorDialog, QListWidget, QListWidgetItem,
    QHBoxLayout, QTabWidget, QSlider, QMessageBox, QSplitter,
    QFrame, QGridLayout, QInputDialog, QStyle, QGroupBox,
    QMainWindow, QDialog, QLineEdit, QDialogButtonBox,
    QTreeWidget, QTreeWidgetItem, QMenu, QStatusBar, QToolBar,
    QLineEdit, QCheckBox, QSizePolicy, QProgressDialog, QFileDialog
)
from PyQt6.QtGui import QIcon, QColor, QPixmap, QFont, QAction, QCursor, QPalette
from PyQt6.QtCore import Qt, QSize, QTimer, QSettings, QThread, pyqtSignal
from phue import Bridge, PhueRegistrationException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("hue_controller.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("HueController")

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
        "search": "Sök...",
        "discover_bridges": "Upptäck bryggor",
        "search_lights": "Sök lampor",

        # Menus
        "file": "&Arkiv",
        "exit": "A&vsluta",
        "view": "&Visa",
        "theme": "&Tema",
        "language": "&Språk",
        "help": "&Hjälp",
        "about": "&Om...",
        "about_text": "Hue Controller v1.5\n\nMed automatisk bridge-upptäckt och förbättrad användarupplevelse.",
        "backup_settings": "Säkerhetskopiera...",
        "restore_settings": "Återställ...",

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
        "software": "Mjukvara: {swversion}",
        "unique_id": "Unikt ID: {uniqueid}",

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
        "discovery_title": "Bridge-upptäckt",
        "discovery_found": "Hittade {count} bryggor",
        "discovery_none": "Inga bryggor hittades. Kontrollera att din Hue Bridge är ansluten och att du är på samma nätverk.",
        "discovery_error": "Kunde inte söka efter bryggor: {error}",
        "backup_dialog_title": "Spara inställningar",
        "backup_success": "Inställningarna har sparats till {filename}",
        "backup_fail": "Kunde inte spara inställningarna:\n{e}",
        "restore_dialog_title": "Återställ inställningar",
        "restore_confirm": "Är du säker på att du vill återställa inställningarna från {filename}?\nDetta kan inte ångras.",
        "restore_success": "Inställningarna har återställts.",
        "restore_fail": "Kunde inte återställa inställningarna:\n{e}",
        "search_lights_title": "Söker efter lampor",
        "search_lights_text": "Söker efter nya lampor... Detta kan ta upp till en minut.",
        "search_lights_success": "{count} nya lampor hittades!",
        "search_lights_none": "Inga nya lampor hittades.",
        "search_lights_fail": "Sökningen misslyckades:\n{e}",
        "touchlink_confirm_title": "Starta Touchlink?",
        "touchlink_confirm_text": "Detta kommer att söka efter och para ihop lampor som är nära bryggan (inom ~30 cm).\nFortsätt?",
        "touchlink_started": "Touchlink-sökning har startat.",

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
        
        # Status
        "status_loading": "Laddar...",
        "status_ready": "Klar",
        "status_connecting": "Ansluter till {ip}...",
        "status_discovering": "Söker efter bryggor...",
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
        "search": "Search...",
        "discover_bridges": "Discover bridges",
        "search_lights": "Search Lights",

        # Menus
        "file": "&File",
        "exit": "E&xit",
        "view": "&View",
        "theme": "&Theme",
        "language": "&Language",
        "help": "&Help",
        "about": "&About...",
        "about_text": "Hue Controller v1.5\n\nWith automatic bridge discovery and improved user experience.",
        "backup_settings": "Backup Settings...",
        "restore_settings": "Restore Settings...",

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
        "software": "Software: {swversion}",
        "unique_id": "Unique ID: {uniqueid}",

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
        "discovery_title": "Bridge Discovery",
        "discovery_found": "Found {count} bridges",
        "discovery_none": "No bridges found. Make sure your Hue Bridge is connected and you're on the same network.",
        "discovery_error": "Could not search for bridges: {error}",
        "backup_dialog_title": "Backup Settings",
        "backup_success": "Settings successfully saved to {filename}",
        "backup_fail": "Failed to save settings:\n{e}",
        "restore_dialog_title": "Restore Settings",
        "restore_confirm": "Are you sure you want to restore settings from {filename}?\nThis action cannot be undone.",
        "restore_success": "Settings successfully restored.",
        "restore_fail": "Failed to restore settings:\n{e}",
        "search_lights_title": "Searching for lights",
        "search_lights_text": "Searching for new lights... This may take up to a minute.",
        "search_lights_success": "{count} new lights found!",
        "search_lights_none": "No new lights were found.",
        "search_lights_fail": "Light search failed:\n{e}",
        "touchlink_confirm_title": "Start Touchlink?",
        "touchlink_confirm_text": "This will search for and pair lights that are very close to the bridge (within ~12 inches).\nContinue?",
        "touchlink_started": "Touchlink search started.",

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
        
        # Status
        "status_loading": "Loading...",
        "status_ready": "Ready",
        "status_connecting": "Connecting to {ip}...",
        "status_discovering": "Discovering bridges...",
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
            return key  # Return key if formatting fails
    return translation

# --- Bridge Discovery Thread ---
class BridgeDiscoveryThread(QThread):
    discovered = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        try:
            # Try the official Hue discovery service first
            discovery_url = "https://discovery.meethue.com/"
            response = requests.get(discovery_url, timeout=10)
            bridges = response.json()
            
            if bridges:
                self.discovered.emit([bridge['internalipaddress'] for bridge in bridges])
                return
            
            # Fallback to local network discovery if official service fails
            self.discovered.emit(self.discover_local())
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Bridge discovery failed: {e}")
            self.error.emit(str(e))
        except Exception as e:
            logger.error(f"Unexpected error during bridge discovery: {e}")
            self.error.emit(str(e))

    def discover_local(self):
        """Fallback method to discover bridges on local network"""
        import socket
        from netaddr import IPNetwork
        
        # Try common network ranges
        potential_ranges = [
            "192.168.0.0/24", 
            "192.168.1.0/24",
            "192.168.2.0/24",
            "10.0.0.0/24",
            "10.0.1.0/24"
        ]
        
        found_bridges = []
        
        for network_range in potential_ranges:
            try:
                for ip in IPNetwork(network_range):
                    try:
                        # Check if port 80 is open (HTTP)
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.1)
                        result = sock.connect_ex((str(ip), 80))
                        sock.close()
                        
                        if result == 0:
                            # Check if it's a Hue bridge by looking for the description.xml
                            desc_url = f"http://{ip}/description.xml"
                            desc_response = requests.get(desc_url, timeout=1)
                            if "Philips hue bridge" in desc_response.text:
                                found_bridges.append(str(ip))
                    except:
                        continue
            except:
                continue
                
        return found_bridges

# --- Icon Management ---
ICON_DIR = "icons"
DEFAULT_ICON_SIZE = QSize(16, 16)

# Global icon variables
icon_light, icon_group, icon_scene, icon_sensor, icon_bridge, icon_dimmer = (QIcon() for _ in range(6))
icon_refresh, icon_add, icon_remove, icon_on, icon_off, icon_color = (QIcon() for _ in range(6))
icon_effect, icon_theme, icon_info_alt, icon_exit, icon_warning, icon_info = (QIcon() for _ in range(6))
icon_error, icon_edit, icon_save, icon_random, icon_search, icon_discover = (QIcon() for _ in range(6))
icon_backup, icon_restore = (QIcon() for _ in range(2))

def load_icons(app_style):
    """Loads icons from Qt's standard set for stability."""
    global icon_light, icon_group, icon_scene, icon_sensor, icon_bridge, icon_dimmer, icon_refresh, icon_add, icon_remove
    global icon_on, icon_off, icon_color, icon_effect, icon_theme, icon_info_alt, icon_exit, icon_edit, icon_save, icon_random
    global icon_warning, icon_info, icon_error, icon_search, icon_discover, icon_backup, icon_restore

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
    icon_search = app_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView)
    icon_discover = app_style.standardIcon(QStyle.StandardPixmap.SP_FileDialogStart)
    icon_backup = app_style.standardIcon(QStyle.StandardPixmap.SP_DriveHDIcon)
    icon_restore = app_style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
    
    logger.info("Icons loaded successfully")

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
QLineEdit { background-color: #3B4252; border: 1px solid #434C5E; padding: 5px; border-radius: 3px; color: #ECEFF4; }
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
QLineEdit { background-color: #ffffff; border: 1px solid #b0b0b0; padding: 5px; border-radius: 3px; }
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
QLineEdit { background-color: #44475a; border: 1px solid #6272a4; padding: 5px; border-radius: 3px; color: #f8f8f2; }
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
QLineEdit { background-color: #051007; border: 1px solid #00FF41; padding: 5px; border-radius: 0px; color: #00FF41; }
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
QLineEdit { background-color: #3A2755; border: 1px solid #FF00FF; padding: 5px; border-radius: 5px; color: #F0F0F0; }
""" + create_container_styles("#4A2F6D", "#FF00FF", "#FFFF00", "#F0F0F0", "#261B3E")

THEMES = { 
    "Nord Dark": NORD_DARK_STYLESHEET, 
    "Light": LIGHT_STYLESHEET, 
    "Dracula": DRACULA_STYLESHEET, 
    "Matrix": MATRIX_STYLESHEET, 
    "Synthwave": SYNTHWAVE_STYLESHEET 
}

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
        except Exception as e: 
            logger.error(f"Could not fetch lights: {e}")
            create_message_box(self, icon_error, tr("error_title"), f"Could not fetch lights:\n{e}").exec()
            
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
        is_colorloop = bridge_effect == 'colorloop'
        self.effect_buttons['colorloop'].blockSignals(True)
        self.effect_buttons['colorloop'].setChecked(is_colorloop)
        self.effect_buttons['colorloop'].blockSignals(False)
        if is_colorloop:
            self.current_effect_type = 'colorloop'
            for name, button in self.effect_buttons.items():
                if name != 'colorloop':
                    button.blockSignals(True)
                    button.setChecked(False)
                    button.blockSignals(False)
        elif self.current_effect_type is None:
            for button in self.effect_buttons.values():
                button.setChecked(False)

    def stop_custom_effect(self):
        if self.effect_timer.isActive(): self.effect_timer.stop()
        if self.control_panel.current_target:
            self.control_panel._send_command({'effect': 'none'}, None)
        logger.info(f"Stopped effect: {self.current_effect_type}")
        self.current_effect_type = None
        for button in self.effect_buttons.values():
            button.blockSignals(True); button.setChecked(False); button.blockSignals(False)

    def start_effect(self, effect_type):
        if not self.control_panel.current_target: return
        self.current_effect_type = effect_type
        self.effect_state_counter = 0
        logger.info(f"Starting effect: {self.current_effect_type}")
        if effect_type == 'colorloop':
            self.control_panel._send_command({'on': True, 'effect': 'colorloop'}, None)
            if self.effect_timer.isActive(): self.effect_timer.stop()
        else:
            self.control_panel._send_command({'on': True, 'effect': 'none'}, None)
            self.run_effect_step()

    def _run_thunderstorm_flash(self):
        if not self.control_panel.current_target: return
        self.control_panel._send_command({'bri': 254, 'xy': [0.32, 0.33], 'transitiontime': 0}, None)
        QTimer.singleShot(80, lambda: self.control_panel._send_command({'on': False, 'transitiontime': 0}, None))
        QTimer.singleShot(150, lambda: self.control_panel._send_command({'on': True, 'bri': 200, 'transitiontime': 0}, None))
        QTimer.singleShot(300, lambda: self.control_panel._send_command({'on': True, 'bri': 20, 'xy': [0.2, 0.15], 'transitiontime': 5}, None))

    def run_effect_step(self):
        if not self.control_panel.current_target or not self.current_effect_type or self.current_effect_type == 'colorloop':
            self.stop_custom_effect(); return

        params = {}; speed_multiplier = (11 - self.speed_slider.value()) / 5.0
        base_interval = 500

        if self.current_effect_type == 'candle':
            params = {'bri': random.randint(50, 150), 'xy': [round(0.5+random.uniform(-0.05,0.05),4), round(0.4+random.uniform(-0.03,0.03),4)], 'transitiontime': 3}
            base_interval = 300 + random.randint(-150, 150)
        elif self.current_effect_type == 'fireplace':
            params = {'bri': random.randint(80, 200), 'xy': [round(0.6+random.uniform(-0.06,0.04),4), round(0.35+random.uniform(-0.04,0.04),4)], 'transitiontime': 4}
            base_interval = 500 + random.randint(-200, 150)
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
        self.settings = QSettings("HueController", "HueEnhanced")
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
        self.info_sw_label = QLabel(tr("software", swversion="-"))
        self.info_sw_label.setObjectName("infoLabel"); self.info_layout.addWidget(self.info_sw_label)
        self.info_uniqueid_label = QLabel(tr("unique_id", uniqueid="-"))
        self.info_uniqueid_label.setObjectName("infoLabel"); self.info_layout.addWidget(self.info_uniqueid_label)
        self.info_group_box.hide(); self.layout.addStretch(); self.controls_widget.hide()
        self.load_favorite_colors()

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
            is_on=False; bri=128; color_capable=False; effect='none'; model='-'; l_type='-'; swversion='-'; uniqueid='-'; current_xy = [0.3127, 0.3290]
            if self.is_group:
                name = self.current_target.name; state = bridge.get_group(self.current_target.group_id)
                is_on = state.get('state', {}).get('any_on', False); bri = state.get('action', {}).get('bri', 128)
                effect = state.get('action', {}).get('effect', 'none'); color_capable = True; l_type = "Group/Room"
                current_xy = state.get('action', {}).get('xy', current_xy)
            else:
                name = self.current_target.name; info = bridge.get_light(self.current_target.light_id)
                if info:
                    model=info.get('modelid','-'); l_type=info.get('type','-'); swversion=info.get('swversion','-'); uniqueid=info.get('uniqueid','-')
                    if 'state' in info: is_on=info['state'].get('on',False); bri=info['state'].get('bri',128); effect=info['state'].get('effect','none'); color_capable='xy' in info['state']; current_xy = info['state'].get('xy', current_xy)
            self.title_label.setText(name); self.color_button.setEnabled(color_capable); self.random_color_button.setEnabled(color_capable)
            self.on_off_button.setChecked(is_on); self.update_on_off_button_style(is_on)
            self.brightness_slider.setValue(bri); self.brightness_value_label.setText(str(bri))
            self.effects_panel.update_effect_buttons_state(effect)
            self.info_model_label.setText(tr("model", model=model)); self.info_type_label.setText(tr("type", type=l_type))
            self.info_sw_label.setText(tr("software", swversion=swversion)); self.info_uniqueid_label.setText(tr("unique_id", uniqueid=uniqueid))
            self.info_group_box.show(); self.controls_widget.show()
        except Exception as e:
            logger.error(f"Could not fetch status: {e}")
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
        except Exception as e: 
            logger.error(f"Command failed: {e}")
            return False
            
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
            
    def load_favorite_colors(self):
        for i, button in enumerate(self.favorite_buttons):
            xy = self.settings.value(f"favorite_colors/{i}")
            if xy and isinstance(xy, list) and len(xy) == 2:
                try:
                    r, g, b = self.xy_to_rgb(float(xy[0]), float(xy[1]))
                    button.setStyleSheet(f"background-color: rgb({r},{g},{b});")
                    button.setProperty("color_xy", xy)
                except (ValueError, TypeError):
                    continue # Ignore invalid stored data

    def save_favorite_color(self, button):
        if not self.current_target: return
        try:
            index = self.favorite_buttons.index(button)
        except ValueError:
            return # Button not in list, should not happen

        try:
            state = self.bridge_callback().get_light(self.current_target.light_id) if not self.is_group else self.bridge_callback().get_group(self.current_target.group_id)
            xy = state['action']['xy'] if self.is_group else state['state']['xy']
            r, g, b = self.xy_to_rgb(xy[0], xy[1])
            button.setStyleSheet(f"background-color: rgb({r},{g},{b});")
            button.setProperty("color_xy", xy)
            self.settings.setValue(f"favorite_colors/{index}", xy)
        except Exception as e:
            logger.error(f"Could not save favorite color: {e}")
            
    def apply_favorite_color(self, button):
        xy_prop = button.property("color_xy")
        if xy_prop and self.current_target:
            # QSettings might return strings, ensure they are floats
            xy = [float(c) for c in xy_prop]
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
        self.settings = QSettings("HueController", "HueEnhanced")
        
        # Load settings: language and theme
        global current_language
        current_language = self.settings.value("language", "sv")
        self.current_theme_name = self.settings.value("theme", "Dracula") # Dracula as default

        self.current_bridge = None; self.current_ip = None
        self.bridge_config = {}; self.theme_menu = None; self.lang_menu = None
        
        # Initialize bridge discovery thread
        self.discovery_thread = BridgeDiscoveryThread()
        self.discovery_thread.discovered.connect(self.handle_discovered_bridges)
        self.discovery_thread.error.connect(self.handle_discovery_error)
        
        self.init_ui()
        self.create_menus()
        self.apply_styles() # Apply loaded theme
        self.update_ui_icons()
        
        # Load saved bridges
        self.load_bridges()
        
        if self.bridge_selector.count() > 0:
            self.bridge_selector.setCurrentIndex(0)
            if self.bridge_selector.currentIndex() == 0: self.handle_bridge_selection()
        else: 
            self.show_welcome_or_add_bridge()
            # Automatically start discovery if no bridges are configured
            self.discover_bridges()

    def init_ui(self):
        self.central_widget = QWidget(); self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar for search
        self.toolbar = QToolBar()
        self.toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)
        
        # Add search box to toolbar
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(tr("search"))
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.filter_lists)
        self.toolbar.addWidget(self.search_edit)
        
        top_bar = QHBoxLayout()
        self.bridge_label = QLabel(tr("bridge"))
        top_bar.addWidget(self.bridge_label)
        self.bridge_selector = QComboBox()
        self.bridge_selector.currentIndexChanged.connect(self.handle_bridge_selection)
        top_bar.addWidget(self.bridge_selector, 1)
        self.add_bridge_btn = QPushButton(tr("add_bridge")); self.add_bridge_btn.clicked.connect(self.add_bridge_flow)
        top_bar.addWidget(self.add_bridge_btn)
        self.discover_bridge_btn = QPushButton(tr("discover_bridges")); self.discover_bridge_btn.setIcon(icon_discover)
        self.discover_bridge_btn.clicked.connect(self.discover_bridges)
        top_bar.addWidget(self.discover_bridge_btn)
        self.remove_bridge_btn = QPushButton(tr("remove_bridge")); self.remove_bridge_btn.setObjectName("removeButton")
        self.remove_bridge_btn.clicked.connect(self.remove_selected_bridge)
        top_bar.addWidget(self.remove_bridge_btn); top_bar.addSpacing(20)
        self.search_lights_btn = QPushButton(tr("search_lights")); self.search_lights_btn.setIcon(icon_search)
        self.search_lights_btn.clicked.connect(self.search_for_lights)
        top_bar.addWidget(self.search_lights_btn)
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
        
        # Add search boxes to each tab
        self.lights_search = QLineEdit()
        self.lights_search.setPlaceholderText(tr("search"))
        self.lights_search.textChanged.connect(self.filter_lights)
        
        self.groups_search = QLineEdit()
        self.groups_search.setPlaceholderText(tr("search"))
        self.groups_search.textChanged.connect(self.filter_groups)
        
        self.scenes_search = QLineEdit()
        self.scenes_search.setPlaceholderText(tr("search"))
        self.scenes_search.textChanged.connect(self.filter_scenes)
        
        self.sensors_search = QLineEdit()
        self.sensors_search.setPlaceholderText(tr("search"))
        self.sensors_search.textChanged.connect(self.filter_sensors)
        
        # Create widgets for each tab with search box
        lights_widget = QWidget()
        lights_layout = QVBoxLayout()
        lights_layout.addWidget(self.lights_search)
        lights_layout.addWidget(self.lights_list)
        lights_widget.setLayout(lights_layout)
        
        groups_widget = QWidget()
        groups_layout = QVBoxLayout()
        groups_layout.addWidget(self.groups_search)
        groups_layout.addWidget(self.groups_list)
        groups_widget.setLayout(groups_layout)
        
        scenes_widget = QWidget()
        scenes_layout = QVBoxLayout()
        scenes_layout.addWidget(self.scenes_search)
        scenes_layout.addWidget(self.scenes_tree)
        scenes_widget.setLayout(scenes_layout)
        
        sensors_widget = QWidget()
        sensors_layout = QVBoxLayout()
        sensors_layout.addWidget(self.sensors_search)
        sensors_layout.addWidget(self.sensors_list)
        sensors_widget.setLayout(sensors_layout)
        
        self.list_tabs.addTab(groups_widget, tr("groups")); self.list_tabs.addTab(lights_widget, tr("lights"))
        self.list_tabs.addTab(scenes_widget, tr("scenes")); self.list_tabs.addTab(sensors_widget, tr("sensors"))
        self.list_tabs.addTab(self.effects_panel, tr("effects"))
        self.splitter.addWidget(self.list_tabs); self.splitter.addWidget(self.control_panel)
        self.splitter.setSizes([480, 520]); self.main_layout.addWidget(self.splitter, 1)
        
        self.lights_list.itemClicked.connect(self.handle_light_selection)
        self.groups_list.itemClicked.connect(self.handle_group_selection)
        self.scenes_tree.itemClicked.connect(self.handle_scene_selection)
        self.sensors_list.itemClicked.connect(self.handle_sensor_selection)

        self.refresh_btn.setEnabled(False); self.remove_bridge_btn.setEnabled(False); 
        self.search_lights_btn.setEnabled(False)
        self.statusBar().showMessage(tr("status_ready"))

    def create_menus(self):
        self.menu_bar = self.menuBar()
        self.file_menu = self.menu_bar.addMenu(tr("file"))
        
        self.backup_action = QAction(icon_backup, tr("backup_settings"), self)
        self.backup_action.triggered.connect(self.backup_settings)
        self.file_menu.addAction(self.backup_action)
        
        self.restore_action = QAction(icon_restore, tr("restore_settings"), self)
        self.restore_action.triggered.connect(self.restore_settings)
        self.file_menu.addAction(self.restore_action)
        
        self.file_menu.addSeparator()
        
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
        self.discover_bridge_btn.setText(tr("discover_bridges"))
        self.remove_bridge_btn.setText(tr("remove_bridge"))
        self.refresh_btn.setText(tr("reload"))
        self.search_lights_btn.setText(tr("search_lights"))
        self.search_edit.setPlaceholderText(tr("search"))
        self.lights_search.setPlaceholderText(tr("search"))
        self.groups_search.setPlaceholderText(tr("search"))
        self.scenes_search.setPlaceholderText(tr("search"))
        self.sensors_search.setPlaceholderText(tr("search"))
        
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.groups_list.parent().parent()), tr("groups"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.lights_list.parent().parent()), tr("lights"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.scenes_tree.parent().parent()), tr("scenes"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.sensors_list.parent().parent()), tr("sensors"))
        self.list_tabs.setTabText(self.list_tabs.indexOf(self.effects_panel), tr("effects"))

        # Menus
        self.file_menu.setTitle(tr("file")); self.exit_action.setText(tr("exit"))
        self.backup_action.setText(tr("backup_settings"))
        self.restore_action.setText(tr("restore_settings"))
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
        self.add_bridge_btn.setIcon(icon_add); 
        self.discover_bridge_btn.setIcon(icon_discover)
        self.remove_bridge_btn.setIcon(icon_remove)
        self.refresh_btn.setIcon(icon_refresh)
        self.search_lights_btn.setIcon(icon_search)
        self.backup_action.setIcon(icon_backup)
        self.restore_action.setIcon(icon_restore)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.groups_list.parent().parent()), icon_group)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.lights_list.parent().parent()), icon_light)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.scenes_tree.parent().parent()), icon_scene)
        self.list_tabs.setTabIcon(self.list_tabs.indexOf(self.sensors_list.parent().parent()), icon_sensor)
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
            self.settings.setValue("theme", name)
            self.apply_styles()

    def change_language(self, lang_code):
        global current_language
        if lang_code in TRANSLATIONS:
            current_language = lang_code
            self.settings.setValue("language", lang_code)
            for action in self.lang_menu.actions():
                action.setChecked(action.text().lower().startswith(lang_code))
            self.retranslate_ui()

    def show_about_dialog(self): 
        about_text = tr("about_text")
        create_message_box(self, icon_info, tr("about"), about_text).exec()
        
    def show_welcome_or_add_bridge(self): 
        create_message_box(self, icon_info, tr("welcome_title"), tr("welcome_text")).exec()
        
    def load_bridges(self):
        """Load bridges from QSettings"""
        size = self.settings.beginReadArray("bridges")
        for i in range(size):
            self.settings.setArrayIndex(i)
            ip = self.settings.value("ip")
            username = self.settings.value("username")
            if ip and username:
                self.bridge_selector.addItem(ip, username)
        self.settings.endArray()
        
    def save_bridges(self):
        """Save bridges to QSettings"""
        self.settings.beginWriteArray("bridges")
        for i in range(self.bridge_selector.count()):
            self.settings.setArrayIndex(i)
            ip = self.bridge_selector.itemText(i)
            username = self.bridge_selector.itemData(i)
            self.settings.setValue("ip", ip)
            self.settings.setValue("username", username)
        self.settings.endArray()
        
    def add_bridge(self, ip, username):
        """Add a bridge to the selector and save it"""
        self.bridge_selector.addItem(ip, username)
        self.save_bridges()
        
    def remove_bridge(self, ip):
        """Remove a bridge from the selector and save"""
        index = self.bridge_selector.findText(ip)
        if index >= 0:
            self.bridge_selector.removeItem(index)
            self.save_bridges()
            
    def discover_bridges(self):
        """Start bridge discovery"""
        self.statusBar().showMessage(tr("status_discovering"))
        self.discovery_thread.start()
        
    def handle_discovered_bridges(self, bridges):
        """Handle discovered bridges"""
        if bridges:
            msg = tr("discovery_found", count=len(bridges))
            self.statusBar().showMessage(msg)
            
            # Ask user if they want to add any of the discovered bridges
            bridge_text = "\n".join([f"• {ip}" for ip in bridges])
            reply = create_message_box(
                self, icon_info, tr("discovery_title"), 
                f"{msg}:\n{bridge_text}\n\nWould you like to add one?",
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            ).exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                # Let user choose which bridge to add
                ip, ok = QInputDialog.getItem(
                    self, tr("discovery_title"), 
                    "Select a bridge to add:", 
                    bridges, 0, False
                )
                if ok and ip:
                    self._pair_bridge(ip)
        else:
            create_message_box(self, icon_info, tr("discovery_title"), tr("discovery_none")).exec()
            self.statusBar().showMessage(tr("status_ready"))
            
    def handle_discovery_error(self, error):
        """Handle discovery errors"""
        logger.error(f"Bridge discovery error: {error}")
        create_message_box(self, icon_error, tr("discovery_title"), tr("discovery_error", error=error)).exec()
        self.statusBar().showMessage(tr("status_ready"))
            
    def handle_bridge_selection(self):
        ip = self.bridge_selector.currentText()
        if ip: 
            self.connect_bridge(ip)
        else: 
            self.current_bridge=None; 
            self.refresh_btn.setEnabled(False); 
            self.remove_bridge_btn.setEnabled(False)
            self.search_lights_btn.setEnabled(False)
            self.backup_action.setEnabled(False)
            self.restore_action.setEnabled(False)
            
    def connect_bridge(self, ip):
        username = self.bridge_selector.currentData()
        if not username: 
            create_message_box(self, icon_error, tr("error_title"), f"Username missing for {ip}.").exec(); 
            return
            
        try:
            self.statusBar().showMessage(tr("status_connecting", ip=ip))
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            bridge = Bridge(ip, username=username); 
            api_info = bridge.get_api()
            self.current_bridge = bridge; 
            self.current_ip = ip; 
            self.bridge_config = api_info.get('config', {})
            bridge_name = self.bridge_config.get('name', ip)
            self.setWindowTitle(tr("app_title_connected", bridge_name=bridge_name))
            self.statusBar().showMessage(tr("status_connected", bridge_name=bridge_name))
            self.refresh_btn.setEnabled(True); 
            self.remove_bridge_btn.setEnabled(True)
            self.search_lights_btn.setEnabled(True)
            self.backup_action.setEnabled(True)
            self.restore_action.setEnabled(True)
            self.refresh_all_from_bridge()
        except Exception as e: 
            logger.error(f"Could not connect to bridge {ip}: {e}")
            create_message_box(self, icon_error, tr("error_title"), f"Could not connect to {ip}:\n{e}").exec()
        finally: 
            QApplication.restoreOverrideCursor()
            
    def add_bridge_flow(self):
        ip, ok = QInputDialog.getText(self, tr("add_bridge_title"), tr("add_bridge_prompt"))
        if ok and ip:
            self._pair_bridge(ip)
            
    def _pair_bridge(self, ip):
        """Handle the bridge pairing process"""
        try:
            temp_bridge = Bridge(ip)
            if create_message_box(
                self, icon_info, tr("press_button_title"), 
                tr("press_button_prompt", ip=ip), 
                buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel
            ).exec() == QMessageBox.StandardButton.Ok:
                temp_bridge.connect()
                self.add_bridge(ip, temp_bridge.username)
                self.bridge_selector.setCurrentText(ip)
        except Exception as e: 
            logger.error(f"Pairing failed with {ip}: {e}")
            create_message_box(self, icon_error, tr("error_title"), tr("pair_fail_prompt", ip=ip, e=e)).exec()
            
    def remove_selected_bridge(self):
        ip = self.bridge_selector.currentText()
        if ip and create_message_box(
            self, icon_warning, tr("confirm_title"), 
            tr("remove_bridge_prompt", ip=ip), 
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ).exec() == QMessageBox.StandardButton.Yes:
            self.remove_bridge(ip)

    def clear_lists(self): 
        self.lights_list.clear(); 
        self.groups_list.clear(); 
        self.scenes_tree.clear(); 
        self.sensors_list.clear()

    def refresh_all_from_bridge(self):
        if not self.current_bridge: return
        
        # Show progress dialog for long operation
        progress = QProgressDialog(tr("status_loading"), "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setValue(0)
        
        try:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
            self.clear_lists(); 
            self.control_panel.update_display(None, None); 
            QApplication.processEvents()
            progress.setValue(10)
            
            if self.bridge_config:
                bridge_name = self.bridge_config.get('name', self.current_ip)
                bridge_item = QListWidgetItem(icon_bridge, f"Bridge: {bridge_name} ({self.current_ip})")
                bridge_item.setData(Qt.ItemDataRole.UserRole, ("bridge", self.bridge_config)); 
                self.sensors_list.addItem(bridge_item)
            progress.setValue(20)
            
            lights = sorted(self.current_bridge.get_light_objects('list'), key=lambda l: l.name.lower())
            for l in lights: 
                item = QListWidgetItem(icon_light, l.name); 
                item.setData(Qt.ItemDataRole.UserRole, ("light", l)); 
                self.lights_list.addItem(item)
            progress.setValue(40)
            
            groups = sorted([g for g in self.current_bridge.groups if g.group_id != 0], key=lambda g: g.name.lower())
            for g in groups: 
                item = QListWidgetItem(icon_group, g.name); 
                item.setData(Qt.ItemDataRole.UserRole, ("group", g)); 
                self.groups_list.addItem(item)
            progress.setValue(60)
            
            scenes = self.current_bridge.get_scene(); 
            scenes_by_group = {}; 
            other_scenes = []
            group_names = {str(g.group_id): g.name for g in self.current_bridge.groups}
            for sid, sdata in scenes.items():
                gid = sdata.get('group'); 
                s_tuple = (sid, sdata.get("name", f"Scene {sid}"), sdata)
                if gid and gid in group_names: 
                    scenes_by_group.setdefault(gid, []).append(s_tuple)
                else: 
                    other_scenes.append(s_tuple)
            progress.setValue(80)
            
            for gid in sorted(scenes_by_group.keys(), key=lambda g: group_names.get(g, '').lower()):
                group_item = QTreeWidgetItem(self.scenes_tree, [group_names.get(gid, f"Group {gid}")]); 
                group_item.setIcon(0, icon_group)
                for sid, sname, sdata in sorted(scenes_by_group[gid], key=lambda s: s[1].lower()):
                    scene_item = QTreeWidgetItem(group_item, [sname]); 
                    scene_item.setIcon(0, icon_scene); 
                    scene_item.setData(0, Qt.ItemDataRole.UserRole, ("scene", sid))
            if other_scenes:
                other_item = QTreeWidgetItem(self.scenes_tree, [tr("other_scenes")]); 
                other_item.setIcon(0, icon_scene)
                for sid, sname, sdata in sorted(other_scenes, key=lambda s: s[1].lower()):
                    scene_item = QTreeWidgetItem(other_item, [sname]); 
                    scene_item.setIcon(0, icon_scene); 
                    scene_item.setData(0, Qt.ItemDataRole.UserRole, ("scene", sid))
            self.scenes_tree.expandAll()
            progress.setValue(90)

            sensors = sorted(self.current_bridge.get_sensor_objects('list'), key=lambda s: s.name.lower())
            for sensor in sensors:
                stext = sensor.name; 
                item_icon = icon_sensor; 
                add = False; 
                tooltip = f"ID: {sensor.sensor_id}\nType: {sensor.type}\nModel: {sensor.modelid}"
                if sensor.type == 'ZLLTemperature' and 'temperature' in sensor.state:
                    stext += f": {sensor.state['temperature']/100.0:.1f}°C"; 
                    add = True
                elif sensor.type == 'ZLLPresence' and 'presence' in sensor.state:
                    stext += f": {'Motion' if sensor.state['presence'] else 'No motion'}"; 
                    add = True
                elif sensor.type == 'ZLLSwitch':
                    item_icon = icon_dimmer; 
                    add = True
                if add:
                    item = QListWidgetItem(item_icon, stext); 
                    item.setData(Qt.ItemDataRole.UserRole, ("sensor", sensor)); 
                    item.setToolTip(tooltip); 
                    self.sensors_list.addItem(item)
            progress.setValue(100)

        except Exception as e: 
            logger.error(f"Could not load data from bridge: {e}")
            create_message_box(self, icon_error, tr("error_title"), f"Could not load data:\n{e}").exec()
        finally: 
            QApplication.restoreOverrideCursor()
            progress.close()

    def filter_lists(self, text):
        """Filter all lists based on search text"""
        self.filter_lights(text)
        self.filter_groups(text)
        self.filter_scenes(text)
        self.filter_sensors(text)
        
    def filter_lights(self, text):
        """Filter lights list based on search text"""
        for i in range(self.lights_list.count()):
            item = self.lights_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def filter_groups(self, text):
        """Filter groups list based on search text"""
        for i in range(self.groups_list.count()):
            item = self.groups_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def filter_scenes(self, text):
        """Filter scenes tree based on search text"""
        def filter_tree_item(item, text):
            hidden = text and text.lower() not in item.text(0).lower()
            item.setHidden(0, hidden)
            
            # Show parent if any child is visible
            for i in range(item.childCount()):
                child = item.child(i)
                if not filter_tree_item(child, text):
                    hidden = False
                    
            item.setHidden(0, hidden)
            return hidden
            
        for i in range(self.scenes_tree.topLevelItemCount()):
            item = self.scenes_tree.topLevelItem(i)
            filter_tree_item(item, text)
            
    def filter_sensors(self, text):
        """Filter sensors list based on search text"""
        for i in range(self.sensors_list.count()):
            item = self.sensors_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def handle_light_selection(self, item):
        if item: self.control_panel.update_display('light', item.data(Qt.ItemDataRole.UserRole)[1])
        
    def handle_group_selection(self, item):
        if item: self.control_panel.update_display('group', item.data(Qt.ItemDataRole.UserRole)[1])
        
    def handle_scene_selection(self, item, column):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data and data[0] == 'scene': self.activate_scene(data[1], item.text(0))
        
    def handle_sensor_selection(self, item):
        if item: 
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and data[0] == 'sensor':
                logger.info(f"Selected sensor: {item.text()}")

    def activate_scene(self, scene_id, scene_name):
        if not self.current_bridge: return
        try:
            self.current_bridge.set_group(0, 'scene', scene_id)
            QTimer.singleShot(500, lambda: self.control_panel.update_display(self.control_panel.target_type, self.control_panel.current_target) if self.control_panel.current_target else None)
        except Exception as e:
            logger.error(f"Could not activate scene {scene_name}: {e}")
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
        except Exception as e: 
            logger.error(f"Could not fetch device info: {e}")
            create_message_box(self, icon_error, tr("error_title"), f"Could not fetch info:\n{e}").exec()
    
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
            try: 
                self.current_bridge.create_group(name, light_ids); 
                self.refresh_all_from_bridge()
            except Exception as e: 
                logger.error(f"Could not create group: {e}")
                create_message_box(self, icon_error, tr("error_title"), tr("create_group_fail", e=e)).exec()
                
    def edit_group(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        dialog = GroupEditorDialog(self, self.current_bridge, existing_group=group_obj)
        if dialog.exec():
            name, light_ids = dialog.get_selected_data()
            if not name: create_message_box(self, icon_warning, tr("warning_title"), tr("no_name_warning")).exec(); return
            try: 
                self.current_bridge.set_group(group_obj.group_id, {'name': name, 'lights': light_ids}); 
                self.refresh_all_from_bridge()
            except Exception as e: 
                logger.error(f"Could not edit group: {e}")
                create_message_box(self, icon_error, tr("error_title"), tr("edit_group_fail", e=e)).exec()
                
    def delete_group(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        if create_message_box(
            self, icon_warning, tr("confirm_title"), 
            tr("delete_group_prompt", group_name=group_obj.name), 
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ).exec() == QMessageBox.StandardButton.Yes:
            try: 
                self.current_bridge.delete_group(group_obj.group_id); 
                self.refresh_all_from_bridge()
            except Exception as e: 
                logger.error(f"Could not delete group: {e}")
                create_message_box(self, icon_error, tr("error_title"), tr("delete_group_fail", e=e)).exec()
                
    def save_group_as_scene(self, item):
        if not self.current_bridge or not item: return
        _, group_obj = item.data(Qt.ItemDataRole.UserRole)
        scene_name, ok = QInputDialog.getText(self, tr("save_scene_title"), tr("save_scene_prompt", group_name=group_obj.name))
        if ok and scene_name:
            try:
                result = self.current_bridge.create_group_scene(group_obj.group_id, scene_name)
                logger.info(f"Result from create_group_scene: {result}")
                create_message_box(self, icon_info, tr("info_title"), tr("save_scene_success", scene_name=scene_name)).exec()
                self.refresh_all_from_bridge()
            except Exception as e:
                logger.error(f"Could not save scene: {e}")
                create_message_box(self, icon_error, tr("error_title"), tr("save_scene_fail", e=e)).exec()

    def backup_settings(self):
        if not self.current_bridge: return
        try:
            filename, _ = QFileDialog.getSaveFileName(self, tr("backup_dialog_title"), f"hue_backup_{self.current_ip}.json", "JSON Files (*.json)")
            if not filename: return
            
            config = self.current_bridge.get_api()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            create_message_box(self, icon_info, tr("info_title"), tr("backup_success", filename=os.path.basename(filename))).exec()
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            create_message_box(self, icon_error, tr("error_title"), tr("backup_fail", e=e)).exec()

    def restore_settings(self):
        if not self.current_bridge: return
        try:
            filename, _ = QFileDialog.getOpenFileName(self, tr("restore_dialog_title"), "", "JSON Files (*.json)")
            if not filename: return

            if create_message_box(self, icon_warning, tr("confirm_title"), tr("restore_confirm", filename=os.path.basename(filename)), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No).exec() != QMessageBox.StandardButton.Yes:
                return

            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # This is a simplified restore. A real restore is very complex.
            # We will just restore the lights, groups, scenes for this example.
            if 'lights' in config:
                for light_id, data in config['lights'].items():
                    self.current_bridge.set_light(int(light_id), {'name': data['name']})
            if 'groups' in config:
                 for group_id, data in config['groups'].items():
                    self.current_bridge.set_group(int(group_id), {'name': data['name'], 'lights': data['lights']})
            
            create_message_box(self, icon_info, tr("info_title"), tr("restore_success")).exec()
            self.refresh_all_from_bridge()

        except Exception as e:
            logger.error(f"Restore failed: {e}")
            create_message_box(self, icon_error, tr("error_title"), tr("restore_fail", e=e)).exec()

    def search_for_lights(self):
        if not self.current_bridge: return
        
        menu = QMenu(self)
        menu.setStyleSheet(self.styleSheet())
        
        search_action = QAction("Normal Search", self)
        search_action.triggered.connect(self._start_light_search)
        menu.addAction(search_action)
        
        touchlink_action = QAction("Touchlink (Wink)", self)
        touchlink_action.triggered.connect(self._start_touchlink_search)
        menu.addAction(touchlink_action)
        
        menu.exec(self.search_lights_btn.mapToGlobal(self.search_lights_btn.rect().bottomLeft()))

    def _start_light_search(self):
        try:
            progress = QProgressDialog(tr("search_lights_title"), "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            
            QApplication.processEvents() # Allow GUI to update
            
            initial_lights = set(self.current_bridge.get_light_objects('id'))
            # Correct way to start a search via API
            self.current_bridge.request('POST', f'/api/{self.current_bridge.username}/lights')
            
            time.sleep(45) # Give bridge time to search
            
            final_lights = set(self.current_bridge.get_light_objects('id'))
            
            progress.close()
            
            new_lights = final_lights - initial_lights
            
            if new_lights:
                create_message_box(self, icon_info, tr("info_title"), tr("search_lights_success", count=len(new_lights))).exec()
                self.refresh_all_from_bridge()
            else:
                create_message_box(self, icon_info, tr("info_title"), tr("search_lights_none")).exec()

        except Exception as e:
            logger.error(f"Light search failed: {e}")
            create_message_box(self, icon_error, tr("error_title"), tr("search_lights_fail", e=e)).exec()

    def _start_touchlink_search(self):
        if create_message_box(self, icon_warning, tr("touchlink_confirm_title"), tr("touchlink_confirm_text"), buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No).exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            # Correct way to start touchlink via API
            self.current_bridge.request('PUT', f'/api/{self.current_bridge.username}/config', {'touchlink': True})
            create_message_box(self, icon_info, tr("info_title"), tr("touchlink_started")).exec()
            # User should check for new lights after a minute or so
            QTimer.singleShot(60000, self.refresh_all_from_bridge)
        except Exception as e:
            logger.error(f"Touchlink failed: {e}")
            create_message_box(self, icon_error, tr("error_title"), f"Touchlink failed:\n{e}").exec()


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
