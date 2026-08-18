from __future__ import annotations

from typing import Any


def P(text: str) -> dict[str, Any]:
    return {"kind": "p", "text": text}


def UL(*items: str) -> dict[str, Any]:
    return {"kind": "bullets", "items": list(items)}


def OL(*items: str) -> dict[str, Any]:
    return {"kind": "numbered", "items": list(items)}


def FLOW(*items: str) -> dict[str, Any]:
    return {"kind": "flow", "items": list(items)}


def NOTE(title: str, text: str, tone: str = "info") -> dict[str, Any]:
    return {"kind": "note", "title": title, "text": text, "tone": tone}


def TABLE(headers: list[str], rows: list[list[str]], widths: list[float] | None = None, small: bool = False) -> dict[str, Any]:
    block: dict[str, Any] = {"kind": "table", "headers": headers, "rows": rows}
    if widths:
        block["widths"] = widths
    if small:
        block["small"] = True
    return block


def SEC(title: str, *blocks: dict[str, Any]) -> dict[str, Any]:
    return {"title": title, "blocks": list(blocks)}


def TRAP(claim: str, judge: str, why: str) -> dict[str, str]:
    if judge not in {"○", "×"}:
        raise ValueError(judge)
    return {"claim": claim, "judge": judge, "why": why}


def PACK(
    n: int,
    title: str,
    group: str,
    field: str,
    minutes: str,
    goals: list[str],
    sections: list[dict[str, Any]],
    traps: list[dict[str, str]],
    memory: list[str],
    sources: list[str] | None = None,
) -> dict[str, Any]:
    """Build one study packet with a consistent schema."""
    return {
        "n": n,
        "title": title,
        "group": group,
        "field": field,
        "minutes": minutes,
        "priority": group.split()[0],
        "goals": goals,
        "sections": sections,
        "traps": traps,
        "memory": memory,
        "sources": sources or [],
    }
