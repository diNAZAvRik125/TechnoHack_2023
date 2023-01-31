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
    def __init__(self, duration: float, flowrate: float, pay_zone_height: float):
        # @todo: add schedule stages
        self.time_start = 0
        self.time_end = duration
        self.flowrate = flowrate
        self.H = pay_zone_height

    def mean_flowrate(self, time_start: float, time_end: float):
        return self.injected_volume(time_start, time_end) / (time_end - time_start)

    def injected_volume(self, time_start: float, time_end: float):
        return (time_end - time_start) * self.flowrate / self.H


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
