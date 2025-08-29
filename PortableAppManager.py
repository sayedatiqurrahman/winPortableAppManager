import sys
import subprocess
import shlex
import re
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QScrollArea, QGridLayout, QFrame, QCheckBox,
    QProgressBar, QTextEdit, QToolButton, QSizePolicy, QSpacerItem
)

# --------------------------
# Configuration / App List
# --------------------------
APPS = [
    # Browsers
    {"Name": "Google Chrome", "Id": "Google.Chrome", "Category": "Browsers"},
    {"Name": "Mozilla Firefox", "Id": "Mozilla.Firefox", "Category": "Browsers"},
    {"Name": "Microsoft Edge", "Id": "Microsoft.Edge", "Category": "Browsers"},
    {"Name": "Brave", "Id": "Brave.Brave", "Category": "Browsers"},
    {"Name": "Opera", "Id": "Opera.Opera", "Category": "Browsers"},
    # Messaging
    {"Name": "WhatsApp Desktop", "Id": "WhatsApp.WhatsApp", "Category": "Messaging"},
    {"Name": "Telegram Desktop", "Id": "Telegram.TelegramDesktop", "Category": "Messaging"},
    {"Name": "Discord", "Id": "Discord.Discord", "Category": "Messaging"},
    {"Name": "Zoom", "Id": "Zoom.Zoom", "Category": "Messaging"},
    {"Name": "Skype", "Id": "Microsoft.Skype", "Category": "Messaging"},
    {"Name": "Slack", "Id": "SlackTechnologies.Slack", "Category": "Messaging"},
    # Multimedia / Design
    {"Name": "VLC Media Player", "Id": "VideoLAN.VLC", "Category": "Multimedia"},
    {"Name": "Spotify", "Id": "Spotify.Spotify", "Category": "Multimedia"},
    {"Name": "OBS Studio", "Id": "OBSProject.OBSStudio", "Category": "Multimedia"},
    {"Name": "GIMP", "Id": "GIMP.GIMP", "Category": "Multimedia"},
    {"Name": "Paint.NET", "Id": "dotPDN.Paint.NET", "Category": "Multimedia"},
    {"Name": "Audacity", "Id": "Audacity.Audacity", "Category": "Multimedia"},
    {"Name": "PotPlayer", "Id": "DAUM.PotPlayer", "Category": "Multimedia"},
    {"Name": "foobar2000", "Id": "foobar2000.foobar2000", "Category": "Multimedia"},
    {"Name": "Krita", "Id": "Krita.Krita", "Category": "Design"},
    {"Name": "Inkscape", "Id": "Inkscape.Inkscape", "Category": "Design"},
    {"Name": "Blender", "Id": "BlenderFoundation.Blender", "Category": "Design"},
    {"Name": "Aseprite", "Id": "Aseprite.Aseprite", "Category": "Design"},
    # Development / AI
    {"Name": "Visual Studio Code", "Id": "Microsoft.VisualStudioCode", "Category": "Development"},
    {"Name": "Git", "Id": "Git.Git", "Category": "Development"},
    {"Name": "Node.js LTS", "Id": "OpenJS.NodeJS.LTS", "Category": "Development"},
    {"Name": "Python 3", "Id": "Python.Python.3", "Category": "Development"},
    {"Name": "Java", "Id": "Oracle.JavaRuntimeEnvironment", "Category": "Development"},
    {"Name": "Docker Desktop", "Id": "Docker.DockerDesktop", "Category": "Development"},
    {"Name": "Postman", "Id": "Postman.Postman", "Category": "Development"},
    {"Name": "IntelliJ IDEA Community", "Id": "JetBrains.IntelliJIDEA.Community", "Category": "Development"},
    {"Name": "PyCharm Community", "Id": "JetBrains.PyCharm.Community", "Category": "Development"},
    {"Name": "Eclipse IDE", "Id": "EclipseAdoptium.EclipseIDE", "Category": "Development"},
    {"Name": "NetBeans IDE", "Id": "Apache.NetBeans", "Category": "Development"},
    {"Name": "Visual Studio Community", "Id": "Microsoft.VisualStudio.Community", "Category": "Development"},
    {"Name": "Sublime Text", "Id": "SublimeHQ.SublimeText", "Category": "Development"},
    {"Name": "Atom Editor", "Id": "GitHub.Atom", "Category": "Development"},
    {"Name": "Notepad++", "Id": "Notepad++.Notepad++", "Category": "Development"},
    {"Name": "MongoDB Compass", "Id": "MongoDB.Compass", "Category": "Development"},
    {"Name": "MySQL Workbench", "Id": "Oracle.MySQLWorkbench", "Category": "Development"},
    {"Name": "DBeaver Community", "Id": "DBeaver.DBeaver", "Category": "Development"},
    {"Name": "SQLiteStudio", "Id": "SQLite.SQLiteStudio", "Category": "Development"},
    {"Name": "XAMPP", "Id": "ApacheFriends.XAMPP", "Category": "Development"},
    {"Name": "Anaconda", "Id": "Anaconda.Anaconda", "Category": "AI/ML"},
    {"Name": "Miniconda", "Id": "Miniconda.Miniconda3", "Category": "AI/ML"},
    {"Name": "Power BI Desktop", "Id": "Microsoft.PowerBIDesktop", "Category": "AI/ML"},
    {"Name": "Jupyter Notebook", "Id": "Jupyter.JupyterLab", "Category": "AI/ML"},
    {"Name": "R Studio", "Id": "RProject.RStudio", "Category": "AI/ML"},
    {"Name": "TensorFlow", "Id": "Google.TensorFlow", "Category": "AI/ML"},
    {"Name": "PyTorch", "Id": "PyTorch.PyTorch", "Category": "AI/ML"},
    {"Name": "Keras", "Id": "Keras.Keras", "Category": "AI/ML"},
    {"Name": "Weka", "Id": "UniversityOfWaikato.Weka", "Category": "AI/ML"},
    {"Name": "RapidMiner Studio", "Id": "RapidMiner.RapidMinerStudio", "Category": "AI/ML"},
    {"Name": "Orange Data Mining", "Id": "OrangeDataMining.Orange", "Category": "AI/ML"},
    {"Name": "KNIME Analytics Platform", "Id": "KNIME.KNIMEAnalyticsPlatform", "Category": "AI/ML"},
    {"Name": "MATLAB Runtime", "Id": "MathWorks.MATLABRuntime", "Category": "AI/ML"},
    {"Name": "Google Colab (Shortcut)", "Id": "Google.Colab", "Category": "AI/ML"},
    # Utilities
    {"Name": "7-Zip", "Id": "7zip.7zip", "Category": "Utilities"},
    {"Name": "WinRAR", "Id": "RARLab.WinRAR", "Category": "Utilities"},
    {"Name": "Notepad++", "Id": "Notepad++.Notepad++", "Category": "Utilities"},
    {"Name": "Everything Search", "Id": "Voidtools.Everything", "Category": "Utilities"},
    {"Name": "CCleaner", "Id": "Piriform.CCleaner", "Category": "Utilities"},
    {"Name": "ShareX", "Id": "ShareX.ShareX", "Category": "Utilities"},
    {"Name": "PowerToys", "Id": "Microsoft.PowerToys", "Category": "Utilities"},
    # Office
    {"Name": "LibreOffice", "Id": "TheDocumentFoundation.LibreOffice", "Category": "Office"},
    {"Name": "OnlyOffice Desktop Editors", "Id": "Ascensio.OnlyOffice", "Category": "Office"},
    {"Name": "Microsoft To Do", "Id": "Microsoft.Todos", "Category": "Office"},
    {"Name": "Evernote", "Id": "Evernote.Evernote", "Category": "Office"},
    {"Name": "Google Drive", "Id": "Google.Drive", "Category": "Office"},
    {"Name": "Dropbox", "Id": "Dropbox.Dropbox", "Category": "Office"},
    # Gaming
    {"Name": "Steam", "Id": "Valve.Steam", "Category": "Gaming"},
    {"Name": "Epic Games Launcher", "Id": "EpicGames.EpicGamesLauncher", "Category": "Gaming"},
    {"Name": "Origin", "Id": "ElectronicArts.Origin", "Category": "Gaming"},
    {"Name": "Battle.net", "Id": "Blizzard.BattleNet", "Category": "Gaming"},
    {"Name": "GeForce Experience", "Id": "NVIDIA.GeForceExperience", "Category": "Gaming"},
    {"Name": "MSI Afterburner", "Id": "MSI.Afterburner", "Category": "Gaming"},
    {"Name": "Razer Synapse", "Id": "Razer.RazerSynapse", "Category": "Gaming"},
    # PC Test
    {"Name": "CPU-Z", "Id": "CPUID.CPU-Z", "Category": "PC Test"},
    {"Name": "HWMonitor", "Id": "CPUID.HWMonitor", "Category": "PC Test"},
    {"Name": "CrystalDiskInfo", "Id": "CrystalDewWorld.CrystalDiskInfo", "Category": "PC Test"},
    {"Name": "GPU-Z", "Id": "TechPowerUp.GPU-Z", "Category": "PC Test"},
    {"Name": "Cinebench", "Id": "Maxon.Cinebench", "Category": "PC Test"},
    {"Name": "3DMark", "Id": "UL.3DMark", "Category": "PC Test"},
    {"Name": "PCMark 10", "Id": "UL.PCMark10", "Category": "PC Test"},
    {"Name": "FurMark", "Id": "Geeks3D.FurMark", "Category": "PC Test"},
    {"Name": "OCCT", "Id": "OCBase.OCCT", "Category": "PC Test"},
    {"Name": "PassMark PerformanceTest", "Id": "PassMark.PerformanceTest", "Category": "PC Test"},
    {"Name": "AIDA64 Extreme", "Id": "FinalWire.AIDA64Extreme", "Category": "PC Test"},
    {"Name": "UserBenchmark", "Id": "UserBenchmark.UserBenchmark", "Category": "PC Test"},
    {"Name": "Prime95", "Id": "GIMPS.Prime95", "Category": "PC Test"},
    {"Name": "MemTest86", "Id": "PassMark.MemTest86", "Category": "PC Test"},
    {"Name": "SiSoftware Sandra", "Id": "SiSoftware.Sandra", "Category": "PC Test"},
]

