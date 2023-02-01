from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSplitter
)
from . import MplWidget
import numpy as np


class PlotResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QHBoxLayout()
        self.graph_splitter = QSplitter(Qt.Vertical)

        # ------------------------------------------------------
        # Effective width plot widget
        # ------------------------------------------------------
        self.effective_width_plot_1 = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$\\bar{w}$",
            title="Effective width",
            is_grid=True,
            is_autoscale=True
        )
        self.effective_width_plot_1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.effective_width_plot_2 = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$\\bar{w}$",
            title="fluid",
            is_grid=True,
            is_autoscale=True
        )
        self.effective_width_plot_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Plot reference to update graph
        self._effective_width_plot_ref_1 = None
        self._effective_width_plot_ref_2 = None

        # ------------------------------------------------------
        # Insert plot widgets to splitter
        # ------------------------------------------------------
        self.graph_splitter.addWidget(self.effective_width_plot_1)
        self.graph_splitter.addWidget(self.effective_width_plot_2)

        self.layout.addWidget(self.graph_splitter)
        self.setLayout(self.layout)

    def plot_results(self, results_data, time_index):
        x = np.array(results_data[time_index]["mesh"]["xc"])
        width = np.array(results_data[time_index]["results"]["effective_width"])

        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref_1 is None:
            self._effective_width_plot_ref_1 = self.effective_width_plot_1.canvas.ax.plot(x, width, 'r')[0]
        else:
            self._effective_width_plot_ref_1.set_xdata(x)
            self._effective_width_plot_ref_1.set_ydata(width)
        self.effective_width_plot_1.canvas.draw()

        y = np.array(results_data[time_index]["mesh"]["dx"])
        fluid = np.array(results_data[time_index]["results"]["fluid_pressure"])
        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref_2 is None:
            self._effective_width_plot_ref_2 = self.effective_width_plot_2.canvas.ax.plot(y, fluid, 'r')[0]
        else:
            self._effective_width_plot_ref_2.set_xdata(y)
            self._effective_width_plot_ref_2.set_ydata(fluid)
        self.effective_width_plot_2.canvas.draw()

    def clear_plots(self):
        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref_1 is not None:
            self._effective_width_plot_ref_1.remove()
            self._effective_width_plot_ref_1 = None

        if self._effective_width_plot_ref_2 is not None:
            self._effective_width_plot_ref_2.remove()
            self._effective_width_plot_ref_2 = None
        self.effective_width_plot.canvas.draw()
