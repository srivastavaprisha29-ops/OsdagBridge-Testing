"""Compare captured desktop output, PDF text and independently calculated values."""

import argparse
import csv
import json
import re
import subprocess
from pathlib import Path


def read_json(folder, name):
    return json.loads((folder / f"{name}.json").read_text())


def extract(pattern, text):
    return float(re.search(pattern, text).group(1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("material_run", type=Path)
    parser.add_argument("consecutive_runs", type=Path)
    parser.add_argument("register", type=Path)
    args = parser.parse_args()
    run = args.material_run
    inputs = read_json(run, "input-normalized")
    outputs = read_json(run, "output")
    materials = read_json(run, "calculation-materials")
    log = (run / "design.log").read_text()
    report = subprocess.check_output(
        ["pdftotext", "-layout", str(run / "Custom_Material_Design_Report.pdf"), "-"],
        text=True,
    )
    rows = []

    def add(name, expected, actual, unit, tolerance, basis):
        result = "Pass" if abs(expected - actual) <= tolerance else "Fail"
        rows.append([name, round(expected, 6), round(actual, 6), unit, tolerance, result, basis])

    def value(label):
        return extract(re.escape(label) + r"\s+([\d.]+)", report)

    add("Span in report", outputs["geometry.span"], value("Span (m)"),
        "m", 0, "Output Dictionary versus report")
    for key, label, unit in [
        ("girder_spacing", "Girder Spacing (m)", "m"),
        ("deck_thickness", "Deck Thickness (mm)", "mm"),
        ("overall_bridge_width", "Overall Bridge Width (m)", "m"),
    ]:
        add(label, outputs[f"typical_section.{key}"], value(label), unit, 0,
            "Output Dictionary versus report")

    for key, label in [
        ("transverse", "Transverse Wind Force"),
        ("longitudinal", "Longitudinal Wind Force"),
        ("vertical", "Vertical Wind Force"),
    ]:
        add(label, outputs[f"loading.wind_load.computed.{key}_wind_force"],
            value(label), "kN", 0.001, "Output Dictionary versus report")

    seismic_forces = re.findall(r"Horizontal Seismic Force\s+([\d.]+)", report)
    for key, reported in zip(("longitudinal", "transverse"), seismic_forces, strict=True):
        add(f"Seismic force {key}", outputs[f"loading.seismic_load.computed.force_{key}"],
            float(reported), "kN", 0.001,
            "Output Dictionary versus report")

    deck = inputs["typical_section.deck_thickness"] / 1000
    add("250 mm slab dead load", deck * 25,
        extract(r"Deck slab load magnitude: ([\d.]+)", log) / 1000,
        "kN/m²", 0.001, "Thickness × 25 kN/m³ wet concrete")
    last_input = read_json(args.consecutive_runs / "run-3", "inputs")
    multi_log = (args.consecutive_runs / "design.log").read_text()
    last_deck = float(re.findall(r"Deck slab load magnitude: ([\d.]+)", multi_log)[-1])
    add("300 mm slab dead load", last_input["typical_section.deck_thickness"] / 1000 * 25,
        last_deck / 1000, "kN/m²", 0.001, "Thickness × 25 kN/m³ wet concrete")
    add("Wearing-course dead load",
        inputs["typical_section.wearing_course.thickness"] / 1000
        * inputs["typical_section.wearing_course.density"],
        extract(r"Wearing course load magnitude: ([\d.]+)", log) / 1000,
        "kN/m²", 0.001, "Saved thickness × saved unit weight")

    area = extract(r"Self weight line load[^\n]+A=([\d.]+)", log)
    steel_weight = materials["steel"]["rho"] / 1000
    applied_sw = extract(r"Self weight line load[^\n]+: ([\d.]+) N/m", log) / 1000
    add("Girder self-weight from resolved unit weight", area * steel_weight,
        applied_sw, "kN/m", 0.001, "Logged section area × resolved unit weight")
    add("Girder self-weight from entered unit weight", area * inputs["material.girder.density"],
        applied_sw, "kN/m", 0.001, "Logged section area × entered unit weight")
    add("Steel unit weight labelled applied in report", steel_weight,
        value("Steel Self-Weight Applied"), "kN/m³", 0.001,
        "Resolved analysis material versus report")

    add("Analysis overall bridge width",
        inputs["geometry.carriageway_width"] + 2 * inputs["typical_section.crash_barrier.width"],
        extract(r"Bridge width from layout: ([\d.]+)", log), "m", 0.001,
        "Undivided carriageway + two barriers; no median or footpaths")
    add("Crash-barrier line load",
        inputs["typical_section.crash_barrier.area"] * inputs["typical_section.crash_barrier.density"],
        extract(r"Crash barrier line load magnitude: ([\d.]+)", log) / 1000,
        "kN/m", 0.005, "Saved barrier area × saved unit weight")
    add("Crash-barrier load in report",
        outputs["typical_section.crash_barrier.load"],
        value("Crash Barrier Load (kN/m)"), "kN/m", 0.005,
        "Output Dictionary versus report")
    dead_load = extract(r"Seismic inputs: DL=([\d.]+) kN", log)
    ah = extract(r"Seismic loads [^\n]+Ah=([\d.]+)", log)
    add("Horizontal seismic force from logged seismic inputs",
        dead_load * ah, outputs["loading.seismic_load.computed.force_longitudinal"],
        "kN", 0.02, "Logged dead load × horizontal coefficient at zero logged live load")
    pressure = extract(r"Wind loads [^\n]+Pz=([\d.]+)", log)
    add("Hourly wind pressure reported as model input", pressure,
        value("Hourly Wind Pressure, Pz"), "N/m²", 0.05, "Analysis log versus report")
    add("Wind pressure at solver fallback speed",
        value("Hourly Wind Pressure, Pz") * (33 / inputs["loading.wind_load.basic_wind_speed"]) ** 2,
        pressure, "N/m²", 0.05, "Pressure scales with speed squared at fixed exposure")
    add("Girder depth in report table",
        outputs["member_properties.girder_details.section_input.depth.G1.M1"] * 1000,
        extract(r"G1\s+([\d.]+) mm\s+[\d.]+ mm", report), "mm", 0.001,
        "Output Dictionary converted from metres versus report")
    with args.register.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["check", "expected", "observed", "unit", "tolerance", "result", "basis"])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
