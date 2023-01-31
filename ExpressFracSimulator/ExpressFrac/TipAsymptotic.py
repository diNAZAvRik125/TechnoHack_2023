import numpy as np
from typing import Sequence, Union


class TipAsymptotic(object):
    def __init__(self, e_prime: float, k_prime: float):
        self.e_prime = e_prime
        self.k_prime = k_prime

    def width(self, s: Union[float, Sequence[float]]) -> Union[float, np.ndarray]:
        return (np.pi / 4) * (self.k_prime / self.e_prime) * np.sqrt(s)

    def volume(self, s: Union[float, Sequence[float]]) -> Union[float, np.ndarray]:
        return (np.pi / 4) * ((2 * self.k_prime) / (3 * self.e_prime)) * np.power(s, 3 / 2)

    def distance(self, w: Union[float, Sequence[float]]) -> Union[float, np.ndarray]:
        return np.power((4 / np.pi) * (self.e_prime / self.k_prime) * w, 2)
