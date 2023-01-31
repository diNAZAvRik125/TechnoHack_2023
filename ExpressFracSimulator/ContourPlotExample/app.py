from PySide6.QtCore import Qt, QLocale
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QWidget,
    QPushButton,
    QSlider,
    QSizePolicy,
    QSplitter
)

import sys
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from TimeSlider import TimeSlider
from MplWidget import MplWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.size_settings = {
            "input_bar_min_width": 250
        }

        # Window title
        self.setWindowTitle("Simple plot app")

        # Main window layout
        page_layout = QHBoxLayout()
        self._set_input_layout(page_layout)
        self._set_results_layout(page_layout)

        # Initialization
        self._update_results_slot()
        self._update_time_slot()

        container = QWidget()
        container.setLayout(page_layout)
        self.setCentralWidget(container)

    def _set_input_layout(self, page_layout):
        layout_input = QVBoxLayout()

        # ------------------------------------------------------
        # Coefficients input layout
        # ------------------------------------------------------
        coeff_form_layout = QFormLayout()

        # Labels and input forms
        coeff_labels = ["A:", "B:", "C:", "k:"]
        self.coeff_inputs = [
            QLineEdit("1"),
            QLineEdit("3"),
            QLineEdit("0"),
            QLineEdit("2.0e-1")
        ]

        # Input form validator allowing dot and comma as decimal separator
        coeff_validator = QDoubleValidator()
        coeff_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        coeff_validator.setLocale(coeff_locale)

        # Assemble coefficients input form and set validator
        for coeff_label, coeff_input in zip(coeff_labels, self.coeff_inputs):
            coeff_form_layout.addRow(coeff_label, coeff_input)
            coeff_input.setValidator(coeff_validator)

        # Put the coefficients layout to the group box
        coeff_group_box = QGroupBox("Coefficients")
        coeff_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        coeff_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        coeff_group_box.setLayout(coeff_form_layout)

        # ------------------------------------------------------
        # Time range input layout
        # ------------------------------------------------------
        time_range_form_layout = QFormLayout()

        # Labels and input forms
        time_range_labels = [
            "Min time:",
            "Max time:",
            "Number of points:"
        ]
        self.time_range_inputs = [
            QLineEdit("0"),
            QLineEdit("11.7"),
            QLineEdit("100")
        ]

        # Number of time points validator
        time_n_points_validator = QIntValidator()
        time_n_points_validator.setBottom(0)

        # Assemble time range input form
        for time_label, time_input in zip(time_range_labels, self.time_range_inputs):
            time_range_form_layout.addRow(time_label, time_input)

        # Set validators
        self.time_range_inputs[0].setValidator(coeff_validator)
        self.time_range_inputs[1].setValidator(coeff_validator)
        self.time_range_inputs[2].setValidator(time_n_points_validator)

        # Put the time range layout to the group box
        time_range_group_box = QGroupBox("Time range")
        time_range_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        time_range_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        time_range_group_box.setLayout(time_range_form_layout)

        # ------------------------------------------------------
        # Update results button
        # ------------------------------------------------------
        self.update_results_button = QPushButton("Update Results")
        self.update_results_button.clicked.connect(self._update_results_slot)

        # ------------------------------------------------------
        # Assemble input layout
        # ------------------------------------------------------
        layout_input.addWidget(coeff_group_box)
        layout_input.addWidget(time_range_group_box)
        layout_input.addWidget(self.update_results_button)
        layout_input.addStretch()

        page_layout.addLayout(layout_input)

    def _set_results_layout(self, page_layout):
        layout_results = QVBoxLayout()

        # ------------------------------------------------------
        # Time Label
        # ------------------------------------------------------
        self.current_time_label = QLabel()
        self.current_time_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        # ------------------------------------------------------
        # Time Slider
        # ------------------------------------------------------
        self.time_slider = TimeSlider()
        self.time_slider.setTickPosition(QSlider.TicksAbove)
        self.time_slider.valueChanged.connect(self._update_time_slot)

        # ------------------------------------------------------
        # Function plot widget
        # ------------------------------------------------------
        self.plot_widget = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$y$",
            title="$y = (A x^2 + B x + C)\\sin{(ktx)}$",
            is_grid=True,
            is_autoscale=True
        )
        self.plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Plot reference to update graph
        self._plot_ref = None

        # ------------------------------------------------------
        # Contour plot widget
        # ------------------------------------------------------
        self.contour_plot_widget = MplWidget(
            self,
            figsize=(6, 4),
            xlabel="$x$",
            ylabel="$y$",
            title="$z = [\\sin(x + t) + \\sin(y (1 + k \\sin{t}) + t)] / (1 + |t|)$"
        )
        self.contour_plot_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Plot reference to update graph
        self._contour_plot_ref = None
        self._contour_cax = None
        self._contour_cb = None

        # ------------------------------------------------------
        # Plot splitter
        # ------------------------------------------------------
        self.plot_splitter = QSplitter(Qt.Vertical)
        self.plot_splitter.addWidget(self.plot_widget)
        self.plot_splitter.addWidget(self.contour_plot_widget)

        # ------------------------------------------------------
        # Assemble results layout
        # ------------------------------------------------------
        layout_results.addWidget(self.current_time_label)
        layout_results.addWidget(self.time_slider)
        layout_results.addWidget(self.plot_splitter)

        page_layout.addLayout(layout_results)

    def _update_results_slot(self):
        coeff_locale = QLocale(QLocale.English, QLocale.UnitedStates)

        # Convert coefficients to floating point values
        self.coeff_values = []
        for coeff_input in self.coeff_inputs:
            coeff, status = coeff_locale.toDouble(coeff_input.text().replace(",", "."))
            # @todo: check for conversion status (second parameter in output tuple)
            self.coeff_values.append(coeff)

        # Get time range data
        min_time, _ = coeff_locale.toDouble(self.time_range_inputs[0].text().replace(",", "."))
        max_time, _ = coeff_locale.toDouble(self.time_range_inputs[1].text().replace(",", "."))
        n_step, _ = coeff_locale.toInt(self.time_range_inputs[2].text())
        self.time_slider.set_n_step(n_step)
        self.time_slider.setMinimum(min_time)
        self.time_slider.setMaximum(max_time)

        # If success then update plot
        self._update_plot_slot()

    def _update_plot_slot(self):
        time = self.time_slider.value()
        x = np.linspace(-10, 10, 100)
        y = (self.coeff_values[0] * x * x + self.coeff_values[1] * x + self.coeff_values[2]) * \
            np.cos(self.coeff_values[3] * x * time)
        xx, yy = np.meshgrid(x, x)
        z_mult = (1 / (1 + np.abs(time)))
        z = z_mult * (np.sin(xx + time) + np.sin(yy * (1 + self.coeff_values[3] * np.sin(time)) + time))

        # ------------------------------------------------------
        # 1D Plot
        # ------------------------------------------------------
        if self._plot_ref is None:
            self._plot_ref = self.plot_widget.canvas.ax.plot(x, y, 'r')[0]
        else:
            self._plot_ref.set_xdata(x)
            self._plot_ref.set_ydata(y)

        self.plot_widget.canvas.draw()

        # ------------------------------------------------------
        # 2D Contour Plot
        # ------------------------------------------------------
        n_contours = 75

        # Update colorbar after contour plot redrawing
        def update_contour_colorbar():
            # Remove colorbar and colorbar axes
            if self._contour_cb:
                self._contour_cb.remove()

            # Create colorbar axes and generate colorbar
            self._contour_cax = make_axes_locatable(
                self.contour_plot_widget.canvas.ax
            ).append_axes("right", size="5%", pad="2.5%")
            self._contour_cb = self.contour_plot_widget.canvas.fig.colorbar(
                self._contour_plot_ref, cax=self._contour_cax
            )

            # Colorbar settings
            self._contour_cax.set_title("$z, \\mu$m")

        if self._contour_plot_ref is None:
            self._contour_plot_ref = self.contour_plot_widget.canvas.ax.contourf(x, x, z, levels=n_contours, cmap="jet")
            update_contour_colorbar()
        else:
            # Remove current contours
            for coll in self._contour_plot_ref.collections:
                coll.remove()
            # Plot new contours
            self._contour_plot_ref = self.contour_plot_widget.canvas.ax.contourf(x, x, z, levels=n_contours, cmap="jet")
            update_contour_colorbar()

        self.contour_plot_widget.canvas.draw()

    def _update_time_slot(self):
        self.current_time_label.setText("Time: " + str(round(self.time_slider.value(), 2)) + " s")
        self._update_plot_slot()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
