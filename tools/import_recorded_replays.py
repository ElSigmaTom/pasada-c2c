#!/usr/bin/env python3
"""Import archived SUMO controller/sensor/probe evidence without rerunning SUMO.

The source archives intentionally contain no ordinary-vehicle trajectories or
per-detector occupancy history. Never synthesize those channels from aggregate
queues. Each run retains the original column names, exact event times, native
network/detector IDs, and archive/member hashes.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


SITES = ["J1", "J2", "J3"]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def typed(value: str):
    if value == "":
        return None
    if value in ("True", "False"):
        return value == "True"
    try:
        return float(value) if any(c in value.lower() for c in (".", "e")) else int(value)
    except ValueError:
        return value


def csv_rows(data: bytes):
    # Numeric-looking OSM edge/lane IDs must remain strings; Python's int also
    # accepts underscore-separated digits, so never infer identity columns.
    identities = {"site", "lane", "edge", "row", "role", "aspect", "road", "beacon", "vehicle", "status", "kind", "id", "class"}
    return [{k: v if k in identities else typed(v) for k, v in r.items()} for r in csv.DictReader(io.StringIO(data.decode("utf-8-sig")))]


def shape(value: str | None):
    return [[float(c) for c in point.split(",")] for point in (value or "").split()]


def write_json(path: Path, value, compressed=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")
    path.write_bytes(gzip.compress(data, compresslevel=9, mtime=0) if compressed else data)


class Archive:
    def __init__(self, path: Path):
        self.path = path
        self.sha256 = digest(path.read_bytes())
        self.zip = zipfile.ZipFile(path)
        self.prefix = self.zip.namelist()[0].split("/")[0]

    def member(self, relative: str):
        return self.prefix + "/" + relative

    def read(self, relative: str):
        return self.zip.read(self.member(relative))

    def json(self, relative: str):
        return json.loads(self.read(relative))


def import_geometry(archive: Archive, layout: str):
    sites = SITES if layout == "CORRIDOR" else [layout]
    member = "network/mandaue.net.xml" if layout == "CORRIDOR" else f"network/isolated_{layout}.net.xml"
    network = archive.read(member)
    root = ET.fromstring(network)
    catalog = archive.json("model/sensors/catalog.json")
    tls_to_site = {catalog[s]["tls"]: s for s in sites}
    lane_lookup = {}
    lanes = []
    for edge in root.findall("edge"):
        for lane in edge.findall("lane"):
            record = {
                "id": lane.get("id"), "edge": edge.get("id"),
                "width": float(lane.get("width", "3.2")), "length": float(lane.get("length", "0")),
                "shape": shape(lane.get("shape")), "allow": lane.get("allow"),
                "disallow": lane.get("disallow"), "internal": edge.get("function") == "internal",
            }
            lanes.append(record)
            lane_lookup[record["id"]] = record
    junctions = [
        {"id": j.get("id"), "type": j.get("type"), "x": float(j.get("x")),
         "y": float(j.get("y")), "shape": shape(j.get("shape")), "site": tls_to_site.get(j.get("id"))}
        for j in root.findall("junction")
    ]
    junction_lookup = {j["id"]: j for j in junctions}
    signals = []
    stage_members = {}
    for site in sites:
        tls = catalog[site]["tls"]
        junction = junction_lookup[tls]
        stages = {}
        for period in ("AM", "PM"):
            relative = f"scenarios/{layout}_{period}_fixed.add.xml"
            data = archive.read(relative)
            stage_members[archive.member(relative)] = digest(data)
            logic = next(x for x in ET.fromstring(data).findall("tlLogic") if x.get("id") == tls)
            plans = [{} for _ in range(4)]
            for phase in logic.findall("phase"):
                match = re.fullmatch(rf"{site}_stage(\d+)_(green|yellow|all_red)", phase.get("name", ""))
                if not match:
                    raise ValueError(f"Unrecognized archived phase {phase.attrib}")
                index, kind = int(match[1]), match[2]
                plans[index][kind] = phase.get("state")
                if kind == "green":
                    plans[index]["duration"] = float(phase.get("duration"))
            for index, plan in enumerate(plans):
                upstream = next(r for r in catalog[site]["rows"] if r.get("stage") == index and "upstream_5" in r["roles"])
                plan["approach_edge"] = upstream["edge"]
                assert all(k in plan for k in ("green", "yellow", "all_red", "duration"))
            stages[period] = plans
        links = []
        for conn in root.findall("connection"):
            if conn.get("tl") == tls:
                links.append({"from_lane": conn.get("from") + "_" + conn.get("fromLane"),
                              "to_lane": conn.get("to") + "_" + conn.get("toLane"),
                              "via_lane": conn.get("via"), "link_index": int(conn.get("linkIndex"))})
        signals.append({"site": site, "tls": tls, "x": junction["x"], "y": junction["y"], "stages": stages, "links": links})
    detectors = []
    for record in csv_rows(archive.read("model/sensors/puck_locations.csv")):
        if record["site"] not in sites:
            continue
        row = next(r for r in catalog[record["site"]]["rows"] if r["id"] == record["row"])
        index = row["lanes"].index(record["lane"])
        assert record["lane"] in lane_lookup, record
        detectors.append({"id": record["row"] + f"_L{index}", "site": record["site"], "row": record["row"],
                          "lane": record["lane"], "edge": record["edge"], "pos_m": record["pos_m"],
                          "x": record["x"], "y": record["y"], "roles": record["role"].split(";"),
                          "stage": record["stage"], "requested_offset_m": record["requested_offset_m"],
                          "actual_chainage_m": record["actual_chainage_m"], "shifted": record["shifted"],
                          "occupancy_history": "unreported"})
    assert len({d["id"] for d in detectors}) == len(detectors)
    for s in signals:
        assert all(c["from_lane"] in lane_lookup and c["to_lane"] in lane_lookup for c in s["links"])
    return {"schema": "pasada.recorded-geometry/1", "layout": layout, "location": root.find("location").attrib,
            "lanes": lanes, "junctions": junctions, "signals": signals, "detectors": detectors,
            "provenance": {"archive": archive.path.name, "archive_sha256": archive.sha256,
                           "network_member": archive.member(member), "sha256": digest(network),
                           "additional_members": {archive.member("model/sensors/catalog.json"): digest(archive.read("model/sensors/catalog.json")),
                                                  archive.member("model/sensors/puck_locations.csv"): digest(archive.read("model/sensors/puck_locations.csv")), **stage_members},
                           "network_source": "OpenStreetMap-derived frozen SUMO study network; not the editable C2C planner template.",
                           "attribution": "© OpenStreetMap contributors · https://www.openstreetmap.org/copyright"}}


def import_run(archive: Archive, study: str, case: str, arm: str, seed: int, tag: str | None):
    if study == "ordinary":
        prefix = f"results/paired_nov01/seed{seed}/{case}/{arm}"
        metric_name = "measurement.json"
    else:
        prefix = f"results/emergency_nov01/{tag}/seed{seed}/{case}/{arm}"
        metric_name = "emergency_metrics.json"
    ident = "-".join([study] + ([tag] if tag else []) + [case, arm, str(seed)])
    members = {}
    def read(name):
        data = archive.read(prefix + "/" + name)
        members[archive.member(prefix + "/" + name)] = digest(data)
        return data
    metrics = json.loads(read(metric_name))
    trace = csv_rows(read("sensor_trace.csv"))
    sites = SITES if case.startswith("CORRIDOR") else [case.split("_")[0]]
    obj = {"schema": "pasada.recorded-run/1", "id": ident,
           "sensor_trace": trace, "supervisor_events": json.loads(read("supervisor_events.json")),
           "initial_states": {site: {"time": 0, "stage": 0, "aspect": "green"} for site in sites},
           "approach_queues": [], "probe_positions": [], "beacon_packets": [], "beacon_events": [], "metrics": metrics,
           "unreported_channels": ["per-detector occupancy", "ordinary-vehicle trajectories"],
           "provenance": {"archive": archive.path.name, "archive_sha256": archive.sha256, "members": members,
                          "evidence_type": "Original archived SUMO run observations; not a rerun or a field test.",
                          "interpolation": "Any displayed interpolation between observed samples is visual only."}}
    if study == "ordinary":
        obj["approach_queues"] = csv_rows(read("approach_queues.csv"))
    else:
        obj["probe_positions"] = csv_rows(read("probe_positions.csv"))
        obj["beacon_packets"] = csv_rows(read("beacon_packets.csv"))
        obj["beacon_events"] = json.loads(read("beacon_events.json"))
    horizon = metrics["horizon_s"] if study == "ordinary" else metrics["actual_end_s"]
    assert trace and all(0 <= r["time_s"] <= horizon for r in trace)
    assert all(0 <= p["time_s"] <= horizon for p in obj["probe_positions"])
    meta = {"id": ident, "study": study, "case": case, "layout": case.split("_")[0], "period": case.split("_")[1],
            "arm": arm, "seed": seed, "horizon_s": horizon, "file": f"runs/{ident}.json.gz", "sites": sites,
            "metrics": metrics, "sample_interval_s": 5, "probe_interval_s": 1 if obj["probe_positions"] else None,
            "source_archive": archive.path.name, "source_run_prefix": archive.member(prefix),
            "sample_counts": {key: len(obj[key]) for key in ("sensor_trace", "approach_queues", "probe_positions", "beacon_packets", "beacon_events")},
            "trajectory_channel": "archived emergency probe only" if study == "emergency" else "unreported"}
    if tag:
        meta["tag"] = tag
    return meta, obj


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ordinary", required=True, type=Path)
    parser.add_argument("--emergency", required=True, type=Path)
    parser.add_argument("--output", default=Path(__file__).resolve().parents[1] / "dist/replays", type=Path)
    args = parser.parse_args(argv)
    ordinary, emergency = Archive(args.ordinary), Archive(args.emergency)
    manifest = {"schema": "pasada.recorded-replays/1", "sources": [{"archive": a.path.name, "sha256": a.sha256} for a in (ordinary, emergency)],
                "geometry": {}, "runs": [], "scope": "48 ordinary and 78 emergency original archived runs; pilot excluded.",
                "field_validated": False,
                "unreported_channels": ["per-detector occupancy", "ordinary-vehicle trajectories"],
                "coordinate_system": "Native SUMO planar metres. Geometry is frozen study input, separate from editable installation planning.",
                "signal_semantics": "Recorded four-stage supervisor, 4 s yellow / 4 s all-red, >=10 s minimum green. Exact transition events drive signal display.",
                "detector_semantics": "Canonical study catalog: 46 / 30 / 42 lane detector instances. Requested offsets and shifted actual chainages are retained."}
    for layout in SITES + ["CORRIDOR"]:
        relative = f"geometry/{layout}.json"
        write_json(args.output / relative, import_geometry(ordinary, layout))
        manifest["geometry"][layout] = relative
    protocol = ordinary.json("results/paired_nov01/protocol.json")
    for seed in protocol["seeds"]:
        for case in protocol["cases"]:
            for arm in protocol["controllers"]:
                meta, data = import_run(ordinary, "ordinary", case, arm, seed, None)
                write_json(args.output / meta["file"], data, compressed=True)
                manifest["runs"].append(meta)
    protocol = emergency.json("results/emergency_nov01/protocol.json")
    for case, arm, seed, tag in protocol["tasks"]:
        meta, data = import_run(emergency, "emergency", case, arm, seed, tag)
        write_json(args.output / meta["file"], data, compressed=True)
        manifest["runs"].append(meta)
    assert len(manifest["runs"]) == 126
    assert len({r["id"] for r in manifest["runs"]}) == 126
    write_json(args.output / "manifest.json", manifest)
    print(f"Imported {len(manifest['runs'])} original runs and four native geometries to {args.output}")
    print(f"Archive evidence only; ordinary trajectories and individual puck occupancy remain unreported.")


if __name__ == "__main__":
    main()
