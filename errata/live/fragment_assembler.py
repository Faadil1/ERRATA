from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import re
from typing import Iterable


@dataclass(frozen=True)
class TranscriptFragment:
    item_id: str
    text: str


class RepairFragmentAssembler:
    """Bounded deterministic fallback for fragmented *correction* speech.

    This intentionally does not parse arbitrary initial service-change commands.
    It exists because real Voice Agent turns can split slow operational speech
    into multiple final transcript.user events. Only explicit correction
    language is eligible: KEEP=<currently skipped stop> and/or "make it <time>".

    Native AssemblyAI tool calls remain the preferred semantic proposer.
    """

    def __init__(self, max_fragments: int = 6):
        self.fragments: deque[TranscriptFragment] = deque(maxlen=max_fragments)

    def add(self, item_id: str, text: str) -> None:
        cleaned = " ".join(text.strip().split())
        if cleaned:
            self.fragments.append(TranscriptFragment(item_id=item_id, text=cleaned))

    def clear(self) -> None:
        self.fragments.clear()

    @property
    def text(self) -> str:
        return " ".join(f.text for f in self.fragments)

    @staticmethod
    def _norm(value: str) -> str:
        return " ".join(
            re.sub(r"[^a-z0-9]+", " ", value.lower()).split()
        )

    def correction_operations(self, state, gtfs) -> list[str]:
        combined = self.text
        normalized = self._norm(combined)
        if not normalized:
            return []

        ops: list[str] = []

        # Conservative KEEP fallback: an explicit "keep" must be present, and
        # the named stop must already be in the canonical skipped set.
        if re.search(r"\bkeep\b", normalized):
            keep_tail = normalized.rsplit("keep", 1)[-1]
            matched = []
            for stop_id in state.skip_stops:
                stop = gtfs.stop_by_id.get(stop_id)
                if not stop:
                    continue
                stop_name = self._norm(stop.stop_name)
                if stop_name and stop_name in keep_tail:
                    matched.append((stop.stop_sequence, stop.stop_name))
            for _, stop_name in sorted(matched):
                ops.append(f"KEEP={stop_name}")

        # Bounded time correction. "make it 10", "make it 9:45", etc.
        time_match = re.search(
            r"\bmake\s+it\s+(?:the\s+)?(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)?)\b",
            normalized,
        )
        if time_match and state.end_time is not None:
            value = time_match.group(1).replace(" ", "")
            ops.append(f"END={value}")

        # Never infer SKIP from fragment history. A misheard KEEP→SKIP must not
        # silently create or reinforce a consequential mutation.
        return ops