# --------------------------
# Winget helpers (robust parsing)
# --------------------------
def run_cmd(cmd: str):
    """Run a shell command and return CompletedProcess"""
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def parse_winget_search_output(output: str):
    """
    Parses winget search output lines with regex:
    - matches lines like: Name  <spaces> Id
    - Name might contain spaces, Id is usually last token with no spaces
    """
    items = []
    lines = output.splitlines()
    # skip potential header lines until a line that looks like data exists
    for ln in lines:
        ln = ln.rstrip()
        if not ln:
            continue
        # attempt to capture: name (anything) then 2+ spaces then id (last token)
        m = re.match(r'^(?P<name>.+?)\s{2,}(?P<id>\S+)(?:\s.*)?$', ln)
        if m:
            name = m.group('name').strip()
            appid = m.group('id').strip()
            items.append({"Name": name, "Id": appid, "Category": "Winget"})
    return items

def winget_search_apps(query: str):
    try:
        res = run_cmd(f'winget search {shlex.quote(query)}')
        return parse_winget_search_output(res.stdout)
    except Exception:
        return []

def winget_list_installed():
    try:
        res = run_cmd('winget list')
        # parse similar to search
        return parse_winget_search_output(res.stdout)
    except Exception:
        return []

def winget_is_installed(app_id: str) -> bool:
    res = run_cmd(f'winget list --id {shlex.quote(app_id)} --exact')
    return app_id.lower() in (res.stdout or "").lower()

