import sys
import subprocess
import shlex
import re
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QScrollArea, QGridLayout, QFrame, QCheckBox,
    QProgressBar, QTextEdit, QToolButton, QSizePolicy
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
        # dark theme basics
        self.setStyleSheet("""
            QWidget { background-color: #121212; color: #e8e8e8; font-family: Segoe UI, Arial; }
            QLineEdit, QTextEdit { background-color: #1e1e1e; color: #ffffff; border: 1px solid #333; padding: 6px; }
            QPushButton { background-color: #1f6feb; color: white; padding: 6px 10px; border-radius: 6px; }
            QPushButton.secondary { background-color: #333; color: #ddd; }
            QToolButton { color: #9ad; }
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
        self.btn_winget_search.clicked.connect(self.on_winget_search)
        self.btn_winget_install = QPushButton("Install Selected")
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
        self.search_explore.setPlaceholderText("Filter preloaded apps or paste search term then press 'Add from Winget' ")
        self.btn_add_winget = QPushButton("Add from Winget")   # this will run winget search and inject into grid
        self.btn_add_winget.setProperty("class", "secondary")
        self.btn_add_winget.clicked.connect(self.inject_winget_search_into_grid)
        self.btn_install_update = QPushButton("Install/Update Selected")
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
        block_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        block_layout = QVBoxLayout(block_frame)
        # header: label + toggle button
        header_layout = QHBoxLayout()
        toggle = QToolButton()
        toggle.setText("▼")
        toggle.setCheckable(True)
        toggle.setChecked(True)
        header_label = QLabel(category_name)
        header_label.setStyleSheet("font-weight: bold; font-size: 13pt; margin-left:6px; color:#9ad;")
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
        card.setStyleSheet("""
            QFrame{ background-color:#1e1e1e; border-radius:8px; padding:8px; }
            QFrame:hover{ background-color:#2a2a2a; }
            QLabel { color: #eee; }
            QCheckBox { color: #fff; }
        """)
        card_layout = QVBoxLayout(card)
        chk = QCheckBox(app["Name"])
        chk.setStyleSheet("font-size:11pt; color: #eaeaea;")
        chk.app_id = app["Id"]
        lbl_id = QLabel(app["Id"])
        lbl_id.setStyleSheet("font-size:9pt; color:#aaa;")
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
        apps = winget_search_apps(term)
        if not apps:
            QMessageBox.information(self, "Info", "No winget results.")
            return
        # inject under a "Search Results" category (create if missing)
        cat = "Search Results"
        if cat not in self.category_blocks:
            self._create_category_block(cat)
        for a in apps:
            # avoid duplicates by Id
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
        self.btn_update_selected = QPushButton("Update Selected")
        self.btn_uninstall_selected = QPushButton("Uninstall Selected")
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
        items = winget_list_installed()
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
            # worker busy
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
        # guard percent in 0..100
        try:
            p = max(0, min(100, int(percent)))
        except Exception:
            p = 0
        self.progress_bar.setValue(p)

    def on_worker_finished(self, summary):
        self.progress_log.append(f"Worker finished: {summary}")
        self.worker = None
        # refresh installed list after operations
        self.populate_installed()
        # process next queued task automatically
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
