#!/usr/bin/env python3
"""
Generate common_iot_service_uuids.json from the Bluetooth SIG service_uuids.yaml.

SIG-defined GATT services are imported verbatim from the official Assigned Numbers
YAML. A small set of well-known community/member 16-bit UUIDs is appended with
explicit source metadata and usage notes.

Default mode preserves existing community entries unless --refresh.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
YAML_PATH = SCRIPT_DIR / "bluetooth_sig_service_uuids.yaml"
JSON_PATH = SCRIPT_DIR / "common_iot_service_uuids.json"

SIG_CATEGORY_BY_ID: dict[str, str] = {
    "gap": "standard",
    "gatt": "standard",
    "immediate_alert": "alert",
    "link_loss": "alert",
    "tx_power": "standard",
    "current_time": "time",
    "reference_time_update": "time",
    "next_dst_change": "time",
    "glucose": "health",
    "health_thermometer": "health",
    "device_information": "standard",
    "heart_rate": "health",
    "phone_alert_status": "alert",
    "battery_service": "standard",
    "blood_pressure": "health",
    "alert_notification": "alert",
    "human_interface_device": "input",
    "scan_parameters": "standard",
    "running_speed_and_cadence": "fitness",
    "automation_io": "home",
    "cycling_speed_and_cadence": "fitness",
    "cycling_power": "fitness",
    "location_and_navigation": "location",
    "environmental_sensing": "sensor",
    "body_composition": "health",
    "user_data": "health",
    "weight_scale": "health",
    "bond_management": "standard",
    "continuous_glucose_monitoring": "health",
    "internet_protocol_support": "data",
    "indoor_positioning": "location",
    "pulse_oximeter": "health",
    "http_proxy": "data",
    "transport_discovery": "standard",
    "object_transfer": "data",
    "fitness_machine": "fitness",
    "mesh_provisioning": "mesh",
    "mesh_proxy": "mesh",
    "reconnection_configuration": "standard",
    "insulin_delivery": "health",
    "binary_sensor": "sensor",
    "emergency_configuration": "standard",
    "authorization_control": "health",
    "physical_activity_monitor": "fitness",
    "elapsed_time": "time",
    "generic_health_sensor": "health",
    "audio_input_control": "audio",
    "volume_control": "audio",
    "volume_offset": "audio",
    "coordinated_set_identification": "audio",
    "device_time": "time",
    "media_control": "audio",
    "generic_media_control": "audio",
    "constant_tone_extension": "audio",
    "telephone_bearer": "audio",
    "generic_telephone_bearer": "audio",
    "microphone_control": "audio",
    "audio_stream_control": "audio",
    "broadcast_audio_scan": "audio",
    "published_audio_capabilities": "audio",
    "basic_audio_announcement": "audio",
    "broadcast_audio_announcement": "audio",
    "common_audio": "audio",
    "hearing_access": "audio",
    "telephony_and_media_audio": "audio",
    "public_broadcast_announcement": "audio",
    "electronic_shelf_label": "home",
    "gaming_audio": "audio",
    "mesh_proxy_solicitation": "mesh",
    "industrial_measurement_device": "sensor",
    "ranging": "location",
    "hid_iso": "input",
    "cookware": "home",
    "voice_assistant": "audio",
    "generic_voice_assistant": "audio",
    "tire_pressure_monitoring_system": "automotive",
}

COMMUNITY_ENTRIES: list[dict[str, str]] = [
    {
        "id": "eddystone",
        "label": "Eddystone",
        "serviceUuid16": "FEAA",
        "category": "beacon",
        "source": "community",
        "member": "Google LLC",
        "comment": (
            "SIG member UUID assigned to Google LLC; widely used for Eddystone "
            "beacon frames. Not a SIG-defined GATT service."
        ),
    },
    {
        "id": "google_fast_pair",
        "label": "Google Fast Pair",
        "serviceUuid16": "FE2C",
        "category": "vendor",
        "source": "community",
        "member": "Google LLC",
        "comment": (
            "SIG member UUID assigned to Google LLC; used by the Fast Pair "
            "protocol. Not a SIG-defined GATT service."
        ),
    },
    {
        "id": "xiaomi_member_uuid",
        "label": "Xiaomi member UUID",
        "serviceUuid16": "FE95",
        "category": "vendor",
        "source": "community",
        "member": "Xiaomi Inc.",
        "comment": (
            "SIG member UUID assigned to Xiaomi Inc. Often seen on Mi Home / "
            "IoT devices, but usage is vendor-defined rather than a SIG GATT "
            "service."
        ),
    },
    {
        "id": "signify_member_uuid",
        "label": "Signify member UUID",
        "serviceUuid16": "FE0F",
        "category": "vendor",
        "source": "community",
        "member": "Signify Netherlands B.V. (formerly Philips Lighting B.V.)",
        "comment": (
            "SIG member UUID assigned to Signify; commonly seen on Philips Hue "
            "devices. Usage is vendor-defined rather than a SIG GATT service."
        ),
    },
    {
        "id": "nordic_uart_service",
        "label": "Nordic UART Service (NUS)",
        "serviceUuid128": "6E400001-B5A3-F393-E0A9-E50E24DCCA9E",
        "category": "vendor",
        "source": "community",
        "member": "Nordic Semiconductor",
        "comment": (
            "Nordic UART Service uses custom 128-bit UUIDs, not a 16-bit SIG "
            "service. Base service UUID shown; TX/RX characteristics use "
            "6E400002-... and 6E400003-...."
        ),
    },
    {
        "id": "ti_sensortag_serial",
        "label": "TI SensorTag serial-like service",
        "serviceUuid16": "FFE0",
        "category": "vendor",
        "source": "community",
        "member": "Texas Instruments",
        "comment": (
            "Commonly associated with TI SensorTag and similar serial-over-BLE "
            "examples. Not the Nordic UART Service and not a SIG-defined GATT "
            "service."
        ),
    },
]


def parse_sig_service_yaml(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line == "uuids:":
            continue

        if line.startswith("- uuid:"):
            if current:
                entries.append(current)
            current = {"uuid": line.split(":", 1)[1].strip()}
            continue

        if line.startswith("name:"):
            value = line.split(":", 1)[1].strip()
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            current["name"] = value
            continue

        if line.startswith("id:"):
            current["id"] = line.split(":", 1)[1].strip()

    if current:
        entries.append(current)

    return entries


def format_uuid16(value: str) -> str:
    number = int(value, 16) if value.lower().startswith("0x") else int(value, 16)
    return f"{number:04X}"


def sig_key(sig_id: str) -> str:
    prefix = "org.bluetooth.service."
    if sig_id.startswith(prefix):
        return sig_id[len(prefix) :]
    return sig_id


def infer_category(sig_id: str) -> str:
    key = sig_key(sig_id)
    return SIG_CATEGORY_BY_ID.get(key, "standard")


def load_sig_services(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        raise FileNotFoundError(f"YAML not found: {path}")

    raw_entries = parse_sig_service_yaml(path.read_text(encoding="utf-8"))
    services: list[dict[str, object]] = []

    for entry in raw_entries:
        sig_id = entry["id"]
        key = sig_key(sig_id)
        services.append(
            {
                "id": key,
                "label": entry["name"],
                "serviceUuid16": format_uuid16(entry["uuid"]),
                "category": infer_category(sig_id),
                "source": "bluetooth_sig",
                "sig_id": sig_id,
            }
        )

    services.sort(key=lambda item: int(str(item["serviceUuid16"]), 16))
    return services


def load_json(path: Path) -> list[dict[str, object]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"expected JSON array in {path}")
    return data


def entry_key(entry: dict[str, object]) -> str:
    if "serviceUuid16" in entry:
        return f"16:{entry['serviceUuid16']}"
    if "serviceUuid128" in entry:
        return f"128:{str(entry['serviceUuid128']).upper()}"
    return f"id:{entry.get('id', '')}"


def merge_entries(
    sig_services: list[dict[str, object]],
    existing: list[dict[str, object]],
    refresh: bool,
) -> list[dict[str, object]]:
    community_defaults = {entry_key(item): item for item in COMMUNITY_ENTRIES}

    if refresh:
        preserved_community = {
            entry_key(item): item
            for item in existing
            if item.get("source") == "community" and entry_key(item) not in community_defaults
        }
        community = {**community_defaults, **preserved_community}
    else:
        existing_community = {
            entry_key(item): item
            for item in existing
            if item.get("source") == "community"
        }
        community = {**community_defaults, **existing_community}

    merged = list(sig_services)
    seen = {entry_key(item) for item in merged}

    for item in community.values():
        key = entry_key(item)
        if key in seen:
            continue
        merged.append(item)
        seen.add(key)

    return merged


def write_json(path: Path, data: list[dict[str, object]]) -> None:
    payload = json.dumps(data, indent=4, ensure_ascii=False)
    payload += "\n"
    path.write_text(payload, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate common_iot_service_uuids.json from Bluetooth SIG YAML"
    )
    parser.add_argument(
        "--yaml",
        type=Path,
        default=YAML_PATH,
        help=f"path to service_uuids.yaml (default: {YAML_PATH.name})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=JSON_PATH,
        help=f"output JSON path (default: {JSON_PATH.name})",
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="replace SIG entries from YAML; reset community entries to defaults",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print merge stats without writing the JSON file",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        sig_services = load_sig_services(args.yaml)
    except (OSError, ValueError) as exc:
        print(f"error reading YAML: {exc}", file=sys.stderr)
        return 1

    existing = load_json(args.output)
    merged = merge_entries(sig_services, existing, refresh=args.refresh)

    sig_count = sum(1 for item in merged if item.get("source") == "bluetooth_sig")
    community_count = sum(1 for item in merged if item.get("source") == "community")

    print(f"sig services: {sig_count}")
    print(f"community entries: {community_count}")
    print(f"total entries: {len(merged)}")

    if args.dry_run:
        print("dry run: no files written")
        return 0

    try:
        write_json(args.output, merged)
    except OSError as exc:
        print(f"error writing JSON: {exc}", file=sys.stderr)
        return 1

    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
