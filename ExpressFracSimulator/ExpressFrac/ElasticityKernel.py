import numpy as np
from scipy.special import ellipe
from typing import Sequence, Union


class ElasticityKernelPKN(object):
    def __init__(self, xc: Sequence[float], dx: Sequence[float], H: float, is_symmetric=True):
        self.is_symmetric = is_symmetric
        if self.is_symmetric:
            self._compute_symmetric_kernel(xc, dx, H)
        else:
            self._compute_asymmetric_kernel(xc, dx, H)

    def _compute_asymmetric_kernel(self, xc: Sequence[float], dx: Sequence[float], H: float):
        receiver, source = np.meshgrid(xc, xc)
        receiver_dx, source_dx = np.meshgrid(dx, dx)
        self.kernel = (-2 / (np.pi * np.pi * H)) * (
            self.g_kernel(2 * (source - 0.5 * source_dx - receiver) / H) -
            self.g_kernel(2 * (source + 0.5 * source_dx - receiver) / H)
        )

    def _compute_symmetric_kernel(self, xc: Sequence[float], dx: Sequence[float], H: float):
        receiver, source = np.meshgrid(xc, xc)
        receiver_dx, source_dx = np.meshgrid(dx, dx)
        self.kernel = (-2 / (np.pi * np.pi * H)) * (
            (
                self.g_kernel(2 * (source - 0.5 * source_dx - receiver) / H) -
                self.g_kernel(2 * (source + 0.5 * source_dx - receiver) / H)
            ) -
            (
                self.g_kernel(2 * (-(source - 0.5 * source_dx) - receiver) / H) -
                self.g_kernel(2 * (-(source + 0.5 * source_dx) - receiver) / H)
            )
        )

    @staticmethod
    def g_kernel(s: Union[float, Sequence[float]]) -> Union[float, np.ndarray]:
        return ellipe(1 / (1 + np.power(s, 2))) * np.sqrt(1 + np.power(s, 2)) / s
