from collections.abc import Iterable

from phase.analysis.catalog import AcceptedCatalog
from phase.analysis.constraints import forecast_linear_images
from phase.analysis.phase_set import fold_mod_one, normalize_phase_set
from phase.analysis.selection import resolve_forecast_selection
from phase.reports.ledger import PublishedReport, ReportLedger
from phase.reports.publish import publish_report
from phase.trials.rational import RationalInput
from phase.trials.registry import TrialRegistry


def forecast(
    registry: TrialRegistry, catalog: AcceptedCatalog, reports: ReportLedger,
    artifact_ids: Iterable[str], time: RationalInput,
) -> PublishedReport:
    selection = resolve_forecast_selection(registry, catalog, artifact_ids, time)
    phases = normalize_phase_set(
        phase for image in forecast_linear_images(selection)
        for phase in fold_mod_one(*image)
    )
    return publish_report(reports, selection, phases)
