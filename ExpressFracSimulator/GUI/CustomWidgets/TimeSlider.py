import math
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QSlider, QVBoxLayout, QStyle, QStyleOptionSlider
from PySide6.QtCore import QRect, QPoint, Qt, QTime


class TimeSlider(QWidget):
    """
    Solution based on
    https://stackoverflow.com/questions/47494305/python-pyqt4-slider-with-tick-labels
    """
    def __init__(self, minimum, maximum, interval=1, time_data=None, labels_fill_factor=0.7, parent=None):
        super().__init__(parent=parent)

        levels = range(minimum, maximum + interval, interval)
        if time_data is not None:
            if not isinstance(time_data, (tuple, list)):
                raise Exception("<time_data> is must be a list or tuple.")
            if len(time_data) != len(levels):
                raise Exception("Size of <labels> doesn't match levels.")
            self.levels = list(zip(levels, map(self.timeToString, time_data)))
        else:
            self.levels = list(zip(levels, map(self.timeToString, levels)))

        self.layout = QVBoxLayout(self)

        # Labels fill factor relative to available slider size
        self.labels_fill_factor = labels_fill_factor

        # gives some space to print labels
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10

        self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(minimum)
        self.slider.setMaximum(maximum)
        self.slider.setValue(minimum)
        self.slider.setTickPosition(QSlider.TicksAbove)
        self.slider.setTickInterval(interval)
        self.slider.setSingleStep(1)

        self.layout.addWidget(self.slider)

    def timeToString(self, time):
        # @todo adaptive time format based on max time value
        return QTime(0, 0).addSecs(time).toString("hh:mm:ss")

    def appendTime(self, time, update_value=True):
        # Increase time counter and append new time label
        max_new = self.slider.maximum() + 1
        self.levels.append((max_new, self.timeToString(time)))
        self.slider.setMaximum(max_new)

        # Update current slider position
        if update_value:
            self.slider.setValue(max_new)

        # Update widget in order to redraw labels
        self.update()

    def reset(self):
        # Reset slider values
        self.slider.setMinimum(-1)
        self.slider.setMaximum(-1)
        self.slider.setValue(-1)

        # Reset slider labels
        self.levels = [(-1, self.timeToString(0))]

        # Reset margins
        self.left_margin = 10
        self.top_margin = 10
        self.right_margin = 10
        self.bottom_margin = 10
        self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

        # Update widget in order to redraw labels
        self.update()

    def paintEvent(self, e):
        super().paintEvent(e)

        # Initialize paint style
        style = self.slider.style()
        painter = QPainter(self)
        st_slider = QStyleOptionSlider()
        st_slider.initFrom(self.slider)
        st_slider.orientation = self.slider.orientation()

        # Obtain pixel metrics for slider components
        tick_mark_offset = style.pixelMetric(QStyle.PM_SliderTickmarkOffset, st_slider, self.slider)
        length = style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.slider)
        available = style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.slider)

        # Compute indices to paint to avoid labels clipping
        label_text = self.timeToString(0)
        label_width = painter.drawText(QRect(), Qt.TextDontPrint, label_text).width()
        n_labels_new = self.labels_fill_factor * available / label_width
        label_interval = math.ceil(len(self.levels) / n_labels_new)
        ind_to_print = list(range(len(self.levels) - 1, -1, -label_interval))

        for index in ind_to_print:
            v, v_str = self.levels[index]

            # Get the size of the label
            rect = painter.drawText(QRect(), Qt.TextDontPrint, v_str)

            # It's assumed the offset is half the length of slider, therefore + length // 2
            x_loc = QStyle.sliderPositionFromValue(
                self.slider.minimum(), self.slider.maximum(), v, available
            ) + length // 2

            # Left bound of the text = center - half of text width + L_margin
            left = x_loc - rect.width() // 2 + self.left_margin
            bottom = self.rect().top() + rect.height()

            # Enlarge margins if clipping
            if v == self.slider.maximum():
                if left <= 0:
                    self.left_margin = rect.width() // 2 - x_loc
                if self.top_margin <= rect.height() + tick_mark_offset:
                    self.top_margin = rect.height() + tick_mark_offset
                self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            if v == self.slider.maximum() and rect.width() // 2 >= self.right_margin:
                self.right_margin = rect.width() // 2
                self.layout.setContentsMargins(self.left_margin, self.top_margin, self.right_margin, self.bottom_margin)

            pos = QPoint(left, bottom)
            painter.drawText(pos, v_str)