def winget_install_or_update(app_id: str):
    # run install or upgrade, return CompletedProcess
    if winget_is_installed(app_id):
        return run_cmd(f'winget upgrade --id {shlex.quote(app_id)} --exact --silent --accept-package-agreements --accept-source-agreements')
    else:
        return run_cmd(f'winget install --id {shlex.quote(app_id)} --exact --silent --accept-package-agreements --accept-source-agreements')

def winget_uninstall(app_id: str):
    return run_cmd(f'winget uninstall --id {shlex.quote(app_id)} --exact --silent')

# --------------------------
# Worker thread
# --------------------------
class WorkerThread(QThread):
    progress_signal = Signal(str, int)     # message, percent
    finished_signal = Signal(str)          # summary
    def __init__(self, tasks, action_label):
        super().__init__()
        self.tasks = tasks[:]  # list of app ids
        self.action_label = action_label
        self._cancelled = False

    def run(self):
        total = len(self.tasks) if self.tasks else 1
        for idx, app_id in enumerate(self.tasks):
            if self._cancelled:
                self.progress_signal.emit("Cancelled by user", 0)
                self.finished_signal.emit("Cancelled")
                return
            msg = f"{self.action_label} {app_id}..."
            percent = int((idx / total) * 100)
            # emit start message
            self.progress_signal.emit(msg, percent)
            # perform action
            try:
                if self.action_label == "Uninstalling":
                    winget_uninstall(app_id)
                else:
                    winget_install_or_update(app_id)
                self.progress_signal.emit(f"{self.action_label} done for {app_id}", min(99, percent + 10))
            except Exception as e:
                self.progress_signal.emit(f"Error for {app_id}: {e}", min(99, percent + 10))
        self.progress_signal.emit(f"{self.action_label} Completed", 100)
        self.finished_signal.emit("Done")

    def cancel(self):
        self._cancelled = True


