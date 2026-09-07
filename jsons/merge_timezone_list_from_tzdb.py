#!/usr/bin/env python3
"""
Build or update timezone_list.json from IANA tzdb tab files.

Recommended inputs (in jsons/tzdb-2026c/):
  - zone1970.tab   canonical timezone list (use this as the primary source)
  - zonenow.tab    optional friendlier labels for current-use zones
  - zone.tab       deprecated; not used by this script

zone1970.tab columns:
    countries (comma-separated ISO 3166-1 alpha-2), coordinates, TZ, comments

zonenow.tab is a coarser, offset-sorted subset for end-user selection. This script
uses it only to improve labels when a timezone appears there.

Output fields per timezone:
    id, label, region, utc_offset_std, dst, countries, coordinates, comment

Usage:
    python merge_timezone_list_from_tzdb.py
    python merge_timezone_list_from_tzdb.py --dry-run
    python merge_timezone_list_from_tzdb.py --refresh
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_ZONE1970 = "tzdb-2026c/zone1970.tab"
DEFAULT_ZONENOW = "tzdb-2026c/zonenow.tab"
DEFAULT_OUTPUT = "timezone_list.json"

REGION_BY_PREFIX = {
    "Africa": "Africa",
    "America": "Americas",
    "Antarctica": "Antarctica",
    "Arctic": "Arctic",
    "Asia": "Asia",
    "Atlantic": "Atlantic",
    "Australia": "Oceania",
    "Europe": "Europe",
    "Indian": "Indian Ocean",
    "Pacific": "Oceania",
    "Etc": "Global",
}


def _text(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def parse_zone1970(tab_path: Path) -> dict[str, dict[str, Any]]:
    zones: dict[str, dict[str, Any]] = {}
    with tab_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue

            countries_raw = _text(parts[0]) or ""
            coordinates = _text(parts[1]) or ""
            tz_id = _text(parts[2])
            if not tz_id:
                continue

            comment = _text(parts[3]) if len(parts) > 3 else None
            countries = [code.strip() for code in countries_raw.split(",") if code.strip()]

            zones[tz_id] = {
                "id": tz_id,
                "countries": countries,
                "coordinates": coordinates,
                "comment": comment,
            }
    return zones


def parse_zonenow_labels(tab_path: Path) -> dict[str, str]:
    labels: dict[str, str] = {}
    if not tab_path.is_file():
        return labels

    with tab_path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 4:
                continue
            tz_id = _text(parts[2])
            label = _text(parts[3])
            if tz_id and label:
                labels[tz_id] = label
    return labels


def latitude_sign(coordinates: str) -> int:
    if not coordinates:
        return 1
    return 1 if coordinates[0] == "+" else -1


def format_utc_offset(offset: timedelta) -> str:
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes = remainder // 60
    return f"{sign}{hours:02d}:{minutes:02d}"


def compute_offset_info(tz_id: str, coordinates: str) -> tuple[str, bool]:
    try:
        tz = ZoneInfo(tz_id)
    except ZoneInfoNotFoundError:
        return "+00:00", False

    jan = datetime(2026, 1, 15, 12, 0, tzinfo=tz)
    jul = datetime(2026, 7, 15, 12, 0, tzinfo=tz)
    jan_offset = jan.utcoffset() or timedelta(0)
    jul_offset = jul.utcoffset() or timedelta(0)

    uses_dst = jan_offset != jul_offset
    if not uses_dst:
        std_offset = jan_offset
    elif latitude_sign(coordinates) >= 0:
        std_offset = min(jan_offset, jul_offset, key=lambda value: value.total_seconds())
    else:
        std_offset = max(jan_offset, jul_offset, key=lambda value: value.total_seconds())

    return format_utc_offset(std_offset), uses_dst


def humanize_timezone_id(tz_id: str) -> str:
    leaf = tz_id.split("/")[-1]
    leaf = leaf.replace("_", " ")
    return re.sub(r"\s+", " ", leaf).strip()


def map_region(tz_id: str) -> str:
    prefix = tz_id.split("/")[0]
    return REGION_BY_PREFIX.get(prefix, prefix)


def choose_label(
    tz_id: str,
    zone1970_comment: str | None,
    zonenow_label: str | None,
) -> str:
    if zonenow_label:
        return zonenow_label
    if zone1970_comment:
        return zone1970_comment
    return humanize_timezone_id(tz_id)


def build_timezone_record(
    tz_id: str,
    zone_data: dict[str, Any],
    zonenow_labels: dict[str, str],
) -> dict[str, Any]:
    coordinates = zone_data.get("coordinates", "")
    utc_offset_std, dst = compute_offset_info(tz_id, coordinates)
    record: dict[str, Any] = {
        "id": tz_id,
        "label": choose_label(
            tz_id,
            zone_data.get("comment"),
            zonenow_labels.get(tz_id),
        ),
        "region": map_region(tz_id),
        "utc_offset_std": utc_offset_std,
        "dst": dst,
        "countries": zone_data.get("countries", []),
        "coordinates": coordinates,
    }
    comment = zone_data.get("comment")
    if comment and comment != record["label"]:
        record["comment"] = comment
    return record


def build_utc_record() -> dict[str, Any]:
    return {
        "id": "UTC",
        "label": "Coordinated Universal Time",
        "region": "Global",
        "utc_offset_std": "+00:00",
        "dst": False,
        "countries": [],
        "coordinates": "+0000+00000",
    }


def merge_timezone_list(
    zone1970: dict[str, dict[str, Any]],
    zonenow_labels: dict[str, str],
    existing: list[dict[str, Any]],
    *,
    refresh: bool,
) -> tuple[list[dict[str, Any]], list[str]]:
    existing_by_id = {
        item["id"]: item
        for item in existing
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }

    merged: list[dict[str, Any]] = []
    added: list[str] = []

    utc_record = existing_by_id.get("UTC") if not refresh else None
    merged.append(utc_record or build_utc_record())
    if "UTC" not in existing_by_id:
        added.append("UTC")

    for tz_id in sorted(zone1970):
        if not refresh and tz_id in existing_by_id:
            merged.append(existing_by_id[tz_id])
            continue

        record = build_timezone_record(tz_id, zone1970[tz_id], zonenow_labels)
        merged.append(record)
        if tz_id not in existing_by_id:
            added.append(tz_id)

    return merged, added


def write_json(path: Path, data: list[dict[str, Any]]) -> None:
    path.write_text(
        json.dumps(data, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate timezone_list.json from IANA tzdb tab files."
    )
    parser.add_argument(
        "--zone1970",
        default=DEFAULT_ZONE1970,
        help=f"Primary tzdb tab file (default: {DEFAULT_ZONE1970}).",
    )
    parser.add_argument(
        "--zonenow",
        default=DEFAULT_ZONENOW,
        help=f"Optional label enrichment tab file (default: {DEFAULT_ZONENOW}).",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output JSON file (default: {DEFAULT_OUTPUT}).",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Rebuild all entries instead of preserving existing ones.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print summary without writing timezone_list.json.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_dir = Path(__file__).resolve().parent
    zone1970_path = base_dir / args.zone1970
    zonenow_path = base_dir / args.zonenow
    output_path = base_dir / args.output

    if not zone1970_path.is_file():
        print(f"Error: zone1970 tab file not found: {zone1970_path}", file=sys.stderr)
        return 1

    zone1970 = parse_zone1970(zone1970_path)
    zonenow_labels = parse_zonenow_labels(zonenow_path)

    existing: list[dict[str, Any]] = []
    if output_path.is_file() and not args.refresh:
        loaded = json.loads(output_path.read_text(encoding="utf-8"))
        if isinstance(loaded, list):
            existing = loaded

    merged, added = merge_timezone_list(
        zone1970,
        zonenow_labels,
        existing,
        refresh=args.refresh,
    )

    print(f"zone1970 timezones parsed: {len(zone1970)}")
    print(f"zonenow labels available:  {len(zonenow_labels)}")
    print(f"Existing JSON entries:     {len(existing)}")
    print(f"Output entries:            {len(merged)}")
    print(f"New entries to add:        {len(added)}")

    if args.dry_run:
        return 0

    write_json(output_path, merged)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
