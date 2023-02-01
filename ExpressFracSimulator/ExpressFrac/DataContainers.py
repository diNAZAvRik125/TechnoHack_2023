import numpy as np


class Mesh(object):
    def __init__(self, xmax: float, nx: int):
        # @todo: xmax and nx validation
        self.xmax = xmax
        self.nx = nx

        dx_scalar = self.xmax / self.nx
        self.dx = dx_scalar * np.ones(nx)
        self.xc = -dx_scalar / 2 + dx_scalar * np.linspace(1, nx, nx)


class PumpingSchedule(object):
    def __init__(self, schedule, flowrate, pay_zone_height: float):
        # @todo: add schedule stages
        self.schedule = schedule
        self.time_start = schedule[0]
        self.time_end = schedule[-1]
        self.flowrate = flowrate
        self.H = pay_zone_height

    def mean_flowrate(self, time_start: float, time_end: float):
        return self.injected_volume(time_start, time_end) / (time_end - time_start)

    def injected_volume(self, time_start: float, time_end: float):
        ind_start = 0
        tlist = [time_start]
        while time_start > self.schedule[ind_start + 1]:
            ind_start = ind_start+1

        ind_end = ind_start+1
        while time_end > self.schedule[ind_end]:
            tlist.append(self.schedule[ind_end])
            ind_end = ind_end+1
        tlist.append(time_end)

        dV = 0
        i = 0
        for j in range(ind_start, ind_end):
            dV = dV + self.flowrate[j]*(tlist[i+1]-tlist[i])
            i = i + 1
        return dV/self.H


class ReservoirProperties(object):
    def __init__(
        self, pay_zone_height: float,
        young_modulus: float, poisson_ratio: float, toughness: float, leakoff_coefficient: float
    ):
        # @todo: input data validation
        self.young_modulus = young_modulus
        self.poisson_ratio = poisson_ratio
        self.toughness = toughness
        self.leakoff_coefficient = leakoff_coefficient
        self.pay_zone_height = pay_zone_height

        self.e_prime = self.young_modulus / (1 - np.power(self.poisson_ratio, 2))
        self.k_prime = np.sqrt(32 / np.pi) * self.toughness
        self.c_prime = 2 * self.leakoff_coefficient
