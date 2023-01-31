import sys
import copy
from PySide6.QtCore import QObject, Signal
from ExpressFrac.Runner import Runner


class CalculationWorker(QObject):
    progress = Signal()
    completed = Signal()

    def __init__(self):
        super().__init__()
        self.results = {}

    def run_simulation(self, input_data):
        sys.stdout.write("CalculationWorker: run simulation")
        # Start calculation and connect notifier
        solver = Runner(input_data, self._time_step_finished_notifier)
        solver.solve()

        # Emit "completed" signal when calculation is finished
        sys.stdout.write("\nCalculationWorker: calculation completed")
        self.completed.emit()

    def _time_step_finished_notifier(self, results_json):
        sys.stdout.write("CalculationWorker: results notifier called. Results saved in worker class")
        self.results = copy.deepcopy(results_json)
        self.progress.emit()
