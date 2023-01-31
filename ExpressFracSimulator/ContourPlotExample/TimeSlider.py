from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider


class TimeSlider(QSlider):
    def __init__(self, orientation=Qt.Horizontal, parent=None, time_start=0, time_end=100, n_step=100):
        super().__init__(orientation, parent)

        self.time_start = time_start
        self.time_end = time_end
        self.n_step = n_step

        self.set_n_step(n_step)
        self.setMinimum(time_start)
        self.setMaximum(time_end)

    def setMinimum(self, time_start):
        self.time_start = time_start

    def setMaximum(self, time_end):
        self.time_end = time_end

    def set_n_step(self, n_step):
        self.n_step = n_step
        super().setMinimum(0)
        super().setMaximum(self.n_step)

    def value(self):
        index = super().value()
        return self.time_start + index * (self.time_end - self.time_start) / self.n_step

    def value_idx(self):
        return super().value()
