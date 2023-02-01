import numpy as np
import json
from pathlib import Path
from .DataContainers import Mesh, PumpingSchedule, ReservoirProperties
from .Fracture import Fracture
from .SolverILSA import SolverILSA


class Runner(object):
    def __init__(self, input_data, notifier=None):
        if isinstance(input_data, dict):
            self.input_data = input_data
        elif isinstance(input_data, str):
            with open(input_data) as f:
                self.input_data = json.load(f)
        else:
            raise Exception("Unsupported input data type: " + str(type(input_data)))

        # Set up notifier
        if notifier is None:
            self.notifier = self._default_notifier
        else:
            self.notifier = notifier
        self.n_notified = 0

        self._parse_input_json()
        self._generate_init_frac()

    def solve(self):
        return self.solver.solve(self.init_fracture, self.dt)

    def _parse_input_json(self):
        # Parse input data
        mesh = Mesh(self.input_data["MeshProperties"]["xmax"], self.input_data["MeshProperties"]["nx"])
        H = self.input_data["ReservoirProperties"]["PayZoneHeight"]
        reservoir_prop = ReservoirProperties(
            H,
            self.input_data["ReservoirProperties"]["YoungModulus"],
            self.input_data["ReservoirProperties"]["PoissonRatio"],
            self.input_data["ReservoirProperties"]["Toughness"],
            self.input_data["ReservoirProperties"]["LeakoffCoefficient"]
        )
        pumping_schedule = PumpingSchedule(
            self.input_data["PumpingSchedule"]["Schedule"],
            self.input_data["PumpingSchedule"]["Flowrate"],
            H
        )

        # Save parsed data to solver
        self.solver = SolverILSA(
            mesh, reservoir_prop, pumping_schedule,
            front_tol=self.input_data["SolverSettings"]["FrontTolerance"],
            max_iter=self.input_data["SolverSettings"]["FrontMaxIter"],
            relaxation=self.input_data["SolverSettings"]["FrontRelaxationCoeff"],
            notifier=self.notifier_wrapper
        )
        self.dt = self.input_data["SolverSettings"]["TimeStep"]

    def _generate_init_frac(self):
        self.init_fracture = Fracture(self.solver.mesh)
        self.init_fracture.update_front_location(1.5 * self.solver.mesh.dx[0])
        self.init_fracture.update_width(np.array([1e-8, 1e-8]))
        self.init_fracture.update_time(0)

    def _default_notifier(self, result_json):
        path = "./" + self.input_data["CaseName"] + "/"
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + "sim_result_" + str(self.n_notified) + ".json", 'w') as fp:
            json.dump(result_json, fp, indent=4)

    def notifier_wrapper(self, result_json):
        self.n_notified += 1
        self.notifier(result_json)
