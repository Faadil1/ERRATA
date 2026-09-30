from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

from errata.live.controlled_parser import parse_operational_transcript
from errata.live.coordinator import LiveTransactionCoordinator, PreparationError


@dataclass
class DirectEntryResult:
    label: str
    text: str
    entry_elapsed_ms: float
    processing_elapsed_ms: float
    total_elapsed_ms: float
    parsed_operations: list[str]
    result: list[dict[str, Any]]
    revision: int
    state_hash: str


def apply_direct_text(
    coordinator: LiveTransactionCoordinator,
    *,
    label: str,
    text: str,
    entry_elapsed_ms: float,
    call_id: str,
) -> DirectEntryResult:
    processing_started = perf_counter()
    parsed = parse_operational_transcript(
        text, coordinator.gtfs, coordinator.state
    )
    if parsed.unresolved_cues:
        raise PreparationError(
            "UNRESOLVED_EXPLICIT_CUES:" + ",".join(parsed.unresolved_cues)
        )
    if not parsed.operations:
        raise PreparationError("NO_BOUNDED_OPERATIONS")

    coordinator.bind_user_transcript(call_id, parsed.transcript)
    coordinator.prepare_tool_call(
        {
            "type": "tool.call",
            "call_id": call_id,
            "name": "stage_transit_change",
            "arguments": {"operations": parsed.operations},
        }
    )
    result = coordinator.finalize_pending()
    processing_elapsed_ms = (perf_counter() - processing_started) * 1000.0
    return DirectEntryResult(
        label=label,
        text=text,
        entry_elapsed_ms=entry_elapsed_ms,
        processing_elapsed_ms=processing_elapsed_ms,
        total_elapsed_ms=entry_elapsed_ms + processing_elapsed_ms,
        parsed_operations=parsed.operations,
        result=result,
        revision=coordinator.state.revision,
        state_hash=coordinator.state.state_hash,
    )


def result_dict(result: DirectEntryResult) -> dict[str, Any]:
    return asdict(result)
