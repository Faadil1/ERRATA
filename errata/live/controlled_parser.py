from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedVoiceBatch:
    transcript: str
    operations: list[str]
    unresolved_cues: tuple[str, ...] = ()


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9:]+", " ", text.lower()).split())


def _route_mentions(text: str, gtfs) -> list[tuple[int, str]]:
    norm = _norm(text)
    out: list[tuple[int, str]] = []
    for route in gtfs.routes:
        short = str(route.get("route_short_name", "")).strip()
        if not short:
            continue
        variants = {short.lower()}
        if short.isdigit() and len(short) == 2:
            variants.add(f"{short[0]} {short[1]}")
        for variant in variants:
            for prefix in ("route ", ""):
                needle = prefix + variant
                match = re.search(rf"\b{re.escape(needle)}\b", norm)
                if match:
                    out.append((match.start(), short))
    return sorted(out)


def _direction_mentions(text: str) -> list[tuple[int, str]]:
    norm = _norm(text)
    aliases = [
        ("westbound", "west"),
        ("west", "west"),
        ("ouest", "west"),
        ("eastbound", "east"),
        ("east", "east"),
        ("direction zero", "0"),
        ("direction 0", "0"),
        ("direction one", "1"),
        ("direction 1", "1"),
    ]
    out = []
    for token, canonical in aliases:
        m = re.search(rf"\b{re.escape(token)}\b", norm)
        if m:
            out.append((m.start(), canonical))

    # Standard GTFS direction_id is an agency-defined binary value; it does not
    # universally mean east/west. Public-network tests therefore use explicit
    # direction 0 / direction 1 wording instead of fabricating a compass label.
    for m in re.finditer(r"\bdirection(?:\s+id)?\s*([01])\b", norm):
        out.append((m.start(), m.group(1)))

    return sorted(out)


def _action_positions(norm: str, action: str) -> list[int]:
    return [m.start() for m in re.finditer(rf"\b{action}\b", norm)]


def _nearest_action_before(position: int, skip_pos: list[int], keep_pos: list[int]) -> str | None:
    candidates = [(p, "SKIP") for p in skip_pos if p <= position]
    candidates += [(p, "KEEP") for p in keep_pos if p <= position]
    if not candidates:
        return None
    return max(candidates, key=lambda x: x[0])[1]


def _stop_mentions(text: str, gtfs) -> list[tuple[int, str]]:
    norm = _norm(text)
    out: list[tuple[int, str]] = []
    for stop in gtfs.stop_by_id.values():
        name_norm = _norm(stop.stop_name)
        if not name_norm:
            continue
        for m in re.finditer(rf"\b{re.escape(name_norm)}\b", norm):
            out.append((m.start(), stop.stop_name))
    return sorted(out)


TIME_RE = r"(\d{1,2}(?::\d{2})?\s*(?:a\.?m\.?|p\.?m\.?)?)"


def parse_operational_transcript(text: str, gtfs, state) -> ParsedVoiceBatch:
    norm = _norm(text)
    events: list[tuple[int, int, str]] = []
    order = 0

    routes = _route_mentions(text, gtfs)
    if routes:
        events.append((routes[0][0], order, f"ROUTE={routes[0][1]}"))
        order += 1

    directions = _direction_mentions(text)
    if directions:
        events.append((directions[0][0], order, f"DIRECTION={directions[0][1]}"))
        order += 1

    skip_pos = _action_positions(norm, "skip")
    keep_pos = _action_positions(norm, "keep")
    for pos, stop_name in _stop_mentions(text, gtfs):
        action = _nearest_action_before(pos, skip_pos, keep_pos)
        if action is None:
            continue
        events.append((pos, order, f"{action}={stop_name}"))
        order += 1

    for m in re.finditer(rf"\buntil\s+{TIME_RE}", norm):
        value = m.group(1).replace(" ", "")
        events.append((m.start(), order, f"END={value}"))
        order += 1

    for m in re.finditer(rf"\bmake\s+it\s+(?:the\s+)?{TIME_RE}", norm):
        value = m.group(1).replace(" ", "")
        events.append((m.start(), order, f"END={value}"))
        order += 1

    events.sort(key=lambda x: (x[0], x[1]))
    ops = [event[2] for event in events]
    if state.route_ref is not None:
        ops = [op for op in ops if not op.startswith("ROUTE=")]
    if state.route_direction is not None:
        ops = [op for op in ops if not op.startswith("DIRECTION=")]

    deduped: list[str] = []
    seen: set[str] = set()
    for op in ops:
        if op in seen:
            continue
        seen.add(op)
        deduped.append(op)
    ops = deduped

    unresolved: list[str] = []
    has_end = any(op.startswith("END=") for op in ops)
    has_skip = any(op.startswith("SKIP=") for op in ops)
    has_keep = any(op.startswith("KEEP=") for op in ops)
    has_route = state.route_ref is not None or any(op.startswith("ROUTE=") for op in ops)

    if re.search(r"\bmake\s+it\b", norm) and not has_end:
        unresolved.append("END_TIME_AFTER_MAKE_IT")
    elif re.search(r"\bmake\b", norm) and not has_end:
        unresolved.append("UNRESOLVED_MAKE_CUE")
    if not has_end and (has_keep or has_skip):
        unbound_time = re.search(
            r"\b(?:(?:[01]?\d|2[0-3])(?::[0-5]\d)?|"
            r"one|two|three|four|five|six|seven|eight|nine|ten|"
            r"eleven|twelve|noon|midnight)\b",
            norm,
        )
        if unbound_time:
            unresolved.append("UNBOUND_TIME_VALUE")
    if re.search(r"\buntil\b", norm) and not has_end:
        unresolved.append("END_TIME_AFTER_UNTIL")
    if re.search(r"\bskip\b", norm) and not has_skip:
        unresolved.append("SKIP_TARGET")
    if re.search(r"\bkeep\b", norm) and not has_keep:
        unresolved.append("KEEP_TARGET")
    if re.search(r"\broute\b", norm) and not has_route:
        unresolved.append("ROUTE_TARGET")

    return ParsedVoiceBatch(
        transcript=text.strip(),
        operations=ops,
        unresolved_cues=tuple(dict.fromkeys(unresolved)),
    )
