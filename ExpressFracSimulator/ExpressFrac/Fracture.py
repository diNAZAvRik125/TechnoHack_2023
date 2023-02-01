import numpy as np
from bisect import bisect_right
from .DataContainers import Mesh


class Fracture(object):
    def __init__(self, mesh: Mesh):
        self.mesh = mesh
        self.width = np.zeros(self.mesh.nx)
        self.pressure = np.zeros(self.mesh.nx)
        self.front_location = 0
        self.tip_ind = 0
        self.survey_ind = 0
        self.time = 0
        self.exposure_time = np.zeros(self.mesh.nx)

    def update_front_location(self, front_location: float):
        self.front_location = front_location
        tip_ind_old = self.tip_ind
        self.tip_ind = bisect_right(self.mesh.xc + self.mesh.dx / 2, self.front_location)
        self.exposure_time[tip_ind_old:self.tip_ind] = self.time
        self.survey_ind = self.tip_ind - 1
        if self.survey_ind < 0:
            raise Exception("Survey index is invalid. Probably the fracture length is less than element size.")

    def update_width(self, fracture_width: np.ndarray):
        if fracture_width.size > self.mesh.nx:
            raise Exception("Invalid dimension: Fracture width size is greater than the mesh.nx")
        self.width = np.zeros(self.mesh.nx)
        self.width[:fracture_width.size] = fracture_width

    def update_pressure(self, fracture_pressure: np.ndarray):
        if fracture_pressure.size > self.mesh.nx:
            raise Exception("Invalid dimension: Fracture width size is greater than the mesh.nx")
        self.pressure = np.zeros(self.mesh.nx)
        self.pressure[:fracture_pressure.size] = fracture_pressure

    def update_time(self, time):
        self.time = time

    def tip_distance(self):
        return np.maximum(self.front_location - (self.mesh.xc[self.tip_ind] - self.mesh.dx[self.tip_ind] / 2), 0)

    def fracture_volume(self):
        return np.sum(self.width * self.mesh.dx)
