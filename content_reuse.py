from __future__ import annotations

from copy import deepcopy

from content_medical import PACKETS_MEDICAL


_BY_OLD_NUMBER = {packet["n"]: packet for packet in PACKETS_MEDICAL}


def legacy_medical(old_number: int, new_number: int, group: str, title: str | None = None) -> dict:
    """Reuse the already authored medical packet under the updated ranking."""
    packet = deepcopy(_BY_OLD_NUMBER[old_number])
    packet["n"] = new_number
    if title:
        packet["title"] = title
    packet.pop("part", None)
    packet["group"] = group
    packet["field"] = "医学・医療編"
    packet["priority"] = group.split()[0]
    return packet
