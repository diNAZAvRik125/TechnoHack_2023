import copy
from PySide6.QtCore import QObject, QLocale
from CustomWidgets import InputDataWidget

class ProjectData(QObject):
    def __init__(self):
        super().__init__()

        self.input_data = {}
        self.results_by_time = []

    def update_input_data(self, input_form_widget: InputDataWidget):
        convert_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.input_data = {
            "ReservoirProperties": {
                "PayZoneHeight": convert_locale.toDouble(
                    input_form_widget.reservoir_prop_input[0].text().replace(",", ".")
                )[0],
                "YoungModulus": convert_locale.toDouble(
                    input_form_widget.reservoir_prop_input[1].text().replace(",", ".")
                )[0],
                "PoissonRatio": convert_locale.toDouble(
                    input_form_widget.reservoir_prop_input[2].text().replace(",", ".")
                )[0],
                "Toughness": convert_locale.toDouble(
                    input_form_widget.reservoir_prop_input[3].text().replace(",", ".")
                )[0],
                "LeakoffCoefficient": convert_locale.toDouble(
                    input_form_widget.reservoir_prop_input[4].text().replace(",", ".")
                )[0]
            },
            "PumpingSchedule": {
                "Duration": convert_locale.toDouble(
                    input_form_widget.pumping_schedule_input[0].text().replace(",", ".")
                )[0],
                "Flowrate": convert_locale.toDouble(
                    input_form_widget.pumping_schedule_input[1].text().replace(",", ".")
                )[0]
            },
            "MeshProperties": {
                "xmax": convert_locale.toDouble(
                    input_form_widget.mesh_prop_input[0].text().replace(",", ".")
                )[0],
                "nx": convert_locale.toDouble(
                    input_form_widget.mesh_prop_input[1].text().replace(",", ".")
                )[0]
            }
        }

    def append_result(self, result_json):
        self.results_by_time.append(copy.deepcopy(result_json))

    def clear_results(self):
        self.results_by_time.clear()
