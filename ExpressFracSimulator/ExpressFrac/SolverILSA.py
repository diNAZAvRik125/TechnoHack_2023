import numpy as np
import copy
from typing import Callable
from .DataContainers import Mesh, PumpingSchedule, ReservoirProperties
from .ElasticityKernel import ElasticityKernelPKN
from .Fracture import Fracture
from .TipAsymptotic import TipAsymptotic


class SolverILSA(object):
    def __init__(
        self, mesh: Mesh, reservoir_prop: ReservoirProperties, pumping_schedule: PumpingSchedule,
        notifier: Callable[[dict], None] = lambda x: None,
        front_tol: float = 1e-4, max_iter: float = 50, relaxation: float = 1
    ):
        # Copy input data
        self.mesh = copy.deepcopy(mesh)
        self.reservoir_prop = copy.deepcopy(reservoir_prop)
        self.pumping_schedule = copy.deepcopy(pumping_schedule)

        # Generate elasticity matrix and tip asymptotic
        self.elasticity_matrix = self.reservoir_prop.e_prime * ElasticityKernelPKN(
            self.mesh.xc, self.mesh.dx, self.reservoir_prop.pay_zone_height, is_symmetric=True
        ).kernel
        self.asymptotic = TipAsymptotic(self.reservoir_prop.e_prime, self.reservoir_prop.k_prime)
        self.init_volume = 0

        # Set solver settings
        self.max_iter = max_iter
        self.front_tol = front_tol
        self.relaxation = relaxation
        self.notifier = notifier

    def solve(self, init_fracture: Fracture, dt: float):
        fracture_old = copy.deepcopy(init_fracture)
        self.init_volume = init_fracture.fracture_volume()

        current_time = 0
        while current_time < self.pumping_schedule.time_end:
            current_time = np.minimum(current_time + dt, self.pumping_schedule.time_end)
            print("Current Time:", current_time)

            fracture_new, error, total_iter = self._solve_timestep(current_time, fracture_old)
            fracture_old = copy.deepcopy(fracture_new)
            import time
            time.sleep(0.08)
            # Call notify here
            results_json = self.fracture_to_json(fracture_old)
            self.notifier(results_json)

        return fracture_old

    def _solve_timestep(self, time_end: float, fracture_old: Fracture):
        fracture_new = copy.deepcopy(fracture_old)
        fracture_new.update_time(time_end)
        frac_volume = self.init_volume + 0.5 * self.pumping_schedule.injected_volume(0, time_end)

        error = 1
        iteration = 0
        front_loc_prev = fracture_new.front_location
        while error > self.front_tol and iteration < self.max_iter:
            # Update front location
            fracture_new.update_front_location(front_loc_prev)

            # Calculate tip width and restrict by half fracture volume
            tip_width = self.asymptotic.volume(fracture_new.tip_distance()) / self.mesh.dx[fracture_new.tip_ind]
            tip_width = np.minimum(tip_width, frac_volume / (2 * self.mesh.dx[0]))

            # Solve elasticity equation for opened part of the fracture
            max_ind = fracture_new.tip_ind + 1
            frac_width, frac_pressure = self._solve_elasticity(
                self.elasticity_matrix[:max_ind, :max_ind],
                tip_width, frac_volume, self.mesh.dx[:max_ind]
            )
            fracture_new.update_width(frac_width)
            fracture_new.update_pressure(frac_pressure)

            # Compute front location
            survey_dist = self.asymptotic.distance(fracture_new.width[fracture_new.survey_ind])
            front_loc_new = self.mesh.xc[fracture_new.survey_ind] + survey_dist

            # Front location relaxation and restriction
            # The new front location must be greater or equal than the location from the previous time step
            front_loc_new = self.relaxation * front_loc_new + (1 - self.relaxation) * front_loc_prev
            front_loc_new = np.maximum(front_loc_new, fracture_old.front_location)

            # Compute relative error
            error = np.abs((front_loc_new - front_loc_prev) / front_loc_prev)
            iteration += 1
            front_loc_prev = front_loc_new

        return fracture_new, error, iteration

    @staticmethod
    def _solve_elasticity(elasticity_matrix, tip_width, frac_volume, dx):
        # Compute auxiliary terms in w = E_1 * p_0 + E_2 * dp_tip,
        # where E_1 = C^{-1} * v_1, and E_2 = C^{-1} * v_2
        dim = elasticity_matrix.shape[0]
        elasticity_coeff_1 = np.linalg.solve(elasticity_matrix, np.ones(dim))
        elasticity_coeff_2 = np.linalg.solve(elasticity_matrix, np.concatenate((np.zeros(dim - 1), [1])))

        # Generate SLAE and solve with respect to [p_0, dp_tip]
        matrix = np.array([
            [np.sum(elasticity_coeff_1 * dx), np.sum(elasticity_coeff_2 * dx)],
            [elasticity_coeff_1[-1], elasticity_coeff_2[-1]]
        ])
        rhs = np.array([frac_volume, tip_width])
        solution = np.linalg.solve(matrix, rhs)

        # Compute width and pressure
        width = solution[0] * elasticity_coeff_1 + solution[1] * elasticity_coeff_2
        pressure = solution[0] * np.ones(dim)
        pressure[-1] = np.maximum(solution[1], 0)
        return width, pressure

    def fracture_to_json(self, fracture: Fracture):
        result = {
            "summary": {},
            "mesh": {},
            "results": {}
        }

        # Write summary information
        result["summary"]["time"] = float(fracture.time)
        result["summary"]["fracture_length"] = float(2 * fracture.front_location)
        result["summary"]["fracture_volume"] = \
            float(2 * fracture.fracture_volume())
        result["summary"]["injected_volume"] = float(self.pumping_schedule.injected_volume(0, fracture.time))

        # Write mesh data
        result["mesh"]["xc"] = fracture.mesh.xc.tolist()
        result["mesh"]["dx"] = fracture.mesh.dx.tolist()

        # Write 1D data
        result["results"]["effective_width"] = fracture.width.tolist()
        result["results"]["fluid_pressure"] = fracture.pressure.tolist()

        return result
