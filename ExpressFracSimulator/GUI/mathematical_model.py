import numpy as np
import time
import sys



class MathModel(object):
    def __init__(self, input_data, notifier=None):
        self.input_data = input_data

        # Set up notifier
        if notifier is None:
            self.notifier = self._default_notifier
        else:
            self.notifier = notifier
        self.n_notified = 0

    def _default_notifier(self, result_json):
        # Write results on disk or save results figures
        pass

    def notifier_wrapper(self, result_json):
        sys.stdout.write("MathModel: notifier wrapper called")
        self.n_notified += 1
        self.notifier(result_json)

    def super_long_time_loop(self):
        sys.stdout.write(
            "MathModel: Input data obtained by mathematical model: {json_data}".format(json_data=self.input_data)
        )
        for i in range(1, 11):
            # Very long time step computation
            time.sleep(1.0)

            # Generate JSON output
            n_data = 100
            results = {
                "time": i,
                "x": np.linspace(-30, 30, n_data),
                "width": np.random.uniform(-1, 1, n_data)
            }
            sys.stdout.write("\nMathModel: time step finished")

            # Call notifier
            self.notifier_wrapper(results)
