from fractions import Fraction
from math import ceil

from phase.station.evidence import CalibrationClause, LinearBound, StationEvidence
from phase.station.selection import FrozenSelection


def compile_station_evidence(selection: FrozenSelection) -> StationEvidence:
    domain = selection.trial.domain
    clauses = []
    for revision in selection.revisions:
        time = domain.require_time(revision.time)
        low = Fraction(0) if revision.arc.crosses_zero() else revision.arc.start
        high = revision.arc.end
        minimum = time * domain.drift_low
        supremum = 1 + time * domain.drift_high
        strips = tuple(
            (LinearBound(Fraction(1), time, min(supremum, high + turn)),
             LinearBound(Fraction(-1), -time, -max(minimum, low + turn)))
            for turn in range(ceil(minimum - high), ceil(supremum - low))
        )
        clauses.append(CalibrationClause(strips))
    return StationEvidence(tuple(clauses))
