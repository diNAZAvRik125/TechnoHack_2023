from PySide6.QtCore import Signal, QObject


class EmittingStream(QObject):
    """
    # Adapted from stackoverflow answer
    https://stackoverflow.com/questions/50077356/redirecting-stdout-from-a-secondary-thread-multithreading-with-a-function-inste
    @todo thread-safety using
    https://stackoverflow.com/questions/21071448/redirecting-stdout-and-stderr-to-a-pyqt4-qtextedit-from-a-secondary-thread
    """
    stdout_written = Signal(str)

    def write(self, text):
        self.stdout_written.emit(str(text))
