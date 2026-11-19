from fractions import Fraction
from typing import NamedTuple

from phase.analysis.selection import ForecastSelection


Window = tuple[Fraction, Fraction]


class LinearImage(NamedTuple):
    lower: Fraction
    upper: Fraction
    lower_closed: bool
    upper_closed: bool


def _intersect(left: tuple[Window, ...], right: tuple[Window, ...]) -> tuple[Window, ...]:
    result = []
    for low_a, high_a in left:
        for low_b, high_b in right:
            low, high = max(low_a, low_b), min(high_a, high_b)
            if low <= high:
                result.append((low, high))
    return tuple(sorted(set(result)))


def _windows_by_time(selection: ForecastSelection) -> dict[Fraction, tuple[Window, ...]]:
    domain = selection.trial.domain
    by_time: dict[Fraction, tuple[Window, ...]] = {}
    for accepted in selection.artifacts:
        for clause in accepted.artifact.evidence.clauses:
            time = clause.time
            bounds = ((time * domain.drift_low, 1 + time * domain.drift_high),)
            windows = tuple((-lower.limit, upper.limit) for upper, lower in clause.alternatives)
            by_time[time] = _intersect(by_time.get(time, bounds), windows)
    return by_time


def _images(windows: tuple[Window, ...], supremum: Fraction, offset: Fraction) -> tuple[LinearImage, ...]:
    return tuple(LinearImage(low + offset, high + offset, True, high < supremum)
                 for low, high in windows if low < supremum)


def forecast_linear_images(selection: ForecastSelection) -> tuple[LinearImage, ...]:
    domain = selection.trial.domain
    drift_low, drift_high = domain.drift_low, domain.drift_high
    by_time = _windows_by_time(selection)
    if any(not windows for windows in by_time.values()):
        return ()

    if len(by_time) == 1 and selection.time in by_time:
        return _images(by_time[selection.time], 1 + selection.time * drift_high, Fraction(0))

    if drift_low == drift_high:
        initial = ((Fraction(0), Fraction(1)),)
        for time, windows in by_time.items():
            shift = time * drift_low
            initial = _intersect(initial, tuple((low - shift, high - shift) for low, high in windows))
        return _images(initial, Fraction(1), selection.time * drift_low)

    phase_low, phase_high = Fraction(0), Fraction(1)
    for time, windows in by_time.items():
        lower = min(low for low, _ in windows)
        upper = max(high for _, high in windows)
        phase_low = max(phase_low, lower - time * domain.drift_high)
        phase_high = min(phase_high, upper - time * domain.drift_low)
        if time:
            drift_low = max(drift_low, (lower - 1) / time)
            drift_high = min(drift_high, upper / time)
    if phase_low > phase_high or phase_low == 1 or drift_low > drift_high:
        return ()
    return (LinearImage(phase_low + selection.time * drift_low,
                        phase_high + selection.time * drift_high, True, phase_high < 1),)
