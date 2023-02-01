import numpy
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
from GUI.ProjectData import ProjectData
from mpl_toolkits.axes_grid1 import make_axes_locatable

class PlotResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.graph_splitter = QSplitter(Qt.Horizontal)
        self.graph_splitter_vertical = QSplitter(Qt.Vertical)

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

        self.fluid_pressure_plot = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$p$",
            title="fluid pressure",
            is_grid=True,
            is_autoscale=True
        )
        self.fluid_pressure_plot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.rings = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$z$",
            title="2D fracture width",
            is_grid=True,
            is_autoscale=True
        )
        self.rings.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Plot reference to update graph
        self._effective_width_plot_ref = None
        self._fluid_pressure_plot_ref = None
        self._rings_ref = None
        self._contour_cax = None
        self._contour_cb = None

        # ------------------------------------------------------
        # Insert plot widgets to splitter
        # ------------------------------------------------------
        self.graph_splitter.addWidget(self.effective_width_plot)
        self.graph_splitter.addWidget(self.fluid_pressure_plot)

        self.graph_splitter_vertical.addWidget(self.graph_splitter)
        self.graph_splitter_vertical.addWidget(self.rings)

        self.layout.addWidget(self.graph_splitter_vertical)
        self.setLayout(self.layout)

    def plot_results(self, projectdata: ProjectData, time_index):
        x = np.array(projectdata.results_by_time[time_index]["mesh"]["xc"])
        width = np.array(projectdata.results_by_time[time_index]["results"]["effective_width"])

        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref is None:
            self._effective_width_plot_ref = self.effective_width_plot.canvas.ax.plot(x, width, 'r')[0]
        else:
            self._effective_width_plot_ref.set_xdata(x)
            self._effective_width_plot_ref.set_ydata(width)
        self.effective_width_plot.canvas.draw()

        y = np.array(projectdata.results_by_time[time_index]["mesh"]["xc"])
        fluid = np.array(projectdata.results_by_time[time_index]["results"]["fluid_pressure"])

        if self._fluid_pressure_plot_ref is None:
            self._fluid_pressure_plot_ref = self.fluid_pressure_plot.canvas.ax.plot(y, fluid, 'g')[0]
        else:
            self._fluid_pressure_plot_ref.set_xdata(y)
            self._fluid_pressure_plot_ref.set_ydata(fluid)
        self.fluid_pressure_plot.canvas.draw()

        # ------------------------------------------------------
        # 2D Plot
        # ------------------------------------------------------

        def update_contour_colorbar():
            # Remove colorbar and colorbar axes
            if self._contour_cb:
                self._contour_cb.remove()

            # Create colorbar axes and generate colorbar
            self._contour_cax = make_axes_locatable(
                self.rings.canvas.ax
            ).append_axes("right", size="5%", pad="2.5%")
            self._contour_cb = self.rings.canvas.fig.colorbar(
                self._rings_ref, cax=self._contour_cax
            )

            # Colorbar settings
            self._contour_cax.set_title("$z, \\mu$m")

        x = np.array(projectdata.results_by_time[time_index]["mesh"]["xc"])
        H = projectdata.input_data["ReservoirProperties"]["PayZoneHeight"]
        z = np.linspace(-1.1 * (H / 2), 1.1 * (H / 2), 10)
        X, Z = np.meshgrid(x, z)
        W, _ = np.meshgrid(width, z)
        Z_cut = Z
        Z_cut[Z_cut>H/2] = H/2
        Z_cut[Z_cut<-H/2] = -H/2
        w2d = ((4*W)/(numpy.pi))*((1-(2*Z_cut/H)**2)**(1/2))

        if self._rings_ref is None:
            self._rings_ref = self.rings.canvas.ax.contourf(X, Z, w2d, levels=10, cmap="jet")
            update_contour_colorbar()
        else:
            for coll in self._rings_ref.collections:
                coll.remove()
                # Plot new contours
            self._rings_ref = self.rings.canvas.ax.contourf(X, Z, w2d, levels=10, cmap="jet")
            update_contour_colorbar()
        self.rings.canvas.draw()

    def clear_plots(self):
        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._effective_width_plot_ref is not None:
            self._effective_width_plot_ref.remove()
            self._effective_width_plot_ref = None

        if self._fluid_pressure_plot_ref is not None:
            self._fluid_pressure_plot_ref.remove()
            self._fluid_pressure_plot_ref = None

        if self._rings_ref is not None:
            self._rings_ref.remove()
            self._rings_ref = None

        self.effective_width_plot.canvas.draw()
        self.fluid_pressure_plot.canvas.draw()
        self.rings.canvas.draw()
