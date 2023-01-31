from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSizePolicy,
    QSplitter
)
from CustomWidgets import MplWidget
import numpy as np


class PlotResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.graph_splitter = QSplitter(Qt.Vertical)

        # ------------------------------------------------------
        # Effective width plot widget
        # ------------------------------------------------------
        self.effective_width_plot = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$\\bar{w}$",
            title="Effective width",
            is_grid=True,
            is_autoscale=True
        )
        self.effective_width_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Plot reference to update graph
        self._effective_width_plot_ref = None

        # ------------------------------------------------------
        # Insert plot widgets to splitter
        # ------------------------------------------------------
        self.graph_splitter.addWidget(self.effective_width_plot)

        self.layout.addWidget(self.graph_splitter)
        self.setLayout(self.layout)

    def plot_results(self, results_data, time_index):
        x = np.array(results_data[time_index]["x"])
        width = np.array(results_data[time_index]["width"])

        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref is None:
            self._effective_width_plot_ref = self.effective_width_plot.canvas.ax.plot(x, width, 'r')[0]
        else:
            self._effective_width_plot_ref.set_xdata(x)
            self._effective_width_plot_ref.set_ydata(width)
        self.effective_width_plot.canvas.draw()

    def clear_plots(self):
        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref is not None:
            self._effective_width_plot_ref.remove()
            self._effective_width_plot_ref = None
        self.effective_width_plot.canvas.draw()
