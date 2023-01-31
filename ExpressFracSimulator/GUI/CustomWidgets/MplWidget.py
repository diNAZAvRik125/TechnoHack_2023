import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout

matplotlib.use('Qt5Agg')
# Font setting for pretty latex rendering
plt.rcParams["mathtext.fontset"] = "cm"
plt.rcParams["font.family"] = "STIXGeneral"


class MplCanvas(FigureCanvas):
    def __init__(
        self, figsize=(5, 4), dpi=100, title=None, xlabel=None, ylabel=None,
        is_grid=False, is_autoscale=False, aspect_ratio="auto"
    ):
        self.fig, self.ax = plt.subplots(1, 1, figsize=figsize, dpi=dpi)
        super().__init__(self.fig)

        self.ax.set_title(title)
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)

        self.is_grid = is_grid
        self.is_autoscale = is_autoscale
        self.aspect_ratio = aspect_ratio
        self.fig.tight_layout()

    def draw(self):
        if self.is_autoscale:
            self.ax.relim()
            self.ax.autoscale()

        self.ax.grid(self.is_grid)
        self.ax.set_aspect(self.aspect_ratio)
        super().draw()


class MplWidget(QWidget):
    resized = Signal()

    def __init__(self, parent=None, **kwargs):
        QWidget.__init__(self, parent)
        self.canvas = MplCanvas(**kwargs)
        self.vbl = QVBoxLayout()
        self.vbl.addWidget(self.canvas)
        self.vbl.addWidget(NavigationToolbar(self.canvas, self))
        self.setLayout(self.vbl)

        # Create and initialize right-click context menu
        self._create_context_actions()
        self._create_contex_menu()
        self._connect_context_actions()

        self.resized.connect(self.update_layout)

    def _create_context_actions(self):
        self.show_grid_action = QAction("Show grid", self)
        self.show_grid_action.setCheckable(True)
        self.show_grid_action.setChecked(self.canvas.is_grid)

        self.enable_autoscale_action = QAction("Enable autoscale", self)
        self.enable_autoscale_action.setCheckable(True)
        self.enable_autoscale_action.setChecked(self.canvas.is_autoscale)

        self.aspect_auto_action = QAction("Automatic aspect ratio", self)
        self.aspect_equal_action = QAction("Equal aspect ratio", self)

    def _create_contex_menu(self):
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addAction(self.show_grid_action)
        self.addAction(self.enable_autoscale_action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        self.addAction(self.aspect_auto_action)
        self.addAction(self.aspect_equal_action)

    def _connect_context_actions(self):
        self.show_grid_action.toggled.connect(self.show_grid)
        self.enable_autoscale_action.toggled.connect(self.enable_autoscale)
        self.aspect_auto_action.triggered.connect(self.set_aspect_auto)
        self.aspect_equal_action.triggered.connect(self.set_aspect_equal)

    def show_grid(self, status: bool):
        self.canvas.is_grid = status
        self.canvas.ax.grid(status)
        self.canvas.draw()

    def enable_autoscale(self, status: bool):
        self.canvas.is_autoscale = status
        self.canvas.draw()

    def set_aspect_auto(self):
        self.canvas.aspect_ratio = "auto"
        self.canvas.draw()

    def set_aspect_equal(self):
        self.canvas.aspect_ratio = "equal"
        self.canvas.draw()

    def resizeEvent(self, event):
        self.resized.emit()
        return QWidget.resizeEvent(self, event)

    def update_layout(self):
        self.canvas.fig.tight_layout()
