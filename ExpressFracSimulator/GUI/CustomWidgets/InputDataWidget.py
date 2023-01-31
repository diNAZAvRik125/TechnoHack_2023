from PySide6.QtCore import (
    QLocale
)
from PySide6.QtGui import (
    QDoubleValidator,
    QIntValidator
)
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QGroupBox,
    QSizePolicy
)
from .Spoiler import Spoiler


class InputDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.size_settings = {
            "input_bar_min_width": 250
        }

        self.layout = QVBoxLayout()

        # Initialize input validators
        self._init_validators()

        # Generate layout
        self._case_name_input()
        self._reservoir_properties_input()
        self._pumping_schedule_input()
        self._mesh_properties_input()
        self._solver_settings_input()

        self.layout.addStretch()

        self.setLayout(self.layout)

    def _init_validators(self):
        # Floating point validator allowing dot and comma as decimal separator
        self.fp_validator = QDoubleValidator()
        coeff_locale = QLocale(QLocale.English, QLocale.UnitedStates)
        self.fp_validator.setLocale(coeff_locale)

        # Integer validator allowing only non-negative values
        self.int_validator = QIntValidator()
        self.int_validator.setBottom(0)

    def _case_name_input(self):
        """
        Case name input layout
        """
        case_name_layout = QVBoxLayout()
        self.case_name_input = QLineEdit("Hydraulic Fracturing Case")
        case_name_layout.addWidget(self.case_name_input)

        # Put the reservoir properties layout to the group box
        case_name_group_box = QGroupBox("Case Name")
        case_name_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        case_name_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        case_name_group_box.setLayout(case_name_layout)

        self.layout.addWidget(case_name_group_box)

    def _reservoir_properties_input(self):
        """
        Reservoir properties input layout
        """
        reservoir_form_layout = QFormLayout()

        # Labels and input forms
        reservoir_labels = [
            "Pay-zone Height:",
            "Young Modulus:",
            "Poisson Ratio:",
            "Toughness:",
            "Leak-off coefficient:"
        ]
        self.reservoir_prop_input = [
            QLineEdit("20"),
            QLineEdit("2.0e9"),
            QLineEdit("0.3"),
            QLineEdit("5.0e6"),
            QLineEdit("0")
        ]

        # Assemble reservoir properties input form and set validator
        for reservoir_label, reservoir_input in zip(reservoir_labels, self.reservoir_prop_input):
            reservoir_form_layout.addRow(reservoir_label, reservoir_input)
            reservoir_input.setValidator(self.fp_validator)

        # Put the reservoir properties layout to the group box
        reservoir_group_box = QGroupBox("Reservoir Properties")
        reservoir_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        reservoir_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        reservoir_group_box.setLayout(reservoir_form_layout)

        self.layout.addWidget(reservoir_group_box)

    def _pumping_schedule_input(self):
        """
        Pumping schedule input layout
        """
        schedule_form_layout = QFormLayout()

        # Labels and input forms
        schedule_labels = [
            "Duration:",
            "Flowrate:"
        ]
        self.pumping_schedule_input = [
            QLineEdit("700"),
            QLineEdit("0.05")
        ]

        # Assemble pumping schedule input form
        for schedule_label, schedule_input in zip(schedule_labels, self.pumping_schedule_input):
            schedule_form_layout.addRow(schedule_label, schedule_input)
            schedule_input.setValidator(self.fp_validator)

        # Put the pumping schedule layout to the group box
        schedule_group_box = QGroupBox("Pumping Schedule")
        schedule_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        schedule_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        schedule_group_box.setLayout(schedule_form_layout)

        self.layout.addWidget(schedule_group_box)

    def _mesh_properties_input(self):
        """
        Mesh properties input layout
        """
        mesh_form_layout = QFormLayout()

        # Labels and input forms
        mesh_labels = [
            "Domain Size:",
            "Number of elements:"
        ]
        self.mesh_prop_input = [
            QLineEdit("100.0"),
            QLineEdit("200")
        ]

        # Assemble mesh properties input form
        for mesh_label, mesh_input in zip(mesh_labels, self.mesh_prop_input):
            mesh_form_layout.addRow(mesh_label, mesh_input)

        # Set mesh validators
        self.mesh_prop_input[0].setValidator(self.fp_validator)
        self.mesh_prop_input[1].setValidator(self.int_validator)

        # Put the mesh properties layout to the group box
        mesh_group_box = QGroupBox("Mesh Properties")
        mesh_group_box.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        mesh_group_box.setMinimumWidth(self.size_settings["input_bar_min_width"])
        mesh_group_box.setLayout(mesh_form_layout)

        self.layout.addWidget(mesh_group_box)

    def _solver_settings_input(self):
        """
        Solver settings input layout
        """
        solver_settings_form_layout = QFormLayout()

        # Labels and input forms
        solver_settings_labels = [
            "Time Step:",
            "Tolerance:",
            "Max Iterations:",
            "Relaxation Coefficient:"
        ]
        self.solver_settings_input = [
            QLineEdit("5.0"),
            QLineEdit("1.0e-4"),
            QLineEdit("200"),
            QLineEdit("0.7"),
        ]

        # Assemble solver settings input form
        for settings_label, settings_input in zip(solver_settings_labels, self.solver_settings_input):
            solver_settings_form_layout.addRow(settings_label, settings_input)

        # Set solver settings validators
        self.solver_settings_input[2].setValidator(self.int_validator)
        for ind in [0, 1, 3]:
            self.solver_settings_input[ind].setValidator(self.fp_validator)

        # Put the solver settings layout to the spoiler
        solver_settings_spoiler = Spoiler(title="Solver Settings")
        solver_settings_spoiler.setContentLayout(solver_settings_form_layout)

        self.layout.addWidget(solver_settings_spoiler)
