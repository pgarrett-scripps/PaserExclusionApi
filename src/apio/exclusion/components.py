import logging
import sys
from dataclasses import dataclass, asdict

from typing import Any

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

#TODO: Remove defaults
@dataclass(eq=True)
class ExclusionInterval():
    """
    Represents an excluded interval for RealTime APIO

    id: can be any type, and does not have to be unique. Can be None to represent any id interval
    charge: The charge of the excluded interval. 0 is interpreted as any charge.
    min_mass
    """
    id: str | None = 'PEPTIDE'
    charge: int | None = 1
    min_mass: float | None = 1000
    max_mass: float | None = 1001
    min_rt: float | None = 1000
    max_rt: float | None = 1001
    min_ook0: float | None = 1000
    max_ook0: float | None = 1001
    min_intensity: float | None = 1000
    max_intensity: float | None = 1001

    def __post_init__(self):
        """
        If any bounds are None, set them to either min/max float
        """

        if self.min_mass is None:
            self.min_mass = sys.float_info.min

        if self.max_mass is None:
            self.max_mass = sys.float_info.max

        if self.min_rt is None:
            self.min_rt = sys.float_info.min

        if self.max_rt is None:
            self.max_rt = sys.float_info.max

        if self.min_ook0 is None:
            self.min_ook0 = sys.float_info.min

        if self.max_ook0 is None:
            self.max_ook0 = sys.float_info.max

        if self.min_intensity is None:
            self.min_intensity = sys.float_info.min

        if self.max_intensity is None:
            self.max_intensity = sys.float_info.max

    def is_enveloped_by(self, other: 'ExclusionInterval'):

        if other.charge is not None and self.charge != other.charge:  # data must have correct charge
            return False

        if self.min_mass < other.min_mass or self.max_mass > other.max_mass:
            return False

        if self.min_rt < other.min_rt or self.max_rt > other.max_rt:
            return False

        if self.min_ook0 < other.min_ook0 or self.max_ook0 > other.max_ook0:
            return False

        if self.min_intensity < other.min_intensity or self.max_intensity > other.max_intensity:
            return False

        return True

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

    def is_point(self):
        if self.min_mass != self.max_mass:
            return False
        if self.min_rt != self.max_rt:
            return False
        if self.min_ook0 != self.max_ook0:
            return False
        if self.min_intensity != self.max_intensity:
            return False
        return True

@dataclass()
class ExclusionPoint:
    """
    Represents a point in the apio list. Values which are set to num will not be considered when verifying bounds
    """
    charge: int | None
    mass: float | None
    rt: float | None
    ook0: float | None
    intensity: float | None

    def is_bounded_by(self, interval: ExclusionInterval) -> bool:
        """
        Check if point given by is_excluded() is within interval
        """
        if self.charge is not None and interval.charge is not None and self.charge != interval.charge:
            logging.debug(f'Charge oob: self {self.charge}, interval {interval.charge}')
            return False
        if self.mass is not None and (self.mass < interval.min_mass or self.mass >= interval.max_mass):
            logging.debug(f'mass oob: self {self.mass}, interval.min {interval.min_mass}, interval.max {interval.max_mass}')
            return False
        if self.rt is not None and (self.rt < interval.min_rt or self.rt >= interval.max_rt):
            logging.debug(f'rt oob: self {self.rt}, interval.min {interval.min_rt}, interval.max {interval.max_rt}')
            return False
        if self.ook0 is not None and (self.ook0 < interval.min_ook0 or self.ook0 >= interval.max_ook0):
            logging.debug(f'ook0 oob: self {self.ook0}, interval.min {interval.min_ook0}, interval.max {interval.max_ook0}')
            return False
        if self.intensity is not None and (self.intensity < interval.min_intensity or self.intensity >= interval.max_intensity):
            logging.debug(f'intensity intensity: self {self.intensity}, interval.min {interval.min_intensity}, interval.max {interval.max_intensity}')
            return False
        return True