import sys
import subprocess
import shlex
import re
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices, QCursor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QScrollArea, QGridLayout, QFrame, QCheckBox,
    QProgressBar, QTextEdit, QToolButton, QSizePolicy, QApplication,
    QStyle # Import QStyle for standard icons
)

# --------------------------
# Configuration / App List
# --------------------------
APPS = [
    # Browsers
    {"Name":"Google Chrome","Id":"Google.Chrome","Category":"Browsers"},
    {"Name":"Mozilla Firefox","Id":"Mozilla.Firefox","Category":"Browsers"},
    {"Name":"Microsoft Edge","Id":"Microsoft.Edge","Category":"Browsers"},
    {"Name":"Brave","Id":"Brave.Brave","Category":"Browsers"},
    {"Name":"Opera","Id":"Opera.Opera","Category":"Browsers"},

    # Messaging
    {"Name":"WhatsApp Desktop","Id":"WhatsApp.WhatsApp","Category":"Messaging"},
    {"Name":"Telegram Desktop","Id":"Telegram.TelegramDesktop","Category":"Messaging"},
    {"Name":"Discord","Id":"Discord.Discord","Category":"Messaging"},
    {"Name":"Zoom","Id":"Zoom.Zoom","Category":"Messaging"},
    {"Name":"Skype","Id":"Microsoft.Skype","Category":"Messaging"},
    {"Name":"Slack","Id":"SlackTechnologies.Slack","Category":"Messaging"},

    # Multimedia / Design
    {"Name":"VLC Media Player","Id":"VideoLAN.VLC","Category":"Multimedia"},
    {"Name":"Spotify","Id":"Spotify.Spotify","Category":"Multimedia"},
    {"Name":"OBS Studio","Id":"OBSProject.OBSStudio","Category":"Multimedia"},
    {"Name":"GIMP","Id":"GIMP.GIMP","Category":"Multimedia"},
    {"Name":"Paint.NET","Id":"dotPDN.Paint.NET","Category":"Multimedia"},
    {"Name":"Audacity","Id":"Audacity.Audacity","Category":"Multimedia"},
    {"Name":"PotPlayer","Id":"DAUM.PotPlayer","Category":"Multimedia"},
    {"Name":"foobar2000","Id":"foobar2000.foobar2000","Category":"Multimedia"},
    {"Name":"Krita","Id":"Krita.Krita","Category":"Design"},
    {"Name":"Inkscape","Id":"Inkscape.Inkscape","Category":"Design"},
    {"Name":"Blender","Id":"BlenderFoundation.Blender","Category":"Design"},
    {"Name":"Aseprite","Id":"Aseprite.Aseprite","Category":"Design"},

    # Development / AI
    {"Name":"Visual Studio Code","Id":"Microsoft.VisualStudioCode","Category":"Development"},
    {"Name":"Git","Id":"Git.Git","Category":"Development"},
    {"Name":"Node.js LTS","Id":"OpenJS.NodeJS.LTS","Category":"Development"},
    {"Name":"Python 3","Id":"Python.Python.3","Category":"Development"},
    {"Name":"Java","Id":"Oracle.JavaRuntimeEnvironment","Category":"Development"},
    {"Name":"Docker Desktop","Id":"Docker.DockerDesktop","Category":"Development"},
    {"Name":"Postman","Id":"Postman.Postman","Category":"Development"},
    {"Name":"IntelliJ IDEA Community","Id":"JetBrains.IntelliJIDEA.Community","Category":"Development"},
    {"Name":"PyCharm Community","Id":"JetBrains.PyCharm.Community","Category":"Development"},
    {"Name":"Anaconda","Id":"Anaconda.Anaconda","Category":"AI/ML"},
    {"Name":"Miniconda","Id":"Miniconda.Miniconda3","Category":"AI/ML"},
    {"Name":"Power BI Desktop","Id":"Microsoft.PowerBIDesktop","Category":"AI/ML"},

    # Utilities
    {"Name":"7-Zip","Id":"7zip.7zip","Category":"Utilities"},
    {"Name":"WinRAR","Id":"RARLab.WinRAR","Category":"Utilities"},
    {"Name":"Notepad++","Id":"Notepad++.Notepad++","Category":"Utilities"},
    {"Name":"Everything Search","Id":"Voidtools.Everything","Category":"Utilities"},
    {"Name":"CCleaner","Id":"Piriform.CCleaner","Category":"Utilities"},
    {"Name":"ShareX","Id":"ShareX.ShareX","Category":"Utilities"},
    {"Name":"PowerToys","Id":"Microsoft.PowerToys","Category":"Utilities"},

    # Office
    {"Name":"LibreOffice","Id":"TheDocumentFoundation.LibreOffice","Category":"Office"},
    {"Name":"OnlyOffice Desktop Editors","Id":"Ascensio.OnlyOffice","Category":"Office"},
    {"Name":"Microsoft To Do","Id":"Microsoft.Todos","Category":"Office"},
    {"Name":"Evernote","Id":"Evernote.Evernote","Category":"Office"},
    {"Name":"Google Drive","Id":"Google.Drive","Category":"Office"},
    {"Name":"Dropbox","Id":"Dropbox.Dropbox","Category":"Office"},

    # Gaming
    {"Name":"Steam","Id":"Valve.Steam","Category":"Gaming"},
    {"Name":"Epic Games Launcher","Id":"EpicGames.EpicGamesLauncher","Category":"Gaming"},
    {"Name":"Origin","Id":"ElectronicArts.Origin","Category":"Gaming"},
    {"Name":"Battle.net","Id":"Blizzard.BattleNet","Category":"Gaming"},
    {"Name":"GeForce Experience","Id":"NVIDIA.GeForceExperience","Category":"Gaming"},
    {"Name":"MSI Afterburner","Id":"MSI.Afterburner","Category":"Gaming"},
    {"Name":"Razer Synapse","Id":"Razer.RazerSynapse","Category":"Gaming"},

    # PC Test
    {"Name":"CPU-Z","Id":"CPUID.CPU-Z","Category":"PC Test"},
    {"Name":"HWMonitor","Id":"CPUID.HWMonitor","Category":"PC Test"},
    {"Name":"CrystalDiskInfo","Id":"CrystalDewWorld.CrystalDiskInfo","Category":"PC Test"},
    {"Name":"GPU-Z","Id":"TechPowerUp.GPU-Z","Category":"PC Test"},
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
    progress_signal = Signal(str, int)   # message, percent
    finished_signal = Signal(str)        # summary
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
            percent = int((idx/total)*100)
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
        self.resize(1100, 700)
        
        # Set application icon
        try:
            self.setWindowIcon(QIcon("headIcon.ico"))
        except Exception as e:
            print(f"Could not load headIcon.ico: {e}")
            pass # Fallback to default icon if not found

        # Modern Dark Theme
        self.setStyleSheet("""
            QWidget { 
                background-color: #1a1a1a; 
                color: #e0e0e0; 
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif; 
                font-size: 10pt;
            }
            QTabWidget::pane {
                border: 1px solid #333333;
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QTabWidget::tab-bar {
                left: 5px; /* move to the right */
            }
            QTabBar::tab {
                background: #2a2a2a;
                border: 1px solid #333333;
                border-bottom-color: #333333; /* same as pane color */
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 100px;
                padding: 10px 15px;
                color: #b0b0b0;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background: #3a3a3a;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                border-color: #4a4a4a;
                border-bottom-color: #3a3a3a; /* overlap to show it's selected */
            }
            QLineEdit, QTextEdit { 
                background-color: #2b2b2b; 
                color: #ffffff; 
                border: 1px solid #444444; 
                padding: 8px; 
                border-radius: 5px;
            }
            QPushButton { 
                background-color: #007acc; 
                color: white; 
                padding: 8px 15px; 
                border-radius: 5px; 
                border: none;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #008fec;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
            QPushButton.secondary { 
                background-color: #444444; 
                color: #e0e0e0; 
            }
            QPushButton.secondary:hover {
                background-color: #555555;
            }
            QPushButton.secondary:pressed {
                background-color: #333333;
            }
            QToolButton { 
                background: transparent;
                color: #007acc;
                border: none;
                font-size: 16pt;
                padding: 5px;
            }
            QToolButton:hover {
                color: #008fec;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #2b2b2b;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 5px;
            }
            QTreeWidget {
                background-color: #1e1e1e;
                alternate-background-color: #222222;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 5px;
                padding: 5px;
                font-size: 9pt;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #444444;
                font-weight: bold;
            }
            QScrollArea {
                border: none;
            }
            QFrame#appCardFrame {
                background-color:#2b2b2b; 
                border-radius:8px; 
                padding:8px;
                border: 1px solid #3a3a3a;
            }
            QFrame#appCardFrame:hover { 
                background-color:#3a3a3a; 
                border: 1px solid #007acc;
            }
            QLabel { 
                color: #e0e0e0; 
            }
            QCheckBox { 
                color: #ffffff; 
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #007acc;
                border-radius: 3px;
                background-color: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background-color: #007acc;
                border: 1px solid #007acc;
                image: url(check_icon.png); /* You might need to provide a check_icon.png */
            }
            QCheckBox::indicator:hover {
                border: 1px solid #008fec;
            }
        """)

        self.task_queue = []
        self.worker = None

        root = QVBoxLayout(self)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)

        # Tabs: Winget Search first (as requested), then Explore, Installed, Progress
        self.setup_winget_tab()
        self.setup_explore_tab()
        self.setup_installed_tab()
        self.setup_progress_tab()
        
        # Developer info at the bottom
        dev_info_layout = QHBoxLayout()
        dev_label = QLabel("Developed by ")
        
        self.dev_link = QLabel("<a href='https://github.com/sayedatiqurrahman' style='color:#007acc; text-decoration:none;'>Sayed Atiqur Rahman</a>")
        self.dev_link.setOpenExternalLinks(True) # Make the link clickable
        self.dev_link.setCursor(QCursor(Qt.PointingHandCursor)) # Change cursor on hover
        self.dev_link.setStyleSheet("QLabel { font-weight: bold; }")

        dev_info_layout.addStretch()
        dev_info_layout.addWidget(dev_label)
        dev_info_layout.addWidget(self.dev_link)
        dev_info_layout.addStretch()
        
        root.addLayout(dev_info_layout)


    # ---------------- Winget Search Tab ----------------
    def setup_winget_tab(self):
        self.tab_winget = QWidget()
        self.tabs.addTab(self.tab_winget, QIcon.fromTheme("system-search"), "Winget Search") # Added icon
        l = QVBoxLayout(self.tab_winget)

        top = QHBoxLayout()
        self.search_winget = QLineEdit()
        self.search_winget.setPlaceholderText("Type to search winget...")
        self.btn_winget_search = QPushButton(QIcon.fromTheme("edit-find"), "Search") # Added icon
        self.btn_winget_search.setProperty("class", "secondary")
        self.btn_winget_search.clicked.connect(self.on_winget_search)
        self.btn_winget_install = QPushButton(QIcon.fromTheme("download"), "Install Selected") # Added icon
        self.btn_winget_install.clicked.connect(self.on_winget_install_selected)
        top.addWidget(QLabel("Search:"))
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
        
        # Show busy cursor while searching
        QApplication.setOverrideCursor(Qt.WaitCursor)
        apps = winget_search_apps(q)
        QApplication.restoreOverrideCursor()

        if not apps:
            QMessageBox.information(self, "Info", "No results found for your query.")
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
        self.tabs.addTab(self.tab_explore, QIcon.fromTheme("folder-open"), "Explore / Browse") # Added icon
        v = QVBoxLayout(self.tab_explore)

        top = QHBoxLayout()
        self.search_explore = QLineEdit()
        self.search_explore.setPlaceholderText("Filter preloaded apps or paste search term then press 'Add from Winget' ")
        self.btn_add_winget = QPushButton(QIcon.fromTheme("add"), "Add from Winget")   # Added icon
        self.btn_add_winget.setProperty("class", "secondary")
        self.btn_add_winget.clicked.connect(self.inject_winget_search_into_grid)
        self.btn_install_update = QPushButton(QIcon.fromTheme("system-software-install"), "Install/Update Selected") # Added icon
        self.btn_install_update.clicked.connect(self.install_selected_from_grid)
        top.addWidget(QLabel("Search/Filter:"))
        top.addWidget(self.search_explore, 1)
        top.addWidget(self.btn_add_winget)
        top.addWidget(self.btn_install_update)
        v.addLayout(top)

        # Scrollable grid for categories
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.grid = QVBoxLayout(container)
        self.grid.setSpacing(18)   # spacing between category blocks
        scroll.setWidget(container)
        v.addWidget(scroll, 1)

        # Build category blocks
        self.app_cards = []         # list of frames for search/filter
        self.category_blocks = {}   # category -> list of frames

        categories = sorted({a["Category"] for a in APPS})
        for cat in categories:
            self._create_category_block(cat)

        # fill blocks with apps
        for app in APPS:
            self._add_app_card(app)

        # wire filtering
        self.search_explore.textChanged.connect(self.filter_explore_grid)

    def _create_category_block(self, category_name):
        block_frame = QFrame()
        block_frame.setObjectName("categoryBlockFrame") # Added object name for specific styling
        block_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        block_layout = QVBoxLayout(block_frame)
        # header: label + toggle button
        header_layout = QHBoxLayout()
        toggle = QToolButton()
        toggle.setText("▼")
        toggle.setCheckable(True)
        toggle.setChecked(True)
        toggle.setStyleSheet("QToolButton { border: none; background: none; color: #007acc; font-weight: bold; font-size: 14pt; } QToolButton:hover { color: #008fec; }")
        
        header_label = QLabel(category_name)
        header_label.setStyleSheet("font-weight: bold; font-size: 13pt; margin-left:6px; color:#ffffff;") # Adjusted color
        
        header_layout.addWidget(toggle)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        block_layout.addLayout(header_layout)
        # container grid for cards inside category
        cards_container = QWidget()
        cards_layout = QGridLayout(cards_container)
        cards_layout.setSpacing(10)
        cards_container._cards_layout = cards_layout  # store pointer
        block_layout.addWidget(cards_container)
        # margins to prevent overlap with other categories
        block_frame.setContentsMargins(6, 10, 6, 10)

        # toggle behavior
        def on_toggle(checked):
            cards_container.setVisible(checked)
            toggle.setText("▼" if checked else "►")
        toggle.clicked.connect(on_toggle)

        # keep block
        self.grid.addWidget(block_frame)
        self.category_blocks[category_name] = {
            "frame": block_frame,
            "cards_container": cards_container,
            "layout": cards_layout,
            "next_pos": (0, 0)
        }

    def _add_app_card(self, app):
        cat = app.get("Category", "Other")
        if cat not in self.category_blocks:
            self._create_category_block(cat)
        block = self.category_blocks[cat]
        layout = block["layout"]
        r, c = block["next_pos"]

        # frame visual
        card = QFrame()
        card.setObjectName("appCardFrame") # Added object name for specific styling
        
        card_layout = QVBoxLayout(card)
        chk = QCheckBox(app["Name"])
        chk.setStyleSheet("font-size:11pt; color: #eaeaea;")
        chk.app_id = app["Id"]
        lbl_id = QLabel(app["Id"])
        lbl_id.setStyleSheet("font-size:9pt; color:#b0b0b0;") # Adjusted color
        card_layout.addWidget(chk)
        card_layout.addWidget(lbl_id)
        # store references
        card._checkbox = chk
        card._app = app

        # add to grid
        layout.addWidget(card, r, c)
        self.app_cards.append(card)
        self.category_blocks[cat]["next_pos"] = (r, c+1) if c+1 < 4 else (r+1, 0)

    def inject_winget_search_into_grid(self):
        term = self.search_explore.text().strip()
        if not term:
            QMessageBox.information(self, "Info", "Type a search term in the filter box to add results from Winget.")
            return
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        apps = winget_search_apps(term)
        QApplication.restoreOverrideCursor()

        if not apps:
            QMessageBox.information(self, "Info", "No winget results found for your search term.")
            return
        # inject under a "Search Results" category (create if missing)
        cat = "Search Results (Winget)"
        if cat not in self.category_blocks:
            self._create_category_block(cat)
        for a in apps:
            # avoid duplicates by Id
            already = any(card._app.get("Id") == a["Id"] for card in self.app_cards)
            if already:
                continue
            self._add_app_card(a)
        
        # Ensure the "Search Results" category is visible
        if cat in self.category_blocks:
            frame = self.category_blocks[cat]["frame"]
            frame.setVisible(True) # Make category frame visible
            # Find the toggle button and ensure it's checked
            toggle_button = frame.findChild(QToolButton)
            if toggle_button and not toggle_button.isChecked():
                toggle_button.click() # Simulate click to open if closed


    def filter_explore_grid(self, text):
        q = text.strip().lower()
        for card in self.app_cards:
            name = card._checkbox.text().lower()
            aid = (card._app.get("Id") or "").lower()
            visible = (q in name) or (q in aid) or (q == "")
            card.setVisible(visible)
            
            # Hide/show category blocks based on visible cards
            cat = card._app.get("Category", "Other")
            if cat in self.category_blocks:
                category_frame = self.category_blocks[cat]["frame"]
                # A category block is visible if any of its cards are visible
                if visible and category_frame.isHidden():
                    category_frame.show()
                elif not visible:
                    # Check if all cards in this category are hidden
                    all_hidden = True
                    for other_card in self.app_cards:
                        if other_card._app.get("Category") == cat and other_card.isVisible():
                            all_hidden = False
                            break
                    if all_hidden and not category_frame.isHidden():
                        category_frame.hide()


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
        self.tabs.addTab(self.tab_installed, QIcon.fromTheme("applications-other"), "Installed • Update / Uninstall") # Added icon
        v = QVBoxLayout(self.tab_installed)

        top = QHBoxLayout()
        self.search_installed = QLineEdit()
        self.search_installed.setPlaceholderText("Search installed apps...")
        self.btn_refresh_installed = QPushButton(QIcon.fromTheme("view-refresh"), "Refresh") # Added icon
        self.btn_refresh_installed.setProperty("class", "secondary")
        self.btn_update_selected = QPushButton(QIcon.fromTheme("system-software-update"), "Update Selected") # Added icon
        self.btn_uninstall_selected = QPushButton(QIcon.fromTheme("edit-delete"), "Uninstall Selected") # Added icon
        top.addWidget(QLabel("Search:"))
        top.addWidget(self.search_installed, 1)
        top.addWidget(self.btn_refresh_installed)
        top.addWidget(self.btn_update_selected)
        top.addWidget(self.btn_uninstall_selected)
        v.addLayout(top)

        self.tree_installed = QTreeWidget()
        self.tree_installed.setHeaderLabels(["Name","Id","Version","Available"])
        self.tree_installed.setSelectionMode(QTreeWidget.MultiSelection)
        v.addWidget(self.tree_installed, 1)

        # signals
        self.btn_refresh_installed.clicked.connect(self.populate_installed)
        self.btn_update_selected.clicked.connect(self.update_selected_installed)
        self.btn_uninstall_selected.clicked.connect(self.uninstall_selected_installed)
        self.search_installed.textChanged.connect(self.filter_installed)

        # initial populate
        self.populate_installed()

    def populate_installed(self):
        self.tree_installed.clear()
        
        QApplication.setOverrideCursor(Qt.WaitCursor)
        items = winget_list_installed()
        QApplication.restoreOverrideCursor()

        for it in items:
            row = QTreeWidgetItem([ it.get("Name",""), it.get("Id",""), "", ""])
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
        
        confirm = QMessageBox.question(self, "Confirm Uninstall", 
                                      f"Are you sure you want to uninstall {len(selected)} selected applications? This action cannot be undone.",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.No:
            return
            
        ids = [r.text(1) for r in selected]
        self.task_queue.append(("Uninstalling", ids))
        self.process_task_queue()

    # ---------------- Progress Tab ----------------
    def setup_progress_tab(self):
        self.tab_progress = QWidget()
        self.tabs.addTab(self.tab_progress, QIcon.fromTheme("document-properties"), "Progress") # Added icon
        v = QVBoxLayout(self.tab_progress)

        self.progress_log = QTextEdit()
        self.progress_log.setReadOnly(True)
        self.progress_log.setStyleSheet("font-family: 'Consolas', 'Courier New', monospace; font-size: 9pt; background-color: #222222; color: #f0f0f0;")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("%p% - %v/%m") # Show percentage and current/total
        
        self.btn_cancel_progress = QPushButton(QIcon.fromTheme("process-stop"), "Cancel") # Added