# --------------------------
# UI: App Manager
# --------------------------
class AppManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Portable App Manager")
        self.setWindowIcon(QIcon("headIcon.ico"))
        self.resize(1100, 700)
        self.setStyleSheet("""
            * {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
            }
            QWidget {
                background-color: #1a1a1a;
                color: #e8e8e8;
            }
            QTabWidget::pane { border: 1px solid #333; }
            QTabWidget::tab-bar { left: 5px; }
            QTabBar::tab {
                background: #2a2a2a;
                color: #c0c0c0;
                border: 1px solid #333;
                border-bottom-color: #1a1a1a;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
                padding: 8px 15px;
            }
            QTabBar::tab:selected {
                background: #1a1a1a;
                color: #f0f0f0;
                border-bottom: none;
            }
            QLineEdit, QTextEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444;
                padding: 6px;
                border-radius: 6px;
            }
            QPushButton {
                background-color: #1f6feb;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2b7afb;
            }
            QPushButton.secondary {
                background-color: #444;
                color: #ddd;
            }
            QPushButton.secondary:hover {
                background-color: #555;
            }
            QToolButton {
                border: none;
                background-color: transparent;
            }
            QTreeWidget {
                background-color: #1e1e1e;
                color: #e8e8e8;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 5px;
            }
            QTreeWidget::item {
                padding: 5px 0;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #444;
            }
            .category-header {
                font-weight: bold;
                font-size: 13pt;
                color:#9ad;
                padding: 5px;
            }
            .app-card {
                background-color:#2a2a2a;
                border-radius:8px;
                padding:8px;
            }
            .app-card:hover {
                background-color:#333;
            }
            .icon-background {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 5px;
            }
        """)
        self.task_queue = []
        self.worker = None

        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        self.setup_winget_tab()
        self.setup_explore_tab()
        self.setup_installed_tab()
        self.setup_progress_tab()
        self.tabs.setTabIcon(0, self.get_svg_icon(self.get_svg_string("search")))
        self.tabs.setTabIcon(1, self.get_svg_icon(self.get_svg_string("explore")))
        self.tabs.setTabIcon(2, self.get_svg_icon(self.get_svg_string("installed")))
        self.tabs.setTabIcon(3, self.get_svg_icon(self.get_svg_string("progress")))

        # Set "Explore / Browse" as the default tab
        self.tabs.setCurrentIndex(1)


    def get_svg_string(self, name):
        svg_icons = {
            "app_icon": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#1f6feb"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "search": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-search"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>""",
            "explore": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-compass"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>""",
            "installed": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-package"><line x1="16.5" y1="9.4" x2="7.5" y2="4.21"></line><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>""",
            "progress": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-activity"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>""",
            "collapsed": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>""",
            "expanded": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#9ad" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14M5 12h14"/></svg>""",
            "default": """<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#b0b0b0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-box"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>""",
            "refresh": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-refresh-cw"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.5 15.2c-1.3-1.6-2-3.6-2-5.7 0-5.5 4.5-10 10-10s10 4.5 10 10-4.5 10-10 10c-1.6 0-3.1-.4-4.5-1.2"></path></svg>""",
            "update": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-upload-cloud"><polyline points="16 16 12 12 8 16"></polyline><line x1="12" y1="12" x2="12" y2="21"></line><path d="M20.39 18.39A5 5 0 0 0 18 10h-1.26A8 8 0 1 0 4 18.39"></path></svg>""",
            "uninstall": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#e8e8e8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-trash-2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>""",
            "chrome": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f44336" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2.07 14.93A8.01 8.01 0 0 1 4.58 8.42L12 12l-2.07 4.93zM12 4c2.68 0 5.16 1.1 6.92 2.88L12 12V4zm8 8a8.01 8.01 0 0 1-2.07 5.93L12 12l8-8v8z"></path></svg>""",
            "firefox": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ff9800" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18a8 8 0 0 1-5.66-2.34L12 12V4h.01c.71 0 1.34.1 1.95.27A8 8 0 0 1 12 20z"></path><path fill="#ff5722" d="M12 4.01V12l5.66 5.66A8 8 0 0 0 12 4.01z"></path></svg>""",
            "edge": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#0078d7" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 13.5l-4.5 4.5L12 12l4.5 4.5L12 22 7.5 17.5z"></path></svg>""",
            "brave": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fb542b" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.5 12.5a2.5 2.5 0 1 1-5 0h5zM12 16a4 4 0 1 0 0-8 4 4 0 0 0 0 8z"></path></svg>""",
            "opera": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ff1f1f" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM12 18a6 6 0 1 1 0-12 6 6 0 0 1 0 12z"></path></svg>""",
            "whatsapp": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#25d366" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10h1l.5.5.5-.5h.5c.3 0 .6-.1.8-.3L21 16.5c.3-.3.3-.8 0-1.1L12.7 5.7c-.3-.3-.8-.3-1.1 0L3 13.3c-.3.3-.3.8 0 1.1L8.5 20l.5.5c.3.3.8.3 1.1 0L17 12.7c.3-.3.3-.8 0-1.1L13.3 4.5c-.3-.3-.8-.3-1.1 0L4.5 13.3c-.3.3-.3.8 0 1.1L12.7 20z"></path></svg>""",
            "telegram": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#0088cc" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.3 8.8l-7.3 3.3c-.3.1-.6.1-.8-.1-.2-.2-.2-.5 0-.7l3.6-2.5c.2-.1.2-.4 0-.5l-3.6-2.5c-.2-.1-.2-.4 0-.5.2-.2.5-.2.8-.1l7.3 3.3c.3.1.6.1.8.1.2.2.2.5 0 .7l-3.6 2.5c-.2.1-.2.4 0 .5l3.6 2.5c.2.1.2.4 0 .5-.2.2-.5.2-.8.1z"></path></svg>""",
            "discord": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#7289da" d="M20 2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2.8 5.7c-.6 0-1.2.2-1.7.5-.5.3-.9.7-1.2 1.2-.4.5-.6 1.1-.6 1.8 0 .6.2 1.2.6 1.7.3.5.7.9 1.2 1.2.5.3 1.1.5 1.7.5s1.2-.2 1.7-.5c.5-.3.9-.7 1.2-1.2.4-.5.6-1.1.6-1.7 0-.7-.2-1.3-.6-1.8-.3-.5-.7-.9-1.2-1.2-.5-.3-1.1-.5-1.7-.5zm-4 8.6c.6 0 1.2-.2 1.7-.5.5-.3.9-.7 1.2-1.2.4-.5.6-1.1.6-1.7 0-.7-.2-1.3-.6-1.8-.3-.5-.7-.9-1.2-1.2-.5-.3-1.1-.5-1.7-.5s-1.2.2-1.7.5c-.5.3-.9.7-1.2 1.2-.4.5-.6 1.1-.6 1.7 0 .7.2 1.3.6 1.8.3.5.7.9 1.2 1.2.5.3 1.1.5 1.7.5z"></path></svg>""",
            "zoom": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#2d8cff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm5 11h-4v4h-2v-4H7v-2h4V7h2v4h4v2z"></path></svg>""",
            "skype": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#00aff0" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14h-2v-4h-4V8h4V4h2v4h4v4h-4v4z"></path></svg>""",
            "slack": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#e01e5a" d="M15.5 10c-.8 0-1.5-.7-1.5-1.5v-2c0-.8.7-1.5 1.5-1.5s1.5.7 1.5 1.5v2c0 .8-.7 1.5-1.5 1.5z"></path><path fill="#2eb67d" d="M10 14.5c0 .8.7 1.5 1.5 1.5h2c.8 0 1.5-.7 1.5-1.5s-.7-1.5-1.5-1.5h-2c-.8 0-1.5.7-1.5 1.5z"></path><path fill="#ecb22e" d="M10 10c0-.8-.7-1.5-1.5-1.5H7c-.8 0-1.5.7-1.5 1.5v2c0 .8.7 1.5 1.5 1.5h2c.8 0 1.5-.7 1.5-1.5z"></path><path fill="#36c5f0" d="M14.5 10c.8 0 1.5-.7 1.5-1.5V7c0-.8-.7-1.5-1.5-1.5H12c-.8 0-1.5.7-1.5 1.5v2c0 .8.7 1.5 1.5 1.5z"></path></svg>""",
            "vlc": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ff8c00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM10 16.5v-9L17 12l-7 4.5z"></path></svg>""",
            "spotify": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#1ed760" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm2.14 15.65c-.24.08-.49.12-.73.12-.24 0-.49-.04-.73-.12-.48-.15-.79-.64-.64-1.12.15-.48.64-.79 1.12-.64.12.04.24.08.36.08.12 0 .24-.04.36-.08.48-.15.79.64.64 1.12zm3.32-3.32c-.3-.1-.6-.15-.9-.15s-.6.05-.9.15c-.6.2-.9.8-.7 1.4.2.6.8.9 1.4.7.3-.1.6-.15.9-.15.3 0 .6.05.9.15.6.2.9-.8.7-1.4zM12 4.4c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm-2 13.6c-1.3 0-2.6-.4-3.7-1.2-.5-.4-.7-1.1-.4-1.7.3-.6.9-.8 1.5-.5.8.6 1.8 1 2.8 1s2-.4 2.8-1c.6-.3 1.2-.1 1.5.5.3.6.1 1.3-.4 1.7-1.1.8-2.4 1.2-3.7 1.2zm7.4-4c-1.1 0-2.2-.3-3.2-.8-.6-.3-1.3-.1-1.7.5-.4.6-.2 1.3.4 1.7 1.3.7 2.8 1.1 4.3 1.1s3-.4 4.3-1.1c.6-.3.8-1 .4-1.7-.4-.6-1-.8-1.7-.5-1 .5-2 .8-3.2.8z"></path></svg>""",
            "obs": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#3f51b5" d="M20 5h-3.17L15 3H9L7.17 5H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm-8 13c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"></path></svg>""",
            "gimp": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#555" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-4.5-8.5c.83 0 1.5-.67 1.5-1.5s-.67-1.5-1.5-1.5-1.5.67-1.5 1.5.67 1.5 1.5 1.5zM12 12c-2.76 0-5 2.24-5 5h10c0-2.76-2.24-5-5-5zm0-2c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5z"></path></svg>""",
            "paint.net": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f44336" d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path><path fill="#4285f4" d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-7h-2v7H6V4h8V2z"></path></svg>""",
            "audacity": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ff5722" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15H8v-2h2v2zm2 0h-2v-4h2v4zm2 0h-2v-6h2v6zm2 0h-2v-8h2v8zm2 0h-2v-10h2v10z"></path></svg>""",
            "krita": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#3f51b5" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM9 17.5l-2-2 3-3 2 2-3 3zm3-3.5l2-2 3-3-2-2-3 3-2 2zm3-3.5l-2-2 3-3 2 2-3 3z"></path></svg>""",
            "inkscape": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#009688" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path><path fill="#ff9800" d="M12 4c-4.41 0-8 3.59-8 8s3.59 8 8 8 8-3.59 8-8-3.59-8-8-8zm0 16c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"></path><path fill="#fff" d="M14 10h-4v4h4v-4zm-2 2l2-2h-4l2 2z"></path></svg>""",
            "blender": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f57c00" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7 16l-3 3c-1.1 1.1-1.1 2.89 0 4s2.89 1.1 4 0l3-3-4-4z"></path></svg>""",
            "vscode": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#007acc" d="M22 12L16 6v12l6-6zM8 6L2 12l6 6V6z"></path><path fill="#4285f4" d="M12 22l-6-6h12l6-6-6-6-6 6z"></path></svg>""",
            "git": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f44d27" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm6 16c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm-6-2.5c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2zm-6-2.5c1.1 0 2 .9 2 2s-.9 2-2 2-2-.9-2-2 .9-2 2-2z"></path></svg>""",
            "nodejs": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#339933" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8V8H8v6z"></path><path fill="#fff" d="M8 8h8v6H8z"></path></svg>""",
            "python": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#3776ab" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2 4c.6 0 1.1-.2 1.5-.6.4-.4.6-.9.6-1.5s-.2-1.1-.6-1.5c-.4-.4-.9-.6-1.5-.6-.6 0-1.1.2-1.5.6-.4.4-.6.9-.6 1.5s.2 1.1.6 1.5c.4.4.9.6 1.5.6zm10 0c-.6 0-1.1-.2-1.5-.6-.4-.4-.6-.9-.6-1.5s.2-1.1.6-1.5c.4-.4.9-.6 1.5-.6.6 0 1.1.2 1.5.6.4.4.6.9.6 1.5s-.2 1.1-.6 1.5c-.4.4-.9.6-1.5.6z"></path></svg>""",
            "java": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f44336" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm2 14c-.6 0-1.1-.2-1.5-.6-.4-.4-.6-.9-.6-1.5s.2-1.1.6-1.5c.4-.4.9-.6 1.5-.6.6 0 1.1.2 1.5.6.4.4.6.9.6 1.5s-.2 1.1-.6 1.5c-.4.4-.9.6-1.5.6zm-4-4c-.6 0-1.1-.2-1.5-.6-.4-.4-.6-.9-.6-1.5s.2-1.1.6-1.5c.4-.4.9-.6 1.5-.6.6 0 1.1.2 1.5.6.4.4.6.9.6 1.5s-.2 1.1-.6 1.5c-.4.4-.9.6-1.5.6zm4-4c-.6 0-1.1-.2-1.5-.6-.4-.4-.6-.9-.6-1.5s.2-1.1.6-1.5c.4-.4.9-.6 1.5-.6.6 0 1.1.2 1.5.6.4.4.6.9.6 1.5s-.2 1.1-.6 1.5c-.4.4-.9.6-1.5.6z"></path></svg>""",
            "docker": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#0db7ed" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "postman": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ff6c37" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM7 16l-3 3c-1.1 1.1-1.1 2.89 0 4s2.89 1.1 4 0l3-3-4-4z"></path><path fill="#ff6c37" d="M17 8.5L12 11l5-2.5V8.5zM12 11l-5-2.5V8.5l5 2.5zM12 11l5-2.5L12 6z"></path></svg>""",
            "intellij": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#f44336" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "pycharm": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#ffeb3b" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path><path fill="#000" d="M12 22l6-6-6-6-6 6 6 6z"></path></svg>""",
            "anaconda": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#4285f4" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "7zip": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "winrar": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2zm-2-4h16v2H4v-2z"></path></svg>""",
            "notepad++": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#9c27b0" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "everything": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#03a9f4" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "ccleaner": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#4caf50" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "sharex": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#e91e63" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "powertoys": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#673ab7" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "libreoffice": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#1a73e8" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zM12 18c-3.31 0-6-2.69-6-6h12c0 3.31-2.69 6-6 6z"></path></svg>""",
            "steam": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#000" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 10c0-2.21 1.79-4 4-4s4 1.79 4 4-1.79 4-4 4-4-1.79-4-4zm8 0c0-2.21-1.79-4-4-4v8c2.21 0 4-1.79 4-4z"></path></svg>""",
            "epicgames": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4 10l-4-4V6l4 4-4 4V18l4-4V10z"></path></svg>""",
            "battle.net": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#00a2ff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "cpuz": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
            "hwmonitor": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="#fff" d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-4 12h8v2H8v-2zm-2-4h12v2H6v-2z"></path></svg>""",
        }
        return svg_icons.get(name, svg_icons["default"])

    def get_svg_icon(self, svg_string: str, size: int = 20, bg_color: QColor = QColor("transparent"), padding: int = 0):
        # Create a pixmap for the final icon
        pixmap_size = size + 2 * padding
        pixmap = QPixmap(pixmap_size, pixmap_size)
        pixmap.fill(Qt.transparent)

        # Draw the background if a color is provided
        if bg_color.isValid() and bg_color.alpha() > 0:
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(Qt.NoPen))
            painter.drawRoundedRect(0, 0, pixmap_size, pixmap_size, 10, 10)
            painter.end()

        # Render the SVG on top
        renderer = QSvgRenderer(svg_string.encode('utf-8'))
        icon_pixmap = QPixmap(size, size)
        icon_pixmap.fill(Qt.transparent)
        painter = QPainter(icon_pixmap)
        renderer.render(painter)
        painter.end()

        # Combine background and icon
        final_painter = QPainter(pixmap)
        final_painter.drawPixmap(padding, padding, icon_pixmap)
        final_painter.end()
        
        return QIcon(pixmap)

    # ---------------- Winget Search Tab ----------------
    def setup_winget_tab(self):
        self.tab_winget = QWidget()
        self.tabs.addTab(self.tab_winget, "Winget Search")
        
        l = QVBoxLayout(self.tab_winget)
        top = QHBoxLayout()
        self.search_winget = QLineEdit()
        self.search_winget.setPlaceholderText("Type to search winget...")
        
        self.btn_winget_search = QPushButton("Search")
        self.btn_winget_search.setProperty("class", "secondary")
        self.btn_winget_search.setIcon(self.get_svg_icon(self.get_svg_string("search"), 16))
        self.btn_winget_search.clicked.connect(self.on_winget_search)

        self.btn_winget_install = QPushButton("Install Selected")
        self.btn_winget_install.setIcon(self.get_svg_icon(self.get_svg_string("installed"), 16))
        self.btn_winget_install.clicked.connect(self.on_winget_install_selected)
        
        top.addWidget(self.search_winget, 1)
        top.addWidget(self.btn_winget_search)
        top.addWidget(self.btn_winget_install)
        l.addLayout(top)

        self.tree_winget = QTreeWidget()
        self.tree_winget.setHeaderLabels(["Name", "Id"])
        self.tree_winget.setSelectionMode(QTreeWidget.MultiSelection)
        l.addWidget(self.tree_winget, 1)

    def on_winget_search(self):
        q = self.search_winget.text().strip()
        if not q:
            QMessageBox.information(self, "Info", "Type something to search.")
            return
        self.tree_winget.clear()
        apps = winget_search_apps(q)
        if not apps:
            QMessageBox.information(self, "Info", "No results.")
            return
        for a in apps:
            node = QTreeWidgetItem([a["Name"], a["Id"]])
            self.tree_winget.addTopLevelItem(node)

    def on_winget_install_selected(self):
        sel = self.tree_winget.selectedItems()
        if not sel:
            QMessageBox.information(self, "Info", "Select items first.")
            return
        ids = [it.text(1) for it in sel]
        self.task_queue.append(("Installing/Updating", ids))
        self.process_task_queue()

    # ---------------- Explore Tab (categories + integrated winget-inject) ----------------
    def setup_explore_tab(self):
        self.tab_explore = QWidget()
        self.tabs.addTab(self.tab_explore, "Explore / Browse")

        v = QVBoxLayout(self.tab_explore)
        top = QHBoxLayout()
        self.search_explore = QLineEdit()
        self.search_explore.setPlaceholderText("Filter preloaded apps or paste search term then press 'Add from Winget'")
        
        self.btn_add_winget = QPushButton("Add from Winget")
        self.btn_add_winget.setProperty("class", "secondary")
        self.btn_add_winget.setIcon(self.get_svg_icon(self.get_svg_string("search"), 16))
        self.btn_add_winget.clicked.connect(self.inject_winget_search_into_grid)
        
        self.btn_install_update = QPushButton("Install/Update Selected")
        self.btn_install_update.setIcon(self.get_svg_icon(self.get_svg_string("update"), 16))
        self.btn_install_update.clicked.connect(self.install_selected_from_grid)
        
        top.addWidget(self.search_explore, 1)
        top.addWidget(self.btn_add_winget)
        top.addWidget(self.btn_install_update)
        v.addLayout(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QVBoxLayout(container)
        self.grid.setSpacing(18)
        self.grid.addStretch(1) # Stretch at the bottom to push content up
        scroll.setWidget(container)
        v.addWidget(scroll, 1)

        self.app_cards = []
        self.category_blocks = {}

        categories = sorted({a["Category"] for a in APPS})
        for cat in categories:
            self._create_category_block(cat)

        for app in APPS:
            self._add_app_card(app)

        self.search_explore.textChanged.connect(self.filter_explore_grid)
        
    def _create_category_block(self, category_name):
        block_frame = QFrame()
        block_frame.setObjectName("categoryBlockFrame")
        block_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        block_layout = QVBoxLayout(block_frame)
        block_layout.setContentsMargins(0, 0, 0, 0)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        toggle = QToolButton()
        toggle.setObjectName("categoryToggle")
        toggle.setCheckable(True)
        toggle.setChecked(True)
        toggle.setFixedSize(24, 24)
        toggle.setIconSize(QSize(18, 18))
        toggle.setIcon(self.get_svg_icon(self.get_svg_string("expanded"), 18))

        header_label = QLabel(category_name)
        header_label.setProperty("class", "category-header")

        header_layout.addWidget(toggle)
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        cards_container = QWidget()
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(10)
        cards_container._cards_layout = cards_layout
        
        block_layout.addWidget(header_widget)
        block_layout.addWidget(cards_container)
        
        def on_toggle(checked):
            cards_container.setVisible(checked)
            toggle.setIcon(self.get_svg_icon(self.get_svg_string("expanded" if checked else "collapsed"), 18))
        
        toggle.clicked.connect(on_toggle)
        header_widget.mousePressEvent = lambda event: toggle.click()

        self.grid.insertWidget(self.grid.count() - 1, block_frame)
        self.category_blocks[category_name] = {
            "frame": block_frame,
            "cards_container": cards_container,
            "layout": cards_layout,
            "next_pos": (0, 0),
            "header": header_widget
        }

    def _add_app_card(self, app):
        cat = app.get("Category", "Other")
        if cat not in self.category_blocks:
            self._create_category_block(cat)
        block = self.category_blocks[cat]
        layout = block["layout"]
        r, c = block["next_pos"]

        card = QFrame()
        card.setProperty("class", "app-card")
        card_layout = QVBoxLayout(card)
        
        icon_bg_label = QLabel()
        icon_bg_label.setFixedSize(50, 50)
        icon_bg_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border-radius: 10px;")
        icon_bg_layout = QHBoxLayout(icon_bg_label)
        icon_bg_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon_label.setPixmap(self.get_app_icon(app["Name"]).pixmap(40, 40))
        icon_bg_layout.addWidget(icon_label, alignment=Qt.AlignCenter)
        
        card_layout.addWidget(icon_bg_label, alignment=Qt.AlignCenter)
        
        chk = QCheckBox(app["Name"])
        chk.setStyleSheet("font-size:11pt; color: #eaeaea;")
        chk.app_id = app["Id"]
        
        lbl_id = QLabel(app["Id"])
        lbl_id.setStyleSheet("font-size:9pt; color:#aaa;")
        lbl_id.setWordWrap(True)

        card_layout.addWidget(chk)
        card_layout.addWidget(lbl_id)

        card._checkbox = chk
        card._app = app

        layout.addWidget(card, r, c)
        self.app_cards.append(card)
        self.category_blocks[cat]["next_pos"] = (r, c + 1) if c + 1 < 4 else (r + 1, 0)

    def get_app_icon(self, app_name):
        name_lower = app_name.lower().replace(" ", "").replace(".", "")
        icon_dict = {
            "chrome": "chrome", "firefox": "firefox", "edge": "edge", "brave": "brave", "opera": "opera",
            "whatsapp": "whatsapp", "telegram": "telegram", "discord": "discord", "zoom": "zoom", "skype": "skype", "slack": "slack",
            "vlc": "vlc", "spotify": "spotify", "obs": "obs", "gimp": "gimp", "paint.net": "paint.net", "audacity": "audacity",
            "krita": "krita", "inkscape": "inkscape", "blender": "blender",
            "vscode": "vscode", "visualstudiocode": "vscode", "git": "git", "nodejs": "nodejs", "python": "python", "java": "java", "docker": "docker",
            "postman": "postman", "intellij": "intellij", "pycharm": "pycharm",
            "anaconda": "anaconda", "7zip": "7zip", "winrar": "winrar", "notepad++": "notepad++", "everything": "everything",
            "ccleaner": "ccleaner", "sharex": "sharex", "powertoys": "powertoys", "libreoffice": "libreoffice",
            "steam": "steam", "epicgames": "epicgames", "battle.net": "battle.net", "cpuz": "cpuz", "hwmonitor": "hwmonitor",
        }
        
        icon_key = ""
        for key in icon_dict:
            if key in name_lower:
                icon_key = icon_dict[key]
                break

        svg_string = self.get_svg_string(icon_key if icon_key else "default")
        return self.get_svg_icon(svg_string, size=40, bg_color=QColor(255, 255, 255, 20), padding=5)

    def inject_winget_search_into_grid(self):
        term = self.search_explore.text().strip()
        if not term:
            QMessageBox.information(self, "Info", "Type a search term in the filter box to add results from Winget.")
            return
        apps = winget_search_apps(term)
        if not apps:
            QMessageBox.information(self, "Info", "No winget results.")
            return
        
        cat = "Search Results"
        if cat not in self.category_blocks:
            self._create_category_block(cat)
        
        for a in apps:
            already = any(card._app.get("Id") == a["Id"] for card in self.app_cards)
            if already:
                continue
            self._add_app_card(a)

    def filter_explore_grid(self, text):
        q = text.strip().lower()
        for card in self.app_cards:
            name = card._checkbox.text().lower()
            aid = (card._app.get("Id") or "").lower()
            visible = (q in name) or (q in aid) or (q == "")
            card.setVisible(visible)

    def install_selected_from_grid(self):
        selected = [card._checkbox.app_id for card in self.app_cards if card._checkbox.isChecked()]
        if not selected:
            QMessageBox.information(self, "Info", "Select apps first.")
            return
        self.task_queue.append(("Installing/Updating", selected))
        self.process_task_queue()

    # ---------------- Installed Tab ----------------
    def setup_installed_tab(self):
        self.tab_installed = QWidget()
        self.tabs.addTab(self.tab_installed, "Installed • Update / Uninstall")
        
        v = QVBoxLayout(self.tab_installed)
        top = QHBoxLayout()
        self.search_installed = QLineEdit()
        self.search_installed.setPlaceholderText("Search installed apps...")
        
        self.btn_refresh_installed = QPushButton("Refresh")
        self.btn_refresh_installed.setProperty("class", "secondary")
        self.btn_refresh_installed.setIcon(self.get_svg_icon(self.get_svg_string("refresh"), 16))
        
        self.btn_update_selected = QPushButton("Update Selected")
        self.btn_update_selected.setIcon(self.get_svg_icon(self.get_svg_string("update"), 16))
        
        self.btn_uninstall_selected = QPushButton("Uninstall Selected")
        self.btn_uninstall_selected.setIcon(self.get_svg_icon(self.get_svg_string("uninstall"), 16))

        top.addWidget(self.search_installed, 1)
        top.addWidget(self.btn_refresh_installed)
        top.addWidget(self.btn_update_selected)
        top.addWidget(self.btn_uninstall_selected)
        v.addLayout(top)

        self.tree_installed = QTreeWidget()
        self.tree_installed.setHeaderLabels(["Name", "Id", "Version", "Available"])
        self.tree_installed.setSelectionMode(QTreeWidget.MultiSelection)
        v.addWidget(self.tree_installed, 1)

        self.btn_refresh_installed.clicked.connect(self.populate_installed)
        self.btn_update_selected.clicked.connect(self.update_selected_installed)
        self.btn_uninstall_selected.clicked.connect(self.uninstall_selected_installed)
        self.search_installed.textChanged.connect(self.filter_installed)
        self.populate_installed()
    
    def populate_installed(self):
        self.tree_installed.clear()
        items = winget_list_installed()
        for it in items:
            row = QTreeWidgetItem([it.get("Name", ""), it.get("Id", ""), "", ""])
            self.tree_installed.addTopLevelItem(row)
        for i in range(self.tree_installed.columnCount()):
            self.tree_installed.resizeColumnToContents(i)

    def filter_installed(self, text):
        q = text.strip().lower()
        for i in range(self.tree_installed.topLevelItemCount()):
            r = self.tree_installed.topLevelItem(i)
            visible = any(q in r.text(c).lower() for c in range(r.columnCount()))
            r.setHidden(not visible)

    def update_selected_installed(self):
        selected = self.tree_installed.selectedItems()
        if not selected:
            QMessageBox.information(self, "Info", "Select installed apps first.")
            return
        ids = [r.text(1) for r in selected]
        self.task_queue.append(("Installing/Updating", ids))
        self.process_task_queue()

    def uninstall_selected_installed(self):
        selected = self.tree_installed.selectedItems()
        if not selected:
            QMessageBox.information(self, "Info", "Select installed apps first.")
            return
        ids = [r.text(1) for r in selected]
        self.task_queue.append(("Uninstalling", ids))
        self.process_task_queue()

    # ---------------- Progress Tab ----------------
    def setup_progress_tab(self):
        self.tab_progress = QWidget()
        self.tabs.addTab(self.tab_progress, "Progress")
        
        v = QVBoxLayout(self.tab_progress)
        self.progress_log = QTextEdit()
        self.progress_log.setReadOnly(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #333;
                color: #fff;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #1f6feb;
                border-radius: 5px;
            }
        """)

        self.btn_cancel_progress = QPushButton("Cancel")
        self.btn_cancel_progress.setProperty("class", "secondary")
        h = QHBoxLayout()
        h.addWidget(self.progress_bar, 1)
        h.addWidget(self.btn_cancel_progress)
        v.addWidget(self.progress_log, 1)
        v.addLayout(h)

        self.btn_cancel_progress.clicked.connect(self.cancel_worker)

    def process_task_queue(self):
        if self.worker and getattr(self.worker, "isRunning", None) and self.worker.isRunning():
            return
        if not self.task_queue:
            return
        action_label, ids = self.task_queue.pop(0)
        self.start_worker(ids, action_label)

    def start_worker(self, ids, action_label):
        self.progress_log.clear()
        self.progress_bar.setValue(0)
        self.worker = WorkerThread(ids, action_label)
        self.worker.progress_signal.connect(self.on_worker_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()
        self.tabs.setCurrentWidget(self.tab_progress)

    def on_worker_progress(self, message, percent):
        self.progress_log.append(message)
        try:
            p = max(0, min(100, int(percent)))
        except Exception:
            p = 0
        self.progress_bar.setValue(p)

    def on_worker_finished(self, summary):
        self.progress_log.append(f"Worker finished: {summary}")
        self.worker = None
        self.populate_installed()
        self.process_task_queue()

    def cancel_worker(self):
        if self.worker:
            self.worker.cancel()


# --------------------------
# Run
# --------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AppManager()
    w.show()
    sys.exit(app.exec())